"""Точный договор обёртки #6DD1 до продолжения обхода эффектов."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import run_to
from ReferenceActionLogRatio import EXP, LOG
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import A, B, C, D, E, F, H, IFF, IXh, IXl, L, PC, R, SP, T, get_registers


ENTRY, CONTINUE, DRAW, AFTER_DRAW = 0x6DD1, 0x6D4C, 0xFA3A, 0x6E21
SAVED_SP, EFFECT = 0xBFFC, 0xA795
OUTPUTS = (0xD9B6, 0xD7C4, 0xD7A2)


def or_flags(value):
    return (value & 0xA8) | (0x40 if value == 0 else 0) | (4 if value.bit_count() % 2 == 0 else 0)


def main():
    flat, voxel = flat_action(), memory_image()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, origin in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[origin:origin + 0x4000])
    banks[3][:] = bytes(voxel[0xC000:])
    banks[2][0x1100:0x1200] = bytes(word & 255 for word in LOG)
    banks[2][0x1200:0x1300] = bytes(word >> 8 for word in LOG)
    banks[2][0x1300:0x1400] = bytes(EXP)
    memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=16)
    cpu = Simulator(memory)
    compared = [index for index in range(len(cpu.registers)) if index not in (R, T)]
    initial = get_registers(dict(PC=ENTRY, SP=0x8EFF, HL=0x1357, DE=0x2468, BC=0x369C,
                                 AF=0xA55A, IX=EFFECT, IY=0x5C3A,
                                 **{'^HL': 0x789A, '^DE': 0xBCDE, '^BC': 0xF012, '^AF': 0x7E69}),
                            {'iff': 1, 'im': 2}, False)
    counts = Counter()

    def prepare(flags, depth, *, x=0x0123, y=0xFFE7, mode=0, size=12):
        memory.recording = False
        for bank, original in zip(memory.banks, banks, strict=True):
            bank[:] = original
        memory.out7ffd(16)
        put(memory, ENTRY + 1, SAVED_SP.to_bytes(2, 'little'))
        for address, value in zip(OUTPUTS, (x, y, depth), strict=True):
            put(memory, address, value.to_bytes(2, 'little'))
        memory[EFFECT + 6] = mode
        put(memory, EFFECT + 8, (0xD800 if size == 12 else 0xC400).to_bytes(2, 'little'))
        put(memory, EFFECT + 16, bytes((size, size)))
        cpu.registers[:] = initial
        cpu.registers[F] = flags
        cpu.registers[R] = flags
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.writes = []
        memory.recording = True
        return ports

    for flags, depth in product(range(256), (0, 1, 0x80, 0x7FFF, 0x8000, 0xFFFF)):
        if not flags & 4 and 0 < depth < 0x8000:
            continue
        ports = prepare(flags, depth)
        expected = cpu.registers[:]
        expected[SP], expected[PC] = SAVED_SP, CONTINUE
        if flags & 4:
            m1, outcome = 2, 'overflow'
        elif depth & 0x8000:
            expected[B], expected[C] = depth >> 8, depth & 255
            expected[F] = ((depth >> 8) & 0xA8) | 0x10 | (flags & 1)
            m1, outcome = 7, 'negative_depth'
        else:
            expected[A], expected[F], expected[B], expected[C] = 0, 0x44, 0, 0
            m1, outcome = 10, 'zero_depth'
        run_to(cpu, CONTINUE)
        expected[R], expected[T] = refresh(flags, m1), cpu.registers[T]
        assert cpu.registers == expected
        assert not memory.writes and not ports.writes and memory.o7ffd == 16
        counts[outcome] += 1

    for mode, size, depth, x, y in product(range(7), (12, 20), (1, 0x100, 0x7FFF),
                                           (0, 0x7FFF), (0, 0xFFFF)):
        ports = prepare(0x81, depth, x=x, y=y, mode=mode, size=size)
        run_to(cpu, DRAW)
        registers = cpu.registers
        assert registers[A] == mode and registers[F] == or_flags((depth >> 8) | (depth & 255))
        assert registers[H] * 256 + registers[L] == (x - size // 2) & 65535
        assert registers[D] * 256 + registers[E] == (y - size // 2) & 65535
        assert registers[B] * 256 + registers[C] == depth
        assert registers[16:18] == [0x13, sub16_flags(y, size // 2)]
        assert registers[18:24] == [0xF0, 0x12, 0xD8 if size == 12 else 0xC4, 0, size, size]
        assert registers[SP] == SAVED_SP - 4 and memory[SAVED_SP - 4:SAVED_SP] == [0x21, 0x6E, EFFECT & 255, EFFECT >> 8]
        assert ports.writes == [(0x7FFD, 0x13)]
        run_to(cpu, AFTER_DRAW)
        expected = cpu.registers[:]
        expected[A], expected[IXh], expected[IXl], expected[SP], expected[PC] = 16, EFFECT >> 8, EFFECT & 255, SAVED_SP, CONTINUE
        before = [bytearray(bank) for bank in memory.banks]
        before[2][SAVED_SP - 0x8000 - 4:SAVED_SP - 0x8000] = bytes((expected[C], expected[B], 0x28, 0x6E))
        memory.writes.clear()
        run_to(cpu, CONTINUE)
        assert all(cpu.registers[index] == expected[index] for index in compared)
        assert memory.banks == before
        assert Counter(memory.writes) == Counter((2, address - 0x8000, value) for address, value in
                                                zip(range(SAVED_SP - 4, SAVED_SP), before[2][0x3FF8:0x3FFC], strict=True))
        assert ports.writes == [(0x7FFD, 0x13), (0x7FFD, 0x10)] and cpu.registers[IFF] == 1
        counts['draw_and_restore'] += 1

    memory.recording = False
    report = dict(passed=True, cases=dict(counts), early_exit_all_registers_and_r_checked=True,
                  full_child_executed=True, child_results_preserved_except_a_ix_sp=True,
                  exact_wrapper_stack_writes_checked=True, entry=ENTRY, continuation=CONTINUE,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionVisualEffectResumeVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены ранние выходы #6DD1 и сохранение результата настоящего рисователя банка 3.')


if __name__ == '__main__':
    main()
