"""Поля 9844..98AB по независимым действующим читателям, без назначения неизвестных игровых кодов."""
from SavedStateLayout import ROOT, SLOTS, parse, structures

TABLES = (
    (0x9844, 'SelectedMapKey', 'FSignatureInput', ('Entry',)),
    (0x9849, 'PlayerSaveHeader', 'FPlayerSaveHeader', ('Entry',)),
    (0x9852, 'OwnedCargoRows', 'FOwnedCargoRow', tuple(f'Row{index:02}' for index in range(30))),
    (0x988E, 'EquipmentQuantityCodes', 'FEquipmentQuantityCode', tuple(f'Item{index:02}' for index in range(30))),
)
FIELDS = {
    'FSignatureInput': (('FirstWord', 2), ('SecondWord', 2), ('Variant', 1)),
    'FPlayerSaveHeader': (('ShipIndex', 1), ('SkimmerIndex', 1), ('StatusCode', 1), ('RankScore', 2),
                          ('Money', 2), ('UsedTonnage', 1), ('Capacity', 1)),
    'FOwnedCargoRow': (('QuantityAndMark', 1), ('Price', 1)),
    'FEquipmentQuantityCode': (('Code', 1),),
}


def render(data, table, prefix='', file_origin=0x6000, data_origin=0x6000):
    address, module, kind, labels = table
    lines = ['                module ' + prefix + module,
             '                ; Документация [сохраняемые поля игрока](../../../Docs/PlayerSavedFields.md)',
             f'                assert $ == #{address - data_origin + file_origin:04X}']
    offset = address - data_origin
    for label in labels:
        lines.append((label + ':').ljust(16) + kind + ' {')
        for index, (field, size) in enumerate(FIELDS[kind]):
            value = int.from_bytes(data[offset:offset + size], 'little')
            line = f'                    #{value:0{size * 2}X}' + (',' if index < len(FIELDS[kind]) - 1 else '')
            lines.append(line.ljust(80) + '; ' + kind + '.' + field + ', исходное значение')
            offset += size
        lines.append('                }')
    lines.extend((f'                assert $ == #{offset + file_origin:04X}', '                endmodule', ''))
    return '\n'.join(lines)


def verify_all():
    import json
    reports = ROOT / 'Tools/Disasm/Reports'
    sm = json.loads((reports / 'SourceMap.json').read_text(encoding='utf-8'))
    types = structures()
    for kind, fields in FIELDS.items():
        assert types[kind] == list(fields)
    count = 0
    for slot, name, origin in ((4, 'STATIONF', 0x6000), *((slot, name, 0x983B) for slot, name in SLOTS)):
        extension = 'C' if slot == 4 else 's'
        data = (ROOT / f'Tools/Disasm/Extracted/Active/{slot:02}_{name}.{extension}.bin').read_bytes()
        for table in TABLES:
            address, module, kind, labels = table
            path = ('Source/Station/Data/' if slot == 4 else f'Source/Resources/{slot}_{name}/') + module + '.asm'
            actual, _ = parse((ROOT / path).read_text(encoding='utf-8'), types)
            size = sum(size for _, size in FIELDS[kind]) * len(labels)
            assert actual == data[address - origin:address - origin + size]
            span = next(item for item in sm if item['path'] == path)
            assert (span['slot'], span['offset'], span['length']) == (slot, address - origin, size)
            count += len(actual)
    assert count == 728
    return count
