"""Вставка в конечную очередь страницы 8F, поля метаданных не переименовываются по догадке."""
FUNCTIONS = {0xE40F: ('InsertRenderQueue', 'Вставка снимка объекта в связанную очередь по исходному знаковому сравнению глубины')}
LOCATION = {0xE40F: 'код ACTION банка 0, адреса E40F..E4A5'}
LOCAL = {0xE431: 'FindNext', 0xE44C: 'InsertHead', 0xE462: 'InsertTail', 0xE474: 'InsertMiddle', 0xE486: 'WritePayload'}
RENAMES = {'Action.UnknownE40F.Entry': 'Action.InsertRenderQueue.Entry', **{'Action.UnknownE40F.Point' + format(a, '04X'): 'Action.InsertRenderQueue.' + n for a, n in LOCAL.items()}}
LABELS = {('Action', a): name for a, name in LOCAL.items()}
CONTRACTS = {('Action', 0xE40F): (
    ['HL, DE, BC и AF числовых аргументов не задают',
     'IX и IY служат временными указателями на узлы, их исходные значения не задают список',
     'Output0, Output1, Output2 задают три слова снимка, Input1 читается в DE и не участвует в сортировке',
     'Head содержит младший байт первого узла либо 01, FreeOffset задаёт 00, 0E, ..., EE либо FC при исчерпании',
     'узлы находятся в странице 8F, конечная цепочка Next не содержит циклов, глубина узла читается по смещению 0C',
     'HeaderWord0 по 9B8D сохраняет частично неизвестный заголовок, PhasePair по 9B12 содержит Phase0/Phase1, Phase2 по 9B14 третью фазу',
     'ACTION доступен в банке 0, IRQ не вмешиваются, SP используется для записи данных и не является возвращаемым стеком этого фрагмента'],
    ['HL после успеха равен HeaderWord0, при отказе пустого списка сохраняется, при отказе непустого содержит результат последнего сравнения глубины',
     'DE равен Input1 по всем путям, это слово читается, но не участвует в сортировке',
     'BC равен Output2 по всем путям, это ключ вставляемого снимка',
     'AF при FreeOffset=FC равен FC6A, после успеха A=Phase2 и F от ADD старого FreeOffset,0E',
     "HL', DE', BC', AF' сохраняются",
     'IX при пустом списке сохраняется, иначе указывает исходную голову либо последнего проверенного предшественника',
     'IY сохраняется при пустом списке и отрицательной первой разности, иначе IYH=8F, IYL равен последнему проверенному следующему смещению либо исходному IYL, пока такого узла не было',
     'I, IM и IFF сохраняются, вызовов процедур и портовых операций нет',
     'при отказе записей RAM нет, SP сохраняется и продолжение начинается по E4A6',
     'после успеха SP=адрес нового узла+3, продолжение по E0E2, исходный SP не восстанавливается, внешнего RET здесь нет',
     'Carry перед каждым сравнением глубины равен результату CP смещения узла с 01, для смещения 00 он равен 1',
     'проверяется только Sign обёрнутой разности word(depth_узла-Output2-Carry), первый отрицательный результат задаёт вставку перед узлом, иначе запись идёт в конец',
     'при успехе новый узел получает Next, Head либо Next предшественника указывает на него, FreeOffset увеличен на 14',
     'HeaderWord0, PhasePair, Phase2 и три слова Output0..2 записаны по смещениям 03..0D, байты 01 и 02 сохранены',
     'R изменяется по полному M1 фактического пути до указанного продолжения, бит 7 сохраняется, сами продолжения не исполнены моделью'],
    ['HL, DE, BC, AF, IX, IY, SP при успехе, R, Head либо связь предшественника, FreeOffset и данные нового узла'],
    ['это исходная очередь отрисовки, имя описывает наблюдаемые поля снимка и последующий потребитель, весь игровой цикл ещё не доказан',
     'SBC не заменяется знаковым сравнением без оборачивания, Overflow отдельно не проверяется, равные глубины у смещения 00 дают отрицательный результат',
     'PUSH AF пишет временный F по смещению 06, следующий PUSH HL заменяет этот байт старшим байтом PhasePair',
     'SP после записи указывает внутрь узла, последующее E0E2 само меняет стек, обычного RET здесь нет',
     'страница 8F в этой фазе является рабочей областью, исходные дисковые байты 8F00 не объявляются начальными узлами',
     'неизвестные байты 01 и 02 сохраняются и явно остаются неизвестными, память для новых узлов не выделяется'])}
COMMENTS = {
    0xE40F: (['-----------------------------------------', 'Подготовка ключа очереди', 'Чтение глубины Output2, Input1 возвращается в DE и здесь не участвует в сравнении.'], None),
    0xE417: (['Проверка пустой цепочки по Head=01.'], None),
    0xE41C: ([], 'переход, если Head равен 01, вставить узел перед пустой цепочкой'),
    0xE41E: (['Создание указателя IX на голову очереди в странице 8F, Carry от CP сохраняется.'], None),
    0xE423: (['Чтение глубины головы и расчёт разности с Output2 и сохранённым займом.'], None),
    0xE42B: ([], 'переход, если бит Sign разности головы установлен, вставить перед головой'),
    0xE42E: (['Подготовка страницы IY для последующих узлов.'], None),
    0xE431: (['-----------------------------------------', 'Поиск места вставки', 'Чтение Next предшественника и проверка конца цепочки, CP также задаёт Carry следующего SBC.'], None),
    0xE436: ([], 'переход, если Next равен 01, вставить после последнего узла'),
    0xE438: (['Создание указателя IY на следующий узел без изменения Carry.'], None),
    0xE43A: (['Чтение глубины следующего узла и расчёт исходной разности с займом, смещение 00 даёт дополнительную единицу.'], None),
    0xE442: ([], 'переход, если бит Sign разности следующего узла установлен, вставить между IX и IY'),
    0xE445: (['Обновление предшественника для следующей проверки.'], None),
    0xE44C: (['-----------------------------------------', 'Вставка перед головой', 'Проверка свободного смещения на FC, отказ не меняет цепочку и стек.'], None),
    0xE451: ([], 'переход, если FreeOffset равен FC, очередь исчерпана'),
    0xE454: (['Создание нового узла с прежней головой в Next и обновление Head.'], None),
    0xE462: (['-----------------------------------------', 'Вставка в конец', 'Проверка свободного смещения перед изменением Next последнего узла.'], None),
    0xE467: ([], 'переход, если FreeOffset равен FC, очередь исчерпана'),
    0xE469: (['Обновление Next предшественника и установка конечного маркера нового узла.'], None),
    0xE474: (['-----------------------------------------', 'Вставка между узлами', 'Проверка свободного смещения до изменения двух связей.'], None),
    0xE479: ([], 'переход, если FreeOffset равен FC, очередь исчерпана'),
    0xE47B: (['Сохранение прежнего Next в новом узле и замена Next предшественника.'], None),
    0xE486: (['-----------------------------------------', 'Запись снимка через SP', 'Расчёт следующего свободного смещения с шагом 14, SP ставится за конец нового узла.'], None),
    0xE48D: (['Запись трёх слов снимка в обратном порядке, Output2 затем Output1 и Output0.'], None),
    0xE496: (['Запись Phase2 через PUSH AF, временный F ниже него затем перекрывается.'], None),
    0xE49A: (['Смещение SP на байт для упаковки трёх исходных полей без добавления выравнивания.'], None),
    0xE49B: (['Запись PhasePair, его старший байт заменяет временный F.'], None),
    0xE49F: (['Запись HeaderWord0, байты узла 01 и 02 остаются нетронутыми.'], None)}


def name_operands(region, function_address, operation):
    if region != 'Action':
        return operation
    for address, label in LOCAL.items():
        if operation.startswith(('JP ', 'JR ')):
            operation = operation.replace('#' + format(address, '04X'), '@Action.InsertRenderQueue.' + label)
    if function_address != 0xE40F:
        return operation
    for address, name in ((0xD9B6, 'ActionPatchedVectorState.Output0'), (0xD7C4, 'ActionPatchedVectorState.Output1'),
        (0xD7A2, 'ActionPatchedVectorState.Output2'), (0xAF56, 'ActionPatchedVectorState.Input1'),
        (0x9BA1, 'ActionRenderQueueInsertState.Head'), (0x9BA2, 'ActionRenderQueueInsertState.FreeOffset'),
        (0x9B8D, 'ActionRenderQueueInsertState.HeaderWord0'), (0x9B12, 'ActionRenderQueueInsertState.PhasePair'), (0x9B14, 'ActionRenderQueueInsertState.Phase2')):
        operation = operation.replace('(#' + format(address, '04X') + ')', '(@' + name + ')')
    for index in ('IX', 'IY'):
        operation = operation.replace('(' + index + '+#00)', '(' + index + '+FActionRenderNode.Next)')
        for offset, field in ((12, 'Low'), (13, 'High')):
            operation = operation.replace('(' + index + '+#' + format(offset, '02X') + ')', '(' + index + '+FActionRenderNode.Components.Component2.' + field + ')')
    operation = operation.replace('CP #01', 'CP @ActionRenderQueueConst.EndLink')
    operation = operation.replace('CP #FC', 'CP @ActionRenderQueueConst.FullOffset')
    operation = operation.replace('LD (HL), #01', 'LD (HL), @ActionRenderQueueConst.EndLink')
    operation = operation.replace('ADD A, #0E', 'ADD A, FActionRenderNode')
    operation = operation.replace('LD IXH, #8F', 'LD IXH, @ActionRenderQueueConst.Page')
    operation = operation.replace('LD IYH, #8F', 'LD IYH, @ActionRenderQueueConst.Page')
    operation = operation.replace('LD H, #8F', 'LD H, @ActionRenderQueueConst.Page')
    return operation


def structure_text():
    lines = ['', '                ; Физическая раскладка создаваемого runtime-узла, дисковые экземпляры не подменяются',
             '                struct FActionRenderNode']
    for name, declaration, note in (
        ('Next', 'db #00', 'младший байт следующего узла в странице 8F, 01 конец'),
        ('Unknown01', 'db #00', 'позиция младшего байта SETS архивного узла, текущая вставка сохраняет'),
        ('Unknown02', 'db #00', 'позиция старшего байта SETS архивного узла, текущая вставка сохраняет'),
        ('HeaderWord0', 'dw #0000', 'снимок ModeBits и ModelByteOffset по 9B8D, порядок байтов сохранён'),
        ('Phases', 'FRenderPhases', 'Phase0, Phase1 и Phase2, снимок 9B12..9B14'),
        ('Components', 'FActionComponents', 'снимок Output0, Output1 и Output2, глубина по +0C')):
        lines.append((name.ljust(16) + declaration).ljust(80) + '; ' + note)
    lines += ['                ends', '                assert FActionRenderNode == #0E',
              '                assert FActionRenderNode.HeaderWord0 == #03',
              '                assert FActionRenderNode.Phases == #05',
              '                assert FActionRenderNode.Phases.Phase2 == #07',
              '                assert FActionRenderNode.Components == #08',
              '                assert FActionRenderNode.Components.Component2 == #0C', '']
    return '\n'.join(lines)


def constant_text():
    lines = ['', '                ; Исходные маркеры связанной очереди, это полные числовые значения',
             '                module ActionRenderQueueConst']
    for name, value, note in (('EndLink', 1, 'конец цепочки Next, не свободное физическое смещение'),
                              ('FullOffset', 252, 'буфер из 18 узлов исчерпан'),
                              ('Page', 143, 'старший байт адресов runtime-узлов')):
        lines.append((name.ljust(16) + 'equ #' + format(value, '02X')).ljust(80) + '; ' + note)
    return '\n'.join(lines + ['                endmodule', ''])


INCLUDE_BLOCKS = (('Includes/Structs/Include.inc', 'struct FActionRenderNode', structure_text()),
                  ('Includes/Const/Include.inc', 'module ActionRenderQueueConst', constant_text()))
