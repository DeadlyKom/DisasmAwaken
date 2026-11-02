"""Формулы генератора, ограничение координат и XOR-точки через линейные таблицы."""
def sub8_flags(a, b):
    result = (a - b) & 255
    return (result & 0xA8) | (0x40 if result == 0 else 0) | 2 | (0x10 if (a & 15) < (b & 15) else 0) | (4 if ((a ^ b) & (a ^ result) & 128) else 0) | int(a < b)


def sub16_flags(a, b):
    result = (a - b) & 65535
    return ((result >> 8) & 0xA8) | (0x40 if result == 0 else 0) | 2 | (0x10 if (a & 4095) < (b & 4095) else 0) | (4 if ((a ^ b) & (a ^ result) & 32768) else 0) | int(a < b)


def random_step(seed):
    mixed = (7 * seed - 4) & 65535
    difference = ((mixed >> 8) - (mixed & 255)) & 65535
    intermediate = (mixed - difference) & 65535
    following = (intermediate - 1) & 65535
    return following, mixed, difference, sub16_flags(mixed, difference)


def coordinates(seed):
    points = []
    for _ in range(35):
        seed, _, _, _ = random_step(seed)
        x = seed & 255
        x = x + 2 if x == 0 else x - 2 if x >= 254 else x
        seed, _, _, _ = random_step(seed)
        y = seed & 127
        y = 2 if y == 0 else y
        # CP берёт недокументированные биты 5 и 3 из операнда, SUB из результата.
        flags = ((sub8_flags(y, 95) & ~0x28) | (95 & 0x28)) if y < 95 else sub8_flags(y, 64)
        y = y if y < 95 else y - 64
        points += [y, x]
    return seed, points, flags


def bitmap_tables():
    result = [0] * 1024
    for value in range(256):
        address = 0x8000 + 32 * value
        result[value] = address >> 8
        result[256 + value] = address & 255
        result[512 + value] = value // 8
        result[768 + value] = 128 >> (value & 7)
    return result


def draw_points(memory):
    writes = []
    for index in range(35):
        y, x = memory[0xC500 + 2 * index:0xC502 + 2 * index]
        # Чтение таблиц отдельно от их построения, потребитель сам их корректность не проверяет.
        address = memory[0x9400 + y] * 256 + ((memory[0x9500 + y] + memory[0x9600 + x]) & 255)
        memory[address] ^= memory[0x9700 + x]
        writes.append((address, memory[address]))
    return writes
