"""Подготовка матрицы и перебор объектных записей кадра ACTION."""
FUNCTIONS = {0xE020: ('RenderSceneFrame', 'Подготовка кадра, проекция объектов и передача в очередь отрисовки')}
LOCAL = {
    0xE036: 'ApproachY', 0xE044: 'SavePosition', 0xE047: 'ResetFrame',
    0xE065: 'StoreC00', 0xE070: 'StoreC10', 0xE07B: 'StoreC20',
    0xE086: 'StoreC01', 0xE091: 'StoreC11', 0xE09C: 'StoreC21',
    0xE0A7: 'StoreC02', 0xE0B2: 'StoreC12', 0xE0BD: 'StoreC22',
    0xE0DD: 'CheckMarker', 0xE0E2: 'AdvanceRecord', 0xE0E4: 'ReadRecord',
    0xE0FD: 'CheckX', 0xE10F: 'CheckY', 0xE121: 'CheckDepth',
    0xE142: 'StorePhaseFlag', 0xE14C: 'ResumeTransform',
    0xE171: 'SaveAbsX', 0xE179: 'SaveAbsDepth', 0xE181: 'CompareDepth',
    0xE185: 'CompareX', 0xE189: 'ScaleLevel', 0xE194: 'ClearLevel',
    0xE195: 'CompareLevel', 0xE19D: 'SaveLevel', 0xE1B2: 'ReadModelHeader',
}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {'Action.UnknownE020.Entry': 'Action.RenderSceneFrame.Entry'}
RENAMES.update({f'Action.UnknownE020.Point{address:04X}': 'Action.RenderSceneFrame.' + name
                for address, name in LOCAL.items() if address != 0xE14C})
ADDITIONAL_SYMBOLS = {'Action.RenderSceneFrame.ResumeTransform': 0xE14C}
CONTINUATIONS = {0xE020: 0xE1B9}
LOCATION = {0xE020: 'код ACTION банка 0'}
CONTRACTS = {('Action', 0xE020): (
    ['CompanionMask, Position, тройка углов и FirstMode задают подготовку кадра',
     'доступны широкий список, объектные записи с конечным маркером, таблицы ACTION и ресурс OBJECT3D',
     'банк 0 выбран, страницы 1, 3 и 4 загружены, SP в общей RAM, IRQ не вмешиваются'],
    ['базис и девять коэффициентов обновляются, выполняются проекция тела по режиму и обход широких векторов',
     'объекты перебираются с шагом #40, выходные слова сохраняются в допущенных записях',
     'при конечном маркере ReadRenderQueue восстанавливает настоящий SP и читает очередь',
     'при допуске очередной записи управление продолжается в PrepareProjectionScale после чтения заголовка'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, SP на участке чтения и записи, R',
     'состояние базиса, матрицы, проекции, записей, очереди, временные слова и регистр 7FFD'],
    ['точные условия отдельных путей приведены в документации, байты очереди проверяются независимо от графического вывода',
     'модель покрывает полный возврат с пустой и непустой очередью на исходных ресурсах',
     'точные все регистры и записи всего кадра, игровые IRQ и нативный вывод не заявляются'],
)}
COMMENTS = {
    0xE020: (['Проверка допуска приближения точки к центру.'], None),
    0xE023: ([], 'переход, если CompanionMask ненулевая, сохранить положение'),
    0xE025: (['Расчёт шага X к #77 по знаку байтовой разности.'], None),
    0xE02D: ([], 'переход, если X уже равен #77'),
    0xE031: ([], 'переход, если разность положительна и шаг X уже выполнен'),
    0xE036: (['Расчёт шага Y к #2B по тому же правилу.'], None),
    0xE03B: ([], 'переход, если Y уже равен #2B'),
    0xE03F: ([], 'переход, если разность положительна и шаг Y уже выполнен'),
    0xE047: (['Сброс допуска и уровня AY, подготовка углов поворота базиса.'], None),
    0xE0C0: (['Проверка режима перед проекцией тела.'], None),
    0xE0C5: ([], 'вызов, если FirstMode отличается от 1'),
    0xE0CB: (['Инициализация пустой очереди и сохранение настоящего SP.'], None),
    0xE0DD: (['Проверка признака конца в младшем байте маркера.'], None),
    0xE0DF: ([], 'переход, если бит 7 младшего байта маркера установлен'),
    0xE0E4: (['Чтение текущей записи через SP после установки маркера по смещению #1B.'], None),
    0xE0F1: ([], 'переход, если старший байт первого слова равен #80'),
    0xE0F8: ([], 'переход, если старший байт X неотрицателен'),
    0xE0FF: ([], 'переход, если модуль старшего байта X не меньше #70'),
    0xE10A: ([], 'переход, если старший байт Y неотрицателен'),
    0xE111: ([], 'переход, если модуль старшего байта Y не меньше #70'),
    0xE11C: ([], 'переход, если старший байт глубины неотрицателен'),
    0xE123: ([], 'переход, если модуль старшего байта глубины не меньше #70'),
    0xE13F: ([], 'переход, если первый и третий углы равны нулю'),
    0xE14C: (['Проверка результата арифметического преобразования.'], 'переход, если преобразование переполнилось'),
    0xE157: (['Подготовка SP для записи трёх выходных слов в запись.'], None),
    0xE16C: ([], 'переход, если старший байт результата X неотрицателен'),
    0xE174: ([], 'переход, если старший байт результата глубины неотрицателен'),
    0xE17C: ([], 'переход, если старший байт результата Y неотрицателен'),
    0xE182: ([], 'переход, если модуль Y не меньше модуля глубины'),
    0xE186: ([], 'переход, если накопленный максимум не меньше модуля X'),
    0xE189: (['Расчёт уровня из максимального модуля.'], None),
    0xE18D: ([], 'переход, если половина максимума не меньше #0F, обнулить кандидат'),
    0xE19A: ([], 'переход, если прежний уровень не меньше кандидата'),
    0xE1A2: ([], 'переход, если глубина отрицательна, пропустить запись'),
    0xE1A5: (['Выбор указателя по преобразованной глубине, вторая запись пары относится к ближнему варианту.'], None),
    0xE1AA: ([], 'переход, если старший байт глубины не меньше порога, сохранить исходное смещение'),
    0xE1B2: (['Восстановление настоящего SP перед чтением заголовка модели.'], None),
}
for address in (0xE062, 0xE06D, 0xE078, 0xE083, 0xE08E, 0xE099, 0xE0A4, 0xE0AF, 0xE0BA):
    COMMENTS[address] = ([], 'переход, если коэффициент отличается от #80, сохранить его')


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xE020:
        return operation
    aliases = {
        '9BA1': 'ActionRenderQueueCursor.Value.Head',
        '9B8D': 'ActionRenderHeader.Value.ModeBits',
        '9B19': 'ActionAimFollowState.Position',
        'E021': 'ActionProjectedBoundsState.CompanionMask',
        'ED83': 'ActionAyEffectsState.ChannelCLevel',
        '9B81': 'ActionGlyphIndicatorState.Control.FirstMode',
        '9B8E': 'ActionObjectVerticesState.ModelByteOffset',
        'AF48': 'ActionPatchedVectorState.Input0',
        'AF56': 'ActionPatchedVectorState.Input1',
        'AF69': 'ActionPatchedVectorState.Input2',
        'D9B6': 'ActionPatchedVectorState.Output0',
        'D7C4': 'ActionPatchedVectorState.Output1',
        'D7A2': 'ActionPatchedVectorState.Output2',
    }
    addresses = ('CB3E', 'CB8B', 'CBD8', 'CB54', 'CBA1', 'CBEE', 'CB6F', 'CBBC', 'CC09')
    for index, operand in enumerate(addresses):
        aliases[operand] = f'ActionPatchedVectorCoeffs.C{index % 3}{index // 3}'
    for operand, alias in aliases.items():
        operation = operation.replace(f'(#{operand})', f'(@{alias})')
    return (operation.replace('LD IY, #E14C', 'LD IY, @Action.RenderSceneFrame.ResumeTransform')
            .replace('CP #1F', 'CP @ActionObjectCopyConst.NearDepthEnd')
            .replace('ADD A, #02', 'ADD A, @FObjectDataPointer'))
