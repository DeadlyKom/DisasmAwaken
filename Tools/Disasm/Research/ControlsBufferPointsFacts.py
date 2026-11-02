"""Генератор координат и 35 физических записей Y,X в банке 1."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FUNCTIONS = {
    0xCA8D: ('NextBufferRandom', 'Получение байта из изменяемого 16-битового состояния генератора'),
    0xCAB3: ('InitializeBufferPoints', 'Подготовка 35 координат Y,X с исходным ограничением диапазонов'),
    0xCAE3: ('XorBufferPoints', 'Наложение 35 точек на линейный буфер через четыре таблицы адресации')}
CONTINUATIONS = {}
LOCAL = {0xCAB6: 'NextPoint', 0xCABF: 'LimitX', 0xCAC5: 'GenerateY',
         0xCAD1: 'LimitY', 0xCAD7: 'StorePoint', 0xCAE6: 'DrawPoint'}
LABELS = {('Controls', a): name for a, name in LOCAL.items()}
RENAMES = {'Controls.Unknown'+format(a, '04X')+'.Entry': 'Controls.'+name+'.Entry' for a, (name, _) in FUNCTIONS.items()}
for a, name in LOCAL.items():
    owner = 0xCAB3 if a < 0xCAE3 else 0xCAE3
    RENAMES['Controls.Unknown'+format(owner,'04X')+'.Point'+format(a,'04X')] = 'Controls.'+FUNCTIONS[owner][0]+'.'+name
CONTRACTS = {
 ('Controls',0xCA8D): (
    ['HL, DE, BC сохраняются, AF входных аргументов не задаёт, Seed читается из операнда CA8F',
     "HL', DE', BC' используются как рабочие, AF', IX и IY входных аргументов не задают",
     'банк 1 выбран, изменяемый операнд Seed доступен для записи, на CPU-стеке внешний возврат'],
    ['HL, DE, BC сохранены, A равен младшему байту нового Seed',
     't=(7*Seed-4) AND FFFF, u=(HIGH(t)-LOW(t)) AND FFFF, v=(t-u) AND FFFF, новый Seed=(v-1) AND FFFF',
     'F соответствует 16-битовому SBC t-u до последующего DEC HL, а не проверке возвращаемого A',
     "HL' равен новому Seed, DE'=u, BC'=LOW(t), AF', IX и IY сохраняются",
     'I, IM и IFF сохраняются, портов и дополнительных PUSH нет, SP=входной SP+2'],
    ["AF, HL', DE', BC', два байта Seed, R"],
    ['оба OR A сбрасывают Carry перед SBC, входные флаги на результат не влияют',
     'для исходного Seed=0 до цикла выполняются 59 переходов, затем период равен 387, это не полный 16-битовый цикл']),
 ('Controls',0xCAB3): (
    ['HL, DE, BC, AF входных аргументов не задают, начальное состояние берётся из Seed',
     'банк 1 выбран, Seed и все 70 байтов ControlsBufferPoints доступны для записи',
     'на CPU-стеке внешний возврат, ещё два байта используются настоящими CALL генератора'],
    ['HL=адрес после Point22, DE и BC сохранены, A=46, F=42',
     'подготовлены 35 записей Y,X, Y=1..94, X=1..253, распределение неравномерное',
     'Seed обновлён 70 раз, перед каждой парой сначала генерируется X, затем Y, физически сохраняются Y, затем X',
     "HL', DE', BC' содержат последний результат генератора, A' содержит Y последней точки, F' только Carry последнего ограничения Y",
     'IX и IY, I, IM и IFF сохраняются, SP=входной SP+2'],
    ["HL, AF, HL', DE', BC', AF', 70 байтов точек, Seed, два байта CPU-стека, R"],
    ['X=0 заменяется на 2, X>=254 уменьшается на 2',
     'Y сначала ограничивается AND 7F, нуль заменяется на 2, значения >=95 уменьшаются на 64',
     'изменённые границы или равномерный генератор исправили бы оригинальный алгоритм, здесь они не вводятся']),
 ('Controls',0xCAE3): (
    ['HL, DE, BC, AF входных аргументов не задают, 35 записей читаются в порядке Y,X',
     'банк 1 выбран, четыре страницы таблиц 9400..97FF подготовлены ActionBoot.BuildBitmapTables',
     'для проверенного договора Y=0..95, X=0..255, линейный буфер 8000..8BFF доступен для записи',
     'на CPU-стеке внешний возврат, данные точек и таблицы не перекрываются с целями XOR'],
    ['HL=9700+X последней точки, DE её адрес назначения, BC=адрес после Point22, A=46, F=42',
     'каждая запись накладывает один пиксель через XOR, выполнены ровно 35 записей, совпадения не удаляются',
     "HL', DE', BC', AF', IX и IY сохраняются, I, IM и IFF сохраняются, SP=входной SP+2"],
    ['HL, DE, BC, AF, 35 записей байтов буфера с возможными совпадениями адресов, R'],
    ['старший байт адреса берётся из 9400+Y, младший складывается по модулю 256 из 9500+Y и 9600+X',
     'маска пикселя читается из 9700+X, проверок координат внутри потребителя нет',
     'исходные 35 нулевых записей не пропускаются, при готовых таблицах они 35 раз меняют один пиксель 8000'])}
COMMENTS = {
 0xCA8D: (['сохранение основных пар через EXX перед вычислением нового состояния генератора'],None),
 0xCA8E: (['чтение существующего изменяемого 16-битового состояния Seed'],None),
 0xCA95: (['вычисление промежуточного 4*Seed-4 по модулю 65536'],None),
 0xCA9B: (['вычисление t=7*Seed-4 добавлением удвоенного и исходного Seed'],None),
 0xCAA0: (['вычисление разности старшего и младшего байтов промежуточного t'],None),
 0xCAAA: (['вычитание полученной разности из t без входного заёма'],None),
 0xCAAC: (['вычисление нового Seed уменьшением промежуточного v на один без изменения флагов SBC'],None),
 0xCAB3: (['выбор первой физической записи Y,X в таблице из 35 точек'],None),
 0xCAB6: (['создание горизонтальной координаты настоящим вызовом генератора'],None),
 0xCAB9: (['проверка нулевой горизонтальной координаты перед заменой на 2'],None),
 0xCABB: ([], 'переход, если X не равен нулю, пропустить замену нулевой координаты'),
 0xCABF: (['проверка верхней границы горизонтальной координаты'],None),
 0xCAC1: ([], 'переход, если X меньше 254, оставить полученное значение'),
 0xCAC5: (['сохранение X в альтернативном A на время второго вызова генератора'],None),
 0xCAC9: (['ограничение вертикальной координаты семью битами'],None),
 0xCACB: (['проверка нулевой вертикальной координаты перед заменой на 2'],None),
 0xCACD: ([], 'переход, если Y не равен нулю, пропустить замену нулевой координаты'),
 0xCAD1: (['проверка верхней границы вертикальной координаты'],None),
 0xCAD3: ([], 'переход, если Y меньше 95, оставить полученное значение'),
 0xCAD7: (['сохранение Y первым физическим байтом записи, затем восстановление и сохранение X'],None),
 0xCADD: (['проверка заполнения всех 70 байтов таблицы'],None),
 0xCADF: ([], 'переход, если младший байт указателя меньше 46, подготовить следующую точку'),
 0xCAE3: (['выбор начала таблицы из 35 пар Y,X'],None),
 0xCAE6: (['получение старшего и младшего байтов адреса строки по координате Y'],None),
 0xCAF0: (['вычисление младшего байта назначения через таблицу X DIV 8 без переноса в D'],None),
 0xCAF6: (['наложение битовой маски точки на существующий байт буфера'],None),
 0xCAFA: (['проверка обработки всех 35 записей координат'],None),
 0xCAFC: ([], 'переход, если обработаны не все 70 байтов координат, наложить следующую точку')}
FIELDS = (('Y',1,'вертикальная координата, первый физический байт'), ('X',1,'горизонтальная координата, второй физический байт'))
TABLE = ('ControlsBufferPoints','Source/Controls/Data/BufferPoints.asm',0x500,0x546,
         'FBufferPoint',FIELDS,tuple('Point'+format(i,'02X') for i in range(35)))


def render(source):
    text, symbols = render_records(source,TABLE,0xC000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[генератор и XOR-точки](../../../Docs/ControlsBufferPoints.md)'), symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0) == 'module ControlsBufferPoints' and clean.pop(0) == 'assert $ == #C500'
    for name in TABLE[6]:
        assert clean.pop(0) == (name+':').ljust(16)+'FBufferPoint {'
        assert re.fullmatch(r'#[0-9A-F]{2},',clean.pop(0)) and re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #C546','endmodule']
    return parse_records(text,TABLE,0xC000)


def name_operands(region,function_address,operation):
    if region == 'Controls' and function_address == 0xCB00:
        operation = operation.replace('#C500','@ControlsBufferPoints.Point00')
    if region == 'Controls' and function_address in FUNCTIONS:
        operation = operation.replace('(#CA8F)','(@ControlsBufferPointsState.Seed)')
        operation = operation.replace('#C500','@ControlsBufferPoints.Point00')
        for before,after in (('CP #46','CP @BufferPointConst.ByteCount'),
            ('CP #01','CP @BufferPointConst.MinCoordinate'),
            ('ADD A, #02','ADD A, @BufferPointConst.EdgeStep'),
            ('SUB #02','SUB @BufferPointConst.EdgeStep'),
            ('CP #FE','CP @BufferPointConst.XUpperLimit'),
            ('AND #7F','AND @BufferPointConst.YIndexMask'),
            ('CP #5F','CP @BufferPointConst.YUpperLimit'),
            ('SUB #40','SUB @BufferPointConst.YFold'),
            ('LD H, #94','LD H, @BufferPointConst.LineHighPage')):
            operation = operation.replace(before,after)
    if region == 'Action' and function_address == 0xA85E:
        operation = operation.replace('CALL #CAE3','CALL @Controls.XorBufferPoints.Entry')
    if region == 'Action' and function_address == 0x6CD6:
        operation = operation.replace('CALL #CAB3','CALL @Controls.InitializeBufferPoints.Entry')
    return operation
