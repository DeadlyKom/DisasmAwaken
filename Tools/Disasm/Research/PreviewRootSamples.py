"""Проверяемая числовая разметка исходной страницы C500 в D3D."""
from math import isqrt

from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'PreviewRootSamples'
TAG = DOCUMENT
REQUIRED_REPORTS = ()
BINDINGS = ()
FIELDS = (('Value', 1, 'исходное значение таблицы, сравнение с корнем описано отдельно'),)
TABLES = ((6, 0xC000, (
    'PreviewRootSamples', 'Source/D3D/Data/PreviewRootSamples.asm', 0x0500, 0x0600,
    'FPreviewRootSample', FIELDS, tuple(f'Index{index:02X}' for index in range(256)),
)),)


def rounded_root(value):
    lower = isqrt(value)
    return lower + (4 * value > (2 * lower + 1) ** 2)


def validate_sources(sources):
    data = sources[6][0x0500:0x0600]
    reference = bytes(0 if index == 0 else 16 * max(2, rounded_root(index))
                      if index < 64 else rounded_root(index * 256)
                      for index in range(256))
    differences = [(index, original, expected)
                   for index, (original, expected) in enumerate(zip(data, reference))
                   if original != expected]
    assert differences == [(0xAF, 0xD3, 0xD4), (0xF4, 0xF0, 0xFA)]
    return dict(values=256, matched_approximate_root_values=254,
                preserved_differences=differences, consumer_proved=False)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходная таблица приближений корня](../../../Docs/PreviewRootSamples.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ('                struct FPreviewRootSample\n'
            'Value           db #00                                                          ; исходное байтовое приближение\n'
            '                ends\n'
            '                assert FPreviewRootSample == 1\n'
            '                assert FPreviewRootSample.Value == 0\n')
