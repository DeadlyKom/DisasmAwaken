"""Исходный физический экземпляр двухсловного состояния в ACTION."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = (('First', 2, 'исходное первое слово генератора, обновляется прежним Second'),
          ('Second', 2, 'исходное второе слово генератора, обновляется смешивающей рекурсией'))
TABLE = ('ActionWordRandomState', 'Source/Action/Data/WordRandomState.asm', 0x3B15, 0x3B19,
         'FWordRandomState', FIELDS, ('Value',))


def validate(source):
    data = source[0x3B15:0x3B19]
    assert len(data)==4
    return data


def render(source):
    text, symbols = render_records(source, TABLE, 0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[двухсловный генератор](../../../Docs/ControlsWordRandom.md)'), symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean[:3] == ['module ActionWordRandomState', 'assert $ == #9B15',
                        'Value:'.ljust(16)+'FWordRandomState {']
    assert re.fullmatch(r'#[0-9A-F]{4},', clean[3])
    assert re.fullmatch(r'#[0-9A-F]{4}', clean[4])
    assert clean[5:] == ['}', 'assert $ == #9B19', 'endmodule']
    return parse_records(text, TABLE, 0x6000)
