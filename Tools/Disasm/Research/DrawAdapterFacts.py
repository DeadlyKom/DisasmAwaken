"""Подтверждённые двухинструкционные обёртки DrawCenteredItem с изменяемым индексом."""

ENTRIES = (
    (30, 0x7A15),
    (28, 0x7A55),
    (29, 0x7A82),
    (9, 0x7A9E),
    (2, 0x7AB4),
    (3, 0x7B0B),
    (37, 0x7B25),
    (36, 0x7B40),
    (21, 0x7B51),
    (14, 0x7C7E),
    (15, 0x7CB6),
    (18, 0x7CF8),
    (17, 0x7D24),
    (16, 0x7D53),
    (35, 0x7D77),
    (4, 0x7D99),
    (5, 0x7DB5),
    (6, 0x7DE1),
    (7, 0x7E19),
    (8, 0x7F11),
    (33, 0xAA4F),
)

FUNCTIONS = {}
CONTRACTS = {}
COMMENTS = {}
DOCUMENTS = {}
for index, address in ENTRIES:
    name = f"DrawItem{index:02d}"
    FUNCTIONS[address] = (name, f"Обёртка рисования элемента {index} через изменяемый индекс и DrawCenteredItem")
    CONTRACTS['Station', address] = (
        [f"DrawItemState.Index{index:02d} содержит актуальный индекс, исходный загрузчик записывает {index}",
         f"DrawItemState.Opcode{index:02d} равен #21 для работы либо #C9 для отключения",
         "при активном коде в окне #C000 выбрана страница станционного кода, действует полный договор DrawCenteredItem",
         "на CPU-стеке находится адрес возврата вызывающей стороны"],
        [f"при активном коде HL - индекс из DrawItemState.Index{index:02d}, DE и BC сохранены",
         "при активном коде AF - A=#C3, F от последнего текстового прохода общего рисователя",
         "при отключённом коде обычный RET сохраняет все регистры и флаги, включая исходный HL",
         "bitmap, карта владельцев, текстовое окно и рабочие регистры определяются DrawCenteredItem"],
        ["HL, AF, HL', AF'"],
        ["до перехода в общий рисователь сама обёртка меняет только HL, флаги и стек не изменяет",
         "непосредственное слово LD HL первоначально равно нулю в дисковом образе, это изменяемый код",
         "DisableDrawList пишет в первый байт RET, EnableDrawList восстанавливает именно LD HL,nn без изменения слова индекса",
         "индекс записывается исходным циклом #4257..#4275 по DrawHandler+1, поле TextIndex записи не меняется",
         "JP передаёт исходный адрес возврата общему рисователю, дополнительного CALL здесь нет",
         "H', DE', BC', IX, IY, I и IFF сохраняются по договору DrawCenteredItem"])
    COMMENTS[address] = ([f"активный Opcode{index:02d} читает индекс Index{index:02d}, временный RET отключает весь обработчик"], None)
    DOCUMENTS['Station', address] = ('DrawAdapters', 'инициализируемая обёртка рисования')


def name_operands(region, address, operation):
    if region == 'Station' and address in FUNCTIONS:
        return operation.replace('JP #C2DF', 'JP @Station.DrawCenteredItem.Entry')
    return operation
