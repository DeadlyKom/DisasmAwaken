"""Обёртка построителя FINALF, точная подготовка, реальный ребёнок и завершающие записи."""
from collections import Counter
import json

from CheckFinal import ROOT, Simulator, get_registers, original_memory, word
from CheckPreviewCoordinateMultiply import Memory
from skoolkit.simutils import A, B, C, D, E, F, H, IFF, L, PC, R, SP, T


def main():
    base = original_memory()
    memory = Memory(base.copy())
    cpu = Simulator(memory)
    cases = 0
    for stack in (0x7FFE, 0xBFFE):
        for c in range(256):
            memory.recording = False
            memory[:] = base
            word(memory, stack, 0x3FFF)
            parameters = ((0x6248, 0xC000), (0x6255, 0x4010), (0x6262, 0xC010),
                          (0x626F, 0x4020), (0x6282, 0x5820), (0x6235, 0x627D), (0x6238, 23))
            for pointer, value in parameters:
                word(memory, pointer, 0xA55A)
            memory[0x8002:0x8004] = [c, c ^ 255]
            memory[0xA935:0xA937] = [c ^ 0x5A, c ^ 0xA5]
            initial = get_registers(dict(PC=0x6196, SP=stack, AF=(c << 8) | (c ^ 0xA5),
                                        HL=0x1357, DE=0x2468, BC=0x3600 | c,
                                        IX=0xABCD, IY=0x5C3A,
                                        **{'^AF': 0xDEF0, '^HL': 0x1234,
                                           '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
            initial[IFF] = c & 1
            expected = initial.copy()
            expected[H], expected[L] = 0x80, 4
            expected[SP], expected[PC], expected[IFF] = stack - 4, 0x61DF, 0
            expected_memory = memory.copy()
            writes = []
            for pointer, value in (*parameters, (stack - 2, 0x8002), (stack - 4, 0x61D0)):
                word(expected_memory, pointer, value)
                writes += [(pointer, value & 255), (pointer + 1, value >> 8)]
            expected_memory[0x8000:0x8002] = [0xED, 0x73]
            writes += [(0x8000, 0xED), (0x8001, 0x73)]
            cpu.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(50):
                if cpu.registers[PC] == 0x61DF:
                    break
                cpu.run()
            else:
                raise AssertionError('Не достигнут вызов BuildDisplayChain')
            assert all(cpu.registers[i] == value for i, value in enumerate(expected) if i not in (R, T))
            assert memory == expected_memory and Counter(memory.writes) == Counter(writes)
            minimum_sp = cpu.registers[SP]
            for _ in range(40000):
                if cpu.registers[PC] == 0x61D0:
                    break
                cpu.run()
                minimum_sp = min(minimum_sp, cpu.registers[SP])
            else:
                raise AssertionError('Не завершён настоящий BuildDisplayChain')
            assert minimum_sp == stack - 12
            assert memory[0x8002:0x8004] == [c, c ^ 255]
            assert memory[0xA935:0xA937] == [c ^ 0x5A, c ^ 0xA5]
            assert cpu.registers[H:L + 1] == [0x5B, 0x20]
            assert cpu.registers[D:E + 1] == [0xA9, 0x34]
            assert cpu.registers[B:C + 1] == [0, c]
            assert (cpu.registers[A], cpu.registers[F]) == (1, 0x9B)
            expected = cpu.registers.copy()
            expected[H], expected[L], expected[D], expected[E] = 0xA9, 0x37, 0x80, 3
            expected[SP], expected[PC] = stack + 2, 0x3FFF
            expected_memory = memory.copy()
            writes = [(0xA934, 0x31), (0x8002, 0x35), (0x8003, 0xA9), (0xA937, 0xC9)]
            for address, value in writes:
                expected_memory[address] = value
            memory.writes = []
            for _ in range(13):
                cpu.run()
            assert all(cpu.registers[i] == value for i, value in enumerate(expected) if i not in (R, T))
            assert memory == expected_memory and Counter(memory.writes) == Counter(writes)
            assert memory[0xA935:0xA937] == [c ^ 0x5A, c ^ 0xA5]
            cases += 1
    report = dict(passed=True, total_cases=cases, all_initial_c_bytes=True,
                  entry_stack_locations=[0x7FFE, 0xBFFE], child_executed=True,
                  independent_prelude_and_postlude=True,
                  exact_registers_except_r_t=True, full_ram_and_write_multiplicity_checked=True,
                  restore_sp_operand_preserved_until_generated_execution=True,
                  stack_depth_below_entry_sp=12, generated_code_executed=False,
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalPrepareFrameContractVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
