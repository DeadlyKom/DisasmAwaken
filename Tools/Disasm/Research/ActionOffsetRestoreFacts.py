"""Восстановление трёх исходных вычитаемых слов для класса 14, родитель остаётся частично неизвестным."""
FUNCTIONS={0xE685:('RestoreHalvedOffsets','Восстановление трёх исходных вычитаемых слов после временного арифметического деления для класса 14')}
LOCAL={0xE68B:'LoadOriginal0',0xE691:'LoadOriginal1',0xE697:'LoadOriginal2'}
LABELS={('Action',address):name for address,name in LOCAL.items()}
ADDITIONAL_SYMBOLS={'Action.RestoreHalvedOffsets.'+name:address for address,name in LOCAL.items()}
RENAMES={'Action.UnknownE685.Entry':'Action.RestoreHalvedOffsets.Entry'}
CONTINUATIONS={};LOCATION={0xE685:'окно ACTION банка 0'}
CONTRACTS={('Action',0xE685):(
    ['IX - адрес FActionRecord, поле ClassCode доступно для чтения, остальные регистры не задают числовых аргументов',
     'при ClassCode=14 Original0, Original1 и Original2 содержат исходные значения, сохранённые префиксом E55C',
     'Active0, Active1 и Active2 являются изменяемыми операндами LD DE,nn перед вычитаниями из трёх компонент',
     'в окне C000 выбран банк 0, SP содержит внешний возврат, IRQ не вмешивается в изменение общих операндов'],
    ['при ClassCode не равном 14 HL сохранён, DE и BC сохранены, A=ClassCode, F от CP ClassCode,14',
     'при ClassCode=14 Active0..Active2 восстановлены из Original0..Original2, HL=Original2, DE и BC сохранены, AF=1442',
     "HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются, SP после RET равен входному SP+2",
     'R получает четыре M1 для другого класса и одиннадцать M1 для класса 14, старший разряд R сохраняется',
     'CPU-стек не записывается, при другом классе RAM не записывается, при классе 14 выполнены ровно шесть байтовых записей'],
    ['HL только для класса 14, AF, R и шесть байтов Active0..Active2 только для класса 14'],
    ['префикс E55C сохраняет исходные слова в непосредственных операндах LoadOriginal0..2, затем временно заменяет активные слова арифметическими половинами',
     'сдвиг SRA H и RR L округляет отрицательные нечётные значения вниз, восстановление не удваивает половины, а читает сохранённые оригиналы',
     'операнды Original0..2 являются частью исполняемых LD HL,nn, EQU обозначает существующие байты кода, отдельной области данных нет',
     '65792 сценария проверили все слова каждого поля и все коды класса, реальные сохранитель и восстановитель, регистры включая R, все банки RAM и порядок записей',
     'эта проверка сохранителя остановлена по E58E, продолжение с чтением заголовка и изменяемым JR проверено отдельно в ActionRecordScale',
     'все 65536 в третьей степени сочетаний слов, игровые роли класса 14, точные T, аппаратные IRQ и нативный запуск не доказаны'])}
COMMENTS={
    0xE685:(['-----------------------------------------','Проверка класса записи','Чтение полного ClassCode, только код HalvedClass использует временно изменённые вычитаемые слова.'],None),
    0xE68A:([],'выход, если ClassCode отличается от HalvedClass и восстановления слов не требуется'),
    0xE68B:(['-----------------------------------------','Первое исходное слово','Непосредственный операнд Original0 сохранён префиксом E55C до временного арифметического деления.'],None),
    0xE68E:(['Восстановление Active0, вычитаемого перед обновлением Component0.'],None),
    0xE691:(['-----------------------------------------','Второе исходное слово','Чтение сохранённого Original1 из непосредственного операнда.'],None),
    0xE694:(['Восстановление Active1, вычитаемого перед обновлением Component1.'],None),
    0xE697:(['-----------------------------------------','Третье исходное слово','Чтение сохранённого Original2 из непосредственного операнда.'],None),
    0xE69A:(['Восстановление Active2, вычитаемого перед обновлением Component2, HL остаётся равным Original2.'],None)}
FIELDS=(('Active0',0xE5B3,'операнд LD DE,nn перед вычитанием для Component0'),
    ('Active1',0xE5D2,'операнд LD DE,nn перед вычитанием для Component1'),
    ('Active2',0xE5ED,'операнд LD DE,nn перед вычитанием для Component2'),
    ('Original0',0xE68C,'операнд LoadOriginal0, исходное Active0 до арифметического деления'),
    ('Original1',0xE692,'операнд LoadOriginal1, исходное Active1 до арифметического деления'),
    ('Original2',0xE698,'операнд LoadOriginal2, исходное Active2 до арифметического деления'),
    ('SavedCpuSP',0xE605,'операнд восстановления CPU SP, заполняемый в E55C'))


def name_operands(region,address,operation):
    if region!='Action' or address not in (0xE685,0xE55C,0xE5A0,0xE658):return operation
    for name,value,_ in FIELDS:
        operation=operation.replace('(#'+format(value,'04X')+')','(@ActionOffsetState.'+name+')')
    if address in (0xE685,0xE55C):
        operation=operation.replace('(IX+#12)','(IX+FActionRecord.ClassCode)')
        operation=operation.replace('CP #14','CP @ActionOffsetConst.HalvedClass')
    return operation


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']!='Action':continue
        if item['target'] in (0xE68C,0xE692,0xE698):
            assert item['target_instruction']==item['target']-1
            item.update(target_region='Action',target_bank=0,target_slot=17,target_offset=item['target']-0x6000,
                target_source_classified=True,target_path='Source/Action/RestoreHalvedOffsets.asm')
        if 0xE685<=item['writer']<0xE69E:
            assert item['target'] in (0xE5B3,0xE5D2,0xE5ED)
            item.update(writer_bank=0,writer_offset=item['writer']-0x6000,writer_source_classified=True,
                target_region='Action',target_bank=0,target_slot=17,target_offset=item['target']-0x6000,
                target_source_classified=True,target_path='Source/Action/UpdateRecordComponents.asm')
