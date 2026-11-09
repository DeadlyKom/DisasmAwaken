"""Разнесённые младшие и старшие адресные байты отсечения предпросмотра."""
import json
import re

from CheckPreviewClipTablePages import CODES, ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'PreviewClipTablePages'
TAG = DOCUMENT
REQUIRED_REPORTS = ('PreviewClipTablePagesVerification', 'PreviewClipDispatchVerification')
BINDINGS = ()
FIELDS = tuple((f'End{index:X}', 1, 'байт адреса по прямому коду второго конца')
               for index in range(16))
TABLES = tuple(
    (6, 0xC000, (name, f'Source/D3D/Data/{name}.asm', start, end, 'FPreviewClipTargetRow',
                  FIELDS, tuple(f'Start{index:X}' for index in range((end - start) // 16))))
    for name, start, end in (('PreviewClipTargetLow', 0xC00, 0xD00),
                             ('PreviewClipTargetHigh', 0xD00, 0xDB0))
)


def code_symbols():
    data = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    return {name: address for name, address in data.items() if name.startswith('D3D.')}


def validate_sources(sources):
    data = sources[6]
    targets = {data[0xC00 + i * 16 + j] + 256 * data[0xD00 + i * 16 + j]
               for i in CODES for j in CODES}
    assert len(targets) == 71 and targets <= set(code_symbols().values())
    assert data[0xDB0:0xDC0] == bytes((128, 64, 32, 16, 8, 4, 2, 1, 127, 191, 223, 239, 247, 251, 253, 254))
    return dict(normal_pairs=81, normal_targets=71, low_bytes=256, high_prefix_bytes=176,
                existing_pixel_masks_preserved=True)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[разнесённые адресные страницы](../../../Docs/PreviewClipTablePages.md)')
    low = definition[2] == 0xC00
    operator = 'LOW' if low else 'HIGH'
    names = {address: name for name, address in reversed(tuple(code_symbols().items()))}
    first = second = 0
    result = []
    for line in text.splitlines():
        match = re.match(r'Start([0-9A-F]):', line)
        if match:
            first, second = int(match[1], 16), 0
        elif re.match(r'\s+#[0-9A-F]{2}', line):
            code = line.partition(';')[0].rstrip()
            if first in CODES and second in CODES:
                index = first * 16 + second
                target = source[0xC00 + index] + 256 * source[0xD00 + index]
                code = ' ' * 20 + f'{operator}(@{names[target]})' + (',' if second < 15 else '')
                note = 'младший байт цели' if low else 'старший байт цели'
            else:
                note = 'исходный байт за пределами девяти допустимых кодов'
            line = code.ljust(80) + f'; End{second:X}, {note}'
            second += 1
        result.append(line)
    return '\n'.join(result) + '\n', labels


def parse(text, origin, definition):
    symbols = code_symbols()

    def literal(match):
        operation, symbol = match.groups()
        address = symbols[symbol]
        return f'#{((address >> 8 if operation == "HIGH" else address) & 255):02X}'

    text = re.sub(r'(LOW|HIGH)\(@([A-Za-z0-9_.]+)\)', literal, text)
    return parse_records(text, definition, origin)


def structures():
    name = 'FPreviewClipTargetRow'
    lines = ['                struct ' + name]
    lines.extend((field.ljust(16) + 'db #00').ljust(80) + '; ' + note for field, _, note in FIELDS)
    lines.extend(('                ends', f'                assert {name} == 16'))
    lines.extend(f'                assert {name}.{field} == {index}'
                 for index, (field, _, _) in enumerate(FIELDS))
    return '\n'.join(lines) + '\n'
