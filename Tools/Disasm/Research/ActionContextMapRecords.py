"""Формат станционных записей в средней части передаваемого контекста ACTION."""

from CheckIntro import ROOT
from SavedStateLayout import parse, records, structures


START, END, ORIGIN = 0x3C8B, 0x3D4C, 0x6000
PATH = 'Source/Action/Data/ContextMapAndOptions.asm'
MODULE = 'ActionContextMapAndOptions'
GROUPS = (
    ('StoredMapPoints', 0x3C8C, 0x3CF2, 'Point'),
    ('StoredMapOrder', 0x3CF2, 0x3CFD, 'Order'),
    ('MapAuxiliaryPoints', 0x3CFD, 0x3D25, 'Aux'),
    ('MapAuxiliaryCodes', 0x3D25, 0x3D30, 'Codes'),
    ('InterfaceChoices', 0x3D30, 0x3D38, 'Choice'),
    ('PointerKeys', 0x3D38, 0x3D44, 'Key'),
    ('InterfaceColors', 0x3D44, 0x3D4A, 'Color'),
    ('ControlOptions', 0x3D4A, 0x3D4C, 'Option'),
)


def render(action, station):
    types = structures()
    lines = ['                module ' + MODULE,
             '                ; Документация [средняя часть переносимого состояния](../../../Docs/ActionContextTail.md)',
             f'                assert $ == #{ORIGIN + START:04X}',
             f'BeforeMap:      db #{action[START]:02X}'.ljust(80) + '; старший байт архивного DALNO, современный читатель неизвестен']
    differences = {}
    for name, begin, end, prefix in GROUPS:
        # Проверка общей схемы по соответствующим полям исходного STATIONF.
        origin = begin - 0x3BBD + 0x383B
        station_data = station[origin:origin + end - begin]
        station_source = (ROOT / f'Source/Station/Data/{name}.asm').read_text('utf-8')
        position = begin
        compared = bytearray()
        lines.extend(('                ; -----------------------------------------',
                      '                ; Переносимая группа ' + name,
                      f'                assert $ == #{ORIGIN + begin:04X}'))
        for index, (station_label, kind, arguments) in enumerate(records(station_source)):
            if position == end:
                break
            label = f'{prefix}{index:02}'
            if name in ('InterfaceChoices', 'InterfaceColors'):
                label = station_label
            elif name == 'PointerKeys':
                label = 'Pointer' + station_label
            elif name == 'ControlOptions':
                assert station_label == 'MouseOption'
                label = 'FlightMouse'
            fields = types[kind] if kind else ((None, 1),)
            original_values = [int(value.strip()[1:], 16) for value in arguments.split(',')]
            assert len(original_values) == len(fields)
            if kind:
                lines.append((label + ':').ljust(16) + kind + ' {')
            for field_index, ((field, width), original) in enumerate(zip(fields, original_values)):
                compared.extend(original.to_bytes(width, 'little'))
                value = int.from_bytes(action[position:position + width], 'little')
                position += width
                literal = f'#{value:0{width * 2}X}'
                if kind:
                    comma = ',' if field_index + 1 < len(fields) else ''
                    lines.append((' ' * 20 + literal + comma).ljust(80) + '; ' + field + ', исходное значение ACTION')
                else:
                    lines.append(((label + ':').ljust(16) + 'db ' + literal).ljust(80) + '; граница станционного списка')
            if kind:
                lines.append('                }')
        assert position == end and compared == station_data, name
        differences[name] = sum(a != b for a, b in zip(action[begin:end], station_data))
    assert differences == dict.fromkeys((name for name, *_ in GROUPS if name != 'MapAuxiliaryCodes'), 0) | {'MapAuxiliaryCodes': 10}
    lines.extend((f'                assert $ == #{ORIGIN + END:04X}', '                endmodule', ''))
    text = '\n'.join(lines)
    raw, labels = parse(text, types)
    assert raw == action[START:END]
    symbols = {f'{MODULE}.{name}': ORIGIN + START + offset for name, offset in labels.items()}
    return text, symbols, differences
