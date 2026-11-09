# Точная копия 3DPART

Логические 8224 байта записи 19 полностью совпадают с ACTION, смещения 6000..801F. Секторный хвост 224 байта сохранён отдельно. [Проверка](../Tools/Disasm/Research/CheckThreeDOverlayMirror.py) сравнивает фактические байты и проверяет отсутствие непонятных ручных комментариев до публикации.

121 контракт перенесён только при одинаковых внешней RAM, загруженном банке 0 и состояниях входа. Общие внешние процедуры вне файла сохраняют ссылки ACTION. Самостоятельная нативная загрузка 3DPART не выполнялась. [Исходная разметка и прежние частичные контракты](../Tools/Disasm/Reports/ThreeDOverlayMirrorVerification.json) сохранены, неоднозначность CF08 остаётся Unknown.

Поля RAM и константы из Includes общие для одинакового адресного пространства. Физические блоки этой копии имеют отдельные метки ThreeDClipPoints, ThreeDClipProductsData, ThreeDLineMasks и [ThreeDClipDispatchPrefix](ClipDispatchPrefixData.md). Новые адреса и области памяти не выделяются.

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
| CF08 | [UnknownCF08](../Source/ThreeD/UnknownCF08.asm) | [UnknownCF08](../Source/Action/UnknownCF08.asm) |
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

Для UnknownCF08 [условный эффект трёх инструкций](ActionClipTableAlias.md#условный-эффект-исполнения)
уточнён отдельно, игровой вход и назначение совмещения по-прежнему неизвестны.

[Физические таблицы диспетчера и заливки](PolygonFillPhysicalData.md) оформлены с исходными байтами и сохранёнными промежутками рабочей RAM.

[Физическая разметка всей младшей страницы CF00](ClipTargetLowPhysicalData.md) сохраняет наложенные рабочие записи и отдельный Unknown CF08.

[Физический заголовок текущей модели](ActionRenderHeaderPhysicalData.md) разделяет младший ModeBits и старший ModelByteOffset по исходным 9B8D и 9B8E. Снимок очереди сохраняет оба поля одним словом, адреса и байты не изменены.
