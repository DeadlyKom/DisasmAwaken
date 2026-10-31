# Периодические входы корабельных панелей

Из трёх бинарных областей выделены 85 исходных байтов, 36 инструкций. Это дополнение к обнаружению исполняемого кода, полный смысловой разбор зависимых рисователей и вызова #E07F банка 4 пока не завершён. Байты и адреса не изменяются.

[Unknown6870](../Source/Station/Unknown6870.asm) проверяет наличие точного DrawItem26.Entry в списке через TestDrawPointer. При отсутствии выполняется условный RET NZ. При совпадении выполнение последовательно продолжается в [DrawItem26](../Source/Station/DrawItem26.asm), дополнительной инструкции JP в образе нет.

[TryDrawModelDescription](../Source/Station/TryDrawModelDescription.asm) аналогично проверяет DrawModelDescriptionPanel.Entry и при совпадении последовательно входит в [DrawModelDescriptionPanel](../Source/Station/DrawModelDescriptionPanel.asm). Пары включений помечены номерами (0), (1), их перестановка меняет поведение исходного кода.

[Unknown68CC](../Source/Station/Unknown68CC.asm) возвращается при ненулевом ActiveItemState.Active, сохраняя запрос отложенного обновления. На разрешённом пути обнуляет PendingRedraw, начинает экранное обновление, вызывает DrawModelListPanel, затем условное рисование DrawModelDescriptionPanel, переносит элемент DrawItem26 по его индексу в конец списка, вызывает его рисование при наличии и завершает обновление. Это установленный порядок вызовов, а не доказанный полный контракт рисователей.

[Unknown68EA](../Source/Station/Unknown68EA.asm) содержит изменяемый операнд ShipPanelState.PendingRedraw. При ненулевом значении переходит к Unknown68CC. При нуле получает последний рисователь списка и возвращается, если он не равен DrawItem26.Entry. На совпадении начинает обновление, вызывает FillWindowBody, ожидает HALT, выбирает банк 4, передаёт ShipPanelState.Selector в #E07F и возвращает банк станционного кода перед EndScreenUpdate. Аппаратные IRQ и весь алгоритм #E07F ещё требуют отдельного разбора.

В DrawItem26 адрес #68EA записывается как периодический callback. Поле PendingRedraw по #68EB и Selector по #6906 являются операндами этого кода, их исходные адреса сохранены. Подготовка этих байтов описана в [ControlPanelGroups](ControlPanelGroups.md).

[ClassifyShipPeriodicCode](../Tools/Disasm/Research/ClassifyShipPeriodicCode.py) сначала формирует отдельный точечный кандидат, проверяет исходные инструкции и байты, сохраняет историю затронутых файлов. Бинарные дубликаты удаляются только после проверки новой физической разметки и сохранённых копий. Это исследовательский сценарий, он не нужен обычной сборке и не запускает ассемблер. Отчёт [ShipPeriodicCodeClassification](../Tools/Disasm/Reports/ShipPeriodicCodeClassification.json).

Зависимый банк исследован отдельно в [D3DPreview](D3DPreview.md). В #E07F установлен EI перед TogglePreviewFaceFill, поэтому сохранение IFF на пути просмотра нельзя предполагать. Полные контракты этого банка ещё не доказаны.

Панели списка и описания разобраны в [ModelListPanel](ModelListPanel.md), [DescriptionPanel](DescriptionPanel.md). Действие описания и полный путь прокрутки разобраны в [DescriptionAction](DescriptionAction.md). Эти результаты не закрывают неизвестные 68CC/68EA и полный кадр D3D.
