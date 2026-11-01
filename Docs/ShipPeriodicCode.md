# Периодические входы корабельных панелей

Первичное выделение сохранило 85 исходных байтов и 36 инструкций из трёх двоичных областей. [Исторический отчёт](../Tools/Disasm/Reports/ShipPeriodicCodeClassification.json) фиксирует именно обнаружение кода. Его старые имена Unknown не являются текущим состоянием разбора.

Теперь [TryDrawShipPreview](../Source/Station/TryDrawShipPreview.asm), [DrawShipPreview](../Source/Station/DrawShipPreview.asm), [RefreshShipPanels](../Source/Station/RefreshShipPanels.asm) и [AnimateShipPreview](../Source/Station/AnimateShipPreview.asm) имеют русские контракты и смысловые имена. [Полный разбор](ShipPreviewCallbacks.md) объясняет точное сравнение адреса, алиас с равным индексом, временный RET, порядок панелей, установку периодического callback и оба пути кадра.

Границы D3D сопоставлены действительным полям текстового окна, H=Height-14, L=Width-13. Прежнее описание с переставленными шириной и высотой исправлено, байты не менялись. Восстановлены настоящие IM2-вектор и переход загрузчика, 359 проверенных пробуждений HALT исполняют исходный ISR. Пределы этой модели, выключенная музыка, заблокированное обновление указателя и отсутствие IRQ внутри рисующих цепочек перечислены отдельно, аппаратное подтверждение не подразумевается.

[TryDrawModelDescription](../Source/Station/TryDrawModelDescription.asm) остаётся отдельным условным входом. После RET NZ возможно последовательное продолжение в [DrawModelDescriptionPanel](../Source/Station/DrawModelDescriptionPanel.asm), порядок include (0), (1) сохранён. Список моделей описан в [ModelListPanel](ModelListPanel.md), описание в [DescriptionPanel](DescriptionPanel.md), прокрутка в [DescriptionAction](DescriptionAction.md).

PendingRedraw по 68EB и Selector по 6906 являются операндами AnimateShipPreview. Их подготовка разобрана в [ControlPanelGroups](ControlPanelGroups.md). Пути действий списка моделей 6774, 6780 и 67A9 теперь разобраны в [ShipModelActions](ShipModelActions.md). Полный игровой цикл, музыкальный режим и произвольные аппаратные IRQ не объявляются доказанными.
