# Числители пересечений ACTION

Две рабочие точки оформлены физическими экземплярами FRenderProjectedPoint, [FirstPoint по CF0B](../Source/Action/Data/ClipFirstPoint.asm) и [SecondPoint по CF1B](../Source/Action/Data/ClipSecondPoint.asm). Поля Second и First имеют по два байта, ClipCode один байт. Все десять исходных байтов равны нулю, нулевой ClipCode здесь означает ещё не подготовленное состояние, а не код внутренней точки F0. Соседние байты страниц таблицы не объединяются с этими записями. [Проверка публикации](../Tools/Disasm/Reports/ActionClipPointsDataClassification.json) сохраняет размер, значения и привязки полей.

[ComputeTopClipProduct](../Source/Action/ComputeTopClipProduct.asm), вход C477, формула (First.First-0)*(First.Second-Second.Second), слот CF37.

[ComputeBottomClipProduct](../Source/Action/ComputeBottomClipProduct.asm), вход C496, формула (First.First-95)*(First.Second-Second.Second), слот CF33.

[ComputeLeftClipProduct](../Source/Action/ComputeLeftClipProduct.asm), вход C4B5, формула (First.First-Second.First)*(First.Second-0), слот CF2F.

[ComputeRightClipProduct](../Source/Action/ComputeRightClipProduct.asm), вход C4D4, формула (First.First-Second.First)*(First.Second-255), слот CF2B.

Все разности оборачиваются до 16 бит. Первый операнд MultiplySigned16 является первой разностью в формуле, второй второй, порядок нельзя менять из-за исходного исключения 8000. Обе операции вычитания отдельно очищают Carry. Результат хранится как FClipProduct, младшее слово по смещению 0 и старшее по 2. Именованные адреса указывают существующие runtime-слоты, новая RAM не выделяется. Четыре исходных слота оформлены [физическими экземплярами FClipProduct](../Source/Action/Data/ClipProducts.asm), правый, левый, нижний и верхний в исходном порядке. Все 16 исходных байтов равны нулю, их точные значения и 12 символьных привязок сверяются без сборки.

[Проверка](../Tools/Disasm/Research/CheckActionClipProducts.py) исполняет настоящие инструкции и дочернее умножение. [Отчёт](../Tools/Disasm/Reports/ActionClipProductsVerification.json) содержит 16560 сценариев, по 4140 на вход. Проверены границы координат, 4096 смешанных наборов на вход и восемь исполнений исключения второго операнда 8000. Сверяются точные регистры и флаги кроме R, вся физическая RAM и кратность записей, включая четыре байта дополнительного CPU-стека. Исходные точки и остальные слоты сохраняются.

На выходе HL содержит старшее слово, DE младшее, BC/AF/IX соответствуют точному договору [MultiplySigned16](./ActionSignedMultiply.md). Альтернативный набор, IY, I, IM, IFF и paging сохраняются. SP после RET увеличен на два. Все совместные входы, R и время, IRQ, сборка и нативный запуск не доказаны. Полный алгоритм отсечения не следует из проверки этих четырёх числителей.
