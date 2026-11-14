"""Исходные байты вокруг снимка стека в выборке текстуры."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'IntroStationTransition'
TAG = 'IntroStackSampleBytes'
REQUIRED_REPORTS = ('IntroStationTransitionVerification', 'BootBankFileReadsVerification')
USE_SECTORS = (3,)
BINDINGS = ()
FIELDS = (('Value', 1, 'исходный байт рядом со снимком SP, копируется при выборке текстуры'),)
TABLES = (
    (3, 0x6300, ('IntroStackSampleBefore', 'Source/Intro/Data/StackSampleBefore.asm',
                  0x02B3, 0x02B4, 'FIntroStackSampleByte', FIELDS, ('Initial',))),
    (3, 0x6300, ('IntroStackSampleAfter', 'Source/Intro/Data/StackSampleAfter.asm',
                  0x02B6, 0x02B7, 'FIntroStackSampleByte', FIELDS, ('Initial',))),
)


def validate_sources(sources):
    reports = ROOT / 'Tools/Disasm/Reports'
    intro = json.loads((reports / 'IntroStationTransitionVerification.json').read_bytes())
    boot = json.loads((reports / 'BootBankFileReadsVerification.json').read_bytes())
    assert sources[3][0x02B3:0x02B7] == bytes(4)
    assert intro['passed'] and intro['total_cases'] == 4
    assert intro['saved_stack_texture_copy'] == dict(bank=1, source=0x65B3, destination=0xDC73,
                                                    data='00ff5f00', read_pc=0x6D9F,
                                                    overwrite_pc=0x6A1B, reads_before_overwrite=0)
    assert boot['passed'] and len(boot['intro_transitions']) == 2
    for profile in boot['intro_transitions']:
        assert profile['intro_stack_storage'] == dict(address=0x65B3, after_load='00000000',
                                                     after_intro='00ff5f00', after_station_load='98cd33c3')
    return dict(texture_copy_profiles=4, trdos_load_profiles=2, scratch_copy=0xDC73,
                scratch_byte_count=4, original_purpose_of_adjacent_bytes_proved=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[копия снимка SP в текстуре](../../../Docs/IntroStationTransition.md#снимок-стека-в-выборке-текстуры)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    return ('                struct FIntroStackSampleByte\n'
            + ('Value'.ljust(16) + 'db #00').ljust(80) + '; ' + FIELDS[0][2] + '\n'
            '                ends\n'
            '                assert FIntroStackSampleByte == 1\n'
            '                assert FIntroStackSampleByte.Value == 0\n')
