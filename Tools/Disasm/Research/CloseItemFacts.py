"""Закрытие активного элемента и договор вызываемого внешнего callback."""
FUNCTIONS = {0x9E77: ("CloseActiveItem", "Закрытие активного элемента, перенос в конец списка и вызов завершающего callback")}
DOCUMENTS = {("Station", 0x9E77): ("ActiveItem", "закрытие и callback активного элемента")}
LABELS = {}
CONTRACTS = {("Station", 0x9E77): (
    ["ActiveItemState.Active=0 означает отсутствие активного элемента, ненулевой байт разрешает закрытие",
     "при активности HL используется как новая обёртка только если MoveItemToTail не найдёт ActiveItemState.Index",
     "активный индекс и таблицы удовлетворяют MoveItemToTail и ToggleItemFrame, HALT получает корректное пробуждение",
     "ActiveItemState.Callback содержит возвращающийся по CPU-стеку callback, сохраняющий стек и доступность кода закрытия"],
    ["при отсутствии активности AF=#0054, все остальные основные, альтернативные и индексные регистры сохранены",
     "при активности HL и DE восстановлены поверх результата callback, BC и прочие регистры остаются от callback",
     "при активности A от callback, F=(F_callback AND #C4) OR (A_callback AND #28) OR 1",
     "активность сброшена до callback, его адрес после возврата заменён EmptyCallback"],
    ["при активности BC, AF, HL', DE', BC', AF', IX, IY согласно результату callback, без активности только AF"],
    ["перед callback MoveItemToTail возвращает выбранный HL, DE загружен активным индексом, BC сохранён",
     "после ToggleItemFrame XOR A подготавливает AF=#0044 для callback, до него индекс уже перенесён в конец списка",
     "FActiveCloseFrame содержит SavedHL, SavedDE, ReturnAddress, callback получает собственный адрес возврата поверх кадра",
     "изменение активности самим callback не отменяется, после него сбрасывается только адрес Callback",
     "сами инструкции закрытия не меняют I и IFF, итог зависит от callback и фактического ISR",
     "SP восстанавливается при соблюдении договора callback, произвольные реальные callback этим разбором не признаны проверенными"])}
COMMENTS = {
    0x9E77: (["чтение целого байта активности из изменяемого операнда LD A"], None),
    0x9E79: (["проверка наличия активного элемента, ноль запрещает любые действия закрытия"], None),
    0x9E7A: ([], "выход, если активного элемента нет, вернуть AF=#0054"),
    0x9E7B: (["сохранение входных DE и HL в динамическом FActiveCloseFrame"], None),
    0x9E7D: (["чтение активного индекса из изменяемого операнда LD DE"], None),
    0x9E80: (["поиск активного индекса и перенос его обработчика в конец списка"], None),
    0x9E83: (["переключение контура активного элемента, если бит 4 не запрещает действие"], None),
    0x9E86: (["сброс активности до вызова callback, его входной AF становится #0044"], None),
    0x9E8A: (["вызов изменяемого ActiveItemState.Callback, исходная цель EmptyCallback"], None),
    0x9E8D: (["сброс цели callback после его нормального возврата, повторное завершение не вызывает прежнюю цель"], None),
    0x9E93: (["восстановление входных HL и DE поверх произвольного результата callback"], None),
    0x9E95: (["установка Carry как признака выполненного закрытия, A и S,Z,P/V остаются от callback"], None),
}


def name_operands(region, address, operation):
    if region != "Station":
        return operation
    for value, name in ((0x9E78, "Active"), (0x9E7E, "Index"), (0x9E8B, "Callback"), (0xCCA4, "NextCallback")):
        operation = operation.replace(f"(#{value:04X})", f"(@ActiveItemState.{name})")
    if address == 0x9E77:
        operation = operation.replace("LD HL, #9A58", "LD HL, @Station.EmptyCallback.Entry")
    return operation
