"""Резервный выбор первой активной записи полного класса 08 и сохранение её индекса."""
FUNCTIONS={0xE97C:('SelectClass8ForRecord','Поиск первой записи класса 8 и сохранение её индекса в текущей записи')}
LOCAL={}
CONTRACTS={('Action',0xE97C):(
    ['HL сохраняется, DE задаёт только сохраняемый E, BC и AF числовых аргументов не задают',
     'IX указывает текущую FActionRecord с доступным Unknown20, IY исходного указателя не задаёт',
     'действуют договоры FindRecordByCode и RecordIYToIndex, от A100 достижима цель либо маркер',
     'исходный ACTION банка 0 доступен, шесть дополнительных байтов CPU-стека не пересекают запись, IRQ не вмешиваются'],
    ['HL и E сохраняются, D=08, BC=0040, IY указывает первую активную запись класса 08 либо маркер',
     'при отсутствии цели AF=8042, Unknown20 сохраняется',
     'при успехе A равен байтовому индексу IY по RecordIYToIndex, F соответствует RecordAddressToIndex и Unknown20 получает A',
     'HL\', DE\', BC\', AF\', IX, I/IM/IFF и paging сохраняются, SP равен входному SP, PC=F0F8',
     'R получает стоимость FindRecordByCode плюс 3 M1 при отсутствии цели либо плюс 23 M1 при успехе',
     'кроме Unknown20 на успешном пути записываются только временные слова CPU-стека, внешний возврат сохраняется'],
    ['BC, D, AF, IY, R, Unknown20 при успехе и до шести временных байтов CPU-стека'],
    ['класс сравнивается целиком с 08, остальные коды 00..FF не приравниваются ему по маске',
     'флаги после успешного преобразования не означают успех поиска, они унаследованы от сдвигов RecordAddressToIndex',
     'физические исходные слоты дают индексы 0..24, глобальный лимит произвольного игрового списка этим не устанавливается',
     '6656 сценариев проверили все 256 кодов проверяемой записи и 26 вариантов позиции, точные регистры, флаги, R и все записи',
     'проверка заканчивается перед первой инструкцией PrepareObjectOffsetTransform по F0F8, его дальнейшие эффекты описаны отдельно',
     'все возможные списки, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись'])}
COMMENTS={
    0xE97C:(['Поиск первой активной записи с полным кодом класса 08.'],None),
    0xE981:([], 'переход, если поиск достиг маркера без класса 8, сохранить прежний индекс и продолжить общий хвост'),
    0xE984:(['Преобразование адреса найденной записи IY в её байтовый индекс без чтения координат.'],None),
    0xE987:(['Сохранение найденного индекса в поле Unknown20 текущей записи IX.'],None),
    0xE98A:(['Передача общего внешнего CPU-стека подготовителю смещений текущей записи.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionSelectClass8Const','''
                ; Полный числовой код резервного выбора записи
                module ActionSelectClass8Const
ClassCode       equ #08                                                         ; искомый полный код класса, сравнение не использует битовую маску
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xE97C):return operation
    return (operation.replace('LD D, #08','LD D, @ActionSelectClass8Const.ClassCode')
            .replace('CALL #E98D','CALL @Action.FindRecordByCode.Entry')
            .replace('CALL #E6BE','CALL @Action.RecordIYToIndex.Entry')
            .replace('(IX+#20)','(IX + @FActionRecord.Unknown20)')
            .replace('JP Z, #F0F8','JP Z, @Action.PrepareObjectOffsetTransform.Entry')
            .replace('JP #F0F8','JP @Action.PrepareObjectOffsetTransform.Entry'))
