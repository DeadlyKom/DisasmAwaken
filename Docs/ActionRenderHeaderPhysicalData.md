# Двухбайтовый заголовок текущей модели

[RenderHeader.asm](../Source/Action/Data/RenderHeader.asm) оформляет два исходных нулевых байта по 9B8D..9B8E фиксированного банка 2. Их слово уже известно как HeaderWord0. FRenderHeaderState разделяет физические ModeBits по смещению 0 и ModelByteOffset по смещению 1. Новая память не выделяется.

[RenderSceneFrame](../Source/Action/RenderSceneFrame.asm) получает ModelByteOffset из поля модели текущей записи. Затем проверяет Phase0 OR Phase2 и записывает ModeBits=01 при обеих нулевых фазах, иначе 00. После преобразования координат он увеличивает ModelByteOffset на два при неотрицательной глубине ниже `#1F00`. [TransformObjectVertices](../Source/Action/TransformObjectVertices.asm) читает по итоговому смещению слово указателя в таблице OBJECT3D по `#9E00`. [Выбор варианта пары](ActionObjectPointers.md#выбор-варианта-по-глубине)

## Разряды ModeBits

| Биты 7..0 | Маска | Доказанное действие |
|---|---|---|
| 7, 6, 5, 4, 3, 2, 1 | FE | известный производитель записывает нули, рассматриваемые потребители эти биты не проверяют, игровые значения единиц неизвестны |
| 0 | 01 | одна фаза Phase1 вместо общего расчёта трёх фаз |

При ModeBits=00 выбирается общий расчёт. [BuildRenderCoefficients ACTION](../Source/Action/BuildRenderCoefficients.asm) и [его копия 3DPART](../Source/ThreeD/BuildRenderCoefficients.asm) проверяют бит 0 через HL. [ComposeRenderMatrix ACTION](../Source/Action/ComposeRenderMatrix.asm) и [копия 3DPART](../Source/ThreeD/ComposeRenderMatrix.asm) повторяют проверку через IY, включая точные четверти Phase1. IY указывает по 9B8D, числовые IY+0 заменены именем FRenderHeaderState.ModeBits. Аппаратный контекст фиксированного банка 2 общий для обеих копий кода.

HeaderWord0 сохраняется целиком в FActionRenderNode.HeaderWord0 и восстанавливается при чтении очереди. Поэтому два физически разных поля одновременно копируются как одно слово. Порядок байтов и размер снимка не изменены. [Вставка очереди](ActionRenderQueueInsert.md) и [чтение очереди](ActionRenderQueueControl.md) описывают исходные PUSH/POP и восстановление SP.

[Физическое описание](../Tools/Disasm/Research/ActionRenderHeaderPhysicalData.py) и [отчёт](../Tools/Disasm/Reports/ActionRenderHeaderPhysicalDataClassification.json) связывают оба прежних адресных имени ASSERT с реальными полями. Сохранены исходные нули, которые не объявляются постоянными значениями во время игры. Проверки [коэффициентов](ActionRenderCoefficients.md), [композиции](ActionRenderMatrix.md) и [подготовки кадра](ActionRenderFrameSetup.md) отделены от сборки и нативного запуска. Игровой смысл остальных битов не назначается.

Исходные инициализаторы 00, 00 относятся именно к дисковому файлу ACTION. То, что код 3DPART читает тот же фиксированный адрес 9B8D, не доказывает состав RAM при любом его игровом входе. Для этой копии требуется подготовленный рабочий контекст по её договору, последовательность загрузки не выводится из одного совпадения адресов.
