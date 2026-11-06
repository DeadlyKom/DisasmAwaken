"""Управление чтением runtime-очереди и отдельный вход загрузки её физического узла."""
FUNCTIONS = {
    0xE4A6: ('ReadRenderQueue', 'Восстановление стека чтения очереди и загрузка снимка узла с обновлением AY'),
    0xE4FF: ('SelectRenderQueueNode', 'Проверка конца очереди либо переход к загрузке выбранного узла')}
LOCATION = {0xE4A6: 'код ACTION банка 0, адреса E4A6..E4DA', 0xE4FF: 'код ACTION банка 0, адреса E4FF..E505'}
LOCAL = {0xE4B1: 'LoadNode'}
CONTINUATIONS = {0xE4A6: 0xE4DB}
RENAMES = {'Action.UnknownE4A6.Entry': 'Action.ReadRenderQueue.Entry',
           'Action.UnknownE4A6.PointE4B1': 'Action.ReadRenderQueue.LoadNode',
           'Action.UnknownE4FF.Entry': 'Action.SelectRenderQueueNode.Entry'}
LABELS = {('Action', 0xE4B1): 'LoadNode'}
CONTRACTS = {
    ('Action', 0xE4A6): (
        ['основной Entry не принимает числовые аргументы в HL, DE, BC и AF',
         'SavedEntrySP по E4A7 задаёт восстанавливаемый стек, Head содержит смещение головы страницы 8F либо 01',
         'дополнительный LoadNode по E4B1 принимает HL как указатель FActionRenderNode, на CPU-стеке доступен возврат всего обхода',
         'для LoadNode курсоры AY и смеситель удовлетворяют договору UpdateAyEffects, R влияет на шум, IRQ не вмешиваются',
         'два неизвестных байта узла 01 и 02 не интерпретируются, ACTION доступен в банке 0'],
        ['Entry восстанавливает SP=SavedEntrySP, A=Head, H=8F, L и DE, BC, F сохраняются, переход в SelectRenderQueueNode по E4FF',
         'если селектор видит Head=01, он возвращается по восстановленному стеку, иначе передаёт HL в LoadNode',
         'LoadNode сохраняет входной HL словом на стеке и записывает адрес этого слова в SavedNodeSP по E4D6',
         'по полям узла восстанавливаются HeaderWord0, PhasePair, Phase2, Output0, Output1 и Output2',
         'после чтения полей восстанавливается SP=SavedNodeSP, затем исполняется настоящий UpdateAyEffects',
         'LoadNode заканчивается перед E4DB, SP равен входному SP минус 2, сохранённый указатель узла остаётся на вершине',
         'после LoadNode DE=Output1, BC=BFFD, A=max(4, ChannelCLevel >> 1), F соответствует CP половины уровня с 4',
         'после LoadNode H равен старшему байту продвинутого курсора B либо нулю при отключённом B, L равен 00 либо 20 по порогу R',
         "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются по обоим входам, paging не меняется",
         'Entry сам RAM не пишет, LoadNode использует четыре дополнительных байта CPU-стека и выполняет обмен AY по договору UpdateAyEffects'],
        ['HL, DE, BC, AF, SP, R по выбранному входу, SavedNodeSP, восстановленные переменные снимка, курсоры AY, четыре байта стека и регистры AY по LoadNode'],
        ['Entry и LoadNode имеют разные границы модели, запись SavedEntrySP выполняется ранее в прологе UnknownE020',
         'при загрузке Phase2 POP AF также читает F из старшего байта PhasePair, последующий AY-потребитель заменяет этот F',
         'полное исполнение RenderQueuedObject и всех вызовов вывода не входит в договор загрузки',
         'частота AY-тиков при обходе и слышимое звучание не подтверждены, R учитывается в точке чтения LD A,R']),
    ('Action', 0xE4FF): (
        ['H задаёт страницу узлов, в текущем обходе H=8F, L сохраняется до проверки конца',
         'DE и BC сохраняются, A задаёт полный байт Head либо Next, входной F числовых аргументов не задаёт',
         'при A=01 на CPU-стеке должен находиться внешний возврат, при ином A исполнение перейдёт в ReadRenderQueue.LoadNode'],
        ['F соответствует CP входного A с 01, A сохраняется',
         'при A=01 выполняется RET, HL сохраняется, SP увеличивается на два',
         'при A не равном 01 L=A, H и SP сохраняются, переход в ReadRenderQueue.LoadNode по E4B1',
         "DE, BC, HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, RAM и порты не изменяются"],
        ['L при выборе узла, F, SP при возврате и R'],
        ['селектор не проверяет допустимость смещения или страницы, числовой маркер конца равен ровно 01',
         'модель проверяет все сочетания A и F, но не исполняет последующую загрузку узла в этом же испытании'])}
COMMENTS = {
    0xE4A6: (['-----------------------------------------', 'Начало чтения очереди', 'Восстановление сохранённого до обхода SP, он нужен для завершающего RET всей очереди.'], None),
    0xE4A9: (['Чтение головы и подготовка страницы узлов без изменения входного F.'], None),
    0xE4B1: (['-----------------------------------------', 'Загрузка выбранного узла', 'Сохранение указателя узла на обычном CPU-стеке и адреса его слова перед чтением данных через SP.'], None),
    0xE4B6: (['Расчёт адреса HeaderWord0, два неизвестных байта узла пропускаются.'], None),
    0xE4BA: (['Восстановление двух исходных слов заголовка снимка в физическом порядке полей.'], None),
    0xE4C2: (['Расчёт положения SP для чтения Phase2 через A, F читается из уже использованного старшего байта PhasePair.'], None),
    0xE4C7: (['Восстановление трёх слов Output0, Output1 и Output2 из полей Components.'], None),
    0xE4D5: (['Восстановление обычного стека, сохранённый указатель узла остаётся на его вершине.'], None),
    0xE4D8: (['Обновление настоящего AY-потребителя перед отдельной цепочкой вывода RenderQueuedObject.'], None),
    0xE4FF: (['-----------------------------------------', 'Проверка конца цепочки', 'Сравнение полного Head либо Next с числовым маркером 01.'], None),
    0xE501: ([], 'выход, если смещение равно 01, очередь закончилась'),
    0xE502: (['Создание полного адреса следующего узла с сохранением страницы в H.'], None)}


def name_operands(region, function_address, operation):
    if region != 'Action':
        return operation
    operation = operation.replace('(#E4A7)', '(@ActionRenderQueueControlState.SavedEntrySP)')
    if function_address == 0xE4A6:
        for address, name in ((0xE4D6, 'ActionRenderQueueControlState.SavedNodeSP'),
            (0x9BA1, 'ActionRenderQueueInsertState.Head'), (0x9B8D, 'ActionRenderQueueInsertState.HeaderWord0'),
            (0x9B12, 'ActionRenderQueueInsertState.PhasePair'), (0x9B14, 'ActionRenderQueueInsertState.Phase2'),
            (0xD9B6, 'ActionPatchedVectorState.Output0'), (0xD7C4, 'ActionPatchedVectorState.Output1'), (0xD7A2, 'ActionPatchedVectorState.Output2')):
            operation = operation.replace('(#' + format(address, '04X') + ')', '(@' + name + ')')
        operation = operation.replace('LD H, #8F', 'LD H, @ActionRenderQueueConst.Page')
        operation = operation.replace('CALL #ECA8', 'CALL @Action.UpdateAyEffects.Entry')
    if function_address == 0xE4FF:
        operation = operation.replace('CP #01', 'CP @ActionRenderQueueConst.EndLink')
    return operation
