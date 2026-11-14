# Точная копия 3DPART

Логические 8224 байта записи 19 полностью совпадают с ACTION, смещения 6000..801F. Секторный хвост 224 байта сохранён отдельно. [Проверка](../Tools/Disasm/Research/CheckThreeDOverlayMirror.py) сравнивает фактические байты и проверяет отсутствие непонятных ручных комментариев до публикации.

121 контракт перенесён при одинаковых внешней RAM, загруженном банке 0 и состояниях входа. Общие внешние процедуры вне файла сохраняют ссылки ACTION. По CF08 обе копии содержат три младших байта указателей, возможный вход исполнения остаётся отдельной гипотезой. [Исходная разметка и прежние частичные контракты](../Tools/Disasm/Reports/ThreeDOverlayMirrorVerification.json)

Поля RAM и константы из Includes общие для одинакового адресного пространства. Физические блоки этой копии имеют отдельные метки ThreeDClipPoints, ThreeDClipProductsData, ThreeDLineMasks и [ThreeDClipDispatchPrefix](ClipDispatchPrefixData.md). Новые адреса и области памяти не выделяются.

В обеих дисковых копиях установлено происхождение трёх промежутков.

| Адреса | Авторское размещение |
|---|---|
| `#CEE3..#CEFF` | `CLIPMATR.a` применяет `ADRXX00` перед младшей страницей `L95` |
| `#D194..#D1BF` | `3D-II.a` задаёт начало развёрнутого пролёта на смещении `#C0` той же страницы |
| `#E009..#E00F` | `3D-II.a` выравнивает `MASKS` до границы 16 байтов |

Байты промежутков и соседние команды сопоставлены с 3DPART из
`awk1.trd`. Ссылки на те же числовые адреса в других банках
описывают отдельные обращения. Например, вызов `#CEFA` использует
CONTROL0 банка 1, а запись по `#D1BA` относится к OBJECT3D банка 4.
[Авторский архив](https://opensourcezx.untergrund.net/a_games-awaken_src.html) ·
[Сверка двух копий и авторских директив](../Tools/Disasm/Reports/ActionArchivedLayoutVerification.json)

## Процедуры

| Адрес | Копия | Первичный разбор |
| --- | --- | --- |
| C000 | [ClipPolygon](../Source/ThreeD/ClipPolygon.asm) | [ClipPolygon](../Source/Action/ClipPolygon.asm) |
| C071 | [ContinueClipPolygon](../Source/ThreeD/ContinueClipPolygon.asm) | [ContinueClipPolygon](../Source/Action/ContinueClipPolygon.asm) |
| C07A | [ReturnClipCase](../Source/ThreeD/ReturnClipCase.asm) | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| C07B | [ClipInsideToBottomRight](../Source/ThreeD/ClipInsideToBottomRight.asm) | [ClipInsideToBottomRight](../Source/Action/ClipInsideToBottomRight.asm) |
| C08A | [ClipRightToBottomRight](../Source/ThreeD/ClipRightToBottomRight.asm) | [ClipRightToBottomRight](../Source/Action/ClipRightToBottomRight.asm) |
| C095 | [ClipInsideToBottomLeft](../Source/ThreeD/ClipInsideToBottomLeft.asm) | [ClipInsideToBottomLeft](../Source/Action/ClipInsideToBottomLeft.asm) |
| C0A4 | [ClipBottomToBottomLeft](../Source/ThreeD/ClipBottomToBottomLeft.asm) | [ClipBottomToBottomLeft](../Source/Action/ClipBottomToBottomLeft.asm) |
| C0AF | [ClipInsideToTopRight](../Source/ThreeD/ClipInsideToTopRight.asm) | [ClipInsideToTopRight](../Source/Action/ClipInsideToTopRight.asm) |
| C0BE | [ClipTopToTopRight](../Source/ThreeD/ClipTopToTopRight.asm) | [ClipTopToTopRight](../Source/Action/ClipTopToTopRight.asm) |
| C0C9 | [ClipInsideToTopLeft](../Source/ThreeD/ClipInsideToTopLeft.asm) | [ClipInsideToTopLeft](../Source/Action/ClipInsideToTopLeft.asm) |
| C0D8 | [ClipLeftToTopLeft](../Source/ThreeD/ClipLeftToTopLeft.asm) | [ClipLeftToTopLeft](../Source/Action/ClipLeftToTopLeft.asm) |
| C0E3 | [ClipRightToInside](../Source/ThreeD/ClipRightToInside.asm) | [ClipRightToInside](../Source/Action/ClipRightToInside.asm) |
| C0E9 | [ClipRightToLeft](../Source/ThreeD/ClipRightToLeft.asm) | [ClipRightToLeft](../Source/Action/ClipRightToLeft.asm) |
| C0EF | [ClipRightToBottom](../Source/ThreeD/ClipRightToBottom.asm) | [ClipRightToBottom](../Source/Action/ClipRightToBottom.asm) |
| C101 | [ClipRightToBottomLeft](../Source/ThreeD/ClipRightToBottomLeft.asm) | [ClipRightToBottomLeft](../Source/Action/ClipRightToBottomLeft.asm) |
| C119 | [ClipRightToTop](../Source/ThreeD/ClipRightToTop.asm) | [ClipRightToTop](../Source/Action/ClipRightToTop.asm) |
| C12B | [ClipRightToTopRight](../Source/ThreeD/ClipRightToTopRight.asm) | [ClipRightToTopRight](../Source/Action/ClipRightToTopRight.asm) |
| C132 | [ClipRightToTopLeft](../Source/ThreeD/ClipRightToTopLeft.asm) | [ClipRightToTopLeft](../Source/Action/ClipRightToTopLeft.asm) |
| C144 | [ClipLeftToInside](../Source/ThreeD/ClipLeftToInside.asm) | [ClipLeftToInside](../Source/Action/ClipLeftToInside.asm) |
| C14A | [ClipLeftToRight](../Source/ThreeD/ClipLeftToRight.asm) | [ClipLeftToRight](../Source/Action/ClipLeftToRight.asm) |
| C150 | [ClipLeftToBottom](../Source/ThreeD/ClipLeftToBottom.asm) | [ClipLeftToBottom](../Source/Action/ClipLeftToBottom.asm) |
| C162 | [ClipLeftToBottomRight](../Source/ThreeD/ClipLeftToBottomRight.asm) | [ClipLeftToBottomRight](../Source/Action/ClipLeftToBottomRight.asm) |
| C174 | [ClipLeftToBottomLeft](../Source/ThreeD/ClipLeftToBottomLeft.asm) | [ClipLeftToBottomLeft](../Source/Action/ClipLeftToBottomLeft.asm) |
| C17B | [ClipLeftToTop](../Source/ThreeD/ClipLeftToTop.asm) | [ClipLeftToTop](../Source/Action/ClipLeftToTop.asm) |
| C18D | [ClipLeftToTopRight](../Source/ThreeD/ClipLeftToTopRight.asm) | [ClipLeftToTopRight](../Source/Action/ClipLeftToTopRight.asm) |
| C1A5 | [ClipBottomToInside](../Source/ThreeD/ClipBottomToInside.asm) | [ClipBottomToInside](../Source/Action/ClipBottomToInside.asm) |
| C1AB | [ClipBottomToRight](../Source/ThreeD/ClipBottomToRight.asm) | [ClipBottomToRight](../Source/Action/ClipBottomToRight.asm) |
| C1BD | [ClipBottomToLeft](../Source/ThreeD/ClipBottomToLeft.asm) | [ClipBottomToLeft](../Source/Action/ClipBottomToLeft.asm) |
| C1CF | [ClipBottomToBottomRight](../Source/ThreeD/ClipBottomToBottomRight.asm) | [ClipBottomToBottomRight](../Source/Action/ClipBottomToBottomRight.asm) |
| C1D6 | [ClipBottomToTop](../Source/ThreeD/ClipBottomToTop.asm) | [ClipBottomToTop](../Source/Action/ClipBottomToTop.asm) |
| C1DC | [ClipBottomToTopRight](../Source/ThreeD/ClipBottomToTopRight.asm) | [ClipBottomToTopRight](../Source/Action/ClipBottomToTopRight.asm) |
| C1F1 | [ClipBottomToTopLeft](../Source/ThreeD/ClipBottomToTopLeft.asm) | [ClipBottomToTopLeft](../Source/Action/ClipBottomToTopLeft.asm) |
| C20C | [ClipBottomRightToInside](../Source/ThreeD/ClipBottomRightToInside.asm) | [ClipBottomRightToInside](../Source/Action/ClipBottomRightToInside.asm) |
| C228 | [ClipBottomRightToRight](../Source/ThreeD/ClipBottomRightToRight.asm) | [ClipBottomRightToRight](../Source/Action/ClipBottomRightToRight.asm) |
| C22F | [ClipBottomRightToLeft](../Source/ThreeD/ClipBottomRightToLeft.asm) | [ClipBottomRightToLeft](../Source/Action/ClipBottomRightToLeft.asm) |
| C24E | [ClipBottomRightToBottom](../Source/ThreeD/ClipBottomRightToBottom.asm) | [ClipBottomRightToBottom](../Source/Action/ClipBottomRightToBottom.asm) |
| C259 | [ClipBottomRightToBottomLeft](../Source/ThreeD/ClipBottomRightToBottomLeft.asm) | [ClipBottomRightToBottomLeft](../Source/Action/ClipBottomRightToBottomLeft.asm) |
| C25F | [ClipBottomRightToTop](../Source/ThreeD/ClipBottomRightToTop.asm) | [ClipBottomRightToTop](../Source/Action/ClipBottomRightToTop.asm) |
| C274 | [ClipBottomRightToTopLeft](../Source/ThreeD/ClipBottomRightToTopLeft.asm) | [ClipBottomRightToTopLeft](../Source/Action/ClipBottomRightToTopLeft.asm) |
| C28D | [ClipBottomLeftToInside](../Source/ThreeD/ClipBottomLeftToInside.asm) | [ClipBottomLeftToInside](../Source/Action/ClipBottomLeftToInside.asm) |
| C2A9 | [ClipBottomLeftToRight](../Source/ThreeD/ClipBottomLeftToRight.asm) | [ClipBottomLeftToRight](../Source/Action/ClipBottomLeftToRight.asm) |
| C2BE | [ClipBottomLeftToLeft](../Source/ThreeD/ClipBottomLeftToLeft.asm) | [ClipBottomLeftToLeft](../Source/Action/ClipBottomLeftToLeft.asm) |
| C2C9 | [ClipBottomLeftToBottom](../Source/ThreeD/ClipBottomLeftToBottom.asm) | [ClipBottomLeftToBottom](../Source/Action/ClipBottomLeftToBottom.asm) |
| C2D0 | [ClipBottomLeftToTop](../Source/ThreeD/ClipBottomLeftToTop.asm) | [ClipBottomLeftToTop](../Source/Action/ClipBottomLeftToTop.asm) |
| C2EF | [ClipBottomLeftToTopRight](../Source/ThreeD/ClipBottomLeftToTopRight.asm) | [ClipBottomLeftToTopRight](../Source/Action/ClipBottomLeftToTopRight.asm) |
| C308 | [ClipBottomLeftToTopLeft](../Source/ThreeD/ClipBottomLeftToTopLeft.asm) | [ClipBottomLeftToTopLeft](../Source/Action/ClipBottomLeftToTopLeft.asm) |
| C30E | [ClipTopToInside](../Source/ThreeD/ClipTopToInside.asm) | [ClipTopToInside](../Source/Action/ClipTopToInside.asm) |
| C314 | [ClipTopToRight](../Source/ThreeD/ClipTopToRight.asm) | [ClipTopToRight](../Source/Action/ClipTopToRight.asm) |
| C326 | [ClipTopToLeft](../Source/ThreeD/ClipTopToLeft.asm) | [ClipTopToLeft](../Source/Action/ClipTopToLeft.asm) |
| C338 | [ClipTopToBottom](../Source/ThreeD/ClipTopToBottom.asm) | [ClipTopToBottom](../Source/Action/ClipTopToBottom.asm) |
| C33E | [ClipTopToBottomRight](../Source/ThreeD/ClipTopToBottomRight.asm) | [ClipTopToBottomRight](../Source/Action/ClipTopToBottomRight.asm) |
| C359 | [ClipTopToBottomLeft](../Source/ThreeD/ClipTopToBottomLeft.asm) | [ClipTopToBottomLeft](../Source/Action/ClipTopToBottomLeft.asm) |
| C36E | [ClipTopToTopLeft](../Source/ThreeD/ClipTopToTopLeft.asm) | [ClipTopToTopLeft](../Source/Action/ClipTopToTopLeft.asm) |
| C375 | [ClipTopRightToInside](../Source/ThreeD/ClipTopRightToInside.asm) | [ClipTopRightToInside](../Source/Action/ClipTopRightToInside.asm) |
| C391 | [ClipTopRightToRight](../Source/ThreeD/ClipTopRightToRight.asm) | [ClipTopRightToRight](../Source/Action/ClipTopRightToRight.asm) |
| C39C | [ClipTopRightToLeft](../Source/ThreeD/ClipTopRightToLeft.asm) | [ClipTopRightToLeft](../Source/Action/ClipTopRightToLeft.asm) |
| C3B1 | [ClipTopRightToBottom](../Source/ThreeD/ClipTopRightToBottom.asm) | [ClipTopRightToBottom](../Source/Action/ClipTopRightToBottom.asm) |
| C3D0 | [ClipTopRightToBottomRight](../Source/ThreeD/ClipTopRightToBottomRight.asm) | [ClipTopRightToBottomRight](../Source/Action/ClipTopRightToBottomRight.asm) |
| C3D6 | [ClipTopRightToBottomLeft](../Source/ThreeD/ClipTopRightToBottomLeft.asm) | [ClipTopRightToBottomLeft](../Source/Action/ClipTopRightToBottomLeft.asm) |
| C3EF | [ClipTopRightToTop](../Source/ThreeD/ClipTopRightToTop.asm) | [ClipTopRightToTop](../Source/Action/ClipTopRightToTop.asm) |
| C3F6 | [ClipTopLeftToInside](../Source/ThreeD/ClipTopLeftToInside.asm) | [ClipTopLeftToInside](../Source/Action/ClipTopLeftToInside.asm) |
| C412 | [ClipTopLeftToRight](../Source/ThreeD/ClipTopLeftToRight.asm) | [ClipTopLeftToRight](../Source/Action/ClipTopLeftToRight.asm) |
| C431 | [ClipTopLeftToLeft](../Source/ThreeD/ClipTopLeftToLeft.asm) | [ClipTopLeftToLeft](../Source/Action/ClipTopLeftToLeft.asm) |
| C438 | [ClipTopLeftToBottom](../Source/ThreeD/ClipTopLeftToBottom.asm) | [ClipTopLeftToBottom](../Source/Action/ClipTopLeftToBottom.asm) |
| C44D | [ClipTopLeftToBottomRight](../Source/ThreeD/ClipTopLeftToBottomRight.asm) | [ClipTopLeftToBottomRight](../Source/Action/ClipTopLeftToBottomRight.asm) |
| C466 | [ClipTopLeftToTop](../Source/ThreeD/ClipTopLeftToTop.asm) | [ClipTopLeftToTop](../Source/Action/ClipTopLeftToTop.asm) |
| C471 | [ClipTopLeftToTopRight](../Source/ThreeD/ClipTopLeftToTopRight.asm) | [ClipTopLeftToTopRight](../Source/Action/ClipTopLeftToTopRight.asm) |
| C477 | [ComputeTopClipProduct](../Source/ThreeD/ComputeTopClipProduct.asm) | [ComputeTopClipProduct](../Source/Action/ComputeTopClipProduct.asm) |
| C496 | [ComputeBottomClipProduct](../Source/ThreeD/ComputeBottomClipProduct.asm) | [ComputeBottomClipProduct](../Source/Action/ComputeBottomClipProduct.asm) |
| C4B5 | [ComputeLeftClipProduct](../Source/ThreeD/ComputeLeftClipProduct.asm) | [ComputeLeftClipProduct](../Source/Action/ComputeLeftClipProduct.asm) |
| C4D4 | [ComputeRightClipProduct](../Source/ThreeD/ComputeRightClipProduct.asm) | [ComputeRightClipProduct](../Source/Action/ComputeRightClipProduct.asm) |
| C4F3 | [ClipInsideToTop](../Source/ThreeD/ClipInsideToTop.asm) | [ClipInsideToTop](../Source/Action/ClipInsideToTop.asm) |
| C4F6 | [AppendTopClipIntersection](../Source/ThreeD/AppendTopClipIntersection.asm) | [AppendTopClipIntersection](../Source/Action/AppendTopClipIntersection.asm) |
| C53D | [ClipInsideToBottom](../Source/ThreeD/ClipInsideToBottom.asm) | [ClipInsideToBottom](../Source/Action/ClipInsideToBottom.asm) |
| C540 | [AppendBottomClipIntersection](../Source/ThreeD/AppendBottomClipIntersection.asm) | [AppendBottomClipIntersection](../Source/Action/AppendBottomClipIntersection.asm) |
| C588 | [ClipInsideToLeft](../Source/ThreeD/ClipInsideToLeft.asm) | [ClipInsideToLeft](../Source/Action/ClipInsideToLeft.asm) |
| C58B | [AppendLeftClipIntersection](../Source/ThreeD/AppendLeftClipIntersection.asm) | [AppendLeftClipIntersection](../Source/Action/AppendLeftClipIntersection.asm) |
| C5E4 | [ClipInsideToRight](../Source/ThreeD/ClipInsideToRight.asm) | [ClipInsideToRight](../Source/Action/ClipInsideToRight.asm) |
| C5E7 | [AppendRightClipIntersection](../Source/ThreeD/AppendRightClipIntersection.asm) | [AppendRightClipIntersection](../Source/Action/AppendRightClipIntersection.asm) |
| C641 | [AppendTopLeftClipCorner](../Source/ThreeD/AppendTopLeftClipCorner.asm) | [AppendTopLeftClipCorner](../Source/Action/AppendTopLeftClipCorner.asm) |
| C64C | [AppendTopRightClipCorner](../Source/ThreeD/AppendTopRightClipCorner.asm) | [AppendTopRightClipCorner](../Source/Action/AppendTopRightClipCorner.asm) |
| C657 | [AppendBottomLeftClipCorner](../Source/ThreeD/AppendBottomLeftClipCorner.asm) | [AppendBottomLeftClipCorner](../Source/Action/AppendBottomLeftClipCorner.asm) |
| C662 | [AppendBottomRightClipCorner](../Source/ThreeD/AppendBottomRightClipCorner.asm) | [AppendBottomRightClipCorner](../Source/Action/AppendBottomRightClipCorner.asm) |
| C66D | [CompareTopLeftProducts](../Source/ThreeD/CompareTopLeftProducts.asm) | [CompareTopLeftProducts](../Source/Action/CompareTopLeftProducts.asm) |
| C681 | [CompareTopRightProducts](../Source/ThreeD/CompareTopRightProducts.asm) | [CompareTopRightProducts](../Source/Action/CompareTopRightProducts.asm) |
| C695 | [CompareBottomLeftProducts](../Source/ThreeD/CompareBottomLeftProducts.asm) | [CompareBottomLeftProducts](../Source/Action/CompareBottomLeftProducts.asm) |
| C6A9 | [CompareBottomRightProducts](../Source/ThreeD/CompareBottomRightProducts.asm) | [CompareBottomRightProducts](../Source/Action/CompareBottomRightProducts.asm) |
| C6BD | [ComputeSecondAxisDelta](../Source/ThreeD/ComputeSecondAxisDelta.asm) | [ComputeSecondAxisDelta](../Source/Action/ComputeSecondAxisDelta.asm) |
| C6C8 | [ComputeFirstAxisDelta](../Source/ThreeD/ComputeFirstAxisDelta.asm) | [ComputeFirstAxisDelta](../Source/Action/ComputeFirstAxisDelta.asm) |
| C6D3 | [AppendSecondClipPoint](../Source/ThreeD/AppendSecondClipPoint.asm) | [AppendSecondClipPoint](../Source/Action/AppendSecondClipPoint.asm) |
| C6EA | [ExitClipContour](../Source/ThreeD/ExitClipContour.asm) | [ExitClipContour](../Source/Action/ExitClipContour.asm) |
| C6F4 | [MultiplySigned16](../Source/ThreeD/MultiplySigned16.asm) | [MultiplySigned16](../Source/Action/MultiplySigned16.asm) |
| C88C | [DivideSigned32To16](../Source/ThreeD/DivideSigned32To16.asm) | [DivideSigned32To16](../Source/Action/DivideSigned32To16.asm) |
| C941 | [ClipSingleEdge](../Source/ThreeD/ClipSingleEdge.asm) | [ClipSingleEdge](../Source/Action/ClipSingleEdge.asm) |
| C99B | [BuildRenderCoefficients](../Source/ThreeD/BuildRenderCoefficients.asm) | [BuildRenderCoefficients](../Source/Action/BuildRenderCoefficients.asm) |
| CB23 | [ComposeRenderMatrix](../Source/ThreeD/ComposeRenderMatrix.asm) | [ComposeRenderMatrix](../Source/Action/ComposeRenderMatrix.asm) |
| D10A | [ClearWorkBuffer](../Source/ThreeD/ClearWorkBuffer.asm) | [ClearWorkBuffer](../Source/Action/ClearWorkBuffer.asm) |
| D12C | [MultiplySignedScaled](../Source/ThreeD/MultiplySignedScaled.asm) | [MultiplySignedScaled](../Source/Action/MultiplySignedScaled.asm) |
| D1C0 | [PolygonFillRows](../Source/ThreeD/PolygonFillRows.asm) | [PolygonFillRows](../Source/Action/PolygonFillRows.asm) |
| D268 | [SelectPolygonRightEdge](../Source/ThreeD/SelectPolygonRightEdge.asm) | [SelectPolygonRightEdge](../Source/Action/SelectPolygonRightEdge.asm) |
| D26B | [WrapPolygonLeftEdge](../Source/ThreeD/WrapPolygonLeftEdge.asm) | [WrapPolygonLeftEdge](../Source/Action/WrapPolygonLeftEdge.asm) |
| D272 | [UpdatePolygonLeftEdge](../Source/ThreeD/UpdatePolygonLeftEdge.asm) | [UpdatePolygonLeftEdge](../Source/Action/UpdatePolygonLeftEdge.asm) |
| D3A8 | [WrapPolygonRightEdge](../Source/ThreeD/WrapPolygonRightEdge.asm) | [WrapPolygonRightEdge](../Source/Action/WrapPolygonRightEdge.asm) |
| D3AD | [UpdatePolygonRightEdge](../Source/ThreeD/UpdatePolygonRightEdge.asm) | [UpdatePolygonRightEdge](../Source/Action/UpdatePolygonRightEdge.asm) |
| D4C1 | [SelectPolygonRowLimit](../Source/ThreeD/SelectPolygonRowLimit.asm) | [SelectPolygonRowLimit](../Source/Action/SelectPolygonRowLimit.asm) |
| D4F5 | [SetShortNegativeRightStep](../Source/ThreeD/SetShortNegativeRightStep.asm) | [SetShortNegativeRightStep](../Source/Action/SetShortNegativeRightStep.asm) |
| D503 | [WrapPolygonLeftTop](../Source/ThreeD/WrapPolygonLeftTop.asm) | [WrapPolygonLeftTop](../Source/Action/WrapPolygonLeftTop.asm) |
| D50A | [WrapPolygonRightTop](../Source/ThreeD/WrapPolygonRightTop.asm) | [WrapPolygonRightTop](../Source/Action/WrapPolygonRightTop.asm) |
| D50F | [ReturnPolygonFill](../Source/ThreeD/ReturnPolygonFill.asm) | [ReturnPolygonFill](../Source/Action/ReturnPolygonFill.asm) |
| D511 | [PreparePolygonFill](../Source/ThreeD/PreparePolygonFill.asm) | [PreparePolygonFill](../Source/Action/PreparePolygonFill.asm) |
| D5C9 | [TransformObjectVertices](../Source/ThreeD/TransformObjectVertices.asm) | [TransformObjectVertices](../Source/Action/TransformObjectVertices.asm) |
| D5F9 | [PrepareRenderVertexProducts](../Source/ThreeD/PrepareRenderVertexProducts.asm) | [PrepareRenderVertexProducts](../Source/Action/PrepareRenderVertexProducts.asm) |
| D694 | [ProjectRenderVertexGroup](../Source/ThreeD/ProjectRenderVertexGroup.asm) | [ProjectRenderVertexGroup](../Source/Action/ProjectRenderVertexGroup.asm) |
| D7A0 | [ProjectRenderVertex](../Source/ThreeD/ProjectRenderVertex.asm) | [ProjectRenderVertex](../Source/Action/ProjectRenderVertex.asm) |
| DBBD | [RenderClippedRecords](../Source/ThreeD/RenderClippedRecords.asm) | [RenderClippedRecords](../Source/Action/RenderClippedRecords.asm) |
| DD23 | [RenderInsideRecords](../Source/ThreeD/RenderInsideRecords.asm) | [RenderInsideRecords](../Source/Action/RenderInsideRecords.asm) |
| DDD1 | [CombineListedVertexCodes](../Source/ThreeD/CombineListedVertexCodes.asm) | [CombineListedVertexCodes](../Source/Action/CombineListedVertexCodes.asm) |
| DDF0 | [DrawLinearLine](../Source/ThreeD/DrawLinearLine.asm) | [DrawLinearLine](../Source/Action/DrawLinearLine.asm) |
| DEF0 | [AbortProjectedVertexScan](../Source/ThreeD/AbortProjectedVertexScan.asm) | [AbortProjectedVertexScan](../Source/Action/AbortProjectedVertexScan.asm) |
| DEF3 | [ClassifyProjectedVertices](../Source/ThreeD/ClassifyProjectedVertices.asm) | [ClassifyProjectedVertices](../Source/Action/ClassifyProjectedVertices.asm) |
| DFB6 | [CheckFaceOrientation](../Source/ThreeD/CheckFaceOrientation.asm) | [CheckFaceOrientation](../Source/Action/CheckFaceOrientation.asm) |

## Физические записи

- [ClipFirstPoint.asm](../Source/ThreeD/Data/ClipFirstPoint.asm)
- [ClipSecondPoint.asm](../Source/ThreeD/Data/ClipSecondPoint.asm)
- [ClipProducts.asm](../Source/ThreeD/Data/ClipProducts.asm)
- [LineMasks.asm](../Source/ThreeD/Data/LineMasks.asm)

Код, входы, данные, таблицы переходов и самомодификация совпадают побайтово. Перенос математики не заменяет проверку всех игровых состояний и всех внешних данных. R/T и IRQ ограничены первичными договорами. Сборка и нативный игровой процесс в этой работе не выполнялись.

Для CF08 [условный эффект трёх инструкций](ActionClipTableAlias.md#условный-эффект-исполнения)
проверен отдельно, игровой вход по этим адресам остаётся неизвестным.

[Физические таблицы диспетчера и заливки](PolygonFillPhysicalData.md) оформлены с исходными байтами и сохранёнными промежутками рабочей RAM.

[Физическая разметка всей младшей страницы CF00](ClipTargetLowPhysicalData.md) сохраняет наложенные рабочие записи и адресные ячейки CF08..CF0A.

[Физический заголовок текущей модели](ActionRenderHeaderPhysicalData.md) разделяет младший ModeBits и старший ModelByteOffset по исходным 9B8D и 9B8E. Снимок очереди сохраняет оба поля одним словом, адреса и байты не изменены.


## Имя образа во входных условиях

В 106 входных договорах реестра отдельной копии исправлено оставшееся от первичного разбора название ACTION на 3DPART. Исходники ThreeD уже содержали верное условие. Новое имя обозначает подключённую в банке 0 отдельную копию слота 19, а не одновременно присутствующий там целый ACTION. Все остальные строки In, весь Out, Corrupt, Note, адреса и байты сохранены. Изменён только литерал CONTRACTS в [фактах копии](../Tools/Disasm/Research/ThreeDOverlayMirrorFacts.py), массовый экспорт не выполнялся.

Равенство 8224 байтов 3DPART диапазону ACTION 6000..801F является основанием переноса локальных договоров при тех же внешних данных и состоянии самомодификации. Оно не устанавливает само по себе путь загрузки, игровой контекст всех вызовов или корректность произвольных данных. Проверенные клавиатурные входы ACTION не добавляются автоматически в договоры отдельной копии. [Проверка физического основания](../Tools/Disasm/Research/CheckThreeDOverlayMirror.py).


## Исполнение ACTION и перенос доказательства на копию

В комментариях MultiplySigned16, DivideSigned32To16 и BuildRenderCoefficients исправлено имя реально исполнявшегося образа. CheckActionSignedMultiply выполняет 917504 случая из ACTION, CheckActionSignedDivision выполняет 1331200 случаев из ACTION. CheckActionRenderCoefficients также создаёт банки из flat_action и сверяет собственные девять изменяемых операндов. Это проверки ACTION, а не отдельные исполнительные прогоны загрузки 3DPART.

Договоры соответствующих процедур 3DPART опираются на тождество всех 8224 байтов с ACTION[6000..801F], одинаковые CPU-адреса и явно заданное равенство внешней RAM, текущего банка и входного контекста. Происхождение и ограничения проверки сохранены в заголовках всех трёх процедур. Само сравнение байтов не доказывает одинаковый предшествующий игровой путь или выполнение отдельной дисковой загрузки 3DPART.

[Проверка копии](../Tools/Disasm/Research/CheckThreeDOverlayMirror.py), [умножение ACTION](../Tools/Disasm/Research/CheckActionSignedMultiply.py), [деление ACTION](../Tools/Disasm/Research/CheckActionSignedDivision.py), [коэффициенты ACTION](../Tools/Disasm/Research/CheckActionRenderCoefficients.py). Исполняемые инструкции и числовые договоры не меняются, устраняется неверное приписывание существующим сценариям другого образа.


## Регистры и порядок байтов пересечений

Четыре копии AppendTop/Bottom/Left/RightClipIntersection из таблицы выше имеют те же локальные инструкции, что и ACTION. [Подробный алгоритм и регистровые результаты](ActionClipIntersections.md) различает два пути DE горизонтальных границ и три пути вертикальных, сохраняемую ветвь BC, результат в A' и счётчик знаков IXL. Для верхней и нижней границы фиксирован First во втором байте, для левой и правой фиксирован Second в первом байте выходной пары.

Заголовки обеих копий согласованы. Исполняющая модель 279552 сценариев относится к ACTION, перенос её локальных выводов на 3DPART требует прежних условий одинаковой внешней RAM, входного контекста и общих процедур. Новое нативное исполнение 3DPART этим не подтверждается.


## Подготовители произведений

ComputeTopClipProduct, ComputeBottomClipProduct, ComputeLeftClipProduct
и ComputeRightClipProduct описывают реальные FirstPoint и SecondPoint.
Восемь заголовков ACTION и 3DPART раскрывают выходной BC по ядру и знаку,
A/F по двум ветвям применения знака, IX по размеру модулей.
[Аргументы, контекст BC и результаты](ActionClipProducts.md#контекст-bc-и-результаты-умножителя).
Инструкции и физические слоты при уточнении комментариев не менялись.
Это не добавляет доказательства нативной загрузки 3DPART.


## Классификация и завершение контура

В ClassifyProjectedVertices раскрыты точный AF' полного прохода и
сохранённый OR предыдущих кодов при маркере, включая маркер первой точки.
[Разбор альтернативного результата](ActionVertexCodes.md#точный-альтернативный-результат).
В ContinueClipPolygon отдельно описан непосредственный конец при B=1,
его сохранённые регистры, три снятых слова и шесть M1.
[Локальная модель и её границы](ActionPolygon.md#непосредственный-конец-continueclippolygon).
Описания ACTION и копии согласованы, исполняемые байты не менялись.
Прямые сценарии модели ACTION не объявляются новым нативным запуском
3DPART, условия общей внешней RAM и кода остаются обязательными.


## Контекст полного полигона

В ClipPolygon DE перед каждым обработчиком равен C071, а альтернативный
AF и IX могут переносить результаты прежних рёбер. Заголовки двух копий
различают эти зависимости и перечисляют регистры в согласованном порядке.
[Писатели, сохранение и наблюдения модели](ActionPolygon.md#контекст-помощников-между-рёбрами).
Перенос доказательств по-прежнему требует тех же внешних данных и кода,
нативный запуск отдельной копии этими уточнениями не подтверждается.


## Делитель и M1

В DivideSigned32To16 порядок входов HL, DE, BC, AF, AF' согласован.
Явно указан сохраняемый BC при двух неотрицательных входах, роль обоих
входных Carry и обязательного Sign. Out отделяет сохраняемые альтернативные
пары от результата AF', включает I/IM/IFF, paging и полное приращение R.
[Формула 114..152 M1 и её проверка на ACTION](ActionSignedDivision.md#полное-число-m1).
Инструкции двух копий не менялись. Перенос этих доказательств сохраняет
прежние условия загрузки и контекста, новый нативный запуск 3DPART
этим уточнением не подтверждается.


### R четырёх линейных ядер

Контракт DrawLinearLine уточнён вместе с ACTION, регистры перечислены в порядке HL, DE, BC, AF, альтернативные пары и IX/IY. [Формулы полного M1](ActionLineRaster.md#полный-m1-и-регистр-r-четырёх-ядер) проверены в 56064 сценариях основного входа и 77824 сценариях вызывающего двух DrawPacked. Перенос на копию 3DPART опирается на побайтовое совпадение и требует тех же масок, рабочих операндов, входных данных, внешней RAM и страницы. Сами инструкции копии не менялись, отдельный нативный запуск и произвольный контекст загрузки этим не доказаны.


### Граница девяти табличных произведений

PrepareRenderVertexProducts копии 3DPART сохраняет тот же локальный договор до D694, результаты и новые ограничения [описаны вместе с ACTION](ActionVertexProducts.md#знак-результата-и-точная-стоимость). Разность двух значений T из 0..127 не даёт #80 и PV, S совпадает с Carry, полный счёт составляет 127 M1. Состояние описывает девять записанных операндов до генератора, его дальнейшие эффекты и полный возврат сюда не включены. Перенос числового доказательства требует тех же коэффициентов, компонентов, таблицы, внешней RAM и состояния банка. Инструкции отдельной копии и жёсткое продолжение без настоящего JP сохранены.


### Подготовитель заливки и два выхода

[PreparePolygonFill копии](../Source/ThreeD/PreparePolygonFill.asm) связан с [общими формулами AF/AF'](ActionPolygonPreparation.md#раздельные-af-и-af-двух-выходов). Серия 3978 сценариев ACTION включает 1060 горизонтальных, все длины 3..60 с обоими входными Carry. Ранний выход восстанавливает HL и выполняет внешний RET, непустой передаёт управление D229 с SP=FFE0 до исполнения строкового заполнителя. Доказательство переносится только при тех же таблицах, режимах, контуре, внешней RAM и состоянии банка. Отдельный нативный запуск копии, полный R/T и все совместные входы этим не доказаны.


### Конечные ошибки и история E строкового ядра

[PolygonFillRows копии](../Source/ThreeD/PolygonFillRows.asm) связан с [точными результатами непустого пути](ActionPolygonFillRows.md#конечные-регистры-непустого-пути). Контракт теперь перечисляет ошибки, шаги, следующий шаблон, индексы и перенос линейного адреса, а не только отсылает к Python. Два реальных контура показали разные E при совпадающих последней строке, BC, IX/IY и HL', все десять сценариев пяти режимов включены в актуальные 11572 исполнения полного заполнителя ACTION. Перенос требует совпадающих данных, RAM, таблиц и банка, R/T, IRQ и отдельный нативный запуск не доказаны.


### Шесть коротких переходников заливки

Для каждого сохранены инструкции и локальная граница, без исполнения следующего обновителя либо поиска. Все 132096 сценариев ACTION повторно сравнивают R и полное M1, все 256 начальных R каждого переходника охвачены. Корневой CPU-стек меняет только общий POP HL/RET.

| Копия | Разбор | M1 |
| --- | --- | --- |
| [SelectPolygonRightEdge](../Source/ThreeD/SelectPolygonRightEdge.asm) | [Передача правому обновителю](ActionPolygonSelectRight.md) | 1 |
| [WrapPolygonLeftEdge](../Source/ThreeD/WrapPolygonLeftEdge.asm) | [Последний индекс левого кольца](ActionPolygonWrapLeft.md) | 3 |
| [WrapPolygonRightEdge](../Source/ThreeD/WrapPolygonRightEdge.asm) | [Первый индекс правого кольца](ActionPolygonWrapRight.md) | 2 |
| [WrapPolygonLeftTop](../Source/ThreeD/WrapPolygonLeftTop.asm) | [Альтернативный индекс верхнего обхода](ActionPolygonWrapLeftTop.md) | 5 |
| [WrapPolygonRightTop](../Source/ThreeD/WrapPolygonRightTop.asm) | [Возврат к обмену AF верхнего обхода](ActionPolygonWrapRightTop.md) | 2 |
| [ReturnPolygonFill](../Source/ThreeD/ReturnPolygonFill.asm) | [Два слова внешней рамки](ActionPolygonReturn.md) | 2 |

Данные, RAM, страница и входной контекст должны соответствовать ACTION, это условие переноса доказательств на побайтово совпадающую копию. Следующие процедуры, произвольные несогласованные контексты, точные T, аппаратные IRQ и отдельный нативный запуск не доказаны.


### Два обновителя рёбер и граница селектора

[Левый](../Source/ThreeD/UpdatePolygonLeftEdge.asm) и [правый](../Source/ThreeD/UpdatePolygonRightEdge.asm) обновители теперь связаны с [общим сравнением выходных регистров](ActionPolygonLeftEdge.md#локальный-выход-и-симметрия-двух-цепочек). Правый останавливается до общего селектора, левый уже проверил готовность правой цепочки и может записать предел и переход. Комментарии сохраняют различие рабочего E отрицательного длинного наклона и разных изменяемых половин HL'. Тела четырёх исходников не менялись. Доказательства прежней серии 97090 сценариев ACTION переносятся только при совпадающих входных данных, RAM, таблицах и странице, следующий селектор, R/T, IRQ и отдельный нативный запуск не доказаны.


### Перспектива и адрес пятого байта

[ProjectRenderVertex копии](../Source/ThreeD/ProjectRenderVertex.asm) связан с [точным положением ClipCode и частичными результатами](ActionPerspective.md#указатель-clipcode-и-контекст-отказа-глубины). SP указывает на ClipCode, четыре байта перед ним получают слова, после двух PUSH прибавляются девять и получается входной SP+5. При отрицательной глубине BC'/AF' сохраняются входными, ни одна база оси ещё не прочитана. На остальных путях регистры относятся к последней достигнутой оси. Прежние 284672 сценария ACTION и статическая сверка неизменных инструкций применимы только при тех же данных, таблицах, RAM и странице. R/T, все совместные входы и отдельный нативный запуск не доказаны.
