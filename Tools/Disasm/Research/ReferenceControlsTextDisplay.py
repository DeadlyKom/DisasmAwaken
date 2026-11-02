"""Модель экранных и управляющих данных текстового окна, без исполнения Z80."""
QUEUE = 0xEC80
ACTIVE = 0xECA3
READER = 0xECAA
COLUMN = 0xEFD6


def word(memory, address):
    return memory[address] + 256 * memory[address + 1]


def put_word(memory, address, value):
    memory[address:address + 2] = [value & 255, value >> 8]


def pixel_address(y, x_byte):
    return 0x4000 + ((y & 192) << 5) + ((y & 7) << 8) + ((y & 56) << 2) + x_byte


def initialize(memory):
    # Обновление только курсоров и операндов тридцати копирующих строк.
    put_word(memory, ACTIVE, 0)
    put_word(memory, READER, QUEUE - 2)
    put_word(memory, 0xEC5D, QUEUE)
    for index in range(30):
        row, scan = divmod(index, 6)
        put_word(memory, 0xED2D + 20 * index, pixel_address(152 + 8 * row + scan, 20))
        put_word(memory, 0xED37 + 20 * index, pixel_address(144 + 8 * row + scan, 20) + 12)


def scroll(memory):
    # Перенос шести растровых строк каждого из пяти текстовых рядов вверх.
    for row in range(5):
        for scan in range(6):
            source = pixel_address(152 + 8 * row + scan, 20)
            target = pixel_address(144 + 8 * row + scan, 20)
            memory[target:target + 12] = memory[source:source + 12]
    # Очистка нижнего ряда с сохранением исходного правого узора 00,01 по вертикали.
    for scan in range(6):
        target = pixel_address(184 + scan, 20)
        memory[target:target + 12] = [0] * 11 + [scan & 1]


def glyph(memory, character, events):
    events.append(('glyph', character))
    column = memory[COLUMN]
    if column >= 24:
        events.append(('scroll',))
        scroll(memory)
        column = 0
    memory[COLUMN] = column + 1
    # Вычисление адреса пары знаков с байтовым переполнением SUB 20.
    code = (character - 32) & 255
    source = 0xC600 + 6 * (code // 2)
    draw_rows(memory, source, pixel_address(184, 20 + column // 2), column + 1, code)


def draw_rows(memory, source, destination, next_column, code):
    # Выбор старшей тетрады чётного знака и младшей тетрады нечётного.
    for scan in range(6):
        bits = memory[(source + scan) & 65535]
        nibble = bits >> 4 if code % 2 == 0 else bits & 15
        target = (((destination >> 8) + scan) & 255) * 256 + (destination & 255)
        if next_column % 2:
            memory[target] = (memory[target] & 15) | (nibble << 4)
        else:
            memory[target] = (memory[target] & 240) | nibble


def decimal(memory, value, events):
    # Преобразование байта в две либо три десятичные цифры, включая ведущий нуль.
    for character in format(value, '02d').encode('ascii'):
        glyph(memory, character, events)


def consume(memory, events, limit=1024):
    # Поиск следующей записи разрешён только при отсутствии активного указателя строки.
    for _ in range(limit):
        pointer = word(memory, ACTIVE)
        if not pointer:
            cursor = (word(memory, READER) + 2) & 65535
            for _ in range(18):
                put_word(memory, READER, cursor)
                kind = memory[cursor]
                if kind == 1:
                    return
                if kind == 0:
                    cursor = QUEUE
                    continue
                low = memory[(cursor + 1) & 65535]
                memory[cursor] = 1
                if kind == 2:
                    decimal(memory, low, events)
                    memory[COLUMN] = (memory[COLUMN] + 1) & 255
                    return
                pointer = kind * 256 + low
                break
            else:
                raise AssertionError('некорректная очередь без достижимой занятой или свободной записи')
        character = memory[pointer]
        put_word(memory, ACTIVE, (pointer + 1) & 65535)
        if character == 10:
            put_word(memory, ACTIVE, 0)
            return
        if character == 13:
            memory[COLUMN] = 0
            events.append(('scroll',))
            scroll(memory)
            continue
        glyph(memory, character, events)
        return
    raise AssertionError('строка не достигла возвращающего управления символа')
