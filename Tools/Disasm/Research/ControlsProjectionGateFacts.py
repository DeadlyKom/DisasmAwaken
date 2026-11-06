"""Проекция и до трёх сравнений с постоянной опорой Component2."""
FUNCTIONS={0xD95F:('ProjectAndCheckComponents','Построение проекции и проверка двух компонент относительно постоянной опоры Component2')}
LOCAL={}
LABELS={}
RENAMES={'Controls.UnknownD95F.Entry':'Controls.ProjectAndCheckComponents.Entry'}
CONTINUATIONS={}
CONTRACTS={('Controls',0xD95F):(
    ['HL, DE, BC, AF числовых аргументов не задают, действуют входные условия BuildBodyProjection',
     'банк 1 выбран, физические Component0..2 и проекция доступны для записи',
     'на CPU-стеке внешний возврат, восемь байтов ниже него доступны вложенным вызовам'],
    ['HL и BC возвращаются от проекции, DE и AF от последнего сравнения либо от отказа проекции',
     'при отказе проекции A=0, F=54 после AND A, сравнения не выполняются',
     'при отказе сравнения A=0, F=44, при допуске NZ и точные AF от CompareComponents',
     'опора всегда Component2, последовательно проверяются Component0, Component1 и сама Component2',
     "HL', DE', AF', IX, IY сохраняются, BC' возвращается от BuildBodyProjection",
     'SP=входной SP+2, I, IM, IFF и банковая страница сохраняются'],
    ["HL, DE, BC, AF, BC', R, записи BuildBodyProjection и восемь временных байтов CPU-стека"],
    ['если усечённый High опоры меньше DirectLimit=0A, CompareComponents допускает любую текущую компоненту',
     'иначе ключ опоры должен быть не меньше ключей Component0 и Component1, сравнение Component2 с собой всегда допускает',
     'отказ проверки не откатывает уже построенную проекцию, IX и IY восстанавливаются на всех возвратах',
     '40960 сценариев проверили настоящие дочерние процедуры и все регистры кроме R, RAM вне рамки и кратность записей вне временной рамки',
     'значения временного стека, R, полный набор компонент, IRQ, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0xD95F:(['Построение двух смещений, флагов и радиуса, частичные записи при отказе сохраняются.'],None),
    0xD962:(['Проверка возвращённого A до замены индексных регистров.'],None),
    0xD963:([], 'выход, если построение проекции вернуло A=0'),
    0xD964:(['Выбор постоянной опоры Component2 и предыдущей позиции для последовательного обхода с шагом FComponent24.'],None),
    0xD970:(['Проверка Component0 относительно постоянной опоры.'],None),
    0xD973:([], 'вызов, если Component0 допущен, проверить Component1'),
    0xD976:([], 'вызов, если Component1 допущен, сравнить опору Component2 с собой')}

def name_operands(region,function_address,operation):
    if region=='Controls' and function_address in FUNCTIONS:
        operation=operation.replace('#9B24','@ActionComponentWork.Component2')
        operation=operation.replace('#9B1B','@ActionComponentWork.Component0-@FComponent24')
    return operation
