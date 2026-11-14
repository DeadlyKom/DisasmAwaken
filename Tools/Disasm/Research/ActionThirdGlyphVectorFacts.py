"""Преобразование трёх исходных слов и публикация третьего знака при разрешении ThirdGate."""
FUNCTIONS={0x6C8F:('UpdateThirdGlyphVector','Подготовка трёх входных слов, расчёт вектора с арифметическим SP и обновление третьего экранного знака')}
LOCAL={};LABELS={};CONTINUATIONS={}
RENAMES={'Action.Unknown6C8F.Entry':'Action.UpdateThirdGlyphVector.Entry'}
LOCATION={0x6C8F:'перенесённый ACTION фиксированного банка 5'}
CONTRACTS={('Action',0x6C8F):(
    ['HL, DE, BC и AF числовых аргументов не задают, B сохраняется, C сохраняется только при запрете',
     'ThirdGate физического Control разрешает расчёт только при нуле, остальные 255 значений завершают процедуру',
     'SourceWord0..2 содержат разряды 23..8 трёх компонент вектора станции ActionWorkVector, единицы расстояния не установлены',
     'действуют договоры ComputePatchedVector, RestoreThirdGlyphStack и PublishThirdGlyphVector, девять коэффициентов доступны в банке 0',
     'CPU SP содержит внешний возврат, его слово не пересекается с изменяемыми операндами и выходами, повторный вход и вмешательство IRQ исключены'],
    ['при ненулевом ThirdGate HL, DE и BC сохранены, A=ThirdGate, F от OR этого байта, RAM не меняется',
     "при запрете HL', DE', BC', AF', IX и IY сохранены, R получает три M1",
     'при допуске Input0..2 получают SourceWord0..2, SavedCpuSP получает входной SP, SavedIX получает входной IX',
     'при допуске HL и DE определены ComputePatchedVector, B сохраняется, C=0, AF определён вычислителем и последующим PublishThirdGlyphVector',
     "при допуске HL', DE', BC' сохраняются, AF' от последнего умножителя, IX сохраняется, IY=RestoreThirdGlyphStack.Entry",
     'при переполнении уже записанные Output сохраняются, последующие остаются прежними, все поля Third сохраняются',
     'при полном расчёте все три Output обновлены, Third получает четверти двух выходных слов и старший байт третьего',
     'при допуске R получает M1 настоящего ComputePatchedVector плюс 16 при переполнении либо плюс 37 при публикации, бит 7 сохраняется',
     'SP после RET равен входному SP+2, I/IM/IFF и paging сохраняются, CPU-стек и порты не записываются'],
    ['HL, DE, C, AF, AF\', IY только при допуске, R',
     'Input0..2, SavedCpuSP, SavedIX и от нуля до трёх Output только при допуске, три поля Third только после полного расчёта'],
    ['третьим знаком управляет та же физическая структура, которую читает Controls.UpdateGlyphIndicators, новые копии полей не вводятся',
     'CPU SP сохраняется в операнд 6CB2 перед переходом JP, вычислитель не вызывается CALL и использует SP как числовой накопитель',
     'продолжение через IY сначала выполняет LD SP,nn и лишь затем RET PE, поэтому отказ тоже возвращается по настоящему CPU-стеку',
     'полная композиция прошла 72460 сценариев, включая все пары ThirdGate и входного F, все байтовые коэффициенты в каждой позиции и шесть мест переполнения',
     'сопоставлены все регистры включая R, восемь банков RAM и кратность записей, дети исполняются без подмены',
     'числовой эталон композиционный, повторно использует ранее проверенный договор арифметического вычислителя, отдельный новый эталон умножения не создавался',
     'полное произведение векторов и матриц, единицы источников, точные T, IRQ, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0x6C8F:(['-----------------------------------------','Разрешение третьего знака','Проверка полного ThirdGate существующего Control, только нуль допускает новое преобразование.'],None),
    0x6C93:([],'выход, если ThirdGate ненулевой, сохранить прежний вычисленный вектор и поля Third'),
    0x6C94:(['-----------------------------------------','Подготовка входных слов вычислителя','Чтение разрядов 23..8 первой компоненты станции и обновление Input0, младшие восемь разрядов отбрасываются.'],None),
    0x6C9A:(['Чтение разрядов 23..8 второй компоненты станции и обновление Input1.'],None),
    0x6CA0:(['Чтение разрядов 23..8 третьей компоненты станции и обновление Input2.'],None),
    0x6CA6:(['-----------------------------------------','Вычисление с арифметическим SP','Сохранение действительного CPU SP в непосредственный операнд восстановления перед расчётом.'],None),
    0x6CAA:(['Подготовка продолжения, которое восстановит CPU SP до первого условного RET.'],None),
    0x6CAE:(['Передача вычислителю через JP, адрес возврата по арифметическому SP не записывается.'],None)}


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x6C8F):return operation
    for value,name in ((0x9B79,'SourceWord0'),(0x9B7C,'SourceWord1'),(0x9B7F,'SourceWord2')):
        operation=operation.replace('(#'+format(value,'04X')+')','(@ActionThirdGlyphVectorState.'+name+')')
    for before,after in (('(#9B82)','(@ActionGlyphIndicatorState.Control.ThirdGate)'),
        ('(#AF48)','(@ActionPatchedVectorState.Input0)'),('(#AF56)','(@ActionPatchedVectorState.Input1)'),
        ('(#AF69)','(@ActionPatchedVectorState.Input2)'),('(#6CB2)','(@ActionThirdGlyphStackState.SavedCpuSP)'),
        ('#6CB1','@Action.RestoreThirdGlyphStack.Entry')):
        operation=operation.replace(before,after)
    return operation


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']!='Action' or not 0x6C8F<=item['writer']<0x6CB1:continue
        target=item['target'];assert target in (0xAF48,0xAF56,0xAF69,0x6CB2)
        item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True,
            target_region='Action',target_bank=5 if target<0x8000 else 2,target_slot=17,
            target_offset=target-0x6000+(0x23D if target<0x8000 else 0),target_source_classified=True,
            target_path='Source/Action/RestoreThirdGlyphStack.asm' if target==0x6CB2 else 'Source/Action/ComputePatchedVector.asm')
