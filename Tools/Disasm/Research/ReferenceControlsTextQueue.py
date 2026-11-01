"""Семантика ограниченного поиска очереди, нулевой маркер тоже расходует одну проверку."""
QUEUE = 0xEC80
PRODUCER = 0xEC5D
CAPACITY = 16


def insert(memory, value):
    cursor = memory[PRODUCER] + 256 * memory[PRODUCER + 1]
    address = cursor
    checked = []
    for _ in range(CAPACITY):
        checked.append(address)
        kind = memory[address]
        if kind == 1:
            following = (address + 2) & 65535
            writes = [(address, value >> 8), (address + 1, value & 255),
                      (PRODUCER, following & 255), (PRODUCER + 1, following >> 8)]
            return dict(accepted=True, writes=writes, probes=checked, next_cursor=following)
        address = QUEUE if kind == 0 else (address + 2) & 65535
    return dict(accepted=False, writes=[], probes=checked, next_cursor=cursor)


def push_word(stack, value):
    return [(stack - 1, value >> 8), (stack - 2, value & 255)]
