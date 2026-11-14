"""Все фазы первого IRQ и задержки второго вывода исходного FINALF."""
from collections import Counter
import json

from CheckFinalCycle import (DELAY_OPERAND, DelayIrqProbe, FinalMemory, InputPorts,
                             ROOT, SP, T, get_registers, interrupt_stack_kind, original_memory)
from skoolkit.simutils import R


FIRST_ENTRY, SECOND_ENTRY, DRAW_END = 0x607A, 0x60AC, 0x6111
PERIODS = (70908, 69888)
FRAME_BYTES = 4


class PhaseProbe(DelayIrqProbe):
    def accept_interrupt(self, registers, memory, prev_pc):
        phase = registers[T] % self.frame_duration
        if super().accept_interrupt(registers, memory, prev_pc):
            self.accepted[-1]['phase'] = phase
            return True
        return False


def reset(cpu, banks, registers, page):
    memory = cpu.memory
    for bank, saved in zip(memory.banks, banks):
        bank[:] = saved
    memory.out7ffd(page)
    cpu.registers[:] = registers
    cpu.accepted.clear()
    cpu.delay_iterations = 0
    memory.irq_stack_reads.clear()
    memory.irq_stack_writes.clear()


def first_phase_states(cpu, original_bitmap):
    memory = cpu.memory
    period = cpu.frame_duration
    cpu.registers[:] = get_registers({'PC': 0x6000, 'SP': 0x5FFE}, None, False)
    cpu.run(0x6000, FIRST_ENTRY, interrupts=True)
    prepared = [bytes(bank) for bank in memory.banks]
    initial = cpu.registers.copy()
    states = {}
    # EI и первый такт HALT занимают суммарно восемь тактов.
    for phase in range(cpu.int_active):
        reset(cpu, prepared, initial, 1)
        cpu.registers[T] = period + phase - 8
        cpu.run_until(SECOND_ENTRY)
        assert [(event['interrupted_instruction'], event['sp']) for event in cpu.accepted] == [
            (0x607B, 0x5FFE), (0x9EE9, 0x6196)
        ]
        assert cpu.accepted[0]['phase'] == phase
        assert cpu.registers[SP] == 0x5FFE and memory.o7ffd == 0
        assert bytes(memory.banks[5][:6144]) == original_bitmap
        banks = tuple(bytes(bank) for bank in memory.banks)
        registers = cpu.registers.copy()
        key = (banks, tuple(value if i != T else value % period
                            for i, value in enumerate(registers) if i != R))
        if key not in states:
            states[key] = dict(banks=banks, registers=registers, first_irq_phases=[])
        states[key]['first_irq_phases'].append(phase)
    assert [row['first_irq_phases'] for row in states.values()] == [list(range(i, 36, 4)) for i in range(4)]
    return states.values()


def check_second_phase(cpu, state, delay):
    reset(cpu, state['banks'], state['registers'], 0)
    memory = cpu.memory
    memory[DELAY_OPERAND] = delay

    def observe(pc):
        # Разное число HALT меняет R, проверяем, что второй вывод его не читает.
        assert memory[pc] != 0xED or memory[pc + 1] != 0x5F
        if pc == 0x616F and cpu.accepted:
            event = cpu.accepted[-1]
            stack = event['sp']
            if interrupt_stack_kind(stack) == 'attribute_stack':
                assert cpu.registers[SP] == stack - FRAME_BYTES
                frame = bytes(memory[stack - FRAME_BYTES:stack])
                assert frame == bytes((event['alternate_f'], event['alternate_a'])) + event['resume'].to_bytes(2, 'little')
                event['attribute_frame_hex'] = frame.hex()

    cpu.run_until(DRAW_END, observe)
    assert cpu.registers[SP] == 0x5FFE and memory.o7ffd == 1
    assert bytes(memory.banks[5][6144:6912]) == b'\xA0' * 768
    assert cpu.delay_iterations == (delay or 256)
    assert [event['sp'] for event in cpu.accepted if event['interrupted_instruction'] == 0x912D] == [0x6196]
    assert all(address >= 0x6192 for address in memory.irq_stack_reads)
    assert all(address >= 0x6192 for address, _ in memory.irq_stack_writes)
    assert not memory.template_gap_accesses
    assert memory.tail_reads == memory.tail_writes == 0
    extra = [event for event in cpu.accepted if event['interrupted_instruction'] != 0x912D]
    assert len(extra) <= 1
    return extra[0] if extra else None


def main():
    flat = original_memory()
    banks = [bytearray([i] * 0x4000) for i in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    banks[2][:] = bytes(flat[0x8000:0xC000])
    profiles = []
    for period in PERIODS:
        memory = FinalMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
        cpu = PhaseProbe(memory, period)
        cpu.set_tracer(InputPorts(cpu, None, False))
        for state in first_phase_states(cpu, bytes(flat[0x7AA9:0x92A9])):
            events = []
            for delay in range(101):
                event = check_second_phase(cpu, state, delay)
                if event:
                    events.append(dict(delay=delay, **event))
            domain = Counter(interrupt_stack_kind(event['sp']) for event in events)
            assert all(event['sp'] >= 0x4000 + FRAME_BYTES for event in events)
            assert all('attribute_frame_hex' in event for event in events
                       if interrupt_stack_kind(event['sp']) == 'attribute_stack')
            profiles.append(dict(period=period, first_irq_phases=state['first_irq_phases'],
                                 phase_at_second_entry=state['registers'][T] % period, delays=101,
                                 additional_interrupts_by_stack=dict(domain), additional_interrupts=events))
    result = dict(passed=True, irq_window_tstates=36, phase_profiles=profiles,
                  first_phase_runs=72, second_phase_runs=len(profiles) * 101,
                  full_phase_delay_combinations=len(PERIODS) * 36 * 101,
                  earlier_irq_gap_accesses=0, template_gap_accesses=0, byte_after_bitmaps_accesses=0,
                  final_attribute_bytes_verified=768,
                  native_execution=False, assembly_executed=False)
    encoded = json.dumps(result, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/FinalIrqPhaseCoverageVerification.json').write_text(encoded, encoding='utf-8')
    print('36 фаз первого IRQ, 101 задержка и два периода, 808 вторых выводов.')


if __name__ == '__main__':
    main()
