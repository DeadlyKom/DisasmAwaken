"""E761, подготовка указателя IY и трёх исходных слов через изменяемые операнды."""
FUNCTIONS={0xE761:('PrepareLinkedRecordContext','Подготовка адреса связанной записи и трёх компонент текущей записи в операндах последующего расчёта')}
LOCAL={0xE76C:'UseIndex',0xE770:'StorePointer'}
STATE_MODULE='ActionLinkedContextState'
STATE_FIELDS=(('RecordPointer',0xE796,'существующий операнд LD IY,nn следующего обработчика по E794'),
              ('Component0',0xF1ED,'существующий операнд LD DE,nn по F1EC для компоненты 0 текущей записи'),
              ('Component1',0xF1F0,'существующий операнд LD BC,nn по F1EF для компоненты 1 текущей записи'),
              ('Component2',0xF1FE,'существующий операнд LD BC,nn по F1FD для альтернативного BC компоненты 2'))
MODIFIED_WRITERS=((0xE770,0xE796,0xE794,2),(0xE77E,0xF1ED,0xF1EC,2),
                  (0xE787,0xF1F0,0xF1EF,2),(0xE790,0xF1FE,0xF1FD,2))
CONTRACTS={('Action',0xE761):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает читаемые LinkedIndex и Components записи',
     'обычный индекс 00..FE адресует A100+64*индекс, особый FF выбирает A780',
     'ACTION банка 0 доступен, четыре изменяемых слова доступны для записи, два дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены'],
    ['HL при недоступности равен выбранному адресу плюс один, иначе равен третьему слову Components текущей записи IX',
     'DE и BC сохраняются',
     'AF содержит A=прочитанный старший байт выбранной Component0 и F от CP с 80, Z означает только недоступность этой записи',
     "HL', DE', BC', AF' сохраняются",
     'IX и IY сохраняются, выбранный адрес записывается в операнд будущего LD IY,nn без изменения живого IY',
     'RecordPointer всегда получает выбранный адрес, даже при Component0.High=80',
     'при доступной цели Component0..2 операндов получают три исходных слова Components текущей записи IX, иначе все три операнда сохраняются',
     'I, IM, IFF и paging сохраняются, SP после внешнего RET равен входному SP+2',
     'R добавляет 11 либо 23 M1 до отказа для FF либо обычного индекса и ещё 16 при подготовке компонент, бит 7 R сохраняется'],
    ['HL, AF, R, RecordPointer, условно три компонентных операнда и два временных байта CPU-стека, SP внешним RET'],
    ['FF в этом договоре не означает индекс 255 и не даёт E0C0, отдельный адрес A780 сохраняется без нового размещения',
     'проверка сравнивает полный старший байт с 80, младший код маркера не читается',
     '197632 сценария покрывают все слова каждой компоненты, все байты связи и все старшие байты A780 для FF и обычного 1A',
     'RecordPointer читает LoadLinkedRecordVectors, Component0..2 читают LoadMotion состояния 02 и LoadMotion состояния 05 с различной ориентацией аргументов',
     'точные регистры, флаги, R, восемь банков и все записи проверены, последующие потребители операндов этим тестом не исполняются',
     'все совместные входы, IRQ, сборка и нативный запуск не проверялись'])}
COMMENTS={0xE761:(['Проверка специального кода связи FF до обычного преобразования индекса.'],None),
    0xE765:([],'переход, если LinkedIndex отличается от FF, восстановить индекс и вычислить его адрес'),
    0xE767:(['Выбор исходного специального адреса A780 вместо обычного адреса индекса 255.'],None),
    0xE76C:(['Восстановление обычного индекса после проверки INC и расчёт адреса без ограничения исходным массивом.'],None),
    0xE770:(['Обновление операнда будущего LD IY,nn выбранным адресом, живой IY здесь сохраняется.'],None),
    0xE773:(['Проверка старшего байта первой компоненты выбранной записи после сохранения указателя.'],None),
    0xE777:([],'выход, если старший байт выбранной Component0 равен 80, сохранить прежние компонентные операнды'),
    0xE778:(['Подготовка исходной компоненты 0 текущей записи в операнд последующего LD DE,nn.'],None),
    0xE781:(['Подготовка исходной компоненты 1 текущей записи в операнд последующего LD BC,nn.'],None),
    0xE78A:(['Подготовка исходной компоненты 2 текущей записи в операнд LD BC,nn после будущего EXX.'],None)}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionLinkedContextConst','''
                ; Исходное специальное значение связи, новая память не выделяется
                module ActionLinkedContextConst
SpecialRecord   equ #A780                                                       ; адрес для LinkedIndex=FF, отдельный от обычного индекса 255
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xE761):return operation
    operation=operation.replace('(IX+#0B)','(IX + @FActionRecord.LinkedIndex)')
    for offset in range(6):
        name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        operation=operation.replace('(IX+#'+format(offset,'02X')+')','(IX + @FActionRecord.'+name+')')
    for name,address,_ in STATE_FIELDS:
        operation=operation.replace('(#'+format(address,'04X')+')','(@ActionLinkedContextState.'+name+')')
    return (operation.replace('CALL #E6A7','CALL @Action.RecordIndexToAddress.Entry')
            .replace('LD HL, #A780','LD HL, @ActionLinkedContextConst.SpecialRecord')
            .replace('CP #80','CP @ActionReuseConst.ReusableHigh'))


def qualify_mutations(records,flow,functions,pieces):
    import json
    from CheckIntro import ROOT
    previous=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xE770,0xE77E,0xE787,0xE790):
            offset=item['target']-0x6000
            owner=next((p for p in pieces if p['offset']<=offset and offset+item['size']<=p['offset']+p['length']),None)
            if owner is None:owner=next(p for p in previous if p['slot']==17 and p['offset']<=offset and offset+item['size']<=p['offset']+p['length'])
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=offset,target_bank=0,target_region='Action',
                target_path=owner['path'],target_source_classified=owner['kind']=='code',writer_source_classified=True)
