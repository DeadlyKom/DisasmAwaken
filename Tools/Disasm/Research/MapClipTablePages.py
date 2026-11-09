"""Физические строки младших и старших адресов диспетчера KARTA."""
import json
import re

from CheckIntro import ROOT
from ClipTargetLowPhysicalData import FIELDS as LOW_FIELDS
from PolygonFillPhysicalData import HIGH_FIELDS
from PreviewSceneTables import parse as parse_records, render as render_records


ORIGIN = 0xC000
SLOT = 7
TAG = DOCUMENT = 'MapClipTablePages'
REQUIRED_REPORTS = ('MapClipDispatch', 'MapClipTablePagesVerification', 'ClipSegmentVerification')
BINDINGS = ()


def table(name, start, structure, fields, rows):
    return (SLOT, ORIGIN, ('MapClip' + name, 'Source/Map/Data/Clip' + name + '.asm',
                           start, start + len(fields) * len(rows), structure, fields, rows))


def rows(first, stop):
    return tuple(f'FirstSides{index:X}' for index in range(first, stop))


TABLES = (
    table('LowRow0', 0x1E00, 'FClipTargetLowHead', LOW_FIELDS[:11], rows(0, 1)),
    table('LowRow1', 0x1E10, 'FClipTargetLowHead', LOW_FIELDS[:11], rows(1, 2)),
    table('LowRow2', 0x1E20, 'FClipTargetLowHead', LOW_FIELDS[:11], rows(2, 3)),
    table('LowTail3', 0x1E3E, 'FMapClipLowTail3', LOW_FIELDS[14:], ('First3Tail',)),
    table('LowRows45', 0x1E40, 'FClipTargetLowRow', LOW_FIELDS, rows(4, 6)),
    table('LowRow6', 0x1E60, 'FClipTargetLowHead', LOW_FIELDS[:11], rows(6, 7)),
    table('LowTail7', 0x1E7B, 'FClipTargetLowTail', LOW_FIELDS[11:], ('First7Tail',)),
    table('LowRows8F', 0x1E80, 'FClipTargetLowRow', LOW_FIELDS, rows(8, 16)),
    table('HighRows09', 0x1F00, 'FClipTargetHighRow', HIGH_FIELDS, rows(0, 10)),
    table('HighRowA', 0x1FA0, 'FMapClipHighHead', HIGH_FIELDS[:11], rows(10, 11)),
)


def target_names():
    reports = ROOT / 'Tools/Disasm/Reports'
    pairs = json.loads((reports / 'MapClipDispatch.json').read_bytes())['pairs']
    symbols = json.loads((reports / 'Symbols.json').read_bytes())
    names = {}
    for row in pairs:
        candidates = [name for name, value in symbols.items()
                      if name.startswith('Map.') and value == row['target']]
        assert len(candidates) == 1, row
        names[row['index']] = candidates[0], row['target']
    return names


def validate_sources(sources):
    source = sources[SLOT]
    targets = target_names()
    assert len(targets) == 81
    for index, (_, address) in targets.items():
        assert source[0x1E00 + index] + 256 * source[0x1F00 + index] == address
    cells = 0
    for _, _, entry in TABLES:
        page = entry[2] & 0xFF00
        for offset in range(entry[2], entry[3]):
            index = offset & 255
            if index in targets:
                cells += 1
            else:
                assert page in (0x1E00, 0x1F00) and source[offset] == 0, hex(offset)
    assert cells == 162
    return dict(valid_pairs=len(targets), named_address_bytes=cells, dispatch_pages=2)


def render(source, origin, entry):
    text, labels = render_records(source, entry, origin)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)')
    offset = entry[2]
    operator = 'LOW' if offset < 0x1F00 else 'HIGH'
    kind = 'младший' if operator == 'LOW' else 'старший'
    targets = target_names()
    lines = []
    for line in text.splitlines():
        match = re.fullmatch(r'( +)#[0-9A-F]{2}(,?) +; (\w+), .*', line)
        if match:
            index = offset & 255
            if index in targets:
                code = f'{match[1]}{operator}(@{targets[index][0]}){match[2]}'
                meaning = f'{kind} байт адреса цели для индекса {index:02X}'
            else:
                code = line.partition(';')[0].rstrip()
                meaning = f'исходный байт индекса {index:02X} вне девяти допустимых кодов стороны'
            assert len(code) < 80
            line = f'{code:<80}; {match[3]}, {meaning}'
            offset += 1
        lines.append(line)
    assert offset == entry[3]
    return '\n'.join(lines) + '\n', labels


def parse(text, origin, entry):
    symbols = {name: address for name, address in target_names().values()}

    def resolve(match):
        value = symbols[match[2]]
        shift = 8 if match[1] == 'HIGH' else 0
        return f'#{(value >> shift) & 255:02X}'

    decoded = re.sub(r'(LOW|HIGH)\(@([A-Za-z_][A-Za-z0-9_.]*)\)', resolve, text)
    return parse_records(decoded, entry, origin)


def structures():
    lines = []
    for name, fields in (('FMapClipLowTail3', LOW_FIELDS[14:]), ('FMapClipHighHead', HIGH_FIELDS[:11])):
        lines.append('                struct ' + name)
        for field, _, meaning in fields:
            lines.append(f'{field:<16}{"db #00":<64}; {meaning}')
        lines.extend(('                ends', f'                assert {name} == {len(fields)}'))
        for index, (field, _, _) in enumerate(fields):
            lines.append(f'                assert {name}.{field} == {index}')
        lines.append('')
    return '\n'.join(lines)
