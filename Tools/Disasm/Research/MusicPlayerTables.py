"""Физические данные проигрывателя, включая наложение нулевой строки громкости на AY."""
import re
from PreviewSceneTables import parse as parse_records, render as render_records

STRUCTURES = {
    'FMusicDataPointer': (('Address', 2, 'абсолютный указатель после InitializeModule, исходный ноль сохраняется'),),
    'FMusicAyRegisters': (
        ('ToneA', 2, 'буфер периода тона A для регистров AY 0 и 1'),
        ('ToneB', 2, 'буфер периода тона B для регистров AY 2 и 3'),
        ('ToneC', 2, 'буфер периода тона C для регистров AY 4 и 5'),
        ('Noise', 1, 'базовый буфер шума, при выводе добавляется текущий вклад IXH'),
        ('Mixer', 1, 'буфер микшера, перед выводом заменяется IXL'),
        ('LevelA', 1, 'сформированный уровень и маска огибающей A'),
        ('LevelB', 1, 'сформированный уровень и маска огибающей B'),
        ('LevelC', 1, 'сформированный уровень и маска огибающей C'),
        ('EnvelopePeriod', 2, 'буфер периода общей огибающей'),
        ('EnvelopeShape', 1, 'нулевой байт пропускает OUT регистра 13, ненулевой выводится и очищается')),
    'FMusicRowCounter': (('Remaining', 1, 'байтовая длительность строки, DEC исходного нуля даёт FF'),),
    'FMusicVolumeRow': tuple(('Level' + format(i, '02X'), 1,
                             'готовый уровень для входной амплитуды ' + str(i)) for i in range(16)),
    'FMusicNotePeriod': (('Period', 2, 'исходное little endian слово периода по индексу ноты'),)}


def table(module, name, start, end, structure, names):
    return module, 'Source/Music/Data/' + name + '.asm', start - 0xDB00, end - 0xDB00, structure, STRUCTURES[structure], names


TABLES = (
    table('MusicDataPointers', 'DataPointers', 0xDBA0, 0xDC00, 'FMusicDataPointer',
          tuple('Sample' + format(i, '02X') for i in range(32)) + tuple('Ornament' + format(i, '02X') for i in range(16))),
    table('MusicAyBuffer', 'AyBuffer', 0xDC00, 0xDC0E, 'FMusicAyRegisters', ('Registers',)),
    table('MusicRowCounters', 'RowCountersBC', 0xDC0E, 0xDC10, 'FMusicRowCounter', ('ChannelB', 'ChannelC')),
    table('MusicVolumes', 'Volumes', 0xDC10, 0xDD00, 'FMusicVolumeRow', tuple('Volume' + format(i, '02X') for i in range(1, 16))),
    table('MusicPeriods', 'Periods', 0xDD00, 0xDDC0, 'FMusicNotePeriod', tuple('Note' + format(i, '02X') for i in range(96))),
    table('MusicRowCounters', 'RowCounterA', 0xDE1E, 0xDE1F, 'FMusicRowCounter', ('ChannelA',)))


def render(source, description):
    text, symbols = render_records(source, description, 0xDB00)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические данные проигрывателя](../../../Docs/MusicPlayerData.md)')
    return text, symbols


def parse(text, description):
    module, path, start, end, structure, fields, names = description
    lines = [line.partition(';')[0].strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    assert lines.pop(0) == 'module ' + module
    assert lines.pop(0) == 'assert $ == #' + format(0xDB00 + start, '04X')
    for name in names:
        assert lines.pop(0) == (name + ':').ljust(16) + structure + ' {'
        for index, (field, width, _) in enumerate(fields):
            expression = r'#[0-9A-F]{' + str(width * 2) + '}' + (',' if index + 1 < len(fields) else '')
            assert re.fullmatch(expression, lines.pop(0))
        assert lines.pop(0) == '}'
    assert lines == ['assert $ == #' + format(0xDB00 + end, '04X'), 'endmodule']
    return parse_records(text, description, 0xDB00)
