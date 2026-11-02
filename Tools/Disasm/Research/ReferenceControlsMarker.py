"""Адресная модель XOR-маркера в линейном буфере, с исходными INC/DEC только младшего байта."""
def low_step(address, amount):
    return (address & 0xFF00) | ((address + amount) & 255)


def marker(memory, position):
    source = 0xF0ED + 4 * (position & 7)
    masks = memory[source:source + 4]
    upper = low_step(0x8000 + position // 8, 1)
    writes = []
    for row in (0, 1, 2, 3, 7, 8, 9, 10):
        writes.append((upper + 32 * row, masks[0]))
    center = upper + 160
    for address, mask in zip((low_step(center, -1), center, low_step(center, 1)), masks[1:]):
        writes.append((address, mask))
    # Слияние выполняется XOR, повторное применение без изменения фона снимает маркер.
    for address, mask in writes:
        memory[address] ^= mask
    return writes
