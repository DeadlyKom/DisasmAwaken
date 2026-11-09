"""DD87, восстановление векторов и списков, изменяемый опкод и настоящая активация параметров."""
from collections import Counter
import json

from CheckActionOverlappingKeyClipReturns import run_to
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsEvenSpan import and_flags
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put


def main():
    flat = flat_action()
    baseline = [bytearray([160 + page] * 16384) for page in range(8)]
    for page, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[page][:] = flat[start:start + 16384]
    baseline[1][:] = base_memory()[0xC000:]
    assert flat[0x7B60:0x7B63] == [0x3E, 0, 0x3D]
    counts = Counter()
    compared = (*range(13), 14, *range(16, 25), 26, 27)

    for equipment in range(256):
        for fold in range(8):
            object_count = (equipment + fold) % 26
            effect_count = (equipment + 2 * fold) % 9
            control = (equipment + fold) & 255
            first = 0x4B38
            low = 0xF0 | ((first & 255) ^ (first >> 8) ^ 0x4A ^ fold) & 7
            second = 0x4A00 | low
            memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=0x11)
            memory[0x9C30] = equipment
            put(memory, 0x9BC6, first.to_bytes(2, 'little') + second.to_bytes(2, 'little') + bytes((control,)))
            for index in range(object_count):
                start = 0xA100 + index * 64
                put(memory, start, (0x80 if index & 1 else index, index))
                memory[start + 0x18] = index
            object_end = 0xA100 + object_count * 64
            put(memory, object_end, (0x80, 0x80))
            for index in range(effect_count):
                memory[0xA795 + index * 18 + 7] = (equipment + index) & 127
            effect_end = 0xA795 + effect_count * 18
            memory[effect_end + 7] = 0x80 | fold
            put(memory, 0xBFFE, (255, 63))
            simulator = Simulator(memory)
            ports = PortTrace(simulator)
            simulator.set_tracer(ports)
            initial = get_registers({'PC': 0xDD87, 'SP': 0xBFFE, 'HL': 0x4567, 'DE': 0x89AB,
                                     'BC': 0xCDEF, 'AF': equipment * 257, 'IX': 0x1111, 'IY': 0x2222,
                                     '^HL': 0x3344, '^DE': 0x5566, '^BC': 0x7788, '^AF': 0x99AA}, None, False)
            simulator.registers[:] = initial
            expected = RecordedBanks(banks=[bank.copy() for bank in memory.banks], out7ffd=0x11)
            expected.writes = []
            expected.recording = True

            # Сначала проверяются точные записи префикса, дочерние процедуры подключаются после границы DE0A.
            put(expected, 0x9B76, (0, 2 if equipment == 255 else 17))
            put(expected, 0x9B70, (0, 0))
            put(expected, 0x9B73, (0, 0))
            template = 0xDF91 if equipment == 255 else 0xDFD9
            put(expected, 0x9B27, expected[template:template + 72])
            for start in range(0xA100, object_end, 64):
                put(expected, start, (0, 128))
                expected[start + 0x18] = 255
            for start in range(0xA795, effect_end, 18):
                expected[start + 7] = 0
            put(expected, 0x9BC1, expected[0x9BC6:0x9BCB])
            opcode = fold or 0xC9
            expected[0x7B60] = opcode
            wanted = list(initial)
            wanted[:8] = [opcode, and_flags(fold), 0, opcode, first >> 8, first & 255, second >> 8, second & 255]
            wanted[8:12] = [effect_end >> 8, effect_end & 255, object_end >> 8, object_end & 255]
            wanted[PC] = 0xDE0A
            memory.writes = []
            memory.recording = True
            run_to(simulator, 0xDE0A, 3000)
            actual = simulator.registers
            assert all(actual[index] == wanted[index] for index in compared), (equipment, fold, actual[:13], wanted[:13])
            assert memory.banks == expected.banks and memory.writes == expected.writes
            assert not ports.writes and actual[SP] == 0xBFFE

            # Настоящая композиция с уже проверенным DE0A до внешнего возврата.
            child = Simulator(expected)
            wanted[15], wanted[25] = actual[15], actual[25]
            child.registers[:] = wanted
            child_ports = PortTrace(child)
            child.set_tracer(child_ports)
            run_to(child, 0x3FFF, 30000)
            run_to(simulator, 0x3FFF, 30000)
            assert actual == child.registers and actual[SP] == 0xC000
            assert memory.banks == expected.banks and memory.writes == expected.writes
            assert ports.writes == child_ports.writes == [(0x7FFD, 0x10)]
            assert memory.o7ffd == 0x10 and memory[0x7B60] == opcode
            counts[f'{opcode:02X}'] += 1

    assert set(counts) == {'C9', *(f'{value:02X}' for value in range(1, 8))}
    result = dict(passed=True, total_cases=counts.total(), opcode_profiles=dict(counts),
                  all_equipment_bytes_and_fold_values=True, prefix_expected_registers_except_R_T=True,
                  all_eight_banks_and_ordered_writes_compared=True,
                  real_parameter_build_and_activation_executed=True, final_page=16,
                  patched_opcode_executed=False, legacy_caller_actual_game_relocation_proved=False,
                  irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsResetFlightContextVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
