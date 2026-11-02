"""XOR-маркер и восемь исходных наборов масок банка 1."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FUNCTIONS = {0xF094: ('XorBufferMarker', 'Наложение одиннадцати байтов маркера на линейный буфер через XOR')}
CONTINUATIONS = {}
LABELS = {}
LOCAL = {}
RENAMES = {'Controls.UnknownF094.Entry': 'Controls.XorBufferMarker.Entry'}
CONTRACTS = {('Controls', 0xF094): (
    ['HL, DE, BC, AF входных аргументов не задают, Position читается словом из 9B19',
     'банк 1 выбран, таблица MarkerPhaseMasks доступна, целевые байты буфера доступны для записи',
     'на CPU-стеке внешний возврат, модель не включает вмешательство ISR'],
    ['HL указывает последний изменённый байт нижнего штриха, DE=Phase00+4*(Position AND 7), BC=0020',
     'A содержит последний записанный байт, F соответствует последнему XOR',
     "HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+2",
     'выполнены ровно 11 записей XOR, четыре верхние, три центральные и четыре нижние'],
    ['HL, DE, BC, AF, одиннадцать байтов буфера, R'],
    ['база получается как 8000+(Position DIV 8), фаза маски определяется тремя младшими битами Position',
     'горизонтальные INC L и DEC L не переносятся в H, пограничная адресация оригинала сохранена',
     'при неизменных Position, масках и фоне повторное наложение восстанавливает исходный буфер',
     'для произвольного 16-битового Position цель может перекрыть сам Position, второй вызов тогда использует уже изменённое значение'])}
COMMENTS = {
 0xF094: (['чтение сохраняемого положения маркера из общей RAM'], None),
 0xF098: (['вычисление линейного байтового смещения Position DIV 8 тремя сдвигами через Carry'], None),
 0xF0A0: (['добавление старшего бита базы 8000 при третьем сдвиге'], None),
 0xF0A6: (['вычисление номера четырёхбайтового набора масок по Position AND 7'], None),
 0xF0AE: (['выбор физического экземпляра масок без копирования таблицы'], None),
 0xF0B3: (['подготовка шага 32 байта между растровыми строками линейного буфера'], None),
 0xF0B6: (['выбор байта верхнего штриха, INC L намеренно не переносит переполнение в H'], None),
 0xF0B7: (['наложение верхних четырёх растровых строк одной вертикальной маской'], None),
 0xF0C6: (['пропуск одной растровой строки перед центральной тройкой масок'], None),
 0xF0C8: (['выбор левого байта центрального ряда без переноса из L в H'], None),
 0xF0C9: (['выбор маски CentralLeft и наложение левого байта центрального ряда'], None),
 0xF0CD: (['выбор маски CentralMiddle для среднего байта того же ряда'], None),
 0xF0D2: (['выбор маски CentralRight для правого байта того же ряда'], None),
 0xF0D7: (['возврат к вертикальной маске и среднему байту перед нижним штрихом'], None),
 0xF0DB: (['пропуск одной растровой строки после центра перед нижними четырьмя строками'], None)}
FIELDS = (('Vertical', 1, 'маска четырёх верхних и четырёх нижних строк'),
          ('CentralLeft', 1, 'маска левого байта центрального ряда'),
          ('CentralMiddle', 1, 'маска среднего байта центрального ряда'),
          ('CentralRight', 1, 'маска правого байта центрального ряда'))
TABLE = ('MarkerPhaseMasks', 'Source/Controls/Data/MarkerPhaseMasks.asm', 0x160F, 0x162F,
         'FMarkerPhaseMasks', FIELDS, tuple('Phase'+format(i, '02X') for i in range(8)))


def render(source):
    text, symbols = render_records(source, TABLE, 0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[XOR-маркер буфера](../../../Docs/ControlsMarker.md)'), symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0) == 'module MarkerPhaseMasks' and clean.pop(0) == 'assert $ == #F0ED'
    for name in TABLE[6]:
        assert clean.pop(0) == (name+':').ljust(16)+'FMarkerPhaseMasks {'
        for index in range(4):
            assert re.fullmatch(r'#[0-9A-F]{2}' + (',' if index < 3 else ''), clean.pop(0))
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #F10D', 'endmodule']
    return parse_records(text, TABLE, 0xDADE)


def name_operands(region, function_address, operation):
    if region == 'Action' and function_address == 0xA85E:
        operation = operation.replace('CALL #F094', 'CALL @Controls.XorBufferMarker.Entry')
    if region == 'Controls' and function_address in FUNCTIONS:
        operation = operation.replace('(#9B19)', '(@ControlsMarkerState.Position)')
        operation = operation.replace('#F0ED', '@MarkerPhaseMasks.Phase00')
    return operation
