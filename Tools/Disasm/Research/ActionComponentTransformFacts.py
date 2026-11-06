"""Рабочий вектор и копировщик трёхбайтовых компонент из четырёхбайтового шага."""
FUNCTIONS={0x6BFF:('CopyAndTransformComponents','Копирование трёх трёхбайтовых компонент с шагом четыре и последующее преобразование рабочего вектора'),
    0x6C19:('TransformWorkComponents','Преобразование старших слов трёх рабочих компонент с очисткой Low и знаковым кодированием результата')}
LOCAL={};LABELS={};CONTINUATIONS={0x6BFF:0x6C19}
RENAMES={'Action.Unknown6BFF.Entry':'Action.CopyAndTransformComponents.Entry',
    'Action.Unknown6C19.Entry':'Action.TransformWorkComponents.Entry'}
LOCATION={address:'перенесённый ACTION фиксированного банка 5' for address in FUNCTIONS}
COMMON_OUT=[
    'HL и DE определены ComputePatchedVector и последующим EncodeSignedComponents, B сохраняет значение перед вычислителем, C=0, AF определён кодировщиком либо отказом вычислителя',
    "HL', DE', BC' сохраняются, AF' от последнего умножителя, IX сохраняется, IY=RestoreComponentStack.Entry",
    'Input0..2 получают старшие слова рабочих компонент, Low всех трёх записей обнулён до расчёта и остаётся нулём при переполнении',
    'при переполнении Middle/High сохраняют слова, переданные в Input после возможного копирования, уже записанные Output сохранены',
    'при полном расчёте Middle/High получают кодированные знак и модуль, компонента 1 использует обратный знак',
    'SavedCpuSP получает исходный CPU SP, SavedIX получает IX, SP после внешнего RET равен входному SP+2, I/IM/IFF и paging сохраняются']
COMMON_NOTE=[
    'вычислитель использует SP как числовой накопитель, продолжение через IY восстанавливает настоящий SP до RET PE',
    'входные Middle/High читаются как исходные слова вычислителя, после успешного пути эти же физические байты содержат код знака и модуля',
    'единицы Low и входных слов не установлены, обнуление Low не заменяется предположением о фиксированной точке',
    '14432 композиционных сценария выполнили настоящие вычислитель, умножители, восстановление SP и кодировщик без подмены',
    'проверены все байтовые коэффициенты каждой позиции, граничные векторы, шесть мест переполнения и 4096 смешанных матриц каждого входа',
    'сопоставлены регистры включая R, восемь банков RAM и кратность записей, математический договор вычислителя повторно использован',
    'полное произведение векторов и матриц, единицы, точные T, IRQ, сборка и нативный запуск не доказаны']
CONTRACTS={('Action',0x6C19):(
    ['HL, DE, BC и AF числовых аргументов не задают, B сохраняется, C будет заменён нулём',
     'ActionComponentWork.Component0..2 содержат три входных слова в Middle/High, Low доступны для записи',
     'действуют договоры ComputePatchedVector, RestoreComponentStack и EncodeSignedComponents, коэффициенты и выходы доступны в банке 0',
     'CPU SP содержит внешний возврат и не пересекается с кодом, рабочими полями и выходами, повторный вход и вмешательство IRQ исключены'],
    [*COMMON_OUT,'B сохраняется, CPU-стек не записывается',
     'R получает 16 M1 подготовки и восстановления SP плюс M1 вычислителя и кодировщика, при его раннем RET PE кодировщик даёт один M1, бит 7 R сохранён'],
    ["HL, DE, C, AF, AF', IY, R, входные операнды, SavedCpuSP, SavedIX, три Low, до трёх Output и шесть байтов Middle/High при полном расчёте"],
    ['(1) жёсткий порядок, сюда продолжается часть (0) CopyAndTransformComponents.asm, прямой вход также допустим',*COMMON_NOTE]),
 ('Action',0x6BFF):(
    ['HL, DE и AF числовых аргументов не задают, BC уменьшается на девять при копировании и влияет на итоговый сохраняемый B',
     'IY указывает источник, читаются байты 0..2, 4..6 и 8..10, назначение четвёртого байта записей здесь не устанавливается',
     'действует договор TransformWorkComponents, CPU-стек допускает два дополнительных байта для PUSH IY',
     'источник и назначение могут перекрываться, чтения следуют оригинальному последовательному порядку, исполняемый код и внешний возврат не разрушаются'],
    [*COMMON_OUT,'B равен старшему байту (входной BC-9) AND FFFF, C=0',
     'три рабочих записи перед расчётом получают девять последовательно считанных байтов источника, Low затем обнулён',
     'в двух байтах под исходным CPU SP остаётся исходный IY, R получает стоимость TransformWorkComponents плюс 24 M1 с сохранением бита 7'],
    ["HL, DE, BC, AF, AF', IY, R, девять рабочих байтов и изменения TransformWorkComponents, два байта CPU-стека"],
    ['(0) жёсткий порядок, исполнение продолжается в TransformWorkComponents.asm, часть (1), настоящего JP между ними нет',
     'девять отдельных LDI уменьшают BC даже при нулевом входе, переход через границу меняет B и сохранён в модели',
     'дополнительно проверены 72 случая перекрытия источника, назначения и стека, включая оборачивание источника через FFFF',
     *COMMON_NOTE])}
COMMENTS={
    0x6BFF:(['-----------------------------------------','Источник и три рабочих компоненты','Перенос IY в HL через CPU-стек, два временных байта остаются изменёнными.'],None),
    0x6C02:(['Выбор первой физической рабочей FComponent24, запись состоит из Low, Middle и High.'],None),
    0x6C05:(['Копирование трёх байтов первой компоненты, BC уменьшается после каждого LDI.'],None),
    0x6C0B:(['Переход к следующей исходной компоненте с пропуском одного байта, назначение пропущенного байта не установлено.'],None),
    0x6C0C:(['Копирование трёх байтов второй компоненты с исходным последовательным порядком чтений и записей.'],None),
    0x6C12:(['Пропуск четвёртого байта второй исходной записи.'],None),
    0x6C13:(['Копирование третьей компоненты, исходный байт 11 не читается, затем начинается подготовитель в соседнем файле.'],None),
    0x6C19:(['-----------------------------------------','Входные слова вычислителя','Чтение Middle/High Component0 и обновление реального Input0, Low пока не участвует.'],None),
    0x6C1F:(['Чтение Middle/High Component1 и обновление Input1.'],None),
    0x6C25:(['Чтение Middle/High Component2 и обновление Input2 до изменения рабочих Low.'],None),
    0x6C2B:(['-----------------------------------------','CPU SP и младшие рабочие байты','Сохранение действительного CPU SP перед арифметическим использованием регистра вычислителем.'],None),
    0x6C2F:(['Подготовка нуля и очистка трёх Low, они остаются очищенными и при отказе вычислителя.'],None),
    0x6C39:(['Подготовка продолжения, которое восстановит CPU SP перед условным RET кодировщика.'],None),
    0x6C3D:(['Передача вычислителю через JP, адрес возврата по арифметическому SP не записывается.'],None)}


def name_operands(region,address,operation):
    if region!='Action' or address not in FUNCTIONS:return operation
    for value,field in ((0x9B1F,'Component0.Middle'),(0x9B22,'Component1.Middle'),(0x9B25,'Component2.Middle'),
        (0x9B1E,'Component0.Low'),(0x9B21,'Component1.Low'),(0x9B24,'Component2.Low')):
        operation=operation.replace('(#'+format(value,'04X')+')','(@ActionComponentWork.'+field+')')
    operation=operation.replace('LD DE, #9B1E','LD DE, @ActionComponentWork.Component0')
    for value,name in ((0xAF48,'Input0'),(0xAF56,'Input1'),(0xAF69,'Input2')):
        operation=operation.replace('(#'+format(value,'04X')+')','(@ActionPatchedVectorState.'+name+')')
    return operation.replace('(#6C41)','(@ActionComponentStackState.SavedCpuSP)').replace('#6C40','@Action.RestoreComponentStack.Entry')


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']!='Action' or not 0x6C19<=item['writer']<0x6C40:continue
        target=item['target'];assert target in (0xAF48,0xAF56,0xAF69,0x6C41)
        item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True,
            target_region='Action',target_bank=5 if target<0x8000 else 2,target_slot=17,
            target_offset=target-0x6000+(0x23D if target<0x8000 else 0),target_source_classified=True,
            target_path='Source/Action/RestoreComponentStack.asm' if target==0x6C41 else 'Source/Action/ComputePatchedVector.asm')
