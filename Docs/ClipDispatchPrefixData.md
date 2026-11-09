# Префикс таблицы отсечения CF00

[ACTION](../Source/Action/Data/ClipDispatchPrefix.asm) и [3DPART](../Source/ThreeD/Data/ClipDispatchPrefix.asm) имеют отдельные физические экземпляры FClipDispatchPrefix. Каждый занимает восемь байтов CF00..CF07 в адресном пространстве соответствующей загруженной копии. Это две дисковые записи, не новые банки или новые области RAM. Исходные байты обеих копий равны D3 E4 88 00 3D 7B 95 00.

| Смещение | Поле | Назначение |
|---|---|---|
| 0 | AppendPointLow | Младший байт адреса [AppendSecondClipPoint](../Source/Action/AppendSecondClipPoint.asm), C6D3 |
| 1 | ToRightLow | Младший байт адреса [ClipInsideToRight](../Source/Action/ClipInsideToRight.asm), C5E4 |
| 2 | ToLeftLow | Младший байт адреса [ClipInsideToLeft](../Source/Action/ClipInsideToLeft.asm), C588 |
| 3 | CornerBlock | Полный байт запрета фактической записи углов |
| 4 | ToBottomLow | Младший байт адреса [ClipInsideToBottom](../Source/Action/ClipInsideToBottom.asm), C53D |
| 5 | ToBottomRLow | Младший байт адреса [ClipInsideToBottomRight](../Source/Action/ClipInsideToBottomRight.asm), C07B |
| 6 | ToBottomLLow | Младший байт адреса [ClipInsideToBottomLeft](../Source/Action/ClipInsideToBottomLeft.asm), C095 |
| 7 | SeenFlags | Сохраняемые отметки уже посещённых углов |

Для копии 3DPART цели имеют такие же адреса и отдельные процедуры ThreeD. Входы этой копии, [ThreeD.ClipPolygon](../Source/ThreeD/ClipPolygon.asm) и [ThreeD.ClipSingleEdge](../Source/ThreeD/ClipSingleEdge.asm), используют соответствующие физические байты того же CPU-адреса. Старший байт каждого адреса находится по D000+индекс, младший по CF00+индекс. Это разделённая таблица, поля Low сами по себе не являются полными указателями.

## Почему рабочие байты не портят допустимые переходы

Девять нормальных кодов положения точек дают 81 допустимую пару. [Исходный реестр](../Tools/Disasm/Reports/ActionClipDispatchTable.json) не содержит индексов 03 и 07. Они соответствовали бы одновременно установленным взаимоисключающим горизонтальным сторонам. Поэтому изменения CF03 и CF07 не меняют адреса этих 81 пар. Это утверждение ограничено нормальными кодами, оно не разрешает произвольные испорченные ClipCode и не доказывает полный граф всех косвенных переходов.

Для CornerBlock значение 00 разрешает добавление угла, любой байт 01..FF подавляет фактическую запись. Это числовой запрет целиком, отдельным разрядам назначение не приписывается. Запрос угла может при этом всё равно обновить SeenFlags.

| Разряд SeenFlags | Назначение |
|---|---|
| 7..4 | Значение не интерпретируется обработчиками углов, они его сохраняют |
| 3 | TL, верхний левый угол, маска 08 |
| 2 | TR, верхний правый угол, маска 04 |
| 1 | BL, нижний левый угол, маска 02 |
| 0 | BR, нижний правый угол, маска 01 |

Нулевое младшее поле означает отсутствие отметок, полная маска младшего поля равна 0F. [ClipPolygon](../Source/Action/ClipPolygon.asm) сначала обнуляет оба полных байта CornerBlock и SeenFlags. [ClipSingleEdge](../Source/Action/ClipSingleEdge.asm) задаёт CornerBlock=1 и не очищает прежние отметки. Поэтому сохранение верхней тетрады относится к обработчикам углов, а не ко всем писателям байта. Полные договоры находятся в [ActionClipCases](ActionClipCases.md), [ActionClipPointWriters](ActionClipPointWriters.md), [ActionSingleEdge](ActionSingleEdge.md) и [ThreeDOverlayMirror](ThreeDOverlayMirror.md).

## Проверка и граница разбора

[Описание структуры и обратимый разбор](../Tools/Disasm/Research/ClipDispatchPrefixData.py), [публикация](../Tools/Disasm/Research/ClassifyClipDispatchPrefixData.py), [отчёт](../Tools/Disasm/Reports/ClipDispatchPrefixDataClassification.json). Проверяются обе физические копии, шестнадцать оригинальных байтов, восемнадцать физических имён, размеры и смещения STRUCT, адресные привязки рабочих байтов и состав адресов по двум страницам таблицы. Исходные инструкции не меняются.

Диапазон CF08..CF0A остаётся отдельным Unknown в обеих копиях. Его положительная табличная роль уже установлена, но игровой вход исполнения не доказан. Типизация префикса не меняет это заключение, см. [ActionClipTableAlias](ActionClipTableAlias.md). Сборка и нативный запуск новой разметки не выполнялись.

[Физическая разметка всей младшей страницы CF00](ClipTargetLowPhysicalData.md) сохраняет наложенные рабочие записи и отдельный Unknown CF08.
