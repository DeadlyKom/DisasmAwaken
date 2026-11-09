"""Два исходных шаблона по шесть широких векторов, выбираемые входом DD87."""
from ActionWideVectorsData import NAMES, parse as parse_vectors, render as render_vectors


FIELDS = tuple((f'Component{index}', 4, 'исходная знаковая 32-битная компонента') for index in range(3))
TABLES = (
    (23, 0xDADE, ('ControlsVectorsNoDiablo', 'Source/Controls/Data/VectorsNoDiablo.asm',
                  0x04B3, 0x04FB, 'FActionWideVector', FIELDS, NAMES)),
    (23, 0xDADE, ('ControlsVectorsWithDiablo', 'Source/Controls/Data/VectorsWithDiablo.asm',
                  0x04FB, 0x0543, 'FActionWideVector', FIELDS, NAMES)),
)
BINDINGS = ()
REQUIRED_REPORTS = ('ControlsResetFlightContextVerification',)
DOCUMENT = 'ControlsResetFlightContext'
TAG = 'ControlsResetVectorTemplates'


def validate_sources(sources):
    control = sources[23]
    assert control[0x02C1:0x02D1] == bytes.fromhex('21 91 df 28 03 21 d9 df 11 27 9b 01 48 00 ed b0')
    assert control[0x04B3:0x04FB] != control[0x04FB:0x0543]
    return dict(templates=2, wide_records_per_template=6, bytes_per_template=72,
                existing_structure_reused=True, all_game_callers_proved=False)


def render(source, origin, table):
    return render_vectors(source, module=table[0], origin=origin + table[2], start=table[2], document=DOCUMENT)


def parse(text, origin, table):
    return parse_vectors(text, module=table[0], origin=origin + table[2])


def structures():
    return ''
