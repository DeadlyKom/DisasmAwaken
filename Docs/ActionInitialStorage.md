# Исходные байты рабочих областей ACTION

Дисковые байты необходимо отличать от содержимого тех же адресов после исполнения загрузчика и кадрового кода. Ниже перечислены подтверждённые рабочие области в фиксированном банке 2 на этапе ACTION. Файлы сохраняют **исходные байты TRD**, вычисленные значения или FF в образ вместо них не подставляются.

| Физическая область после загрузки | Ресурс в проекте | Писатель и последующее назначение |
| --- | --- | --- |
| 81CC..8BFF | [InitialLinearBufferTail.bin](../Source/Action/Resources/InitialLinearBufferTail.bin) | хвост линейного буфера, ClearWorkBuffer записывает FF перед обычным выводом кадра |
| 8F00..8FFB | [InitialRenderQueuePool.bin](../Source/Action/Resources/InitialRenderQueuePool.bin) | InsertRenderQueue создаёт рабочие узлы, ReadRenderQueue читает их по цепочке |
| 9000..90FF | [InitialClipOutputPage.bin](../Source/Action/Resources/InitialClipOutputPage.bin) | копирование граней и отсечение пишут пары координат для заливки и линий |
| 9100..91FF | [InitialLogarithmLow.bin](../Source/Action/Resources/InitialLogarithmLow.bin) | BuildLogarithmTable создаёт младшие байты таблицы логарифма |
| 9200..92FF | [InitialLogarithmHigh.bin](../Source/Action/Resources/InitialLogarithmHigh.bin) | тот же построитель создаёт старшие байты |
| 9300..93FF | [InitialExponential.bin](../Source/Action/Resources/InitialExponential.bin) | BuildExponentialTable создаёт 256 байтов обратной аппроксимации |
| 9400..94FF | [InitialRowHigh.bin](../Source/Action/Resources/InitialRowHigh.bin) | BuildBitmapTables создаёт HIGH(8000+32*Y) |
| 9500..95FF | [InitialRowLow.bin](../Source/Action/Resources/InitialRowLow.bin) | тот же построитель создаёт LOW(32*Y) |
| 9600..96FF | [InitialColumnByte.bin](../Source/Action/Resources/InitialColumnByte.bin) | тот же построитель создаёт X DIV 8 |
| 9700..97FF | [InitialColumnMask.bin](../Source/Action/Resources/InitialColumnMask.bin) | тот же построитель создаёт 80 >> (X AND 7) |

## Линейный буфер

Полный рабочий буфер 8000..8BFF состоит из 96 строк по 32 байта, 256 пикселей в строке. Байт по адресу A соответствует строке `(A-8000) DIV 32` и группе восьми пикселей с начальным X=`8*((A-8000) AND 31)`, старший бит расположен левее. Это линейная адресация, а не раскладка ULA.

Физический выделенный хвост начинается с байта 12 строки 14, содержит оставшиеся 20 байтов этой строки и все строки 15..95, всего 2612 байтов. Первые 460 исходных дисковых байтов соответствующей области уже входят в отдельно оформленный переносимый код. После переноса они тоже попадают в будущий рабочий буфер, поэтому физическая разметка исходника и поздняя роль адреса не должны смешиваться.

[ClearWorkBuffer](../Source/Action/ClearWorkBuffer.asm) перезаписывает каждый из 3072 байтов значением FF, используя временный SP. [DrawLinearLine](../Source/Action/DrawLinearLine.asm), заливка полигонов и кадровый вывод используют уже рабочий растр. Подтверждённый обычный [UpdateFrame](../Source/Action/UpdateFrame.asm) вызывает очистку перед рисованием. По исходным рисункам байтов не делаются выводы о замысле изображения или ненужности данных.

## Создаваемые таблицы

[InitializeFlight](../Source/ActionBoot/InitializeFlight.asm) вызывает построение экспоненты, логарифма и пиксельных таблиц. Семь страниц по 256 байтов полностью перезаписываются. Геометрические делители читают логарифмические страницы и экспоненту, растеризация и банковые точки используют четыре страницы пиксельной адресации. Начальные ресурсы не являются готовыми математическими таблицами, их нельзя заменить рассчитанными значениями при обратной сборке.

## Области геометрии

[InsertRenderQueue](../Source/Action/InsertRenderQueue.asm) использует 18 мест
по 14 байтов в 8F00..8FFB. При FreeOffset=FC вставка отказывается от создания
узла. Последние четыре байта 8FFC..8FFF входят в авторский резерв
страницы L9D. Они лежат за границей 18 полных узлов.
[Хвост L9D](../Source/Action/Resources/RenderQueuePageTail.bin) ·
[Сверка авторского размещения](../Tools/Disasm/Reports/ActionArchivedWorkspaceVerification.json)

[RenderInsideRecords](../Source/Action/RenderInsideRecords.asm) и
[RenderClippedRecords](../Source/Action/RenderClippedRecords.asm) копируют
внутренние грани на страницу 90. Писатели отсечения размещают там же пары
Second, First, оборачивая младший байт адреса. [PreparePolygonFill](../Source/Action/PreparePolygonFill.asm)
читает число пар из OutputSize. Договоры потребителей описаны отдельно
в [добавлении пересечений](ActionClipIntersections.md) и [очереди граней](ActionRenderQueueInsert.md).
Расширенный профиль [растеризации](ActionLineRaster.md) может писать в обе
страницы по адресам пикселей, поэтому роли не объявлены исключительными.

[Сверка размещения](../Tools/Disasm/Reports/ActionRenderWorkspaceClassification.json)
подтверждает сохранность 508 исходных байтов. Начальные байты этих страниц
могут иметь другие назначения в более ранних фазах, которые этой сверкой
не охвачены.

## Проверка

[CheckActionInitialStorage.py](../Tools/Disasm/Research/CheckActionInitialStorage.py) исполняет исходные очистку и три генератора. Проверены исходный шаблон и заполнения 00, FF, A5. Для всех 3072 байтов растра и 1792 табличных байтов контролируется каждое чтение до первой записи. Таких чтений не оказалось, все адреса перезаписаны, готовые значения совпали с независимыми формулами. [Результат](../Tools/Disasm/Reports/ActionInitialStorageVerification.json).

Это доказательство локальных писателей и роли адресов в ACTION. Порядок первых чтений произвольной другой фазы игры, все косвенные обращения за пределами этих процедур, аппаратные IRQ, сборка и нативный запуск не доказаны. Все 4404 дисковых байта сохранены буквально и сверены [публикацией](../Tools/Disasm/Reports/ActionInitialStorageClassification.json).
