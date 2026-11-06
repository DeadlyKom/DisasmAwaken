"""Сброс трёх существующих изменяемых баз, исходный LD HL,0000 остаётся инструкцией."""
FUNCTIONS={0xF572:('ResetRecordUpdateBases','Обнуление трёх базовых слов в изменяемых операндах обновления компонент')}
LOCAL={};LABELS={};CONTINUATIONS={}
RENAMES={'Action.UnknownF572.Entry':'Action.ResetRecordUpdateBases.Entry'}
LOCATION={0xF572:'окно ACTION банка 0'}
CONTRACTS={('Action',0xF572):(
    ['HL не задаёт аргумента, DE, BC, AF и альтернативные регистры задают сохраняемый контекст',
     'непосредственное слово LD HL,nn по F573 равно исходному нулю, изменённый операнд этим договором не покрыт',
     'Base0, Base1 и Base2 являются доступными для записи операндами UpdateRecordComponents в банке 0',
     'CPU-стек содержит внешний возврат, не пересекающийся с изменяемыми байтами, IRQ не вмешивается'],
    ["HL=0000, DE, BC, AF, HL', DE', BC', AF', IX и IY сохраняются",
     'Base0, Base1 и Base2 равны нулю, остальные байты RAM не изменены',
     'R получает пять M1 с сохранением бита 7, I/IM/IFF и paging сохраняются, SP после RET равен входному SP+2',
     'CPU-стек и порты не записываются, шесть записей RAM выполнены в порядке Base0, Base1, Base2, младший байт перед старшим в модели'],
    ['HL, R и шесть байтов существующих базовых операндов'],
    ['загруженный в HL ноль является непосредственным операндом инструкции, входной HL на результат не влияет',
     'обнуление Base не меняет Active, Original или WarningLatch, выражение последующего обновления получает Component-Active',
     '65536 сценариев проверили все входные AF и все прежние слова каждого Base как три перестановки полного домена',
     'проверены регистры включая R, все физические банки RAM и кратность записей, полное произведение трёх прежних слов не перебиралось',
     'порядок байтов в модели не доказывает аппаратные шинные циклы, писатель исходного операнда F573 не установлен',
     'IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0xF572:(['-----------------------------------------','Сброс общей базы обновления','Подготовка нулевого базового слова из исходного непосредственного операнда, входной HL не используется.'],None),
    0xF575:(['Обнуление Base0 внутри LoadBase0 перед вычитанием Active0.'],None),
    0xF578:(['Обнуление Base1 внутри LoadBase1 перед вычитанием Active1.'],None),
    0xF57B:(['Обнуление Base2 внутри LoadBase2 перед вычитанием Active2, остальные операнды не меняются.'],None)}


def name_operands(region,address,operation):
    if (region,address)!=('Action',0xF572):return operation
    for value,name in ((0xE5B0,'Base0'),(0xE5CF,'Base1'),(0xE5EA,'Base2')):
        operation=operation.replace('(#'+format(value,'04X')+')','(@ActionRecordUpdateState.'+name+')')
    return operation


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']=='Action' and 0xF572<=item['writer']<0xF57F:
            assert item['target'] in (0xE5B0,0xE5CF,0xE5EA)
            item.update(writer_bank=0,writer_offset=item['writer']-0x6000,writer_source_classified=True,
                target_region='Action',target_bank=0,target_slot=17,target_offset=item['target']-0x6000,
                target_source_classified=True,target_path='Source/Action/UpdateRecordComponents.asm')
