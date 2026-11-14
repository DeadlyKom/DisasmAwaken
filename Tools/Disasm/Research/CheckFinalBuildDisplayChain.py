"""Самостоятельный построитель FINALF, геометрический эталон, полная RAM и стек."""
from collections import Counter
import json

from CheckFinal import ROOT, Simulator, get_registers, original_memory, screen_offset, word
from CheckPreviewCoordinateMultiply import Memory
from skoolkit.simutils import A, B, C, D, E, F, H, IFF, L, PC, R, SP, T


def main():
    base = original_memory()
    memory = Memory(base.copy())
    cpu = Simulator(memory)
    initial = get_registers(dict(PC=0x61DF, SP=0xBFFE, AF=0xA55A,
                                HL=0x8004, DE=0x1357, BC=0x369C,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    bitmap = base[0x6247:0x627B]
    attributes = base[0x627D:0x6294]
    cases = 0

    def check(start, c):
        nonlocal cases
        memory.recording = False
        memory[:] = base
        memory[start:start + 0x2930] = [(i * 37 + c * 11) & 255 for i in range(0x2930)]
        for address, value in ((0x6248, 0xC000), (0x6255, 0x4010), (0x6262, 0xC010),
                               (0x626F, 0x4020), (0x6282, 0x5820)):
            word(memory, address, value)
        expected_memory = memory.copy()
        cursor = start
        counts = Counter()
        for row in range(24):
            for phase in range(8):
                chunk = bitmap.copy()
                offset = screen_offset(8 * row + phase)
                for field, value in ((1, 0xC000 + offset), (14, 0x4010 + offset),
                                     (27, 0xC010 + offset), (40, 0x4020 + offset)):
                    word(chunk, field, value)
                expected_memory[cursor:cursor + 52] = chunk
                counts.update(range(cursor, cursor + 52))
                cursor += 52
            chunk = attributes.copy()
            word(chunk, 5, 0x5820 + 32 * row)
            expected_memory[cursor:cursor + 23] = chunk
            counts.update(range(cursor, cursor + 23))
            cursor += 23
            if row + 1 in (10, 18):
                pointer = 0x62A7 if row + 1 == 10 else 0x62A5
                word(expected_memory, pointer, cursor)
                counts.update((pointer, pointer + 1))
                cursor += 4
        assert cursor == start + 0x2930
        for address, value, multiplicity in ((0x6248, 0xD800, 192), (0x6255, 0x5810, 192),
                                             (0x6262, 0xD810, 192), (0x626F, 0x5820, 192),
                                             (0x6282, 0x5B20, 24), (0xBFF6, 0x622C, 384),
                                             (0xBFF8, 0x61E9, 192), (0xBFFA, 0x61EF, 216),
                                             (0xBFFC, 0x0100 | c, 24)):
            word(expected_memory, address, value)
            counts[address] += multiplicity
            counts[address + 1] += multiplicity
        cpu.registers[:] = initial
        cpu.registers[H], cpu.registers[L] = start >> 8, start & 255
        cpu.registers[C], cpu.registers[F] = c, c
        cpu.registers[IFF] = c & 1
        expected = cpu.registers[:]
        expected[H], expected[L] = 0x5B, 0x20
        expected[D], expected[E] = cursor >> 8, cursor & 255
        expected[B], expected[C] = 0, c
        expected[A], expected[F] = 1, 0x9B
        expected[PC], expected[SP] = 0x3FFF, 0xC000
        memory.writes = []
        memory.recording = True
        minimum_sp = cpu.registers[SP]
        for _ in range(40000):
            if cpu.registers[PC] == 0x3FFF:
                break
            cpu.run()
            minimum_sp = min(minimum_sp, cpu.registers[SP])
        else:
            raise AssertionError(('Не завершён BuildDisplayChain', start, c))
        assert all(cpu.registers[i] == value for i, value in enumerate(expected) if i not in (R, T)), (start, c, cpu.registers, expected)
        assert memory == expected_memory, (start, c, 'RAM')
        assert Counter(address for address, value in memory.writes) == counts, (start, c, 'число записей')
        assert len(memory.writes) == 13756
        assert minimum_sp == 0xBFF6
        cases += 1

    for c in range(256):
        check(0x8004, c)
    for start in (0x7000, 0x9000):
        for c in (0, 1, 31, 63, 127, 128, 254, 255):
            check(start, c)
    report = dict(passed=True, total_cases=cases, all_initial_c_bytes=True,
                  destinations=[0x7000, 0x8004, 0x9000], body_extent=0x2930,
                  copied_bytes=10536, skipped_sync_bytes=8,
                  exact_registers_except_r_t=True, full_64k_final_memory_checked=True,
                  exact_write_counts_per_address=True, writes_per_case=13756,
                  stack_depth_below_entry_sp=8, generated_code_executed=False,
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalBuildDisplayChainVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
