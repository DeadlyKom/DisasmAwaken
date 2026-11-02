"""Исходные CA8D/CAB3/CAE3 и фактический построитель таблиц 43CF."""
from pathlib import Path
import json
import sys
import collections

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory, payload
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
import ReferenceControlsBufferPoints as reference


def main():
    base = base_memory()
    boot = payload(17)[0x212:0x23D]
    base[0x43CF:0x43CF + len(boot)] = boot
    memory = Memory(base)
    simulator = Simulator(memory)
    counts = {}
    transitions = []

    def run(entry, expected, expected_writes, seed=0, expected_registers=None):
        initial = get_registers({'AF': seed, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'PC': entry, 'SP': 0xBFFE}, None, False)
        initial[14], initial[26], initial[27] = seed & 255, seed & 1, seed % 3
        simulator.registers[:] = initial
        memory[0xBFFE:0xC000] = expected[0xBFFE:0xC000] = [255, 63]
        memory.writes = []
        memory.recording = True
        for _ in range(9000):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат', hex(entry), seed))
        memory.recording = False
        # CALL из инициализатора сохраняет только один двухбайтовый адрес возврата.
        if entry == 0xCAB3:
            expected[0xBFFC:0xBFFE] = [0xC9, 0xCA]
        assert memory == expected, ('память', hex(entry), seed)
        if expected_writes is not None:
            assert memory.writes == expected_writes, ('записи', hex(entry), seed)
        registers = simulator.registers
        assert registers[SP] == 0xC000
        assert all(registers[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27))
        for index, value in (expected_registers or {}).items():
            assert registers[index] == value, ('регистр', hex(entry), seed, index, registers[index], value)
        return registers, initial

    # Проверка построителя таблиц на его оригинальных байтах, сравнение всех четырёх страниц.
    memory[:] = base
    expected = list(memory)
    expected[0x9400:0x9800] = reference.bitmap_tables()
    regs, initial = run(0x43CF, expected, None)
    assert len(memory.writes) == 1024 and len({a for a, _ in memory.writes}) == 1024
    assert set(memory.writes) == {(a,expected[a]) for a in range(0x9400,0x9800)}
    assert regs[:8] == [0x20, 0x62, 0, 0x20, 0xA0, 0, 0x96, 0], regs[:8]
    assert regs[16:24] == [0x80, 0x83, *initial[18:24]], regs[16:24]
    with_tables = list(memory)
    counts['bitmap_tables'] = 1
    # Проверка перехода генератора для каждого исходного 16-битового состояния.
    memory[:] = base
    for seed in range(65536):
        memory.recording = False
        memory[0xCA8F:0xCA91] = [seed & 255, seed >> 8]
        following, mixed, difference, flags = reference.random_step(seed)
        expected = list(memory)
        expected[0xCA8F:0xCA91] = [following & 255, following >> 8]
        regs, initial = run(0xCA8D, expected, [(0xCA8F, following & 255), (0xCA90, following >> 8)], seed)
        assert regs[:8] == [following & 255, flags, *initial[2:8]]
        assert regs[16:24] == [*initial[16:18], 0, mixed & 255, difference >> 8, difference & 255, following >> 8, following & 255]
        transitions.append(memory[0xCA8F] + 256 * memory[0xCA90])
    counts['random_step'] = 65536
    # Поиск периода штатного нулевого состояния по переходам, фактически полученным из исходных инструкций.
    visited = {}
    state = 0
    while state not in visited:
        visited[state] = len(visited)
        state = transitions[state]
    orbit = dict(seed=0, prefix_length=visited[state], cycle_length=len(visited) - visited[state], repeated_state=state,
                 distinct_next_states=len(set(transitions)))
    print('Random states 65536', flush=True)
    # Проверка составной подготовки 35 пар с настоящими семьюдесятью вызовами генератора.
    for seed in (*range(256), *(i * 257 for i in range(256))):
        memory.recording = False
        memory[:] = base
        memory[0xCA8F:0xCA91] = [seed & 255, seed >> 8]
        following, points, y_flags = reference.coordinates(seed)
        expected = list(memory)
        expected[0xCA8F:0xCA91] = [following & 255, following >> 8]
        expected[0xC500:0xC546] = points
        regs, initial = run(0xCAB3, expected, None, seed)
        # Проверка всех записей CALL, состояния генератора и физических полей каждой пары.
        writes = []
        state = seed
        for index in range(35):
            for return_address in (0xCAB9,0xCAC9):
                state,mixed,difference,_ = reference.random_step(state)
                writes += [(0xBFFC,return_address & 255),(0xBFFD,return_address >> 8),
                    (0xCA8F,state & 255),(0xCA90,state >> 8)]
            writes += [(0xC500+2*index,points[2*index]),(0xC501+2*index,points[2*index+1])]
        assert collections.Counter(memory.writes) == collections.Counter(writes)
        assert regs[:8] == [0x46, 0x42, *initial[2:6], 0xC5, 0x46]
        assert regs[16:18] == [points[-2], y_flags & 1], (seed, regs[16:18], points[-2], y_flags)
        assert regs[18:24] == [0,mixed & 255,difference >> 8,difference & 255,following >> 8,following & 255]
        assert all(1 <= points[i] <= (94 if i % 2 == 0 else 253) for i in range(70))
    counts['initialize_points'] = 512
    # Проверка всех координат линейного растра 256 на 96, пакетами по 35 точек.
    point_cases = 0
    viewport_batches = (256 * 96 + 34) // 35
    for batch in range(viewport_batches + 2):
        memory.recording = False
        memory[:] = with_tables
        for index in range(35):
            value = (batch * 35 + index) % (256 * 96)
            point = [value // 256,value & 255]
            if batch == viewport_batches:
                point = [0,0]
            elif batch == viewport_batches+1:
                point = [5,7] if index < 34 else [6,8]
            memory[0xC500 + 2 * index:0xC502 + 2 * index] = point
        expected = list(memory)
        writes = reference.draw_points(expected)
        regs, initial = run(0xCAE3, expected, writes, batch)
        y, x = memory[0xC544:0xC546]
        target = 0x8000 + 32 * y + x // 8
        assert regs[:8] == [0x46, 0x42, 0xC5, 0x46, target >> 8, target & 255, 0x97, x]
        assert regs[16:24] == initial[16:24]
        point_cases += 1
    counts['draw_batches'] = point_cases
    report = dict(passed=True, cases_by_kind=counts, total_cases=sum(counts.values()),
        all_random_seed_words=True, all_viewport_coordinates=True, original_bitmap_builder=True,
        actual_random_calls_executed=True, exact_memory_and_writes_checked=True,
        xor_duplicates_not_removed=True, fields_order_y_then_x=True,
        independent_random_flags=True, generator_orbit=orbit, invalid_point_y_above_95_proved=False,
        native_execution=False, irq_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBufferPointsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
