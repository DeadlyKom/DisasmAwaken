"""M1 фиксированного неотсечённого XOR-пакета B2,00,05,00."""
from functools import lru_cache
from CheckActionParameterActivation import flat_action

RANGES = ((0xDD23, 0xDD29), (0xDD6F, 0xDD76), (0xDD7C, 0xDD8F),
          (0xDD9C, 0xDDCA), (0xDDCA, 0xDDD1), (0xDD23, 0xDD26))


@lru_cache(maxsize=1)
def layout():
    from InspectZ80 import decoder
    flat = flat_action()
    blocks = []
    m1 = 0
    # Подсчёт только фактически пройденных блоков фиксированного заголовка.
    # Последний блок повторно читает терминатор и выполняет RET Z.
    for start, end in RANGES:
        instructions = decoder(flat).disassemble(start, end, 'h')
        m1 += sum(2 if instruction.bytes[0] in (0xCB, 0xED, 0xDD, 0xFD) else 1
                  for instruction in instructions)
        blocks.append((start, bytes(flat[start:end])))
    return m1, tuple(blocks)


def eligible(read, pointer):
    if bytes(read(pointer + i) for i in range(4)) != bytes((0xB2, 0, 5, 0)):
        return False
    # Изменённые инструкции сборщика не покрываются постоянной стоимостью.
    return all(bytes(read(start + i) for i in range(len(block))) == block for start, block in layout()[1])


def refresh_cost(line_m1):
    return layout()[0] + line_m1
