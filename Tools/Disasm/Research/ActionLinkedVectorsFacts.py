"""E794, чтение двух трёхсловных наборов и фиксированный особый вектор связи 1A."""
FUNCTIONS={0xE794:('LoadLinkedRecordVectors','Подготовка двух трёхсловных наборов из связанной записи либо фиксированных значений связи 1A')}
LOCAL={0xE7C5:'ReadRecord'}
MODIFIED_WRITERS=((0xE7A6,0xAF48,0xAF47,2),(0xE7AA,0xAF56,0xAF55,2),(0xE7AE,0xAF69,0xAF68,2),
                  (0xE7D3,0xAF48,0xAF47,2),(0xE7DC,0xAF56,0xAF55,2),(0xE7E5,0xAF69,0xAF68,2))
CONTRACTS={('Action',0xE794):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступный LinkedIndex текущей FActionRecord',
     'операнд RecordPointer по E796 предварительно установлен PrepareLinkedRecordContext, кроме особой связи 1A, которая игнорирует его',
     'выбранная запись читается по Components и словам 1A, 1C и 1E, первый старший байт этого второго набора задаёт отказ при 80',
     'ACTION банка 0 выбран, Input0..2 банка 2 и Output0..2 банка 0 доступны для записи, IRQ и повторный вход исключены'],
    ['сначала IY получает RecordPointer, при LinkedIndex=1A он заменяется A780 независимо от подготовленного адреса',
     'при связи 1A Input0..2 и Output0 равны нулю, Output1=FFB0, Output2=FFFF, HL=FFB0, DE=FFFF, BC=0, AF=1A18',
     'для остальных связей байт IY.ViewPosition.X.High=80 возвращает AF=8041 без изменения HL, DE, BC и всех шести подготовляемых слов',
     'иначе Input0..2 получают Components выбранного IY, Output0..2 получают ViewPosition.X, Y и Depth',
     'на обычном успехе HL=Output1, DE=Output2, BC=Output0, A равен ViewPosition.X.High и F соответствует AND A, Carry=0',
     "HL', DE', BC', AF', IX, I/IM/IFF и paging сохраняются, SP после RET увеличен на два, CPU-стек не записывается",
     'R добавляет 24 M1 для связи 1A, 11 при отказе и 44 при обычном копировании, бит 7 R сохраняется'],
    ['HL, DE, BC, AF, IY, R, условно Input0..2 и Output0..2, SP внешним RET'],
    ['старший байт Components не проверяется, отказ относится к полному байту ViewPosition.X.High второго трёхсловного набора',
     'прямой вход с исходным нулевым операндом RecordPointer не объявляется допустимым обычным вызовом',
     '394240 сценариев покрыли полные домены шести слов, все адресные индексы и все байты текущей связи',
     'сверены точные регистры, флаги, R, восемь банков и все записи, последующее преобразование здесь не исполняется',
     'общее игровое имя второго набора, полное произведение входов, IRQ, сборка и нативный запуск не доказаны'])}
COMMENTS={0xE794:(['Чтение ранее подготовленного адреса из изменяемого операнда, исходные нулевые байты инструкции сохранены.'],None),
    0xE798:(['Проверка особой связи 1A, её фиксированные наборы не зависят от подготовленной записи.'],None),
    0xE79D:([],'переход, если LinkedIndex отличается от 1A, читать два набора выбранной записи'),
    0xE79F:(['Обнуление трёх входных компонент и первой выходной компоненты для особой связи.'],None),
    0xE7B2:(['Подготовка фиксированных Output1=FFB0 и Output2=FFFF, их физические единицы не назначаются.'],None),
    0xE7BF:(['Выбор специального IY=A780 и возврат Carry=0 через AND A.'],None),
    0xE7C5:(['Проверка старшего байта первого слова второго набора, это ViewPosition.X.High, а не Component0.High.'],None),
    0xE7CA:(['Подготовка Carry=1 только для раннего отказа, обычный путь затем очищает его через AND A.'],None),
    0xE7CB:([],'выход, если ViewPosition.X.High выбранной записи равен 80, сохранить шесть прежних подготовленных слов'),
    0xE7CC:(['Установка Carry=0 и смысловых флагов старшего байта на обычном пути подготовки.'],None),
    0xE7CD:(['Подготовка трёх Components выбранной записи в существующие операнды Input0..2.'],None),
    0xE7E8:(['Подготовка первого слова второго набора, уже прочитанный ViewPosition.X.High становится B.'],None),
    0xE7F0:(['Подготовка второго слова второго набора в HL и Output1.'],None),
    0xE7F9:(['Подготовка третьего слова второго набора в DE и Output2.'],None)}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionLinkedVectorsConst','''
                ; Фиксированный контекст особой связи 1A
                module ActionLinkedVectorsConst
SpecialLink     equ #1A                                                         ; числовой код особой связи, подготовленный адрес игнорируется
FixedMiddle     equ #FFB0                                                       ; исходное второе выходное слово особого контекста
FixedLast       equ #FFFF                                                       ; исходное третье выходное слово особого контекста
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xE794):return operation
    operation=operation.replace('(IX+#0B)','(IX + @FActionRecord.LinkedIndex)')
    for offset in (*range(6),*range(26,32)):
        name=('Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')) if offset<6 else 'Unknown'+format(offset,'02X')
        operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionRecord.'+name+')')
    for index,address in enumerate((0xAF48,0xAF56,0xAF69)):
        operation=operation.replace('(#'+format(address,'04X')+')','(@ActionPatchedVectorState.Input'+str(index)+')')
    for index,address in enumerate((0xD9B6,0xD7C4,0xD7A2)):
        operation=operation.replace('(#'+format(address,'04X')+')','(@ActionPatchedVectorState.Output'+str(index)+')')
    return (operation.replace('CP #1A','CP @ActionLinkedVectorsConst.SpecialLink')
            .replace('LD HL, #FFB0','LD HL, @ActionLinkedVectorsConst.FixedMiddle')
            .replace('LD DE, #FFFF','LD DE, @ActionLinkedVectorsConst.FixedLast')
            .replace('LD IY, #A780','LD IY, @ActionLinkedContextConst.SpecialRecord')
            .replace('CP #80','CP @ActionReuseConst.ReusableHigh'))


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xE7A6,0xE7AA,0xE7AE,0xE7D3,0xE7DC,0xE7E5):
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=item['target']-0x6000,target_bank=2,target_region='Action',
                target_path='Source/Action/ComputePatchedVector.asm',target_source_classified=True,writer_source_classified=True)
