# Исходные байты рабочих страниц предпросмотра

В записи D3D (слот 6) выделены четыре страницы. При загрузке файла с C000
они попадают в окно банка 4. Из образа берутся исходные байты, вычисленные
позднее значения в файл не подставляются.

| Адреса | Смещение файла | Ресурс |
|---|---|---|
| C800..C8FF | 0800 | [Страница контуров](../Source/D3D/Resources/InitialPreviewContour.bin) |
| C900..C9FF | 0900 | [Старшие байты строк](../Source/D3D/Resources/InitialPreviewRowHigh.bin) |
| CA00..CAFF | 0A00 | [Младшие байты строк](../Source/D3D/Resources/InitialPreviewRowLow.bin) |
| CB00..CBFF | 0B00 | [Байтовые столбцы](../Source/D3D/Resources/InitialPreviewColumn.bin) |

[RenderPreviewInsideFaces](../Source/D3D/RenderPreviewInsideFaces.asm) и
[RenderPreviewClippedFaces](../Source/D3D/RenderPreviewClippedFaces.asm)
копируют пары колонка, строка внутренних граней в C800.
[AppendPreviewClipPoint](../Source/D3D/AppendPreviewClipPoint.asm) и
писатели пересечений дописывают отсечённые пары со смещения ByteCount.
При увеличении младшего байта адрес оборачивается внутри страницы C8.
[FillPreviewPolygon](../Source/D3D/FillPreviewPolygon.asm) использует
пары для обхода рёбер. Исходное содержимое страницы не объявляется
готовым контуром.

[SetupPreviewModel](../Source/D3D/SetupPreviewModel.asm) вызывает
[BuildSpriteLineTable](../Source/Station/BuildSpriteLineTable.asm)
из фиксированной памяти при подключённом банке 4. Построитель заполняет
C900 и CA00 байтами 256 адресов строк и CB00 байтовыми столбцами.
Эти страницы относятся к предпросмотру. Те же CPU-адреса в другом
банке могут иметь самостоятельное назначение.

[Проверка настройки](../Tools/Disasm/Reports/PreviewSetupVerification.json)
исполняет исходный построитель и сверяет все изменённые адреса.
[Проверка пересечений](../Tools/Disasm/Reports/PreviewClipIntersectionsVerification.json)
сверяет страницу C8 и соседние контрольные байты. [Сверка размещения](../Tools/Disasm/Reports/PreviewRenderWorkspaceClassification.json)
подтверждает 1024 дисковых байта. Хвост C7FC..C7FF сохраняется отдельно
с неизвестным назначением. Область CC00..CDAF оформлена в
[адресных страницах отсечения](PreviewClipTablePages.md).
