"""Физическая разметка именно исходного Antichrist, без переноса и дублирования общих потоков."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
ORIGIN = 0xE700
STREAM_END = 3720
EFFECT_WIDTH = {1: 3, 2: 5, 3: 1, 4: 1, 5: 2, 8: 3, 9: 1}
EXTRA_STRUCTURES = {
    'FMusicModuleHeader': (
        ('Description', 99, 'text', '99 исходных символов названия, автора и строки компилятора'),
        ('Unknown63', 1, 'db', 'исходный байт 02 по смещению 99, InitializeModule его пропускает, назначение не доказано'),
        ('RowTempo', 1, 'db', 'начальное количество тиков на строку, копируется в изменяемый операнд'),
        ('PositionCount', 1, 'db', 'байт количества позиций, попадает в F при POP AF, границу списка задаёт FF'),
        ('LoopIndex', 1, 'db', 'смещение позиции возврата от начала списка в байтах'),
        ('PatternTable', 2, 'dw', 'относительный адрес таблицы троек указателей')),
    'FMusicRelativePointer': (('Offset', 2, 'dw', 'относительный адрес от начала композиции, ноль сохраняется буквально'),),
    'FMusicPositionByte': (('Value', 1, 'db', 'смещение в единицах слова для тройки паттернов, FF завершает список'),),
    'FMusicPatternPointers': (
        ('ChannelA', 2, 'dw', 'относительный адрес потока A'),
        ('ChannelB', 2, 'dw', 'относительный адрес потока B'),
        ('ChannelC', 2, 'dw', 'относительный адрес потока C')),
    'FMusicOrnamentStep': (('NoteDelta', 1, 'db', 'байтовая поправка индекса ноты с оборачиванием при сложении'),)}


def word(data, offset):
    return int.from_bytes(data[offset:offset + 2], 'little')


def stream_records(data, start, end, channel):
    """Чтение физических команд и LIFO-параметров по доказанной грамматике декодера."""
    records, cursor, row = [], start, 0
    while cursor < end:
        deferred = []
        first = True
        while True:
            address = cursor
            opcode = data[cursor]
            cursor += 1
            width = 0
            terminal = False
            if opcode == 0:
                assert address == end - 1 and first
                records.append(dict(offset=address, length=1, label='End', kind='end', note='исходный нулевой байт физической границы потока, переход позиции описан в MusicPattern.md'))
                return records
            if opcode >= 0xF0:
                width = 1
                note = 'орнамент ' + str(opcode - 0xF0) + ', следующий байт является уже удвоенным индексом сэмпла'
            elif opcode >= 0xD0:
                terminal = opcode == 0xD0
                note = 'завершение строки без новой ноты' if terminal else 'выбор сэмпла ' + str(opcode - 0xD0)
            elif opcode >= 0xC0:
                terminal = opcode == 0xC0
                note = 'выключение ноты и завершение строки' if terminal else 'строка громкости ' + str(opcode - 0xC0)
            elif opcode >= 0xB0:
                width = 0 if opcode == 0xB0 else 1 if opcode == 0xB1 else 2
                note = ('снятие маски огибающей' if opcode == 0xB0 else 'перезагрузка длительности строки' if opcode == 0xB1
                        else 'форма огибающей ' + str(opcode - 0xB1) + ', период старшим байтом вперёд')
            elif opcode >= 0x50:
                terminal = True
                note = 'нота с индексом #' + format(opcode - 0x50, '02X') + ', завершение строки'
            elif opcode >= 0x40:
                note = 'выбор орнамента ' + str(opcode - 0x40)
            elif channel == 'B' and opcode >= 0x20:
                note = 'базовый шум #' + format(opcode - 0x20, '02X')
            elif opcode >= 0x10:
                width = 1 if opcode == 0x10 else 3
                note = ('снятие маски огибающей и сырой удвоенный индекс сэмпла' if opcode == 0x10
                        else 'форма огибающей ' + str(opcode - 0x10) + ', старший и младший период, сырой индекс сэмпла')
            else:
                assert opcode in EFFECT_WIDTH, ('reserved_effect_in_original_stream', channel, address, opcode)
                deferred.append(opcode)
                note = 'отложенный эффект #' + format(opcode, '02X') + ', параметры читаются после терминатора'
            cursor += width
            assert cursor <= end
            records.append(dict(offset=address, length=cursor - address, label='Row' + format(row, '02X') if first else '', kind='command', note=note))
            first = False
            if terminal:
                break
        for effect in reversed(deferred):
            width = EFFECT_WIDTH[effect]
            assert cursor + width <= end
            records.append(dict(offset=cursor, length=width, label='', kind='parameters',
                                note='параметры отложенного эффекта #' + format(effect, '02X') + ', порядок RET от последнего к первому'))
            cursor += width
        row += 1
    raise ValueError(('missing_original_stream_end', start, end))


def layout(data):
    assert len(data) == 4137 and data[100:103] == bytes((3, 28, 4)) and word(data, 103) == 230
    assert data[229] == 255 and all(value % 3 == 0 for value in data[201:229])
    groups = [tuple(word(data, 230 + 6 * index + 2 * channel) for channel in range(3)) for index in range(19)]
    references = {}
    for index, group in enumerate(groups):
        for channel, address in zip('ABC', group):
            references.setdefault(address, []).append(dict(pattern=index, channel=channel))
    streams = sorted(references)
    assert len(streams) == 41 and streams[0] == 344
    ranges = [dict(kind='header', offset=0, length=105), dict(kind='sample_offsets', offset=105, length=64),
              dict(kind='ornament_offsets', offset=169, length=32), dict(kind='positions', offset=201, length=29),
              dict(kind='pattern_offsets', offset=230, length=114)]
    for address, end in zip(streams, streams[1:] + [STREAM_END]):
        aliases = references[address]
        channel = aliases[0]['channel']
        assert all(alias['channel'] == channel for alias in aliases)
        records = stream_records(data, address, end, channel)
        assert sum(record['length'] for record in records) == end - address
        ranges.append(dict(kind='pattern', offset=address, length=end - address, channel=channel,
                           name='Pattern' + channel + format(aliases[0]['pattern'], '02X'), references=aliases, records=records))
    for kind, base, count, stride in (('sample', 105, 32, 4), ('ornament', 169, 16, 1)):
        present = set()
        for index in range(count):
            address = word(data, base + index * 2)
            if not address:
                continue
            assert address not in present
            present.add(address)
            loop, length = data[address:address + 2]
            assert 0 <= loop < length
            end = address + 2 + stride * length
            assert end <= len(data)
            ranges.append(dict(kind=kind, offset=address, length=end - address, index=index,
                               loop_position=loop, step_count=length, step_size=stride))
    ranges.sort(key=lambda item: item['offset'])
    cursor = 0
    for item in ranges:
        assert item['offset'] == cursor
        cursor += item['length']
        item['sha256'] = hashlib.sha256(data[item['offset']:cursor]).hexdigest()
    assert cursor == len(data)
    return ranges


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()[0xC00:]
    ranges = layout(raw)
    report = dict(passed=True, module_bytes=len(raw), ranges=ranges,
        positions=28, pattern_groups=19, unique_pattern_streams=41,
        samples=sum(item['kind'] == 'sample' for item in ranges),
        sample_steps=sum(item.get('step_count', 0) for item in ranges if item['kind'] == 'sample'),
        ornaments=sum(item['kind'] == 'ornament' for item in ranges),
        ornament_steps=sum(item.get('step_count', 0) for item in ranges if item['kind'] == 'ornament'),
        physical_bytes_covered=4137, shared_streams_preserved=True, zero_offsets_preserved=True,
        header_byte_99_semantics_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicCompositionLayout.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'ranges'}, indent=2))


if __name__ == '__main__':
    main()
