# Хвостовые обёртки наведения списков

Четыре трёхбайтовые процедуры содержат по одному исходному JP. Они не создают новый CPU-кадр, не сохраняют регистры и передают внешний адрес возврата непосредственно получателю. Их In, Out и Corrupt совпадают с договором соответствующего получателя, включая все ошибки попадания и побочные эффекты XOR-полосы.

| Обёртка | Адрес | Получатель |
|---|---|---|
| [HandleShipListHover](../Source/Station/HandleShipListHover.asm) | `#6771` | [UpdateShipListHover](../Source/Station/UpdateShipListHover.asm) |
| [HandleHelpIndexHover](../Source/Station/HandleHelpIndexHover.asm) | `#69DD` | [UpdateIndexListHover](../Source/Station/UpdateIndexListHover.asm) |
| [HandleSaveSlotHover](../Source/Station/HandleSaveSlotHover.asm) | `#741E` | [UpdateToPositionHover](../Source/Station/UpdateToPositionHover.asm) |
| [HandleLoadSlotHover](../Source/Station/HandleLoadSlotHover.asm) | `#74A7` | [UpdateFromPositionHover](../Source/Station/UpdateFromPositionHover.asm) |

У моделей старший операнд запроса строк меняется через `ModelListState.HoverRows`. У разделов справки `HelpPanelState.VisibleTitles` записывается [DrawHelpContents](../Source/Station/DrawHelpContents.asm). Исходное значение 30 не является постоянным ограничением во время исполнения. Младшие отступы равны 27 и 11 пикселям соответственно.

В двух списках сохранения D=40 передаётся как пиксельная высота, E=3 как отступ. Этот путь использует UpdatePixelHover и не заменяется строчным ограничением геометрии. Договоры [PanelHover](PanelHover.md) и [SaveSlots](SaveSlots.md) описывают точные проверки указателя и отложенные дисковые действия.

[CheckListHoverAdapters.py](../Tools/Disasm/Research/CheckListHoverAdapters.py) сравнивает исполнение обёртки и прямого получателя на одинаковой подготовленной памяти. Проверены 448 пар запусков, для моделей и справки числа строк 0, 1, 2, 30, 31, FF, восемь положений Y, прежняя строка 0 либо FF и точный рисователь на последней либо предпоследней позиции. Сверены основные, альтернативные и индексные регистры, все восемь банков памяти и записи портов. [Отчёт](../Tools/Disasm/Reports/ListHoverAdaptersVerification.json).

Это проверка эквивалентности обёрток с настоящими помощниками, независимый алгоритм всего bitmap здесь не вычисляется. Прерывания, сборка и нативная игра не выполнялись.
