"""Прямой вход C882 при разных числах страниц и начальных символьных строках экрана."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsTextDisplay import pixel_address
from ControlsBufferCopyRegisters import expected_registers, check_registers


def main():
    base = base_memory()
    memory = Memory(base)
    simulator = Simulator(memory)
    cases = 0
    # Проверка всех допустимых непустых отрезков символьных строк внутри одной трети экрана.
    for third in range(3):
        for row in range(8):
            for count in range(1, 9 - row):
                for profile in range(16):
                    memory.recording = False
                    memory[:] = base
                    source = 0x8000 + profile * 256
                    for offset in range(0x3000):
                        memory[0x8000 + offset] = (offset * 73 + (offset >> 5) * 31 + profile * 17) & 255
                    for address in range(0x4000, 0x5B00):
                        memory[address] = (address * 29 + profile * 13) & 255
                    memory[0xBFFE:0xC000] = [255, 63]
                    expected = list(memory)
                    destination = 0x400F + third * 2048 + row * 32
                    for y in range(count * 8):
                        target = pixel_address(third * 64 + row * 8 + y, 0)
                        expected[target:target + 32] = memory[source + y * 32:source + y * 32 + 32]
                    initial = get_registers({'AF': count * 256 + profile * 17, 'HL': source,
                        'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0, '^HL': destination,
                        '^DE': 0x5678, '^BC': 0x9ABC, 'IX': 0xABCD, 'IY': 0x5C3A,
                        'PC': 0xC882, 'SP': 0xBFFE}, None, False)
                    initial[14], initial[26], initial[27] = profile, profile & 1, profile % 3
                    simulator.registers[:] = initial
                    memory.writes = []
                    memory.recording = True
                    for _ in range(7000):
                        if simulator.registers[PC] == 0x3FFF:
                            break
                        simulator.run()
                    else:
                        raise AssertionError(('возврат', third, row, count, profile))
                    memory.recording = False
                    excluded = {0xCA84, 0xCA8A, 0xCA8B}
                    assert all(memory[a] == expected[a] for a in range(65536) if a not in excluded), ('память', third, row, count, profile)
                    pixels = [(a, v) for a, v in memory.writes if 0x4000 <= a < 0x5800]
                    assert len(pixels) == len({a for a, _ in pixels}) == count * 256
                    assert len(memory.writes) == count * 257 + 2
                    r = simulator.registers
                    assert r[SP] == 0xC000 and r[6] * 256 + r[7] == source + 256 * count
                    assert r[22] * 256 + r[23] == destination + 32 * count
                    assert memory[0xCA84] == 1 and memory[0xCA8A:0xCA8C] == [254, 191]
                    assert all(r[i] == initial[i] for i in (14, 26, 27))
                    check_registers(r, expected_registers(initial, expected, source, destination, count))
                    cases += 1
    report = dict(passed=True, direct_worker_calls=cases, all_screen_thirds=True,
        all_nonempty_character_row_intervals=True, source_page_profiles=16,
        exact_screen_and_other_ram_checked=True, exact_pixel_write_set=True,
        original_instructions=True, no_call_stubs=True, all_documented_register_outputs_checked=True,
        exact_main_and_alternate_flags_checked=True,
        contract_source_page_aligned=True, contract_destination_within_one_screen_third=True,
        zero_count_proved=False, crossing_screen_third_proved=False,
        irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyWorkerVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
