"""Полный алгоритм цели класса 9, сравнение R влияет на флаги, но не выбирает запись."""
FUNCTIONS={0x65C6:('ConfigureClass9Link','Запись кода 0D с сохранением LinkedIndex либо кода 01 со сбросом LinkedIndex в FF')}
LOCAL={0x65D1:'ResetLink'}
CONTRACTS={('Action',0x65C6):(
    ['HL, DE, BC, AF аргументов не задают, IX указывает доступную FActionRecord',
     'SavedStateCode читается, StateCode и LinkedIndex доступны для записи, CPU-стек содержит внешний возврат',
     'R является входным состоянием аппаратного счётчика M1, прерывания не вмешиваются'],
    ['при SavedStateCode=0D StateCode=0D, LinkedIndex сохранён, A=0D, F=4A',
     'иначе StateCode=01, LinkedIndex=FF, A=R после шести M1, F соответствует сравнению A с 70',
     "HL, DE, BC, HL', DE', BC', AF', IX, IY сохраняются",
     'R получает 7 M1 для кода 0D либо 12 для остальных, его бит 7 сохраняется',
     'SP=входной SP+2, I, IM, IFF и страница сохраняются, CPU-стек не записывается'],
    ['AF, R, StateCode, при SavedStateCode не равном 0D также LinkedIndex'],
    ['цель Class09 исходной таблицы, полный игровой смысл SavedStateCode и StateCode пока не доказан',
     'CP 70 после LD A,R не управляет ветвью, он меняет только выходные флаги, обе записи выполняются при любом R',
     '72192 сценария покрыли все пары SavedStateCode и R и все 26 исследовательских позиций существующих записей',
     'проверены регистры включая R, восемь банков RAM и точный порядок байтовых записей',
     'IRQ, точные T, сборка и нативное исполнение не доказаны'])}
COMMENTS={
0x65C6:(['Чтение управляющего байта, специальным является только полное значение 0D.'],None),
0x65C9:(['Проверка ветви, сохраняющей LinkedIndex без чтения R.'],None),
0x65CB:([], 'переход, если SavedStateCode отличается от 0D, записать код 01 и LinkedIndex=FF'),
0x65CD:(['Обновление StateCode специальным исходным кодом, LinkedIndex остаётся неизменным.'],None),
0x65D1:(['Чтение R после шести M1 от входа, его старший бит сохраняет входное значение.'],None),
0x65D3:(['Формирование выходных флагов, проверка порога не управляет дальнейшими записями.'],None),
0x65D5:(['Обновление StateCode и LinkedIndex для всех неспециальных значений SavedStateCode.'],None)}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionClass9Const',
    '\n                ; Числовые коды исходной цели Class09\n                module ActionClass9Const\n'+
    'SpecialCode'.ljust(16)+'equ #0D'.ljust(64)+'; значение SavedStateCode, сохраняющее LinkedIndex\n'+
    'DefaultCode'.ljust(16)+'equ #01'.ljust(64)+'; запись в StateCode в остальных случаях\n'+
    'DefaultIndex'.ljust(16)+'equ #FF'.ljust(64)+'; исходная запись в LinkedIndex для обычной ветви\n'+
    'FlagThreshold'.ljust(16)+'equ #70'.ljust(64)+'; порог сравнения R, влияющий только на выходные флаги\n'
    '                endmodule\n\n'),)


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x65C6):return operation
    for value,field in ((0x16,'SavedStateCode'),(0x0A,'StateCode'),(0x0B,'LinkedIndex')):
        operation=operation.replace('(IX+#'+format(value,'02X')+')','(IX + @FActionRecord.'+field+')')
    for value,name in (('#0D','SpecialCode'),('#01','DefaultCode'),('#FF','DefaultIndex'),('#70','FlagThreshold')):
        operation=operation.replace(value,'@ActionClass9Const.'+name)
    return operation
