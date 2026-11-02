"""Независимый конечный регистровый результат копирования непустого отрезка строк."""
def expected_registers(initial, memory, source, destination, count):
    result = list(initial)
    last = source + 256 * count - 16
    # Вычисление адреса следующей символьной строки и флагов последнего ADD HL,F910.
    before_add = destination + 32 * (count - 1) + 0x710
    after_add = (before_add + 0xF910) & 65535
    add_flags = (memory[last + 8] & 0xC4) | ((after_add >> 8) & 0x28)
    add_flags |= 0x10 if (before_add & 4095) + 0x910 > 4095 else 0
    add_flags |= int(before_add + 0xF910 > 65535)
    # Основной AF заканчивает DEC 1 в 0, Carry берётся из первого пиксельного слова последней группы.
    result[0:8] = [0, 0x42 | (memory[last] & 1), memory[last + 3], memory[last + 2],
                   memory[last + 5], memory[last + 4], (source + 256 * count) >> 8, 0]
    result[8:12] = [memory[last + 7], memory[last + 6], memory[last + 15], memory[last + 14]]
    result[12] = initial[12] + 2
    result[16:24] = [memory[last + 9], add_flags, memory[last + 11], memory[last + 10],
                     0xF9, 0x10, after_add >> 8, after_add & 255]
    return result


def check_registers(actual, expected):
    # Проверка всех основных, альтернативных, индексных и специальных регистров кроме R и внутренних счётчиков симулятора.
    compared = (*range(13), 14, *range(16, 24), 26, 27)
    assert all(actual[i] == expected[i] for i in compared), [(i, actual[i], expected[i]) for i in compared if actual[i] != expected[i]]
