"""Заполнение линейных 96 строк по 32 байта с подменой SP, без изменения AF."""
FUNCTIONS={0xD10A:('ClearWorkBuffer','Заполнение линейного буфера 8000..8BFF байтами FF через временный SP с восстановлением CPU-стека')}
LOCAL={0xD116:'WriteBlock',0xD128:'RestoreStack'}
LABELS={('Action',a):n for a,n in LOCAL.items()}
RENAMES={'Action.ClearWorkBuffer.PointD116':'Action.ClearWorkBuffer.WriteBlock'}
ADDITIONAL_SYMBOLS={'Action.ClearWorkBuffer.RestoreStack':0xD128}
LOCATION={0xD10A:'банковое окно ACTION банка 0'}
CONTINUATIONS={}
CONTRACTS={('Action',0xD10A):(
    ['HL, DE, BC и AF числовых аргументов не задают, входные C и AF должны сохраниться',
     "HL', DE', BC', AF', IX и IY содержат сохраняемый контекст",
     'буфер 8000..8BFF доступен на запись, ACTION банка 0 и операнд SavedSP доступны для самомодификации',
     'SP указывает на внешний адрес возврата, стек не пересекается с очищаемым буфером и кодом процедуры',
     'аппаратные прерывания не вмешиваются во временный SP, инструкция DI здесь не выполняется'],
    ['HL=FFFF, B=0, DE, C и AF сохраняются',
     "HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются",
     'ровно 3072 байта 8000..8BFF получают FF, каждый записывается один раз',
     'SavedSP по D129 содержит входной SP, SP восстановлен и после RET равен входному SP+2',
     'R увеличен на 1639 M1 с сохранением старшего разряда, время без ожиданий памяти и IRQ равно 18206 тактам',
     'CPU-стек не записывается, кроме использования буфера как временной области PUSH, порты не используются'],
    ['HL, BC, только B, R, SavedSP и 3072 байта линейного буфера'],
    ['каждый из 96 проходов выполняет 16 PUSH HL, то есть ровно 32 байта нисходящей записи',
     'все инструкции сохраняют AF, DJNZ не меняет флаги, исходное заполнение равно FF',
     'область 8C00 и выше не заполняется, таблицы масок начинаются сразу после буфера',
     '1536 сценариев проверяют все значения F, A и C, шесть исходных SP, регистры, R, RAM и кратность записей',
     'тайминг относится к данному фрагменту от Entry до RET без дополнительных ожиданий, IRQ и нативный запуск не выполнялись'])}
COMMENTS={0xD10A:(['-----------------------------------------','CPU-стек и граница буфера','Сохранение обычного SP перед заменой его на исключённый верхний адрес буфера.'],None),
    0xD111:(['Выбор исходного слова FF/FF и 96 блоков по 32 байта.'],None),
    0xD116:(['-----------------------------------------','Нисходящая запись одного блока','Шестнадцать PUSH заполняют одну линейную строку, флаги и AF остаются входными.'],None),
    0xD128:(['-----------------------------------------','Восстановление CPU-возврата','Возврат исходного SP из изменяемого операнда перед RET.'],None)}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xD10A:
        for old,new in (('(#D129)','(@ActionWorkBufferState.SavedSP)'),('LD SP, #8C00','LD SP, @ActionWorkBufferConst.BufferEnd'),
            ('LD HL, #FFFF','LD HL, @ActionWorkBufferConst.FillWord'),('LD B, #60','LD B, @ActionWorkBufferConst.BlockCount')):
            operation=operation.replace(old,new)
    return operation


def qualify_mutations(records,regions,functions):
    item=next(m for m in records if m['region']=='Action' and m['writer']==0xD10A)
    assert item['target']==0xD129 and item['size']==2
    item.update(writer_bank=0,target_bank=0,target_region='Action',target_slot=17,target_offset=0x7129,
                writer_source_classified=True,target_source_classified=True,target_path='Source/Action/ClearWorkBuffer.asm')
