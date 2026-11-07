"""Согласованный физический формат BAR и маскированных изображений BD0..BD3."""
import re
from CheckIntro import ROOT


def original():
    base = ROOT / 'Tools/Disasm/Extracted/Active'
    return ((base / '39_BAR.C.bin').read_bytes(),
            [(base / f'{40 + bank}_BD{bank}.C.bin').read_bytes() for bank in range(4)])


def decode(bar, banks):
    pointers = [int.from_bytes(bar[index:index + 2], 'little') for index in range(0, 72, 2)]
    groups, sprites = [], set()
    position = 72
    while position < len(bar):
        mode = int.from_bytes(bar[position:position + 2], 'little')
        count = mode & 0x3FFF
        assert not mode & 0x8000 and count > 0
        end = position + 4 + count * 14
        assert end <= len(bar)
        records = []
        for index in range(count):
            start = position + 4 + index * 14
            row = bar[start:start + 14]
            bank, address, width, height = row[9], int.from_bytes(row[10:12], 'little'), row[12], row[13]
            offset, size = address - 0xC000, 2 * width * height
            assert 0 <= bank < 4 and width > 0 and height > 0
            assert 0 <= offset and offset + size <= len(banks[bank])
            data = banks[bank][offset:offset + size]
            assert all(mask & pixels == 0 for mask, pixels in zip(data[::2], data[1::2]))
            sprites.add((bank, offset, width, height))
            records.append(dict(offset=start, bank=bank, address=address, width=width, height=height))
        groups.append(dict(offset=position, end=end, count=count, mode=mode, records=records))
        position = end
    assert position == len(bar)
    starts = {group['offset'] for group in groups}
    assert set(pointers) <= starts and min(pointers) == 72
    # Проверка непересечения всех уникальных изображений, повторные ссылки на тот же кадр допустимы.
    ends = {}
    for bank in range(4):
        current = 0
        for _, offset, width, height in sorted(sprite for sprite in sprites if sprite[0] == bank):
            assert offset == current
            current += 2 * width * height
        ends[bank] = current
    return pointers, groups, sorted(sprites), ends


TYPES = {
    'FFighterPosePointer': (2,),
    'FFighterPoseHeader': (2, 1, 1),
    'FFighterPoseStep': (1,) * 10 + (2, 1, 1),
}


def parse(text):
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    pattern = r'(\w+):\s+(FFighterPose\w+)\s*\{([^}]+)\}'
    raw, labels = bytearray(), {}
    for match in re.finditer(pattern, code):
        assert match[1] not in labels
        labels[match[1]] = len(raw)
        sizes = TYPES[match[2]]
        values = [value.strip() for value in match[3].split(',')]
        assert len(values) == len(sizes)
        for value, size in zip(values, sizes):
            assert re.fullmatch(r'#[0-9A-Fa-f]+', value)
            raw.extend(int(value[1:], 16).to_bytes(size, 'little'))
    return bytes(raw), labels


def render(bar, pointers, groups):
    fields = {
        'FFighterPosePointer': ('FileOffset',),
        'FFighterPoseHeader': ('CountMode', 'Unknown02', 'Unknown03'),
        'FFighterPoseStep': tuple(f'Unknown{index:02X}' for index in range(9)) +
                            ('BankIndex', 'SpriteAddress', 'WidthBytes', 'Height'),
    }
    lines = ['                module FighterPoseData',
             '                ; Документация [таблицы и кадры бойцов](../../../Docs/FighterAssets.md)',
             '                ; Метки являются смещениями BAR, исполнительный адрес этому файлу не назначается.',
             '                assert $ == #0000']
    def row(label, kind, offset):
        lines.append((label + ':').ljust(16) + kind + ' {')
        for index, (field, size) in enumerate(zip(fields[kind], TYPES[kind])):
            value = int.from_bytes(bar[offset:offset + size], 'little')
            text = f'                    #{value:0{size * 2}X}'
            if index + 1 < len(TYPES[kind]):
                text += ','
            lines.append(text.ljust(80) + '; ' + kind + '.' + field + ', исходное значение')
            offset += size
        lines.append('                }')
    for index, pointer in enumerate(pointers):
        row(f'Index{index:02}', 'FFighterPosePointer', 2 * index)
    for group in groups:
        offset = group['offset']
        lines.append(f'                assert $ == #{offset:04X}')
        row(f'Group{offset:04X}', 'FFighterPoseHeader', offset)
        for index, record in enumerate(group['records']):
            row(f'R{offset:04X}_{index:02}', 'FFighterPoseStep', record['offset'])
    lines += ['                assert $ == #0C04', '                endmodule', '']
    text = '\n'.join(lines)
    assert parse(text)[0] == bar
    return text
