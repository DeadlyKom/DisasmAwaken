"""Слова и байты между действующими полями исходного PLAYER."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'ActionPanelPhysicalData'
TAG = 'ActionArchivedPlayerPanel'
REQUIRED_REPORTS = ('ActionArchivedPlayerPanelVerification', 'ActionPlayerEffectFieldsVerification')
BINDINGS = ()
WORD_FIELDS = (('Value', 2, 'исходное слово после ACTION, текущий потребитель неизвестен'),)
SUFFIX_FIELDS = (
    ('Byte0', 1, 'исходный ноль после скорости, назначение неизвестно'),
    ('TypeCode', 1, 'полный класс игрока, большой эффект выбирает маску и допуск дочерних записей'),
    ('Byte2', 1, 'исходный ноль перед SHILD, назначение неизвестно'),
)
TABLES = (
    (17, 0x6000, ('ActionPlayerPanelWord', 'Source/Action/Data/PlayerPanelWord.asm',
                  0x478D, 0x478F, 'FArchivedPlayerPanelWord', WORD_FIELDS, ('Initial',))),
    (17, 0x6000, ('ActionPlayerPanelType', 'Source/Action/Data/PlayerPanelType.asm',
                  0x4791, 0x4794, 'FArchivedPlayerPanelType', SUFFIX_FIELDS, ('Initial',))),
)


def validate_sources(sources):
    action = sources[17]
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/ActionArchivedPlayerPanelVerification.json').read_bytes())
    assert proof['passed'] and proof['authored_bytes'] == 21
    assert proof['archived_type_offset'] == 0x12 and proof['current_type'] == 0xA792
    assert bytes.fromhex(proof['panel_hex']) == action[0x4780:0x4795]
    assert proof['ejection_profiles'] == 512 and proof['sole_panel_range_read'] == 0xA790
    assert proof['panel_range_writes'] == 0 and not proof['unclassified_neighbors_read_in_test']
    effect = json.loads((ROOT / 'Tools/Disasm/Reports/ActionPlayerEffectFieldsVerification.json').read_bytes())
    assert effect['passed'] and effect['cases'] == 512 and effect['type_address'] == 0xA792
    assert effect['actual_reader_counts'] == {'EA29': 512, 'EA37': 512, 'EA6F': 512, 'F63E': 256}
    return dict(archived_player_start=0xA880, current_player_start=0xA780,
                byte_exact_authored_extent=21, archived_type_address=0xA892, current_type_address=0xA792,
                current_game_consumers_proved=False, current_type_effect_consumers_proved=True,
                type_effect_readers=[0xEA29, 0xEA6F], conditional_type_rank_reader=0xF63E)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходное объявление PLAYER](../../../Docs/ActionPanelPhysicalData.md#архивное-объявление-player)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for _, _, table in TABLES:
        name, fields = table[4:6]
        lines.append('                struct ' + name)
        offset = 0
        assertions = []
        for field, width, note in fields:
            declaration = 'db #00' if width == 1 else 'dw #0000'
            lines.append((field.ljust(16) + declaration).ljust(80) + '; ' + note)
            assertions.append('                assert ' + name + '.' + field + ' == ' + str(offset))
            offset += width
        lines.extend(('                ends', '                assert ' + name + ' == ' + str(offset), *assertions, ''))
    return '\n'.join(lines)
