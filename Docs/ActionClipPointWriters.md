# Писатели углов и второй точки ACTION

[AppendTopLeftClipCorner](../Source/Action/AppendTopLeftClipCorner.asm), вход C641.

[AppendTopRightClipCorner](../Source/Action/AppendTopRightClipCorner.asm), вход C64C.

[AppendBottomLeftClipCorner](../Source/Action/AppendBottomLeftClipCorner.asm), вход C657.

[AppendBottomRightClipCorner](../Source/Action/AppendBottomRightClipCorner.asm), вход C662.

[AppendSecondClipPoint](../Source/Action/AppendSecondClipPoint.asm), вход C6D3.

Четыре угла получают полный CornerBlock по CF03. При любом ненулевом значении процедура возвращается с A=CornerBlock и флагами AND A без записей RAM. HL, DE и BC в этом случае сохраняются. При нуле выбирается фиксированная пара и выполняется JP в общий StorePair писателя второй точки. Верхние углы имеют First=0, нижние First=95, левые Second=0, правые Second=255.

AppendSecondClipPoint.Entry читает только младшие байты двух координат SecondPoint. Общий StorePair получает E как Second, D как First, читает OutputSize и пишет два байта в страницу 90 через INC L. Перенос между страницами намеренно не выполняется, размер увеличивается на два по модулю 256. Ограничения координат и ёмкости не проверяются.

После записи HL=9000 OR новый размер, A=новый размер, DE содержит записанную пару, BC сохранён. F относится к последнему INC L. Прямой писатель сохраняет входной Carry, вызов угла очищает его предварительным AND A. Альтернативные регистры, IX/IY, I/IM/IFF и paging сохраняются. CPU-стек не записывается, после RET SP увеличен на два. Приращение R равно 14 для Entry второй точки, 10 для StorePair, 3 для запрещённого угла и 15 для записанного угла, старший бит R сохраняется.

[Модель](../Tools/Disasm/Research/CheckActionClipPointWriters.py) прошла [393216 сценариев](../Tools/Disasm/Reports/ActionClipPointWritersVerification.json), все 65536 упакованных концов ребра при двух Carry и все 65536 сочетаний запрета/смещения для каждого угла. Исполняется настоящий общий писатель. Проверяются точные регистры, флаги, R, вся физическая RAM и кратность записей. Полная область всех входных регистров, IRQ, сборка и нативный игровой вывод не доказаны.

[Физический префикс CF00..CF07](ClipDispatchPrefixData.md) разделяет шесть младших адресных байтов и два рабочих состояния. [Три ячейки CF08..CF0A](ActionClipTableAlias.md) оформлены отдельно.
