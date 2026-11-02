"""Проверка F094 при каждом 16-битовом положении и повторном XOR."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsMarker import marker


def main():
    base = base_memory()
    memory = Memory(base)
    simulator = Simulator(memory)
    cases = 0
    # Проверка каждого исходного положения, включая потерю переноса при INC L и DEC L.
    for position in range(65536):
        memory.recording = False
        memory[:] = base
        memory[0x9B19:0x9B1B] = [position & 255, position >> 8]
        memory[0xBFFE:0xC000] = [255, 63]
        expected = list(memory)
        planned = marker(expected, position)
        initial = get_registers({'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            'AF': position, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'PC': 0xF094, 'SP': 0xBFFE}, None, False)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(110):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат', position))
        memory.recording = False
        assert memory == expected, ('память', position)
        assert sorted(memory.writes) == sorted((address, expected[address]) for address, _ in planned), ('записи', position)
        registers = simulator.registers
        assert registers[SP] == 0xC000 and registers[2:4] == [0, 32]
        assert all(registers[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27, *range(16, 24)))
        assert registers[4] * 256 + registers[5] == 0xF0ED + 4 * (position & 7)
        assert registers[6] * 256 + registers[7] == planned[7][0]
        cases += 1
    # Проверка инволюции отдельно, запись позиции внутри самой области маркера не подменяется предположением.
    involutions = 0
    for position in range(0, 65536, 7):
        memory = list(base)
        before = list(memory)
        marker(memory, position)
        marker(memory, position)
        assert memory == before
        involutions += 1
    report = dict(passed=True, original_position_cases=cases, reference_double_xor_cases=involutions,
        every_memory_byte_and_write_checked=True, exact_write_set=True, all_eight_mask_phases=True,
        low_byte_wrap_preserved=True, original_instructions=True, exact_primary_outputs_except_af=True,
        alternate_and_index_registers_preserved=True, marker_position_may_overlap_target=True,
        native_execution=False, irq_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsMarkerVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
