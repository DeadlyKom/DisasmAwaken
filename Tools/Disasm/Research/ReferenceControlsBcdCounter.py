"""Модель четырёх BCD-пар и их частичного экранного обновления."""
from ReferenceControlsTextDisplay import draw_rows


def pair(value):
    return (value // 10) * 16 + value % 10


def encode(value):
    # Преобразование целого в физический порядок E,D,L,H существующих четырёх байтов.
    digits = [pair((value // (100 ** index)) % 100) for index in range(4)]
    return [digits[2], digits[3], digits[0], digits[1]]


def decode(memory):
    e, d, l, h = memory[0x9BBD:0x9BC1]
    digits = [l, h, e, d]
    assert all((v & 15) < 10 and v >> 4 < 10 for v in digits)
    return sum((10 * (v >> 4) + (v & 15)) * 100 ** i for i, v in enumerate(digits))


def nibble(memory, value, column, events):
    index = 16 + (value & 15)
    events.append((value & 15, column))
    draw_rows(memory, 0xC600 + 6 * (index // 2), 0x5100 + column // 2, (column + 1) & 255, index)


def display(memory, values, mask, events):
    # Вывод начинается с младшей пары, более старшие пары выбираются цепочкой переносов.
    for index, (value, right_column) in enumerate(zip(values, (47, 44, 41, 39))):
        nibble(memory, value, right_column, events)
        nibble(memory, value >> 4, right_column - 1, events)
        if index == 3 or not mask & (1 << index):
            return


def tick(memory, events):
    gate = memory[0xF10E]
    memory[0xF10E] = (gate >> 1) | ((gate & 1) << 7)
    if not gate & 1:
        return
    value = decode(memory)
    # Вычисление маски переносов между парами по исходному значению до инкремента.
    mask = 0
    for index in range(3):
        if value % (100 ** (index + 1)) != 100 ** (index + 1) - 1:
            break
        mask |= 1 << index
    memory[0x9BBD:0x9BC1] = encode((value + 1) % 100000000)
    e, d, l, h = memory[0x9BBD:0x9BC1]
    display(memory, (l, h, e, d), mask, events)
