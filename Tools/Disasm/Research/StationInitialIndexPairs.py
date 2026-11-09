"""Физическая страница индексных пар станции, включая исходно читаемую вторую половину."""
from PreviewSceneTables import parse as parse_records, render as render_records


FIELDS = (
    ('Low', 1, 'младший байт ключа, проверяется первым при поиске'),
    ('High', 1, 'старший байт ключа, FF означает свободную пару'),
)
TABLES = ((4, 0x6000, ('StationInitialItemIndex', 'Source/Station/Data/InitialItemIndex.asm',
                        0x2500, 0x2600, 'FStationItemIndexPair', FIELDS,
                        tuple(f'Pair{index:02X}' for index in range(128)))),)
BINDINGS = (('StationState', 'ItemIndex', 0x8500, 'StationInitialItemIndex.Pair00.Low'),)
REQUIRED_REPORTS = ('StationInitialWorkspaceVerification',)
DOCUMENT = 'StationInitialWorkspace'
TAG = 'StationInitialIndexPairs'


def validate_sources(sources):
    data = sources[4][0x2500:0x2600]
    assert len(data) == 256 and data[:128] != bytes([255]) * 128 and any(data[128:])
    return dict(original_index_bytes=256, index_pairs=128, reset_prefix_bytes=128,
                original_second_half_preserved=True, initialized_values_not_serialized=True)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходная страница индексных пар](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = ['                struct FStationItemIndexPair']
    for field, _, note in FIELDS:
        lines.append((field.ljust(16) + 'db #00').ljust(80) + '; ' + note)
    lines.extend(('                ends', '                assert FStationItemIndexPair == 2',
                  '                assert FStationItemIndexPair.Low == 0',
                  '                assert FStationItemIndexPair.High == 1'))
    return '\n'.join(lines) + '\n'
