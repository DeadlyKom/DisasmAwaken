"""Физические строки таблиц преобразования и кадров двух эффектов VOXAL."""
import re

TABLES = (
    ('VoxelPalette', 'Source/Voxel/Data/Palette.asm', 0, 1024, 16, 64),
    ('LargeEffectFrames', 'Source/Voxel/Data/LargeEffectFrames.asm', 1024, 6144, 32, 160),
    ('SmallEffectFrames', 'Source/Voxel/Data/SmallEffectFrames.asm', 6144, 8640, 16, 156),
)


def structures():
    lines = []
    for width in (16, 32):
        name = 'FEffectByteRow' + str(width)
        lines.append('                struct ' + name)
        for col in range(width):
            lines.append((f'Pair{col:02}'.ljust(16) + 'db #00').ljust(80) +
                         '; исходная пара четырёхбитных кодов либо результат табличной выборки')
        lines.extend(('                ends', f'                assert {name} == #{width:02X}', ''))
    return '\n'.join(lines)


def render(data, table):
    module, path, start, end, width, count = table
    assert end - start == width * count
    lines = ['                module ' + module,
             '                ; Документация [таблицы и кадры](../../../Docs/VoxelPhysicalResources.md)',
             f'                assert $ == #{0xC000 + start:04X}']
    labels = {}
    for row in range(count):
        if module == 'VoxelPalette':
            page, high = divmod(row, 16)
            name = f'Page{page}High{high:X}'
            lines.append(f'                ; Страница #{0xC0 + page:02X}, старший код {high}, поля выбирают младший код 0..15.')
        else:
            rows = 20 if width == 32 else 12
            frame, frame_row = divmod(row, rows)
            name = f'Frame{frame:02}' if not frame_row else f'F{frame:02}R{frame_row:02}'
            if not frame_row:
                lines.append(f'                ; Кадр {frame}, {rows} строк по {width} байтов.')
        address = 0xC000 + start + row * width
        labels[module + '.' + name] = address
        lines.append((name + ':').ljust(16) + f'FEffectByteRow{width} {{')
        values = data[start + row * width:start + (row + 1) * width]
        for col, value in enumerate(values):
            line = f'                    #{value:02X}' + (',' if col < width - 1 else '')
            lines.append(line.ljust(80) + f'; Pair{col:02}')
        lines.append('                }')
    lines.extend((f'                assert $ == #{0xC000 + end:04X}', '                endmodule', ''))
    return '\n'.join(lines), labels


def parse(text):
    position = None
    remaining = 0
    data = bytearray()
    labels = {}
    module = None
    for original in text.splitlines():
        line = original.partition(';')[0].strip()
        if not line or line == 'endmodule':
            continue
        if line.startswith('module '):
            assert module is None
            module = line.split()[1]
            continue
        if line.startswith('assert $ == #'):
            value = int(line.rsplit('#', 1)[1], 16)
            if position is None:
                position = value
            else:
                assert position == value and not remaining
            continue
        match = re.fullmatch(r'(\w+):\s+FEffectByteRow(16|32) \{', line)
        if match:
            assert not remaining
            labels[module + '.' + match[1]] = position
            remaining = int(match[2])
            continue
        if line == '}':
            assert not remaining
            continue
        match = re.fullmatch(r'#([0-9A-F]{2}),?', line)
        assert match and remaining, original
        data.append(int(match[1], 16))
        position += 1
        remaining -= 1
    assert module and not remaining
    return bytes(data), labels
