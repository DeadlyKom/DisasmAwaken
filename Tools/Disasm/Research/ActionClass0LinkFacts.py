"""Полная цепь класса 0 и общий вход 661A, включая подстановку нуля и отдельный код 26."""
FUNCTIONS={0x660E:('ConfigureClass0Link','Применение подстановки либо выбор новой связи после порога R с общим входом SelectLink')}
LOCAL={0x661A:'SelectLink'}
CONTRACTS={('Action',0x660E):(
    ['HL, DE, BC, AF аргументов не задают, IX указывает доступную FActionRecord',
     'действуют договоры CopyRecordLinkOverride и FindFilteredRecordOr26, выбран банк 0',
     'Stream10 и поля записи доступны для записи, достижим подходящий элемент списка либо маркер',
     'CPU-стек не пересекает запись, код и состояние генератора, восемь байтов ниже внешнего возврата доступны вызовам',
     'дополнительный вход SelectLink принимает Carry как запрет поиска и сохраняет входной StateCode до успешной находки'],
    ['при LinkOverride=1..FE возвращается результат подстановки, LinkedIndex=LinkOverride, StateCode=02',
     'при LinkOverride=0 либо FF читается R после 14 либо 8 M1 соответственно, StateCode=02, LinkedIndex=FF',
     'если прочитанный R меньше текущего Class0RLimit, возвращаются A=этот R и F от CP с Class0RLimit, поиск не выполняется',
     'иначе Stream10 обновлён, HL, E, BC, AF и IY возвращаются от FindFilteredRecordOr26',
     'при NZ результата LinkedIndex=A и StateCode=02, при Z очищенный LinkedIndex=FF сохраняется',
     "D, AF', IX сохраняются, прочие альтернативные регистры сохраняются до вызова генератора, затем содержат его результат",
     'SP=входной SP+2, I, IM, IFF и страница сохраняются, точные регистры и R перечислены по ветвям в документации'],
    ["HL, E, BC, AF, HL', DE', BC', IY, R, LinkedIndex, StateCode, Stream10 и до восьми байтов CPU-стека"],
    ['SelectLink является общим внутренним входом 661A, начинает с LinkedIndex=FF и при Carry возвращает неизменные AF и StateCode',
     'разрешённая подстановка нуля выполняет запись, но возвращает Z и потому не прекращает эту цепочку',
     'код 26 является отдельным результатом дочернего выбора, не объявляется найденным индексом',
     '214528 сценариев исполнили настоящие подстановку, генератор, фильтр, итератор и преобразование индекса без подмены',
     'проверены регистры включая R, все восемь банков RAM, значения стека и кратность записей',
     'полное игровое значение StateCode и LinkOverride, полный домен состояний и списков, распределение, период, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x660E:(['Применение исходной подстановки, только её ненулевой результат с NZ завершает вызов.'],None),
0x6611:([], 'выход, если LinkOverride находится в 1..FE, оставить результат подстановки'),
0x6612:(['Чтение R после 8 M1 для запрета FF либо 14 M1 для разрешённого нуля.'],None),
0x6614:(['Проверка текущего Class0RLimit, исходный порог 70 может быть изменён ApplyParameterSet.'],None),
0x6616:(['Обновление исходного кода StateCode перед общим выбором связи.'],None),
0x661A:(['Сброс LinkedIndex до проверки Carry, дополнительный вход других обработчиков классов.'],None),
0x661E:([], 'выход, если входной Carry установлен, оставить LinkedIndex=FF без поиска'),
0x661F:(['Поиск допустимого индекса либо получение отдельного кода 26 через настоящий поток 10.'],None),
0x6622:([], 'выход, если поиск вернул маркер с Z, оставить LinkedIndex=FF'),
0x6623:(['Обновление LinkedIndex возвращённым A, индекс 0 допускается по NZ так же, как отдельный код 26.'],None),
0x6626:(['Запись исходного кода StateCode после принятого результата выбора.'],None)}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionClass0Const',
    '\n                ; Исходный код записи при выборе связи класса 0\n                module ActionClass0Const\n'+
    'RecordCode'.ljust(16)+'equ #02'.ljust(64)+'; запись в StateCode перед выбором либо после принятого результата\n'
    '                endmodule\n\n'),)


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x660E):return operation
    for value,name in ((0x662B,'CopyRecordLinkOverride'),(0xE6E2,'FindFilteredRecordOr26')):
        operation=operation.replace('#'+format(value,'04X'),'@Action.'+name+'.Entry')
    for value,field in ((0x0A,'StateCode'),(0x0B,'LinkedIndex')):
        operation=operation.replace('(IX+#'+format(value,'02X')+')','(IX + @FActionRecord.'+field+')')
    return operation.replace('#70','@ActionClass9Const.FlagThreshold').replace('#FF','@ActionClass9Const.DefaultIndex').replace('#02','@ActionClass0Const.RecordCode')
