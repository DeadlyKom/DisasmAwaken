"""Загрузка runtime-узла и композиция с настоящим UpdateAyEffects до первого вызова рисователя."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from CheckActionAyEffects import AyLatch, cp4
from ReferenceControlsPointRespawn import refresh


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    flow = next(r for r in json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if r['name'] == 'Action')
    def cost(start, end):
        return sum(2 if i['hex'][:2] in ('cb', 'dd', 'ed', 'fd') else 1 for i in flow['instructions'] if start <= i['address'] < end)
    active_cost = (cost(0xECA8, 0xECE4), cost(0xECF5, 0xED35))
    stop_cost = (cost(0xECE4, 0xECF5), cost(0xED35, 0xED46))
    parent_cost, sample_cost, tail_cost = cost(0xE4B1, 0xE4DB), cost(0xED46, 0xED5C), cost(0xED46, 0xED8F) - 2
    counts, touched = Counter(), set()

    def check(active=3, end=0, r=0, level=0, offset=0, seed=0):
        nonlocal touched
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        address = 0x8F00 + offset
        words = tuple((seed * factor + bias) & 65535 for factor, bias in ((73, 0x1234), (109, 0x5678), (257, 0), (313, 0x8000), (419, 0xFFFF)))
        word0, word1, x, y, z = words
        meta = (seed * 17) & 255
        for a, value in ((address + 3, word0), (address + 5, word1), (address + 8, x), (address + 10, y), (address + 12, z)):
            memory[a], memory[a + 1] = value & 255, value >> 8
        memory[address + 7] = meta
        cursors = tuple((base + (5 if end & (1 << channel) else 0) * 4) if active & (1 << channel) else 0x37
                        for channel, base in enumerate((0xEE02, 0xEE1B)))
        for operand, value in zip((0xECA9, 0xECF6), cursors):
            memory[operand], memory[operand + 1] = value & 255, value >> 8
        memory[0xED83] = level
        initial = get_registers({'AF': 0xA5FF, 'HL': address, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE4B1}, None, False)
        initial[14], initial[15], initial[26], initial[27] = seed & 255, r, seed & 1, seed % 3
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes, events, reads = [], [], []
        mixer = seed & 255
        original_mixer = mixer
        def byte(a, value):
            bank = 5 if a < 0x8000 else 2 if a < 0xC000 else 0
            writes.append((bank, a & 0x3FFF, value))
            expected[bank][a & 0x3FFF] = value
        def word(a, value):
            byte(a, value & 255)
            byte(a + 1, value >> 8)
        def select(reg):
            events.append((0xFFFD, reg))
        def output(value, outi=False):
            events.append((0xBEFD if outi else 0xBFFD, value))
        # Сохранение адреса узла на CPU-стеке и загрузка снимка в исходные переменные.
        word(0xBFFC, address)
        word(0xE4D6, 0xBFFC)
        for a, value in ((0x9B8D, word0), (0x9B12, word1), (0xD9B6, x), (0xD7C4, y), (0xD7A2, z)):
            word(a, value)
        byte(0x9B14, meta)
        word(0xBFFA, 0xE4DB)
        # Композиция с ранее независимо проверенным договором AY, все настоящие дочерние инструкции исполняются.
        m1 = parent_cost
        for channel, cursor in enumerate(cursors):
            if not active & (1 << channel):
                m1 += 4
                continue
            low, high, control, volume = flat[cursor:cursor + 4]
            select(channel * 2)
            output(low, True)
            select(channel * 2 + 1)
            output(high, True)
            select(7)
            reads.append((0xFFFD, mixer))
            mixer = (mixer & (0xED if channel else 0xF6)) | (((control << 1) | (control >> 7)) & 255 if channel else control)
            output(mixer)
            select(8 + channel)
            output(volume, True)
            following = cursor + 4
            operand = 0xECF6 if channel else 0xECA9
            word(operand, following)
            m1 += active_cost[channel]
            if end & (1 << channel):
                assert flat[following] == 0
                byte(operand + 1, 0)
                select(7)
                reads.append((0xFFFD, mixer))
                mixer |= 0x12 if channel else 9
                output(mixer)
                m1 += stop_cost[channel]
        sampled = refresh(r, m1 + sample_cost)
        noise = 32 if sampled >= 32 else 0
        select(5)
        output(12)
        select(7)
        reads.append((0xFFFD, mixer))
        mixer = (mixer & 0xDB) | noise
        output(mixer)
        select(6)
        output(5)
        select(10)
        output(max(4, level >> 1))
        m1 += tail_cost + int(sampled >= 32) + int((level >> 1) < 4)
        wanted[0:2] = [max(4, level >> 1), cp4(level >> 1)]
        wanted[2:4] = [0xBF, 0xFD]
        wanted[4:6] = [y >> 8, y & 255]
        wanted[6:8] = [((cursors[1] + 4) >> 8) if active & 2 else 0, noise]
        wanted[SP], wanted[PC], wanted[15] = 0xBFFC, 0xE4DB, refresh(r, m1)
        simulator.registers[:] = initial
        trace = AyLatch(original_mixer)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        for _ in range(190):
            if simulator.registers[PC] == 0xE4DB:
                break
            simulator.run()
        else:
            raise AssertionError('граница перед рисователем')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (active, end, r, level, offset,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), (active, end, 'RAM')
        assert trace.events == events and trace.reads == reads and trace.mixer == mixer
        touched = {(bank, index) for bank, index, value in memory.writes}
        counts[str(active) + ':' + str(end)] += 1
    # Проверка всех входных R и уровней, активности и завершения обеих строк по исходным адресам.
    for value in range(256):
        for active in range(4):
            for end in range(4):
                check(active, end, value, value, seed=value)
    # Проверка каждого физического узла и всех уровней с различными исходными снимками и смесителем.
    for offset in range(0, 252, 14):
        for value in range(256):
            check(r=value ^ 255, level=value, offset=offset, seed=offset * 257 + value)
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts),
        method='parent_snapshot_stack_oracle_composed_with_previously_proved_ay_contract',
        independent_complete_child_oracle=False, children_executed_without_stubs=True,
        exact_registers_flags_refresh_sp=True, every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_port_reads_and_writes_checked=True, node_offsets_checked=list(range(0, 252, 14)),
        saved_node_pointer_retained_on_stack=True, maximum_additional_stack_bytes=4,
        execution_boundary='E4B1..E4DB, first renderer call not executed', all_joint_inputs_exhausted=False,
        whole_queue_consumer_proved=False, actual_ay_hardware_executed=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderQueueLoadVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
