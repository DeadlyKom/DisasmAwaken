"""Три насыщаемых модуля с исходным восстановлением знака по биту 23."""
FUNCTIONS={0x7F0E:('ClampPatchedVectorWords','Сведение трёх изменяемых 32-битных значений к словам с исходным насыщением и знаком по биту 23')}
LOCAL={0x7F21:'SaveFirst',0x7F35:'SaveSecond',0x7F49:'CollectWords',0x7F5B:'SignSecond',0x7F69:'SignThird'}
LABELS={('Action',a):name for a,name in LOCAL.items()}
RENAMES={'Action.Unknown7F0E.Entry':'Action.ClampPatchedVectorWords.Entry'}
RENAMES.update({'Action.Unknown7F0E.Point'+format(a,'04X'):'Action.ClampPatchedVectorWords.'+name for a,name in LOCAL.items()})
CONTINUATIONS={}
CONTRACTS={('Action',0x7F0E):(
    ['HL, DE, BC, AF входных аргументов не задают',
     'FirstHigh/Low, SecondHigh/Low, ThirdHigh/Low содержат три 32-битных значения в операндах LD DE/HL',
     'операнды стабильны на протяжении вызова, перенесённый код и AbsSigned32 доступны',
     'CPU-стек допускает шесть дополнительных байтов и содержит внешний возврат, IRQ не вмешиваются'],
    ['HL, DE, BC содержат результаты для первой, второй, третьей компонент соответственно',
     'для каждого signed32 вычислен модуль по модулю 2^32, модуль от 8000 заменён на 7F00',
     'затем слово отрицается по модулю 2^16 при исходном бите 23, это не проверка знакового бита 31',
     'AF определяется третьей компонентой, точные формулы приведены в документации, Carry всегда сброшен',
     "HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются",
     'кроме временных шести байтов CPU-стека RAM не записывается, R имеет точную формулу в документации'],
    ['HL, DE, BC, AF, R, шесть временных байтов CPU-стека'],
    ['порог 8000 и подстановка 7F00 сохранены буквально, минимальный signed32 также попадает под насыщение',
     'знак читается по младшему байту исходного старшего слова, необычный выбор бита 23 не исправлен',
     'нулевые литералы LD DE/HL являются исходными изменяемыми операндами, их писатели находятся в StepRecordTowardWideVector',
     '666296 сценариев проверили реальные три вызова AbsSigned32, все младшие слова при старших 0/FFFF и все старшие слова',
     'проверены регистры включая R, кратность записей, остаток CPU-стека и все восемь банков RAM',
     'полное произведение трёх dword, аппаратный порядок байтов записи, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x7F0E:(['Чтение первого значения из изменяемых операндов FirstHigh и FirstLow.'],None),
0x7F22:(['Чтение второго значения из изменяемых операндов SecondHigh и SecondLow.'],None),
0x7F36:(['Чтение третьего значения из изменяемых операндов ThirdHigh и ThirdLow.'],None),
0x7F49:(['Преобразование временных модулей в окончательный порядок HL, DE, BC.'],None),
0x7F4D:(['Проверка бита 23 исходной первой компоненты по младшему байту FirstHigh.'],None),
0x7F51:([], 'переход, если исходный бит 23 первой компоненты нулевой, сохранить положительное слово'),
0x7F54:(['Расчёт отрицательного первого слова по модулю 65536.'],None),
0x7F5B:(['Проверка бита 23 исходной второй компоненты по младшему байту SecondHigh.'],None),
0x7F5F:([], 'переход, если исходный бит 23 второй компоненты нулевой, сохранить положительное слово'),
0x7F62:(['Расчёт отрицательного второго слова по модулю 65536.'],None),
0x7F69:(['Проверка бита 23 исходной третьей компоненты по младшему байту ThirdHigh.'],None),
0x7F6D:([], 'выход, если исходный бит 23 третьей компоненты нулевой, сохранить положительное слово'),
0x7F6E:(['Расчёт отрицательного третьего слова, конечные флаги остаются после последнего CPL.'],None)}
for call,check,jump,load,push in ((0x7F14,0x7F17,0x7F1C,0x7F1E,0x7F21),(0x7F28,0x7F2B,0x7F30,0x7F32,0x7F35),
    (0x7F3C,0x7F3F,0x7F44,0x7F46,None)):
    COMMENTS[call]=(['Расчёт модуля полного DE:HL с исходной особенностью минимального signed32.'],None)
    COMMENTS[check]=(['Проверка модуля на превышение 7FFF по верхнему слову и биту 15 нижнего.'],None)
    COMMENTS[jump]=([], 'переход, если модуль не больше 7FFF, сохранить младшее слово без насыщения')
    COMMENTS[load]=(['Подстановка исходного насыщения 7F00, более высокое значение 7FFF не используется.'],None)
    if push:COMMENTS[push]=(['Сохранение модуля на CPU-стеке до завершения следующих компонент.'],None)
CONST_BLOCK=('\n                ; Исходное насыщение трёх изменяемых координат\n                module ActionClampWordsConst\n'+
    'HighMask'.ljust(16)+'equ #80'.ljust(64)+'; бит 15 модуля исключает сохранение нижнего слова\n'+
    'Saturation'.ljust(16)+'equ #7F00'.ljust(64)+'; исходная подстановка при модуле не меньше 8000\n'+
    '                endmodule\n\n')
STRUCT_BLOCK=('\n                ; Динамическая рамка в третьем AbsSigned32, память не выделяется\n'+
    '                struct FClampVectorFrame\n'+
    'ReturnAbs'.ljust(16)+'dw #7F3F'.ljust(64)+'; возврат третьего вызова AbsSigned32\n'+
    'SecondMagnitude'.ljust(16)+'dw #0000'.ljust(64)+'; сохранённый насыщенный модуль второй компоненты\n'+
    'FirstMagnitude'.ljust(16)+'dw #0000'.ljust(64)+'; сохранённый насыщенный модуль первой компоненты\n'+
    'CallerReturn'.ljust(16)+'dw #0000'.ljust(64)+'; внешний возврат ClampPatchedVectorWords\n'+
    '                ends\n                assert FClampVectorFrame == #08\n\n')


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x7F0E):return operation
    for value,name in ((0x7F0F,'FirstHigh'),(0x7F23,'SecondHigh'),(0x7F37,'ThirdHigh')):
        operation=operation.replace('#'+format(value,'04X'),'@ActionClampVectorWordsState.'+name)
    return operation.replace('AND #80','AND @ActionClampWordsConst.HighMask').replace('#7F00','@ActionClampWordsConst.Saturation')


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']=='Action' and item['target'] in (0x7F0F,0x7F12,0x7F23,0x7F26,0x7F37,0x7F3A):
            assert item['size']==2 and item['target_instruction']==item['target']-1
            item.update(target_region='Action',target_bank=5,target_slot=17,target_offset=item['target']-0x6000+0x23D,
                target_source_classified=True,target_path='Source/Action/ClampPatchedVectorWords.asm')
