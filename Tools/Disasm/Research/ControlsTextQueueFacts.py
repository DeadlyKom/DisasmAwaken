"""Производитель очереди чисел и строк банка 1, код типа не является битовым флагом."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FUNCTIONS = {
    0xEC56: ('QueueNumber', 'Подготовка числовой записи типа 2 из A и продолжение в производителе текстовой очереди'),
    0xEC59: ('QueueTextItem', 'Ограниченный поиск свободной записи очереди и сохранение числа либо указателя строки')}
LABELS = {('Controls', 0xEC61): 'FindFree', ('Controls', 0xEC6C): 'RestoreRegs',
          ('Controls', 0xEC70): 'WrapSearch', ('Controls', 0xEC77): 'StoreItem'}
RENAMES = {'Controls.UnknownEC56.Entry': 'Controls.QueueNumber.Entry',
           'Controls.UnknownEC59.Entry': 'Controls.QueueTextItem.Entry',
           **{'Controls.UnknownEC59.Point'+format(a, '04X'): 'Controls.QueueTextItem.'+name for (_, a), name in LABELS.items()}}
FIELDS = (('HighKind', 1, '00 маркер конца, 01 свободно, 02 число, 03..FF старший байт указателя строки'),
          ('LowValue', 1, 'числовое значение при HighKind=02, младший байт адреса при HighKind>=03'))
TABLE = ('ControlsTextQueue', 'Source/Controls/Data/TextQueue.asm', 0x11A2, 0x11C4,
         'FTextQueueItem', FIELDS, tuple('Slot'+format(i, '02X') for i in range(16))+('End',))
CONTRACTS = {}
for address in FUNCTIONS:
    number = address == 0xEC56
    CONTRACTS['Controls', address] = (
        ['HL сохраняется, '+('DE входных аргументов не задаёт, формируется слово 0200 OR A' if number else 'DE задаёт запись, D записывается первым байтом HighKind, E вторым LowValue'),
         'BC сохраняется, AF '+('задаёт A исходного байтового числа и сохраняется целиком' if number else 'сохраняется целиком и аргументов не задаёт'),
         'выбран банк 1 с CONTROL0 и CONTROL, код и таблица доступны для записи, WriteCursor указывает Slot00..Slot0F либо End',
         'HighKind=00 является концом кольца, HighKind=01 свободной записью, поиск ограничен 16 чтениями',
         'на CPU-стеке находится внешний возврат, требуется ещё шесть байтов для сохранённых HL, BC и AF',
         'локальный договор не включает вмешательство ISR, процедура сама DI не выполняет'],
        ['HL сохранён, '+('DE=0200 OR входной A' if number else 'DE сохранён')+', BC и AF сохранены',
         'при найденном HighKind=01 записаны D и E, WriteCursor получает адрес после двух байтов записи',
         'маркер HighKind=00 переносит поиск на Slot00 и тоже расходует одну из 16 попыток',
         'если за 16 чтений свободная запись не найдена, очередь и WriteCursor не меняются, признака отказа в регистрах нет',
         'рамка сохранённых регистров остаётся в RAM стека, внешний RET задаёт SP=входной SP+2',
         "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, портов ввода и вывода нет"],
        [('DE при QueueNumber, ' if number else '')+'шесть байтов рамки CPU-стека, найденная запись и WriteCursor при успехе, R'],
        ['запись хранит D перед E, указатель строки физически big endian, это два байтовых поля, не DW little endian',
         'тип 02 потребитель передаёт десятичному выводу байта, это число с минимальной шириной два знака, не код символа',
         'D=00 и D=01 не проверяются производителем, такая запись при дальнейшем чтении означает маркер либо свободное место',
         'при старте на End и единственном свободном Slot0F поиск возвращает отказ, исходная особенность не исправлена',
         'QueueNumber не делает CALL к QueueTextItem, исполнение продолжается физически, см. TextQueueProducer.md'])
COMMENTS = {
    0xEC56: (['перенос байтового числа A в полезное значение записи'], None),
    0xEC57: (['выбор числового типа, потребитель печатает E десятичными цифрами'], None),
    0xEC59: (['сохранение регистров, поиск не возвращает в них признак отказа'], None),
    0xEC5C: (['чтение изменяемого курсора записи, он может указывать на конечный маркер'], None),
    0xEC5F: (['ограничение поиска шестнадцатью чтениями, обход маркера тоже входит в лимит'], None),
    0xEC61: (['проверка HighKind текущего физического элемента на свободное значение 01'], None),
    0xEC63: ([], 'переход, если исходный HighKind равен 01, сохранить запись в свободное место'),
    0xEC65: (['восстановление HighKind после DEC для проверки конечного значения 00'], None),
    0xEC66: ([], 'переход, если исходный HighKind равен 00, перейти к началу кольца'),
    0xEC68: (['выбор следующей двухбайтовой записи после занятого элемента'], None),
    0xEC6C: (['восстановление входных AF, BC и HL, в том числе при молчаливом отказе'], None),
    0xEC70: (['возврат к Slot00 после маркера, DJNZ расходует отдельную попытку'], None),
    0xEC77: (['запись HighKind из D, затем LowValue из E, без проверки зарезервированных значений D'], None),
    0xEC7B: (['сохранение адреса после записанного элемента в операнде WriteCursor'], None)}


def name_operands(region, address, operation):
    if region == 'Controls' and address in FUNCTIONS:
        operation = operation.replace('(#EC5D)', '(@ControlsTextQueueState.WriteCursor)')
        operation = operation.replace('#EC80', '@ControlsTextQueue.Slot00')
        if address == 0xEC56:
            operation = operation.replace('LD D, #02', 'LD D, @TextQueueConst.Number')
        else:
            operation = operation.replace('LD B, #10', 'LD B, @TextQueueConst.Capacity')
    return operation


def render(source):
    text, symbols = render_records(source, TABLE, 0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[производитель текстовой очереди](../../../Docs/TextQueueProducer.md)'), symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0) == 'module ControlsTextQueue' and clean.pop(0) == 'assert $ == #EC80'
    for name in TABLE[6]:
        assert clean.pop(0) == (name+':').ljust(16)+'FTextQueueItem {'
        assert re.fullmatch(r'#[0-9A-F]{2},', clean.pop(0)) and re.fullmatch(r'#[0-9A-F]{2}', clean.pop(0))
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #ECA2', 'endmodule']
    return parse_records(text, TABLE, 0xDADE)
