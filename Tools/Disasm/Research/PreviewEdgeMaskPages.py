"""Физические страницы C0 и C1 с буквальными масками всех восьми индексов."""
from PolygonFillPhysicalData import PATTERNS
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'PreviewEdgeMaskPages'
TAG = DOCUMENT
REQUIRED_REPORTS = ('PreviewEdgeMaskPagesVerification',)
BINDINGS = ()
FIELDS = tuple(
    (f'{side}{operation}{mode}', 1, note)
    for side in ('Left', 'Right')
    for mode in range(8)
    for operation, note in (
        ('And', 'AND краевого байта' if mode < 5 else 'исходный операнд AND, геометрическая маска не подтверждена'),
        ('Or', 'OR шаблона внутри края' if mode < 5 else 'исходный операнд OR, игровое применение не подтверждено'),
    )
)
TABLES = ((6, 0xC000, (
    'PreviewEdgeMasks', 'Source/D3D/Data/PreviewEdgeMasks.asm', 0, 512,
    'FPreviewEdgeMaskPhase', FIELDS,
    tuple(f'{parity}{phase}' for parity in ('Even', 'Odd') for phase in range(8)),
)),)


def validate_sources(sources):
    data = sources[6]
    assert len(FIELDS) == 32
    for parity in range(2):
        for phase in range(8):
            left = (255 << (8 - phase)) & 255
            right = 255 >> phase
            for mode, (first, delta) in enumerate(PATTERNS):
                pattern = first ^ (delta if parity else 0)
                offset = parity * 256 + phase * 32 + mode * 2
                assert data[offset:offset + 2] == bytes((left, pattern & ~left))
                assert data[offset + 16:offset + 18] == bytes((right, pattern & ~right))
    return dict(mask_pages=2, byte_pairs=256, geometric_pairs=160,
                nongeometric_domain_bytes_preserved=192)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходные маски краёв](../../../Docs/PreviewEdgeMaskPages.md)')
    text = text.replace('                assert $ == #C000',
                        '                assert $ == #C000\n'
                        '                assert HIGH($) == @PreviewPolygonPrepConst.FirstMaskPage')
    return text, labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    name = 'FPreviewEdgeMaskPhase'
    lines = ['                struct ' + name]
    lines.extend((field.ljust(16) + 'db #00').ljust(80) + '; ' + note for field, _, note in FIELDS)
    lines.extend(('                ends', f'                assert {name} == 32'))
    lines.extend(f'                assert {name}.{field} == {offset}'
                 for offset, (field, _, _) in enumerate(FIELDS))
    return '\n'.join(lines) + '\n'
