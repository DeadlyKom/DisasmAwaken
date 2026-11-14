"""Контракт исходного IRQ FINALF, общая RAM, защёлка и банковый CPU-стек."""
from collections import Counter
import json

from CheckActionParameterActivation import RecordedBanks
from CheckFinal import ROOT, Simulator, get_registers, original_memory
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import B, C, F, IFF, PC, R, SP, T


def main():
    flat = original_memory()
    banks = [bytearray([0x80 + bank] * 0x4000) for bank in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    banks[2][:] = bytes(flat[0x8000:0xC000])
    memory = RecordedBanks(banks=banks, out7ffd=16)
    cpu = Simulator(memory)
    initial = get_registers(dict(PC=0x616C, SP=0x6194, HL=0x1357,
                                DE=0x2468, BC=0x369C, AF=0xA55A,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    counts = Counter()

    def check(page, flags, old_page=16, stack=0x6194):
        memory.recording = False
        memory.out7ffd(old_page)
        memory[0x6173] = page
        if stack >= 0xC000:
            for bank, data in enumerate(banks):
                data[stack - 0xC000 - 2:stack - 0xC000 + 2] = bytes((0x40 + bank, 0x50 + bank, bank, 0x30))
        else:
            memory[stack], memory[stack + 1] = 255, 63
        cpu.registers[:] = initial
        cpu.registers[F] = flags
        cpu.registers[16:18] = [(page + flags) & 255, flags ^ 0xC3]
        cpu.registers[SP], cpu.registers[R] = stack, flags
        cpu.registers[14], cpu.registers[27] = (page ^ old_page) & 255, flags % 3
        expected = cpu.registers[:]
        expected[B], expected[C] = 0x7F, 0xFD
        expected[SP], expected[IFF] = stack + 2, 1
        expected[R], expected[T] = refresh(flags, 11), 76
        effective = old_page if old_page & 32 else page
        old_bank, new_bank = old_page & 7, effective & 7
        expected[PC] = 0x3FFF if stack < 0xC000 else 0x3000 + new_bank
        pushed = (expected[16], expected[17])
        if stack >= 0xC000 and old_bank != new_bank:
            expected[16:18] = [0x50 + new_bank, 0x40 + new_bank]
        trace = PortTrace(cpu)
        cpu.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        for _ in range(10):
            cpu.run()
        assert cpu.registers == expected, (page, flags, old_page, stack, cpu.registers, expected)
        # Проверка физического банка каждого байта PUSH, рамка может пересекать 7FFF/8000.
        def physical_bank(address):
            return 5 if address < 0x8000 else 2 if address < 0xC000 else old_bank
        assert Counter(memory.writes) == Counter(((physical_bank(stack - 1), (stack - 1) & 0x3FFF, pushed[0]),
                                                 (physical_bank(stack - 2), (stack - 2) & 0x3FFF, pushed[1])))
        assert trace.writes == [(0x7FFD, page)] and memory.o7ffd == effective
        counts['common_locked' if old_page & 32 else 'common_unlocked' if stack < 0xC000 else
               'banked_same' if old_bank == new_bank else 'banked_changed'] += 1

    for page in range(256):
        for flags in range(256):
            check(page, flags)
            check(page, flags, old_page=48)
    for old_bank in range(8):
        for new_bank in range(8):
            check(16 + new_bank, (old_bank * 37 + new_bank * 11) & 255,
                  old_page=16 + old_bank, stack=0xC100)
    # Проверка всех байтов старой и новой защёлки на общей RAM и разорванной рамке PUSH.
    boundary_cases = 0
    for stack in (0x7FFE, 0x8000, 0x8001, 0x8002, 0xBFFE):
        for old_page in range(256):
            for page in range(256):
                check(page, (page * 37 + old_page * 11) & 255, old_page=old_page, stack=stack)
                boundary_cases += 1
    report = dict(passed=True, total_cases=counts.total(), cases=dict(counts),
                  common_stack_boundary_cases=boundary_cases,
                  common_stack_addresses=[0x7FFE,0x8000,0x8001,0x8002,0xBFFE],
                  all_old_and_new_latch_bytes_at_each_common_stack=True,
                  split_push_across_bank5_bank2_checked=True,
                  I_IM_preservation_checked=True,
                  exact_registers_flags_r_t=True, exact_two_stack_writes=True,
                  irq_entry_and_nested_interrupts_executed=False,
                  banking_stack_precondition_demonstrated=True,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalInterruptContractVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
