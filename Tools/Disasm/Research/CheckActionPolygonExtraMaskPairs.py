"""Проверка дополнительных индексов D511 по исходным байтам и трассе чтений."""

from collections import Counter
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionPolygonFill import fill


class MaskMemory(RecordedBanks):
    def __getitem__(self, index):
        value = super().__getitem__(index)
        if self.recording and isinstance(index, int):
            if 0x8C00 <= index < 0x8E00 or 0xD10A <= index < 0xD110:
                self.reads.append((index, value))
        return value


def check_overlay(flat):
    base = [bytearray(0x4000) for _ in range(8)]
    for bank, origin in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        base[bank][:] = flat[origin:origin + 0x4000]
    memory = MaskMemory(banks=[bytearray(b) for b in base], out7ffd=16)
    simulator = Simulator(memory)
    touched = set()
    cases = 0
    for mode in (5, 6, 7):
        for left_phase in range(8):
            for right_phase in range(8):
                for first_row in (0, 7):
                    x_left, x_right = 8 + left_phase, 48 + right_phase
                    vertices = ((first_row, x_left), (first_row, x_right),
                                (first_row + 2, x_right), (first_row + 2, x_left))
                    for bank in (0, 2):
                        memory.banks[bank][:] = base[bank]
                    memory.banks[2][:3072] = bytes((i * 37 + cases) & 255 for i in range(3072))
                    for index, (row, column) in enumerate(vertices):
                        memory[0x9000 + 2 * index], memory[0x9001 + 2 * index] = column, row
                    memory[0x9BA3], memory[0xD560] = 2 * len(vertices), mode
                    memory[0xBFFE], memory[0xBFFF] = 255, 63
                    simulator.registers[:] = get_registers(
                        {'PC': 0xD511, 'SP': 0xBFFE, 'HL': 0x1357}, None, False)
                    expected_ram, expected_writes = fill(memory.banks, vertices, mode)
                    pattern_address = 0xD100 + 2 * mode
                    expected_reads = [(a, flat[a]) for a in (pattern_address, pattern_address + 1)]
                    for page in (0x8C00, 0x8D00):
                        left = page + 32 * left_phase + 2 * mode
                        right = page + 32 * right_phase + 16 + 2 * mode
                        expected_reads.extend((a, flat[a]) for a in (left, left + 1, right, right + 1))
                        touched.update((left, left + 1, right, right + 1))
                    memory.reads, memory.writes = [], []
                    memory.recording = True
                    for _ in range(10000):
                        if simulator.registers[PC] == 0x3FFF:
                            break
                        simulator.run()
                    else:
                        raise AssertionError(('возврат D511', vertices, mode))
                    memory.recording = False
                    assert simulator.registers[SP] == 0xC000
                    assert memory.reads == expected_reads, (vertices, mode, memory.reads, expected_reads)
                    assert memory.banks == expected_ram, (vertices, mode, 'RAM')
                    assert Counter(memory.writes) == Counter(expected_writes), (vertices, mode, 'записи')
                    cases += 1
    return cases, touched


def main():
    extracted = ROOT / 'Tools/Disasm/Extracted/Active'
    flat = flat_action()
    initial_mask_pages = bytes(flat[0x8C00:0x8E00])
    for name in ('06_D3D.C.bin', '18_DATAS.C.bin'):
        assert (extracted / name).read_bytes()[:512] == initial_mask_pages
    overlay = (extracted / '19_3DPART.C.bin').read_bytes()
    assert overlay == bytes(flat[0xC000:0xC000 + len(overlay)])
    three_d = list(flat)
    three_d[0xC000:0xC000 + len(overlay)] = overlay
    action_cases, action_bytes = check_overlay(flat)
    overlay_cases, overlay_bytes = check_overlay(three_d)
    assert action_bytes == overlay_bytes and len(action_bytes) == 192
    report = dict(passed=True, action_cases=action_cases, three_d_cases=overlay_cases,
                  shared_pages_original_bytes=512, selected_extra_mask_bytes=len(action_bytes),
                  selected_pattern_bytes=bytes(flat[0xD10A:0xD110]).hex(),
                  mask_addresses=sorted(action_bytes), geometry_and_gameplay_for_modes_5_to_7_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionPolygonExtraMaskPairsVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'mask_addresses'}, indent=2))


if __name__ == '__main__':
    main()
