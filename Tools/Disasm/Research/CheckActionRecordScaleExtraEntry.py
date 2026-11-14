"""Проверка условного дополнительного удвоения E59F с исходным JR E59D."""

import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, Simulator, get_registers
from CheckScreenUpdate import PortTrace


ENTRY = 0xE59F
NEXT = 0xE5A0


def main():
    flat = flat_action()
    assert flat[ENTRY:NEXT] == [0x29]
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = flat[start:start + 0x4000]
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    pointers = [flat[address] | flat[address + 1] << 8 for address in range(0x9E00, 0x9F00, 2)]
    assert set(objects[pointer - 0xC000 + 1] for pointer in pointers) == {1, 2, 3, 4, 5}
    memory = RecordedBanks(banks=banks, out7ffd=16)
    simulator = Simulator(memory)

    # Проверка маршрута от настоящего чтения заголовка для обоих путей класса.
    header_address = pointers[0] - 0xC000 + 1
    for code in (0, 0x14):
        memory.banks[0][:] = flat[0xC000:]
        memory.banks[4][header_address] = 6
        memory[0xA106], memory[0xA112] = 0, code
        initial = get_registers({'PC': 0xE55C, 'IX': 0xA100, 'SP': 0xBFFE}, None, False)
        simulator.registers[:] = initial
        ports = PortTrace(simulator)
        simulator.set_tracer(ports)
        simulator.run(stop=ENTRY)
        assert memory[0xE59E] == 0 and simulator.registers[6:8] == [0, 200]
        assert ports.writes == [(0x7FFD, 20), (0x7FFD, 16)]
        simulator.run()
        assert simulator.registers[PC] == NEXT and simulator.registers[6:8] == [1, 144]
    memory.banks[4][header_address] = objects[header_address]

    # Расчёт 16-битного удвоения, переноса и всех сохраняемых флагов.
    memory.recording = True
    memory.writes = []
    for value in range(65536):
        old_flags = (value ^ (value >> 8)) & 255
        initial = get_registers({'PC': ENTRY, 'HL': value, 'AF': 0x5A00 | old_flags,
                                 'DE': 0x2468, 'BC': 0x369C, 'IX': 0xA100, 'IY': 0x5C3A,
                                 'R': value & 255, 'SP': 0xBFFE}, None, False)
        simulator.registers[:] = initial
        simulator.run()
        result = (value * 2) & 65535
        expected = initial.copy()
        expected[6:8] = [result >> 8, result & 255]
        expected[1] = ((old_flags & 0xC4) | ((result >> 8) & 0x28) |
                       (0x10 if value & 0x0800 else 0) | (value >> 15))
        expected[15] = (initial[15] & 128) | ((initial[15] + 1) & 127)
        expected[PC] = NEXT
        assert all(simulator.registers[i] == expected[i] for i in range(len(expected)) if i != 25)
    assert not memory.writes
    report = dict(passed=True, total_cases=65538, all_HL_words=65536,
                  modified_header_profiles=2, original_header_values=[1, 2, 3, 4, 5],
                  extra_entry=ENTRY, continuation=NEXT, original_game_path_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionRecordScaleExtraEntryVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
