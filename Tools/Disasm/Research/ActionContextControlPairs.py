"""Физические пары остатка настроек после активного ввода ACTION."""
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'ActionContextTail'
TAG = 'ActionContextControlPairs'
REQUIRED_REPORTS = ('StationHyperJumpCostTransferVerification',)
BINDINGS = ()
FIELDS = (
    ('ValueOrRow', 1, 'селектор строки клавиатуры или исходный нулевой параметр'),
    ('KeyMask', 1, 'маска клавиши или исходный нулевой параметр'),
)
TABLES = ((17, 0x6000, (
    'ActionContextControlPairs', 'Source/Action/Data/ContextControlPairs.asm', 0x3D82, 0x3DA0,
    'FSettingWord', FIELDS, tuple(f'Option{index:02d}' for index in range(28, 43)),
)),)


def validate_sources(sources):
    first, end = 0x3D82, 0x3DA0
    offset = first - 0x3BBD
    data = sources[17][first:end]
    assert offset == 0x1C5 and data == sources[4][0x383B + offset:0x383B + offset + len(data)]
    assert len(data) == 30 and data[-2:] == bytes(2)
    for row, mask in zip(data[:-2:2], data[1:-2:2]):
        assert (row ^ 255).bit_count() == mask.bit_count() == 1
        assert mask <= 16
    for slot in (11, 12, 13, 14, 16):
        assert sources[slot][offset:offset + len(data)] == data
    return dict(matrix_pairs=14, trailing_zero_pair=True, context_offset=offset,
                original_station_and_five_save_copies_match=True, direct_action_scan_proved=False)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[перенос хвоста станционного контекста](../../../Docs/ActionContextTail.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ''
