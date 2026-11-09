"""Три добавочные строки оснащения и реально прочитанный маркер 80."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records
from SavedStateLayout import SLOTS


DOCUMENT = 'EquipmentPhysicalTables'
TAG = 'StationPrimaryQuantityTail'
REQUIRED_REPORTS = ('EquipmentRowsVerification',)
BINDINGS = ()
FIELDS = (('Code', 1, 'исходный код количества, 80 завершает общий печататель'),)
ROWS = ('Item1E', 'Item1F', 'Item20', 'EndSlot')
TABLES = ((4, 0x6000, (
    'StationPrimaryQuantityTail', 'Source/Station/Data/PrimaryQuantityTail.asm',
    0x38AC, 0x38B0, 'FEquipmentQuantityCode', FIELDS, ROWS,
)),) + tuple(
    (slot, 0, (name.title() + 'PrimaryQuantityTail',
               f'Source/Resources/{slot:02d}_{name}/PrimaryQuantityTail.asm',
               0x71, 0x75, 'FEquipmentQuantityCode', FIELDS, ROWS))
    for slot, name in SLOTS
)


def validate_sources(sources):
    data = bytes.fromhex('FF 00 FF 80')
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/EquipmentRowsVerification.json').read_bytes())
    for top in range(30, 34):
        assert proof['original_tail_reads'][str(top)] == [
            [0x98AC + index, data[index]] for index in range(top - 30, 4)
        ]
    assert sources[4][0x38AC:0x38B0] == data
    for slot, name in SLOTS:
        assert sources[slot][0x71:0x75] == (bytes(4) if name == 'SAVE5' else data)
    return dict(original_data_rows=33, end_marker_address=0x98AF,
                end_marker_original_value=128, save5_zero_preserved=True)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физический хвост количеств](../../../Docs/EquipmentPhysicalTables.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ''
