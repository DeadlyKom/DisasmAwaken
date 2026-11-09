"""Два исходных байта ACTION под временным SP заливки."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'ActionPolygonFill'
TAG = 'ActionPolygonScratch'
REQUIRED_REPORTS = ('ActionPolygonEdgesVerification', 'ActionPolygonFillBitmapVerification')
BINDINGS = ()
FIELDS = (
    ('Row', 1, 'младший байт PUSH HL, текущая строка из D'),
    ('MaskPage', 1, 'старший байт PUSH HL, текущая страница масок из H'),
)
TABLES = ((17, 0x6000, (
    'ActionPolygonScratch', 'Source/Action/Data/PolygonScratch.asm', 0x9FDE, 0x9FE0,
    'FPolygonEdgeScratch', FIELDS, ('Value',),
)),)


def validate_sources(sources):
    reports = ROOT / 'Tools/Disasm/Reports'
    edges = json.loads((reports / 'ActionPolygonEdgesVerification.json').read_bytes())
    fill = json.loads((reports / 'ActionPolygonFillBitmapVerification.json').read_bytes())
    assert edges['passed'] and edges['temporary_stack_bytes'] == 2
    assert fill['passed'] and fill['all_physical_ram_bytes_proved'] and fill['write_multiplicity_proved']
    assert sources[17][0x9FDE:0x9FE0] == bytes(2)
    return dict(temporary_stack_top=0xFFE0, scratch_address=0xFFDE, initial_zero_bytes=2)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[временный кадр заливки](../../../Docs/ActionPolygonFill.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    lines = ['                struct FPolygonEdgeScratch']
    lines.extend((field.ljust(16) + 'db #00').ljust(80) + '; ' + note for field, _, note in FIELDS)
    lines.extend(('                ends', '                assert FPolygonEdgeScratch == 2',
                  '                assert FPolygonEdgeScratch.Row == 0',
                  '                assert FPolygonEdgeScratch.MaskPage == 1'))
    return '\n'.join(lines) + '\n'
