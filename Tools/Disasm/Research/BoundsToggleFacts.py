"""Исходное переключение геометрии и условное продолжение интерактивного действия."""
FUNCTIONS = {
    0xCC2C: ("FinishItemAction", "Условное завершение действия, выбор активации либо переключения геометрии"),
    0xCC30: ("ToggleItemBounds", "Возврат сохранённой геометрии либо установка исходного большого прямоугольника"),
}
DOCUMENTS = {("Station", a): ("BoundsToggle", "смена геометрии и продолжение действия") for a in FUNCTIONS}
LABELS = {("Station", 0xCC4C): "Restore", ("Station", 0xCC67): "CheckHeight"}
CONTRACTS = {
    ("Station", 0xCC2C): (
        ["HL и DE удовлетворяют ActivateItem либо ToggleItemBounds на выбранной ветви, BC сохраняется этими хвостами",
         "AF - Carry прерывает действие, при Carry=0 нулевой A выбирает геометрию, ненулевой активацию",
         "на CPU-стеке лежит адрес возврата исходного действия"],
        ["при входном Carry=1 AF и прочие регистры сохранены, выполнен обычный RET",
         "при Carry=0,A=0 результат соответствует ToggleItemBounds, при A!=0 соответствует ActivateItem"],
        ["на возврате по Carry регистры сохранены, иначе HL, AF, HL', AF', IX согласно выбранному хвосту"],
        ["внутреннее продолжение ActivateInterfaceCallback после условного CALL интерактивного обработчика",
         "AND A очищает Carry перед выбором двух хвостов, Z соответствует входному A",
         "при переходе к хвосту адрес возврата остаётся на стеке, дополнительный CALL не создаётся",
         "договор TrackItemGeometry и ограничения пробуждения HALT разобраны отдельно в TrackGeometry.md"]),
    ("Station", 0xCC30): (
        ["HL - новая обёртка только для отсутствующего в списке DE-индекса, DE - индекс FInterfaceItem",
         "выполняются предусловия MoveItemToTail, четыре текущих и четыре сохранённых поля доступны",
         "стек вмещает динамический FBoundsToggleFrame, значение геометрии интерпретируется как байтовое без валидации"],
        ["HL=входной DE-индекс, DE и BC сохранены, IX - физическое начало выбранной записи",
         "при Width<16 и Height<8 текущие X,Y,Width,Height становятся 6,4,20,10, A=прежний Height,F=#81",
         "иначе текущие поля заменяются SavedX..SavedHeight, A=SavedHeight",
         "на восстановлении F=(F_compare AND #C4) OR (SavedHeight AND #28) OR 1, Compare относится к Width-16 либо Height-8",
         "InterfaceState.EventEnabled=0, обработчик перенесён в конец списка до изменения геометрии"],
        ["HL, AF, IX"],
        ["альтернативные регистры, IY, I и IFF сохраняются, SP восстанавливается",
         "Saved-поля и остальные двенадцать байтов записи сохраняются, проверки знаковых координат и размеров нет",
         "сравнение Height выполняется только при Width<16, любой другой размер выбирает восстановление",
         "большой прямоугольник задан исходными байтами, нового размещения данных не вводится",
         "FBoundsToggleFrame содержит WorkspaceIndex, SavedIndex, ReturnAddress, первое слово снимается до умножения индекса",
         "карта владельцев и пиксели здесь не обновляются, EventEnabled=0 запрашивает последующее перестроение"]),
}
COMMENTS = {
    0xCC2C: ([], "выход, если предыдущее действие вернуло Carry, передать его AF вызывающему коду"),
    0xCC2D: (["проверка результата действия по A с очисткой Carry перед выбором хвоста"], None),
    0xCC2E: ([], "переход, если A ненулевой, установить активный элемент и callback"),
    0xCC30: (["запрос перестроения интерфейса и запрет событий до него"], None),
    0xCC34: (["создание FBoundsToggleFrame.SavedIndex и временного WorkspaceIndex из DE"], None),
    0xCC36: (["перенос обработчика выбранного индекса до изменения геометрии"], None),
    0xCC39: (["извлечение WorkspaceIndex в HL, выбранный обработчик MoveItemToTail больше не нужен"], None),
    0xCC3A: (["расчёт байтового смещения записи как 16*индекс по модулю 65536"], None),
    0xCC3E: (["перенос смещения в DE и сохранение исходного индекса в выходном HL"], None),
    0xCC3F: (["расчёт IX как физического адреса FInterfaceItem с исходным смещением"], None),
    0xCC45: (["проверка текущей ширины на порог 16, большие значения выбирают сохранённую геометрию"], None),
    0xCC4A: ([], "переход, если Width меньше 16, проверить порог Height"),
    0xCC4C: (["восстановление четырёх текущих полей из физического сохранённого прямоугольника"], None),
    0xCC64: (["восстановление DE-индекса и установка Carry, S,Z,P/V остаются от сравнения размера"], None),
    0xCC67: (["проверка высоты только у записей с шириной меньше 16"], None),
    0xCC6C: ([], "переход, если Height не меньше 8, восстановить сохранённый прямоугольник"),
    0xCC6E: (["установка исходного большого прямоугольника 6,4,20,10 без изменения Saved-полей"], None),
    0xCC7E: (["восстановление DE-индекса, Carry=1, остальные значимые флаги от Height-8"], None),
}


def name_operands(region, address, operation):
    if region != "Station" or address not in FUNCTIONS:
        return operation
    if address == 0xCC30:
        operation = operation.replace("LD IX, #F0FD", "LD IX, @StationState.Items")
        operation = operation.replace("CP #10", "CP @BoundsToggleConst.WidthLimit").replace("CP #08", "CP @BoundsToggleConst.HeightLimit")
        for field, value, name in (("X", 6, "ExpandedX"), ("Y", 4, "ExpandedY"), ("Width", 20, "ExpandedWidth"), ("Height", 10, "ExpandedHeight")):
            offset = ("X", "Y", "Width", "Height").index(field)
            operation = operation.replace(f"LD (IX + #{offset:02X}), #{value:02X}", f"LD (IX + FInterfaceItem.{field}), @BoundsToggleConst.{name}")
        fields = {0: "X", 1: "Y", 2: "Width", 3: "Height", 8: "SavedX", 9: "SavedY", 10: "SavedWidth", 11: "SavedHeight"}
        for value, name in fields.items():
            operation = operation.replace(f"(IX + #{value:02X})", f"(IX + FInterfaceItem.{name})")
    return operation
