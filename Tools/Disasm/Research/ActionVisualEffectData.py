"""Восемь записей FVisualEffect и физический префикс маркера списка."""
import re
from struct import Struct


PATH = 'Source/Action/Data/VisualEffects.asm'
MODULE = 'ActionVisualEffects'
ORIGIN = 0xA795
START, END = 0x4795, 0x482D
FORMAT = Struct('<HHHBBHHBBHBB')
FIELDS = ('SavedHL', 'SavedDE', 'SavedBC', 'Mode', 'State', 'Source',
          'Cursor', 'Unknown0C', 'Unknown0D', 'Unknown0E', 'Unknown10', 'Unknown11')
OFFSETS = (0, 2, 4, 6, 7, 8, 10, 12, 13, 14, 16, 17)
WIDTHS = (4, 4, 4, 2, 2, 4, 4, 2, 2, 4, 2, 2)
NOTES = ('сохранённое слово HL', 'сохранённое слово DE', 'сохранённое слово BC',
         'режим проекции', 'начальное свободное состояние', 'текущий адрес ресурса',
         'адрес перезапуска ресурса', 'счётчик ресурса', 'значение перезагрузки счётчика',
         'шаг адреса ресурса', 'размер по X', 'размер по Y')


def render(source):
    lines = ['                module ' + MODULE,
             '                ; Документация [обход визуальных эффектов](../../../Docs/ActionVisualEffectWalk.md)',
             '                assert $ == #A795']
    for index in range(8):
        lines.append((f'Effect{index}:').ljust(16) + 'FVisualEffect {')
        for n, (value, width, field, note) in enumerate(zip(
                FORMAT.unpack_from(source, START + FORMAT.size * index), WIDTHS, FIELDS, NOTES)):
            expression = f'                        #{value:0{width}X}' + (',' if n < len(FIELDS) - 1 else '')
            lines.append(expression.ljust(80) + '; ' + field + ', ' + note)
        lines.append('                }')
    marker = ', '.join(f'#{value:02X}' for value in source[END - 8:END])
    lines.extend(['                ; Только префикс маркера, State отрицателен по смещению 7.',
                  'EndMarker:      db ' + marker, '                assert $ == #A82D',
                  '                endmodule'])
    text = '\n'.join(lines) + '\n'
    decoded, symbols = parse(text)
    assert decoded == source[START:END]
    return text, symbols


def parse(text):
    lines = [part for line in text.splitlines() if (part := line.split(';', 1)[0].strip())]
    assert lines[:2] == ['module ' + MODULE, 'assert $ == #A795']
    raw = bytearray()
    symbols = {}
    cursor = 2
    for index in range(8):
        label = f'Effect{index}'
        assert lines[cursor] == f'{label}:        FVisualEffect {{'
        start = ORIGIN + len(raw)
        name = MODULE + '.' + label
        symbols[name] = start
        symbols.update({name + '.' + field: start + offset for field, offset in zip(FIELDS, OFFSETS)})
        values = []
        for n, width in enumerate(WIDTHS):
            line = lines[cursor + n + 1]
            assert re.fullmatch(r'#[0-9A-F]{' + str(width) + '}' + (',' if n < len(WIDTHS) - 1 else ''), line)
            values.append(int(line[1:1 + width], 16))
        raw.extend(FORMAT.pack(*values))
        cursor += len(WIDTHS) + 2
        assert lines[cursor - 1] == '}'
    assert re.fullmatch(r'EndMarker:      db (#[0-9A-F]{2}, ){7}#[0-9A-F]{2}', lines[cursor])
    symbols[MODULE + '.EndMarker'] = ORIGIN + len(raw)
    raw.extend(int(value, 16) for value in re.findall(r'#([0-9A-F]{2})', lines[cursor]))
    assert lines[cursor + 1:] == ['assert $ == #A82D', 'endmodule']
    return bytes(raw), symbols
