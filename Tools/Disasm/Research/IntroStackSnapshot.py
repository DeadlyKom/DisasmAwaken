"""Исходное слово, куда InitializeIntro записывает SP после очистки экрана."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'IntroStationTransition'
TAG = 'IntroStackSnapshot'
REQUIRED_REPORTS = ('IntroStationTransitionVerification',)
USE_SECTORS = (3,)
BINDINGS = ()
FIELDS = (('Stack', 2, 'слово SP после подготовки экрана и до смены банка'),)
TABLES = ((3, 0x6300, (
    'IntroStackSnapshot', 'Source/Intro/Data/StackSnapshot.asm', 0x02B4, 0x02B6,
    'FIntroStackSnapshot', FIELDS, ('Value',),
)),)


def validate_sources(sources):
    assert sources[3][0x02B3:0x02B7] == bytes(4)
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/IntroStationTransitionVerification.json').read_bytes())
    assert (proof['saved_intro_stack_address'], proof['saved_intro_stack_value']) == (0x65B4, 0x5FFF)
    return dict(original_stack_word=0, observed_saved_sp=0x5FFF, consumer_proved=False)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[передача управления станции](../../../Docs/IntroStationTransition.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ('                struct FIntroStackSnapshot\n'
            'Stack           dw #0000                                                        ; сохранённое слово CPU-SP\n'
            '                ends\n'
            '                assert FIntroStackSnapshot == 2\n'
            '                assert FIntroStackSnapshot.Stack == 0\n')
