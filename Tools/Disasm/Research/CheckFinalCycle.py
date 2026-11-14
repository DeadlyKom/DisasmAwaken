"""Полный запуск FINALF до смены двух экранов и выбора выхода по Space."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks
from CheckFinal import original_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from skoolkit.simutils import IFF, T


BITMAP_END = 0xAAA9
IRQ_GAP_START, IRQ_STACK_TOP = 0x617A, 0x6196
TEMPLATE_GAPS = frozenset((0x627B, 0x627C, 0x6294, 0x6295))
DELAY_OPERAND, DELAY_START = 0x60D4, 0x60D5
SYNC_HALTS = frozenset((0x607B, 0x9EE9, 0x912D))


def interrupt_stack_kind(stack):
    if stack >= 0xC000:
        return 'source_stack'
    if stack < 0x5800:
        return 'screen_stack'
    if stack < 0x5B00:
        return 'attribute_stack'
    return 'cpu_stack'


class FinalMemory(RecordedBanks):
    tail_reads = 0
    tail_writes = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.irq_stack_reads = []
        self.irq_stack_writes = []
        self.template_gap_accesses = []

    def __getitem__(self, address):
        if address == BITMAP_END:
            self.tail_reads += 1
        if isinstance(address, int) and IRQ_GAP_START <= address < IRQ_STACK_TOP:
            self.irq_stack_reads.append(address)
        if isinstance(address, int) and address in TEMPLATE_GAPS:
            self.template_gap_accesses.append(('read', address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if address == BITMAP_END:
            self.tail_writes += 1
        if isinstance(address, int) and IRQ_GAP_START <= address < IRQ_STACK_TOP:
            self.irq_stack_writes.append((address, value))
        if isinstance(address, int) and address in TEMPLATE_GAPS:
            self.template_gap_accesses.append(('write', address))
        super().__setitem__(address, value)


class InputPorts(PortTrace):
    def __init__(self, simulator, speed, space):
        super().__init__(simulator)
        self.speed = speed
        self.space = space
        self.reads = []

    def read_port(self, registers, port):
        self.reads.append(port)
        if port == self.speed or port == 0x7FFE and self.space:
            return 254
        return 255


class DelayIrqProbe(Simulator):
    def __init__(self, memory, period):
        super().__init__(memory, config={'frame_duration': period, 'int_active': 36})
        self.accepted = []
        self.delay_iterations = 0

    def accept_interrupt(self, registers, memory, prev_pc):
        event = dict(interrupted_instruction=prev_pc, resume=registers[PC], sp=registers[SP],
                     page=memory.o7ffd & 7, alternate_a=registers[16], alternate_f=registers[17],
                     paging_latch=memory.o7ffd, irq_page_operand=memory[0x6173])
        if super().accept_interrupt(registers, memory, prev_pc):
            # Проверка сохранения физической рамки при банковом SP, OUT выполняется между PUSH и POP AF.
            if event['sp'] >= 0xC004:
                assert event['paging_latch'] & 32 or event['page'] == event['irq_page_operand'] & 7, event
            self.accepted.append(event)
            return True
        return False

    def run_until(self, target, observe=None):
        registers = self.registers
        for _ in range(150000):
            pc = registers[PC]
            if pc == target:
                return
            if pc == DELAY_START:
                self.delay_iterations += 1
            if observe is not None:
                observe(pc)
            self.opcodes[self.memory[pc]]()
            if registers[IFF] and registers[T] % self.frame_duration < self.int_active:
                self.accept_interrupt(registers, self.memory, pc)
        raise AssertionError(('Граница финального кадра не достигнута', target, registers[PC]))


def check_delay_pair(cpu, bitmaps):
    memory = cpu.memory
    delay = memory[DELAY_OPERAND]
    source = bytearray(memory.banks[1][:6144])
    cpu.accepted.clear()
    cpu.delay_iterations = 0
    assert cpu.registers[PC] == 0x607A
    cpu.run_until(0x60AC)
    assert cpu.registers[SP] == 0x5FFE and bytes(memory.banks[5][:6144]) == bitmaps[1]
    cpu.run_until(0x6111)
    assert cpu.registers[SP] == 0x5FFE and memory.o7ffd == 1
    assert cpu.delay_iterations == (delay or 256)
    assert [event['interrupted_instruction'] for event in cpu.accepted if
            event['interrupted_instruction'] in SYNC_HALTS] == [0x607B, 0x9EE9, 0x912D]
    extra = [event for event in cpu.accepted if event['interrupted_instruction'] not in SYNC_HALTS]
    assert len(extra) <= 1
    kind = 'scheduled_only'
    if extra:
        event = extra[0]
        stack = event['sp']
        kind = interrupt_stack_kind(stack)
        if kind == 'source_stack':
            assert event['page'] == 1 and 0xC004 <= stack <= 0xD800
            # Аппаратная рамка выше пары AF, которую кладёт исходный обработчик.
            start = stack - 0xC000 - 4
            source[start:start + 4] = bytes((event['alternate_f'], event['alternate_a'])) + event['resume'].to_bytes(2, 'little')
        else:
            assert stack >= 0x4004
    assert bytes(memory.banks[1][:6144]) == source, (delay, extra)
    assert bytes(memory.banks[5][6144:6912]) == b'\xA0' * 768
    assert not memory.template_gap_accesses
    assert memory.tail_reads == memory.tail_writes == 0
    assert all(address >= IRQ_STACK_TOP - 4 for address in memory.irq_stack_reads)
    assert all(address >= IRQ_STACK_TOP - 4 for address, _ in memory.irq_stack_writes)
    screen_delta = [dict(address=0x4000 + offset, original=expected, actual=actual)
                    for offset, (expected, actual) in enumerate(zip(bitmaps[2], memory.banks[5])) if expected != actual]
    source_delta = sum(expected != actual for expected, actual in zip(bitmaps[2], source))
    return dict(delay=delay, delay_iterations=cpu.delay_iterations, irq_case=kind,
                additional_irq=extra[0] if extra else None,
                source_bytes_differing_from_disk=source_delta, screen_delta=screen_delta)


def check_delay_range(banks, bitmaps):
    profiles = []
    for period in (70908, 69888):
        memory = FinalMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
        cpu = DelayIrqProbe(memory, period)
        ports = InputPorts(cpu, None, False)
        cpu.set_tracer(ports)
        cpu.registers[:] = get_registers({'PC': 0x6000, 'SP': 0x5FFE}, None, False)
        cpu.run(0x6000, 0x607A, interrupts=True)
        initial = cpu.registers.copy()
        prepared = [bank.copy() for bank in memory.banks]
        cases = []
        for delay in range(101):
            for bank, saved in zip(memory.banks, prepared):
                bank[:] = saved
            memory.out7ffd(1)
            cpu.registers[:] = initial
            memory[DELAY_OPERAND] = delay
            cases.append(check_delay_pair(cpu, bitmaps))
        assert cases[0]['irq_case'] == 'cpu_stack' and cases[0]['delay_iterations'] == 256
        assert cases[1]['irq_case'] == 'scheduled_only' and not cases[1]['screen_delta']
        profiles.append(dict(period_tstates=period, cases=len(cases),
                             delays_without_additional_irq=[row['delay'] for row in cases if not row['additional_irq']],
                             additional_irq_cases=[row for row in cases if row['additional_irq']]))
    nominal = {row['delay']: row for row in profiles[0]['additional_irq_cases']}
    assert nominal[72]['source_bytes_differing_from_disk'] == 4 and len(nominal[72]['screen_delta']) == 2
    assert nominal[80]['source_bytes_differing_from_disk'] == 0 and len(nominal[80]['screen_delta']) == 4
    assert [(row['address'], row['actual']) for row in nominal[72]['screen_delta']] == [(0x4F38, 0xFD), (0x4F39, 0x7F)]
    assert [(row['address'], row['actual']) for row in nominal[80]['screen_delta']] == list(enumerate(b'\x42\xA0\x29\x90', 0x4B1C))

    # Повторный запуск без подстановки задержки. Q доводит 1 до 0, затем A доводит 0 до 100.
    memory = FinalMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
    cpu = DelayIrqProbe(memory, 70908)
    ports = InputPorts(cpu, 0xFBFE, False)
    cpu.set_tracer(ports)
    cpu.registers[:] = get_registers({'PC': 0x6000, 'SP': 0x5FFE}, None, False)
    cpu.run(0x6000, 0x607A, interrupts=True)
    assert check_delay_pair(cpu, bitmaps)['delay'] == 1
    cpu.run_until(0x607A)
    ports.speed = 0xFDFE
    for delay in range(101):
        final = check_delay_pair(cpu, bitmaps)
        assert final['delay'] == delay
        cpu.run_until(0x607A)
    assert memory[DELAY_OPERAND] == 100 and final['source_bytes_differing_from_disk'] > 4
    return dict(period_profiles=profiles, irq_window_tstates=36,
                original_keyboard_path=dict(starting_delay=1, q_reached_zero=True, a_reached_100=True,
                                            complete_pairs=102, last_pair=final),
                original_bank1_interrupt_stack_writes_verified=True)


def main():
    flat = original_memory()
    assert flat[BITMAP_END] == 0xA3
    sectors = (ROOT / 'Tools/Disasm/Extracted/Active/29_FINALF.C.sectors.bin').read_bytes()
    bitmap_end_offset = BITMAP_END - 0x6000
    assert len(sectors) == 0x4B00 and sectors[bitmap_end_offset - 1] != 0xA3
    assert sectors[bitmap_end_offset:] == b'\xA3' * 87
    bitmaps = tuple(bytes(flat[0x62A9 + index * 0x1800:0x62A9 + (index + 1) * 0x1800])
                    for index in range(3))
    assert all(flat[address] == 0 for address in TEMPLATE_GAPS)
    banks = [bytearray([i] * 0x4000) for i in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    banks[2][:] = bytes(flat[0x8000:0xC000])
    cases = 0
    for time, (speed, space) in product((0, 100, 70880), ((None, False), (0xFBFE, False), (0xFDFE, True))):
        memory = FinalMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
        sim = Simulator(memory, config={'frame_duration': 70908, 'int_active': 36})
        trace = InputPorts(sim, speed, space)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6000, 'SP': 0x5FFE}, None, False)
        initial[25] = time
        sim.registers[:] = initial
        sim.run(0x6000, 0x607A, interrupts=True)
        context = (time, speed, space)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 1, context
        assert sim.registers[14] == 0xBE and sim.registers[27] == 2 and not sim.registers[26]
        assert bytes(memory[0xBE00:0xBF01]) == b'\xBF' * 257
        assert bytes(memory[0xBFBF:0xBFC2]) == bytes.fromhex('c36c61')
        for bank, bitmap in zip((7, 0, 1), bitmaps):
            assert bytes(memory.banks[bank][:6144]) == bitmap
        assert bytes(memory.banks[7][6144:6912]) == b'\x88' * 768
        assert trace.writes == [(0x7FFD, page) for page in (31, 7, 0, 1)]
        sim.run(0x607A, 0x60AC, interrupts=True)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 0, context
        assert bytes(memory.banks[5][:6144]) == bitmaps[1], context
        assert bytes(memory.banks[5][6144:6912]) == b'\x90' * 768, context
        sim.run(0x60AC, 0x6111, interrupts=True)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 1, context
        assert bytes(memory.banks[5][:6144]) == bitmaps[2], context
        assert bytes(memory.banks[5][6144:6912]) == b'\xA0' * 768, context
        paging = [value for port, value in trace.writes if port == 0x7FFD]
        assert paging == [31, 7, 0, 1, 0, 8, 0, 1, 1], (context, paging)
        expected_exit = 0x6148 if space else 0x607A
        sim.run(0x6111, expected_exit, interrupts=True)
        assert sim.registers[PC] == expected_exit and sim.registers[SP] == 0x5FFE
        assert memory[0x60D4] == {None: 1, 0xFBFE: 0, 0xFDFE: 2}[speed]
        assert trace.reads == ([0xFBFE, 0x7FFE] if speed == 0xFBFE else [0xFBFE, 0xFDFE, 0x7FFE])
        if space:
            sim.run(0x6148, 0x616B, interrupts=True)
            assert memory.o7ffd == 31 and bytes(memory.banks[7][6144:6912]) == bytes(768)
            assert sim.registers[27] == 0 and not sim.registers[26]
        # Проверка первого байта за третьим растром, он находится в фиксированном банке 2.
        assert memory.tail_reads == memory.tail_writes == 0, context
        assert memory.banks[2][BITMAP_END - 0x8000] == 0xA3, context
        assert not memory.template_gap_accesses
        # Из всего промежутка между обработчиком и построителем используются два слова стека.
        for address in range(IRQ_STACK_TOP - 4, IRQ_STACK_TOP):
            assert memory.irq_stack_reads.count(address) == 2, (context, memory.irq_stack_reads)
            assert sum(target == address for target, _ in memory.irq_stack_writes) == 2, (context, memory.irq_stack_writes)
        assert len(memory.irq_stack_reads) == len(memory.irq_stack_writes) == 8, context
        cases += 1
    report = dict(passed=True, total_cases=cases, three_source_bitmaps_compared=True,
                  both_generated_draws_compared=True, frame_duration=70908,
                  byte_after_bitmaps=dict(address=BITMAP_END, original_value=0xA3, reads=0, writes=0,
                                          physical_run_bytes=87, bytes_beyond_logical_file=86),
                  template_gaps=dict(addresses=sorted(TEMPLATE_GAPS), reads=0, writes=0),
                  temporary_irq_stack=dict(start=IRQ_STACK_TOP - 4, end_exclusive=IRQ_STACK_TOP,
                                           frame_bytes=4, paired_pushes_per_case=2,
                                           earlier_gap_bytes_untouched=IRQ_STACK_TOP - 4 - IRQ_GAP_START),
                  delay_irq_profiles=check_delay_range(banks, bitmaps),
                  actual_im2_executed=True, im2_switches_per_case=3,
                  banked_stack_mapping_verified_for_every_accepted_irq=True,
                  native_final_scene_verified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/FinalCycleVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'delay_irq_profiles'}, indent=2))


if __name__ == '__main__':
    main()
