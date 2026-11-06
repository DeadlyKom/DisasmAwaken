"""E36A..E40E, сопровождение точки и захват цели, оригинальная банковая очередь без подмены."""
from collections import Counter
from itertools import product
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace, put
from CheckMusic import Simulator, get_registers, PC, SP
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import cp_flags, refresh
from ReferenceControlsTextQueue import QUEUE, PRODUCER, insert
from CheckActionMissileLaunch import queue_cost


def logical(value):
    return (value & 0xA8) | (64 if not value else 0) | (4 if value.bit_count() % 2 == 0 else 0)


def inc_flags(value):
    result = (value + 1) & 255
    return (result & 0xA8) | (64 if not result else 0) | (16 if value & 15 == 15 else 0) | (4 if value == 127 else 0)


def follow(old, target):
    difference = (target - old) & 255
    signed = 0 if difference == 255 else difference if difference < 128 else difference - 256
    return (old + (signed >> 1)) & 255


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    baseline[1] = bytearray(base_memory()[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, queue_results, touched = Counter(), Counter(), set()
    maximum_depth = 0

    def check(x=0, y=0, sx=0, sy=0, old_x=119, old_y=43, gate=0, request=0,
              targets=(255, 255, 255), record=0xA100, head=0, mask=0, page=16):
        nonlocal touched, maximum_depth
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        memory.out7ffd(page)
        serial = counts.total()
        for address, value in ((0xE372, x), (0xE375, y), (0xECA9, 0x5678)):
            put(memory, address, [value & 255, value >> 8])
        for address, value in ((0xD9B7, sx), (0xD7C5, sy), (0xE021, gate), (0xAA8E, request), (0x9B19, old_x), (0x9B1A, old_y)):
            memory[address] = value
        put(memory, 0x9B1B, targets)
        for index in range(16):
            memory.banks[1][0x2C80 + 2 * index] = 128 if mask & (1 << index) else 1
            memory.banks[1][0x2C81 + 2 * index] = (index * 73 + serial) & 255
        memory.banks[1][0x2CA0:0x2CA2] = bytes([0, 0])
        cursor = QUEUE + 2 * head
        memory.banks[1][0x2C5D:0x2C5F] = bytes([cursor & 255, cursor >> 8])
        initial = get_registers({'AF': (serial * 73) & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': (serial * 17) & 65535, '^HL': record, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE36A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes, ports = [], []
        m1, depth = 3, 0

        def byte(address, value):
            bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
            writes.append((bank, address & 0x3FFF, value))
            expected[bank][address & 0x3FFF] = value

        def word(address, value):
            byte(address, value & 255)
            byte(address + 1, value >> 8)

        def pair(index, value):
            wanted[index:index + 2] = [value >> 8, value & 255]

        # Проверка полного байта запрета и двух модулей, при раннем отказе записей состояния нет.
        wanted[0:2] = [gate, and_flags(gate)]
        if gate:
            path = 'frame_blocked'
        else:
            pair(2, x)
            pair(4, y)
            high = (x >> 8) | (y >> 8)
            wanted[0:2] = [high, logical(high)]
            m1 += 5
            if high:
                path = 'high_rejected'
            else:
                wanted[0:2] = [x, cp_flags(x, 16)]
                m1 += 3
                if x >= 16:
                    path = 'x_rejected'
                else:
                    wanted[0:2] = [y, cp_flags(y, 16)]
                    m1 += 3
                    if y >= 16:
                        path = 'y_rejected'
                    else:
                        # Расчёт целевой точки по знакам исходного вектора, затем двух исходных асимметричных шагов.
                        tx, ty = (119 - x if sx & 128 else 119 + x), (43 - y if sy & 128 else 43 + y)
                        nx, ny = follow(old_x, tx), follow(old_y, ty)
                        pair(2, tx)
                        pair(4, ty)
                        pair(6, nx | (ny << 8))
                        word(0x9B19, nx | (ny << 8))
                        byte(0xE021, 1)
                        wanted[0:2] = [request, and_flags(request)]
                        m1 += 41 + 2 * bool(sx & 128) + 2 * bool(sy & 128)
                        m1 -= int((tx - old_x) & 255 == 255) + int((ty - old_y) & 255 == 255)
                        if not request:
                            path = 'follow_only'
                        else:
                            # Снятие запроса и выбор первого FF, изменение звука предшествует проверке свободного слота.
                            byte(0xAA8E, 0)
                            word(0xECA9, 0xEE02)
                            m1 += 4
                            free = next((i for i, value in enumerate(targets) if value == 255), None)
                            checked = 3 if free is None else free + 1
                            m1 += 4 * checked
                            if free is not None:
                                # Расчёт восьмибитного кода из произвольного HL', допустимость игрового указателя здесь не предполагается.
                                delta = (record - 0xA100) & 65535
                                index = (delta >> 6) & 255
                                pair(6, (delta & 0xFF00) | ((delta << 2) & 255))
                                pair(2, 0x5F00)
                                pair(4, 0x9B1B + free)
                                low = (record << 2) & 255
                                flag = (logical(low) & ~0x28) | (index & 0x28) | ((delta >> 14) & 1)
                                wanted[0:2] = [index, flag]
                                wanted[16:18] = [record >> 8, initial[17]]
                                byte(0x9B1B + free, index)
                                m1 += 18
                                path = 'target_' + str(free)
                            else:
                                # Проверка композиции с настоящим банковым производителем, переполнение очереди не отменяет предыдущие записи.
                                pair(6, 0xEE1B)
                                pair(4, 0x9B1D)
                                value = targets[2]
                                wanted[0:2] = [(value + 1) & 255, inc_flags(value)]
                                word(0xECA9, 0xEE1B)
                                virtual = {a: expected[1][a - 0xC000] for a in range(QUEUE, QUEUE + 34)}
                                virtual[PRODUCER], virtual[PRODUCER + 1] = cursor & 255, cursor >> 8
                                result = insert(virtual, 0xF258)
                                queue_results['accepted' if result['accepted'] else 'dropped'] += 1
                                for address, value in result['writes']:
                                    writes.append((1, address - 0xC000, value))
                                    expected[1][address - 0xC000] = value
                                ports = [(0x7FFD, 17), (0x7FFD, 16)]
                                m1 += 7 + 24 + queue_cost(virtual, result)
                                depth = 18
                                path = 'targets_full'
        wanted[PC], wanted[15] = 0xE40F, refresh(initial[15], m1)
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        for _ in range(400):
            if simulator.registers[PC] == 0xE40F:
                break
            simulator.run()
        else:
            raise AssertionError('граница E40F')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (path, x, y, sx, sy, old_x, old_y, record,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        # Проверка всей RAM и кратности записей вне временного стека, его содержимое независимо не вычисляется.
        def stack(item):
            return item[0] == 2 and 0x3FEC <= item[1] < 0x3FFE
        actual_data = [item for item in memory.writes if not stack(item)]
        assert Counter(actual_data) == Counter(writes), (path, actual_data, writes)
        stack_writes = [item for item in memory.writes if stack(item)]
        actual_depth = 0x3FFE - min(i for b, i, v in stack_writes) if stack_writes else 0
        assert actual_depth == depth, (path, actual_depth, depth)
        maximum_depth = max(maximum_depth, depth)
        expected[2][0x3FEC:0x3FFE] = memory.banks[2][0x3FEC:0x3FFE]
        assert all(a == b for a, b in zip(expected, memory.banks)), path
        assert trace.writes == ports and memory.o7ffd == (16 if ports else page)
        touched = {(b, i) for b, i, v in memory.writes}
        counts[path] += 1

    # Проверка всех слов модулей по отдельным сечениям и всех байтов запрета.
    for value in range(65536):
        check(x=value)
        check(y=value)
    for value in range(256):
        check(gate=value)
    # Проверка всех пар старых координат и всех возможных знаков и малых расстояний по отдельным осям.
    for value in range(256):
        for distance in range(16):
            for sign in (0, 128):
                check(x=distance, sx=sign, old_x=value, request=1)
                check(y=distance, sy=sign, old_y=value, request=1)
    # Проверка каждого входного HL' при записи кода, без требования выравнивания указателя.
    for value in range(65536):
        check(record=value, request=1, targets=(3, 4, 255))
    for request in range(256):
        for targets in ((255, 3, 4), (3, 255, 4), (3, 4, 255), (3, 4, 5)):
            check(request=request, targets=targets)
    # Проверка четырёх незаблокированных конфигураций банка 0, границ кольца и молчаливого отказа.
    for page, head, mask in product((0, 8, 16, 24), (0, 15, 16), (0, 32767, 65535)):
        check(request=1, targets=(1, 2, 3), page=page, head=head, mask=mask)
    for value in range(256):
        check(request=1, targets=(value, value, value), record=0xA100 + 64 * (value % 25))
    assert set(counts) == {'frame_blocked', 'high_rejected', 'x_rejected', 'y_rejected', 'follow_only', 'target_0', 'target_1', 'target_2', 'targets_full'}
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), queue_results=dict(queue_results),
        method='independent_parent_follow_and_index_oracle_with_real_banked_queue', independent_complete_child_oracle=False,
        children_executed_without_stubs=True, exact_registers_flags_refresh_sp=True,
        every_non_stack_physical_ram_byte_and_write_multiplicity_checked=True, temporary_stack_contents_independently_checked=False,
        maximum_additional_stack_bytes=maximum_depth, all_pointer_words_tested=True,
        minus_one_suppressed_but_other_negative_differences_round_down=True, full_queue_preserves_prior_state_changes=True,
        execution_boundary='E36A..E40F, rendering continuation not executed', all_joint_inputs_exhausted=False,
        whole_projection_scan_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionAimFollowVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
