"""E40F..E4A5, вставка в исходную связанную очередь и запись данных через SP."""
from collections import Counter
from itertools import product
from functools import cache
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import cp_flags, refresh
from CheckActionCloseBounds import arithmetic


def add_flags(left, right):
    total = left + right
    value = total & 255
    return (value & 0xA8) | (64 if not value else 0) | (16 if (left & 15) + (right & 15) > 15 else 0) | (4 if (~(left ^ right) & (left ^ value) & 128) else 0) | int(total > 255)


def main():
    baseline = flat_action()
    memory = Memory(baseline)
    simulator = Simulator(memory)
    counts = Counter()
    carry_zero_offset = Counter()
    touched = set()
    flow = next(r for r in json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if r['name'] == 'Action')
    # Сохранение стоимости неизменного диапазона, список инструкций этого запуска не изменяется.
    @cache
    def cost(start, end):
        return sum(2 if i['hex'][:2] in ('cb', 'dd', 'ed', 'fd') else 1 for i in flow['instructions'] if start <= i['address'] < end)

    def check(depth=100, node_depths=(200, 50), rotation=0, reverse=False, full=False, meta=0x73, flags=255):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = baseline[address]
        count = len(node_depths)
        offsets = list(range(0, 14 * count, 14))
        if offsets:
            rotation %= count
            offsets = offsets[rotation:] + offsets[:rotation]
            if reverse:
                offsets.reverse()
        free = 252 if full else count * 14
        assert 0 <= free <= 252
        serial = counts.total()
        # Создание конечного списка с допустимыми физическими смещениями, произвольные глубины не объявляются отсортированными.
        for i, (offset, value) in enumerate(zip(offsets, node_depths)):
            memory[0x8F00 + offset] = offsets[i + 1] if i + 1 < count else 1
            memory[0x8F0C + offset:0x8F0E + offset] = [value & 255, value >> 8]
        memory[0x9BA1:0x9BA3] = [offsets[0] if offsets else 1, free]
        x, y, input1 = (serial * 71) & 65535, (serial * 109) & 65535, (serial * 257) & 65535
        word0, word1 = (serial * 13) & 65535, (serial * 29) & 65535
        for address, value in ((0xD7A2, depth), (0xD9B6, x), (0xD7C4, y), (0xAF56, input1), (0x9B8D, word0), (0x9B12, word1)):
            memory[address:address + 2] = [value & 255, value >> 8]
        memory[0x9B14] = meta
        initial = get_registers({'AF': 0xA500 | flags, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE40F}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        wanted, expected, writes = list(initial), list(memory), []
        def pair(index, value):
            wanted[index:index + 2] = [value >> 8, value & 255]
        def byte(address, value):
            expected[address] = value
            writes.append((address, value))
        def word(address, value):
            byte(address, value & 255)
            byte(address + 1, value >> 8)
        pair(2, depth)
        pair(4, input1)
        m1 = cost(0xE40F, 0xE41E)
        insertion = 0
        previous = None
        # Поиск места по исходному знаковому биту SBC, Carry от CP offset,1 сохраняется даже для смещения 00.
        if offsets:
            pair(8, 0x8F00 + offsets[0])
            value, flag = arithmetic(node_depths[0], depth, int(offsets[0] == 0), False)
            pair(6, value)
            m1 += cost(0xE41E, 0xE42E)
            if offsets[0] == 0:
                carry_zero_offset['head'] += 1
            if not value & 32768:
                wanted[10] = 0x8F
                m1 += cost(0xE42E, 0xE431)
                insertion = count
                for i in range(count):
                    pair(8, 0x8F00 + offsets[i])
                    m1 += cost(0xE431, 0xE438)
                    if i + 1 == count:
                        previous = offsets[i]
                        break
                    pair(10, 0x8F00 + offsets[i + 1])
                    value, flag = arithmetic(node_depths[i + 1], depth, int(offsets[i + 1] == 0), False)
                    pair(6, value)
                    m1 += cost(0xE438, 0xE445)
                    if offsets[i + 1] == 0:
                        carry_zero_offset['following'] += 1
                    if value & 32768:
                        insertion, previous = i + 1, offsets[i]
                        break
                    m1 += cost(0xE445, 0xE44C)
        mode = 'head' if insertion == 0 else 'tail' if insertion == count else 'middle'
        allocation = {'head': 0xE44C, 'tail': 0xE462, 'middle': 0xE474}[mode]
        if full:
            m1 += cost(allocation, allocation + (8 if mode == 'head' else 7))
            wanted[0:2] = [252, cp_flags(252, 252)]
            wanted[PC] = 0xE4A6
            path = 'full_' + mode
        else:
            m1 += cost(allocation, {'head': 0xE462, 'tail': 0xE474, 'middle': 0xE486}[mode])
            # Обновление связей, младшие байты 01 и FC имеют разные роли конца списка и исчерпанного буфера.
            following = offsets[insertion] if insertion < count else 1
            byte(0x8F00 + free, following)
            if previous is None:
                byte(0x9BA1, free)
            else:
                byte(0x8F00 + previous, free)
            next_free = free + 14
            byte(0x9BA2, next_free)
            flag = add_flags(free, 14)
            # Запись точного перекрытия PUSH AF и следующего PUSH HL, байт F по +6 затем заменяется старшим байтом word1.
            base = 0x8F00 + free
            word(base + 12, depth)
            word(base + 10, y)
            word(base + 8, x)
            word(base + 6, (meta << 8) | flag)
            word(base + 5, word1)
            word(base + 3, word0)
            pair(6, word0)
            wanted[0:2] = [meta, flag]
            wanted[SP], wanted[PC] = base + 3, 0xE0E2
            m1 += cost(0xE486, 0xE4A6)
            path = 'insert_' + mode
        wanted[15] = refresh(initial[15], m1)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        measured_m1 = 0
        for _ in range(400):
            if simulator.registers[PC] in (0xE0E2, 0xE4A6):
                break
            before_r = simulator.registers[15]
            simulator.run()
            increment = (simulator.registers[15] - before_r) & 127
            assert increment in (1, 2)
            measured_m1 += increment
        else:
            raise AssertionError('граница вставки')
        assert measured_m1 == m1, (path, 'full M1', measured_m1, m1)
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (path, depth, node_depths, offsets,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes), (path, memory.writes, writes)
        touched = {a for a, v in memory.writes}
        counts[path] += 1

    # Проверка всех слов кандидата и существующей глубины, включая оборачивание SBC и исходный дополнительный займ.
    for value in range(65536):
        check(depth=value)
        check(node_depths=(value,))
    # Проверка каждого числа занятых узлов, перестановок физического нулевого смещения и полного буфера.
    for count in range(19):
        for rotation in range(max(1, count)):
            for reverse, full, depth in product((False, True), (False, True), (0, 1, 100, 32767, 32768, 65535)):
                if count == 18 and not full:
                    continue
                values = tuple((60000 - 317 * i) & 65535 for i in range(count))
                check(depth, values, rotation, reverse, full)
    # Проверка равных и крайних глубин нескольких соседей, всех исходных F и байтов метаданных.
    for values in product((0, 1, 32767, 32768, 65535), repeat=3):
        for depth in (0, 1, 32767, 32768, 65535):
            for full in (False, True):
                check(depth, values, rotation=2, full=full)
    for value in range(256):
        check(meta=value, flags=value)
    assert set(counts) == {a + b for a in ('insert_', 'full_') for b in ('head', 'tail', 'middle')}
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), zero_offset_borrow_paths=dict(carry_zero_offset),
        method='independent_finite_linked_list_and_overlapping_payload_oracle', exact_registers_flags_refresh_sp=True,
        full_M1_count_compared_not_only_R_modulo_128=True,
        every_ram_byte_and_write_multiplicity_checked=True, original_sign_only_compare_with_borrow_preserved=True,
        tested_node_counts=list(range(19)), free_offset_domain='00,0E,..,EE or FC full', node_stride=14,
        payload_offsets_written=list(range(3, 14)), offsets_1_and_2_preserved=True, push_af_low_byte_overwritten=True,
        successful_sp_equals_node_plus_3=True, exhausted_queue_preserves_entry_sp=True,
        execution_boundary='E40F..E0E2 or E4A6, continuations not executed', synthetic_finite_lists=True,
        original_disk_8f00_not_claimed_to_be_runtime_nodes=True, all_joint_inputs_exhausted=False,
        whole_projection_scan_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderQueueInsertVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
