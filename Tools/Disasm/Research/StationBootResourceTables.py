"""Шесть исходных ключей и таблица шестнадцати размеров фонов станции."""
import re

from ActionBootFileKeys import parse as parse_keys, render as render_keys
from PreviewSceneTables import parse as parse_records, render as render_records


KEYS = (('Karta', 'KARTA   '), ('Muz1', 'MUZ1    '), ('StationScreens', 'stscr   '),
        ('Help', 'HELP    '), ('D3D', 'D3D     '), ('Lang', 'LANG    '))
SIZES = bytes((13, 11, 11, 12, 8, 14, 19, 15, 15, 13, 19, 12, 16, 20, 21, 20))
KEY_FIELDS = (('Name', 8, 'исходное имя с пробелами'), ('Extension', 1, 'тип C без терминатора'))
SIZE_FIELDS = (('Sectors', 1, 'число физических секторов этого фона'),)
TABLES = (
    (4, 0x3CE7, ('StationBootFileKeys', 'Source/StationBoot/Data/FileKeys.asm',
                 0x343, 0x379, 'FTrDosFileKey', KEY_FIELDS, tuple(label for label, _ in KEYS))),
    (4, 0x3CE7, ('StationBackdropSizes', 'Source/StationBoot/Data/BackdropSizes.asm',
                 0x379, 0x389, 'FBackdropSectorCount', SIZE_FIELDS, tuple(f'Backdrop{index:02d}' for index in range(16)))),
)
BINDINGS = ()
REQUIRED_REPORTS = ('StationBootstrapVerification', 'StationBackdropSelectionVerification', 'UnpackResourceVerification')
DOCUMENT = 'StationBootResourceTables'
TAG = DOCUMENT


def name_operands(region, address, operation):
    if (region, address) != ('StationBoot', 0x4070):
        return operation
    for index, (label, _) in enumerate(KEYS):
        operation = operation.replace(f'LD HL, #{0x402A + index * 9:04X}',
                                      'LD HL, @StationBootFileKeys.' + label + '.Name')
    operation=operation.replace('LD A, #09','LD A, @FTrDosFileKey').replace('(#5D06)','(@TrDosState.SearchKeyLength)').replace('LD DE, #5CDD','LD DE, @TrDosState.Descriptor')
    return operation.replace('LD BC, #0009', 'LD BC, @FTrDosFileKey').replace(
        'LD DE, #4060', 'LD DE, @StationBackdropSizes.Backdrop00.Sectors')


def validate_sources(sources):
    station = sources[4]
    assert station[0x343:0x379] == b''.join(name.encode('ascii') + b'C' for _, name in KEYS)
    assert station[0x379:0x389] == SIZES and sum(SIZES) == 239
    for address, word in zip((0x402A, 0x4033, 0x403C, 0x4045, 0x404E, 0x4057),
                             (b'KARTA   C', b'MUZ1    C', b'stscr   C', b'HELP    C', b'D3D     C', b'LANG    C')):
        offset = address - 0x3CE7
        assert station[offset:offset + 9] == word
        assert bytes((0x21, address & 255, address >> 8)) in station[0x389:0x5CE]
    assert bytes.fromhex('11 60 40 19') in station[0x389:0x5CE]
    return dict(file_keys=6, backdrop_sizes=16, backdrop_sector_sum=239, physical_bytes=70,
                station_relocation_preserved=True)


def render(source, origin, table):
    if table[4] == 'FTrDosFileKey':
        text, _ = render_keys(source[table[2]:table[3]], keys=KEYS, module=table[0],
                              origin=origin + table[2], document=DOCUMENT, title='ключи загрузчика станции')
        raw, labels = parse(text, origin, table)
        assert raw == source[table[2]:table[3]]
        return text, labels
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[секторные размеры фонов](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    if table[4] != 'FTrDosFileKey':
        return parse_records(text, table, origin)
    raw = parse_keys(text)
    assert tuple(re.findall(r'^(\w+): +FTrDosFileKey', text, re.M)) == table[-1]
    labels = {}
    for index, (label, name) in enumerate(KEYS):
        address = origin + table[2] + index * 9
        key = table[0] + '.' + label
        assert raw[index * 9:index * 9 + 9] == name.encode('ascii') + b'C'
        labels.update({key: address, key + '.Name': address, key + '.Extension': address + 8})
    return raw, labels


def structures():
    return (
        '                struct FBackdropSectorCount\n' +
        'Sectors         db #00'.ljust(80) + '; число физических секторов упакованного фона\n'
        '                ends\n'
        '                assert FBackdropSectorCount == 1\n'
        '                assert FBackdropSectorCount.Sectors == 0\n'
    )
