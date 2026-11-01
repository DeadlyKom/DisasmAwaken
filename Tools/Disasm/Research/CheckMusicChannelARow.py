"""Оригинальные байты входа тика и подготовки A, без исполнения синтеза и сборки."""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    memory = [0xA5] * 65536
    memory[0xDB00:0xDB00 + len(raw)] = raw
    simulator = Simulator(memory)
    cases = 0
    samples = [(v, (v * 257) ^ 0x5AA5, (v * 127 + 1) & 65535,
                (v * 31) & 65535) for v in range(256)]
    samples += [(v, 0x1234, 0x5678, step) for v in (0, 1, 255)
                for step in (0, 1, 0x7FFF, 0x8000, 0xA55A, 0xFFFF)]
    # Проверка всех сочетаний пропускаемых блоков и изменяемых команд сброса и разрешения.
    for value, sample, ornament, step in samples:
        for bits in range(32):
            volume = value ^ 0xA5
            envelope = value ^ 0x5A
            target = (value + 19) & 255
            delay = (value * 73 + 7) & 255
            branch = 0x1D if value & 1 else 0
            memory[0xDE1F] = 1
            for n, address in enumerate((0xDE31, 0xDE61, 0xDE72)):
                memory[address] = 6 if bits & (1 << n) else 0x18
            memory[0xDE48] = 0x2F if bits & 8 else 0
            memory[0xDE2E] = 1 if bits & 16 else 0x22
            for address, operand in ((0xDE4D, value), (0xDE5D, volume), (0xDE6E, envelope),
                                     (0xDE75, target), (0xDE7A, delay), (0xDE88, branch)):
                memory[address] = operand
            for address, operand in ((0xDE52, sample), (0xDE68, ornament), (0xDE82, step)):
                memory[address:address + 2] = [operand & 255, operand >> 8]
            for address in (0xDFFA, 0xE03E, 0xE055, 0xE07C, 0xE09F, 0xE0D7, 0xE06C,
                            0xE06D, 0xDFEF, 0xE0BB, 0xDFF6, 0xDFF7, 0xE011, 0xE02D,
                            0xE078, 0xE079, 0xE037, 0xE0B3, 0xE0CE, 0xE0A8, 0xE0A9,
                            0xE0AF, 0xE098, 0xE099):
                memory[address] = 0xA5
            initial = get_registers({'HL': 0x1357, 'DE': 0xABCD, 'BC': 0x2468,
                'AF': 0x9800 | value, 'IX': 0x369C, 'IY': 0x5C3A, '^HL': 0x1234,
                '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0,
                'SP': 0xBFFE, 'PC': 0xDE1F}, None, False)
            before = memory.copy()
            simulator.registers[:] = initial
            for _ in range(90):
                if simulator.registers[PC] == 0xDE90:
                    break
                simulator.run()
            else:
                raise AssertionError('channel_a_row_continuation')
            expected = before.copy()
            expected[0xDE1F] = 0xC3
            expected[0xE02D] = volume
            hl, b, c, f, a = 0, 0xE0 if bits & 16 else 0x9A, 0x98 if bits & 16 else 0xBC, 0x44, volume
            if not bits & 16:
                expected[0xE098:0xE09A] = [0, 0]
            if bits & 1:
                for address in (0xDFFA, 0xE03E, 0xE055, 0xE07C, 0xE09F, 0xE0D7, 0xE06C, 0xE06D):
                    expected[address] = 0
                expected[0xDFEF] = 0xFF if bits & 8 else 0
                expected[0xE0BB] = value
                expected[0xDFF6:0xDFF8] = [sample & 255, sample >> 8]
                expected[0xE011] = 0x10
                hl, b, f = sample, 0x29, 0x7E if bits & 8 else 0x44
            if bits & 2:
                expected[0xE07C] = 0
                expected[0xE078:0xE07A] = [ornament & 255, ornament >> 8]
                expected[0xE037] = envelope
                hl, b, f, a = ornament, 0x0F, 0x44, envelope
            if bits & 4:
                expected[0xE0B3] = target
                expected[0xE09F] = expected[0xE0CE] = delay
                expected[0xE0A8:0xE0AA] = [step & 255, step >> 8]
                expected[0xE0AF] = branch
                expected[0xE0D7] = 0
                hl, b, f, a = step, 0x1C, 0x44, 0
            registers = simulator.registers
            assert memory == expected, ('memory', value, bits)
            assert registers[:8] == [a, f, b, c, 6, 0x18, hl >> 8, hl & 255], ('main', value, bits, registers[:8])
            assert registers[16:24] == [0xDE, 0xF0, 0xDF, 0xE3, 0xAB, 0xCD, 0x13, 0x57], ('alternate', registers[16:24])
            assert all(registers[i] == initial[i] for i in (8, 9, 10, 11, SP, 14, 26, 27))
            cases += 1
    # Проверка прямого JP с каждым входным F, до первой инструкции синтеза.
    for flags in range(256):
        memory[0xDE1F] = 0xC3
        initial = get_registers({'HL': 0x1357, 'DE': 0xABCD, 'BC': 0x2468,
            'AF': 0x9800 | flags, 'IX': 0x369C, 'IY': 0x5C3A, '^HL': 0x1234,
            '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'SP': 0xBFFE, 'PC': 0xDE1F}, None, False)
        before = memory.copy()
        simulator.registers[:] = initial
        simulator.run()
        registers = simulator.registers
        assert registers[PC] == 0xDFE3 and memory == before
        assert all(registers[i] == initial[i] for i in (*range(12), SP, 14, *range(16, 24), 26, 27))
    report = dict(passed=True, row_cases=cases, direct_jump_cases=256,
        all_gate_enable_reset_combinations=True, all_memory_compared=True,
        main_and_alternate_registers_checked=True, entry_ld_bc_and_exx_checked=True,
        control_gates_not_self_cleared=True, stop_addresses=[0xDE90, 0xDFE3],
        irq_executed=False, synthesis_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicChannelARowVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
