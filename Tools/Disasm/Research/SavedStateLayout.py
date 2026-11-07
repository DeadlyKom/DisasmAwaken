"""Физический формат SAVE по доказанному двухсекторному переносу станции."""
import re
from collections import Counter
from pathlib import Path

from CheckIntro import ROOT

START, SIZE = 0x983B, 512
SLOTS = ((11, 'SAVE1'), (12, 'SAVE2'), (13, 'SAVE3'),
         (14, 'SAVE4'), (15, 'SAVE5'), (16, 'SAVE0'))


def structures():
    result = {}
    text = (ROOT / 'Includes/Structs/Include.inc').read_text(encoding='utf-8')
    for match in re.finditer(r'\bstruct\s+(\w+)\s*\n(.*?)\bends\b', text, re.S | re.I):
        fields = []
        for line in match[2].splitlines():
            code = line.partition(';')[0].strip()
            if not code:
                continue
            field = re.fullmatch(r'(\w+)\s+(db|dw)\s+#[0-9a-fA-F]+', code, re.I)
            if not field:
                break
            fields.append((field[1], 1 if field[2].lower() == 'db' else 2))
        else:
            result[match[1]] = fields
    return result


def records(source):
    """Чтение существующих плоских экземпляров и отдельных маркеров списка."""
    code = '\n'.join(line.partition(';')[0] for line in source.splitlines())
    pattern = r'(\w+):\s+(?:(F\w+)\s*\{([^}]+)\}|db\s+(#[0-9A-Fa-f]+))'
    result = []
    for match in re.finditer(pattern, code):
        result.append((match[1], match[2], match[3] or match[4]))
    return result


def render(data, span, name, types):
    source = (ROOT / span['path']).read_text(encoding='utf-8')
    rows = records(source)
    offset = span['offset'] - (START - 0x6000)
    module = name.title() + Path(span['path']).stem
    lines = ['                module ' + module,
             '                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)',
             '                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.',
             f'                assert $ == #{offset:04X}']
    cursor = offset
    counts = Counter(label for label, _, _ in rows)
    seen = Counter()
    for label, kind, values in rows:
        if counts[label] > 1:
            old = label
            label = label + chr(ord('A') + seen[old])
            seen[old] += 1
        assert len(label) < 16
        if kind is None:
            lines.append((label + ':').ljust(16) + f'db #{data[cursor]:02X}'.ljust(64) +
                         '; исходный байт границы списка, сохранён без нормализации')
            cursor += 1
            continue
        fields = types[kind]
        assert len(values.split(',')) == len(fields)
        lines.append((label + ':').ljust(16) + kind + ' {')
        for index, (field, size) in enumerate(fields):
            value = int.from_bytes(data[cursor:cursor + size], 'little')
            assert cursor + size <= offset + span['length']
            line = f'                    #{value:0{size * 2}X}' + (',' if index < len(fields) - 1 else '')
            lines.append(line.ljust(80) + '; ' + kind + '.' + field + ', значение дискового слота')
            cursor += size
        lines.append('                }')
    assert cursor == offset + span['length']
    lines += [f'                assert $ == #{cursor:04X}', '                endmodule', '']
    return '\n'.join(lines), module


def parse(text, types):
    raw = bytearray()
    labels = {}
    for label, kind, values in records(text):
        assert label not in labels
        labels[label] = len(raw)
        if kind is None:
            raw.append(int(values[1:], 16))
            continue
        fields = types[kind]
        values = [value.strip() for value in values.split(',')]
        assert len(values) == len(fields)
        for value, (_, size) in zip(values, fields):
            assert re.fullmatch(r'#[0-9A-Fa-f]+', value)
            raw.extend(int(value[1:], 16).to_bytes(size, 'little'))
    return bytes(raw), labels
