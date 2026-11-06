"""Прямое продолжение после чтения узла, назначения вызываемых банковых входов не доказаны."""
FUNCTIONS = {0xE4DB: ('UnknownE4DB', 'Unknown, полный алгоритм двух рисователей после подготовки точек не доказан')}
SEMANTIC_STATUS = 'unknown'
FALLTHROUGH = True
LOCAL = {0xE4FA: 'PointE4FA', 0xE4FD: 'PointE4FD'}
CONTRACTS = {('Action', 0xE4DB): (
    ['Unknown, полный договор DBBD и всей цепочки не установлен, DD23 описан как RenderInsideRecords',
     'после ReadRenderQueue.LoadNode на CPU-стеке сохранён указатель узла'],
    ['Unknown, физическое продолжение после чтения Next идёт в SelectRenderQueueNode по E4FF'],
    ["Unknown, включая HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, страницы и изменяемый код"],
    ['из бинарного фрагмента выделены только исходные инструкции, это не доказательство назначения внешних вычислений',
     'договор RenderInsideRecords доказан отдельно, результат рисователя DBBD ещё требует разбора'])}
COMMENTS = {
    0xE4DB: (['-----------------------------------------', 'Неизвестная цепочка вычислений', 'Подготовительные вызовы и RenderInsideRecords доказаны отдельно, рисователь DBBD ещё требует разбора.'], None),
    0xE4E7: ([], 'переход, если найден маркер отказа перспективы 80xx, пропустить вывод объекта'),
    0xE4EA: (['Проверка общего отсечения, нулевой старший бит означает все точки снаружи одной границы.'], None),
    0xE4ED: ([], 'переход, если все точки снаружи хотя бы одной границы, пропустить вывод объекта'),
    0xE4EF: (['Проверка наличия точек снаружи хотя бы одной границы для выбора рисователя.'], None),
    0xE4F2: ([], 'переход, если хотя бы одна точка снаружи, вызвать DBBD вместо DD23'),
    0xE4FD: (['Восстановление сохранённого указателя узла и чтение Next перед последовательным продолжением по E4FF.'], None)}


def name_operands(region, function_address, operation):
    if region=='Action' and function_address==0xE4DB:
        operation=operation.replace('CALL #D5C9','CALL @Action.TransformObjectVertices.Entry').replace('CALL #DEF3','CALL @Action.ClassifyProjectedVertices.Entry')
    return operation
