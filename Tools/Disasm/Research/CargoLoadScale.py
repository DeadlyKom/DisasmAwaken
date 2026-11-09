"""Тридцать кодов масштаба груза, которые LANG читает из STATIONF."""
from collections import Counter

from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'WeightedLoad'
TAG = 'CargoLoadScale'
REQUIRED_REPORTS = ('WeightedLoadVerification', 'UnclassifiedInitialAccesses')
BINDINGS = ()
TABLES = ((4, 0x6000, ('StationCargoScale', 'Source/Station/Data/CargoLoadScale.asm',
    0x34FA, 0x3518, 'FCargoLoadScale', (('Code', 1, 'код масштаба количества'),),
    tuple(f'Row{index:02X}' for index in range(30)))),)


def validate_sources(sources):
    source = sources[4]
    assert source[0x34F7:0x34FA] == bytes((1, 0, 0))
    assert Counter(source[0x34FA:0x3518]) == {0: 21, 1: 3, 2: 6}
    return dict(unchanged_quantity_codes=21, divide_by_sixteen_codes=3, zero_contribution_codes=6)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[масштабирование груза](../../../Docs/WeightedLoad.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ('                struct FCargoLoadScale\n'
            'Code            db #00                                                          ; код вклада строки груза\n'
            '                ends\n'
            '                assert FCargoLoadScale == 1\n'
            '                assert FCargoLoadScale.Code == 0\n')
