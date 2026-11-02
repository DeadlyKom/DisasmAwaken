"""Полный договор прямого построителя масок двух сторон окружности."""
FUNCTIONS = {0xD320: ('BuildCircleSpan', 'Построение адресов и включающих масок двух краёв сечения большого контура')}
LOCAL = {}
LABELS = {}
CONTINUATIONS = {}
RENAMES = {'Controls.UnknownD320.Entry': 'Controls.BuildCircleSpan.Entry'}
CONTRACTS = {('Controls', 0xD320): (
    ['HL, DE, BC и AF входных аргументов не задают',
     'банк 1 выбран, физические Flags и Radius, байты CenterY и CenterX доступны для чтения',
     'общий Mode читается масочными помощниками, SavedB доступен для записи',
     'на стеке внешний возврат, ещё два байта нужны последовательно для CALL и PUSH AF, IRQ не вмешиваются'],
    ['при Xl=(CenterX-Radius) AND FF, Xr=(CenterX+Radius) AND FF, Pl=8000+32*CenterY+(Xl DIV 8), Pr=8000+32*CenterY+(Xr DIV 8)',
     'HL=Pr, D=Radius, E=LOW Pl, B=(FF << (7-(Xl AND 7))) AND FF, C=FF >> (Xr AND 7)',
     'A=B, F=42, Z и N установлены, остальные биты F сброшены',
     "HL', DE', BC' сохраняются кроме E'=0 и C'=(-Radius) AND FF, AF', IX и IY сохраняются",
     'SavedB содержит левую маску B, I, IM и IFF сохраняются, SP=входной SP+2',
     'R учитывает прямой путь и 1+(Xl AND 7) шагов левой маски и 8-(Xr AND 7) шагов правой маски'],
    ["HL, DE, BC, AF, E', C', SavedB, два байта CPU-стека, R"],
    ['радиус, центр и переносы X не ограничиваются, вычисленные адреса не разыменовываются',
     'обе маски включают свой край, последующий рисователь сохраняет их биты и заполняет открытый интервал',
     'последний JP в BuildRightSpanMask использует внешний возврат этой процедуры, отдельного CALL справа нет',
     'два временных байта сначала получают возврат D335, затем Xr и флаги ADD CenterX,Radius',
     'влияние общего Mode на флаги уничтожено внутри помощников, F=42 не проверяет возвращаемую маску'])}
COMMENTS = {
    0xD320: (['загрузка центральной строки и горизонтального центра сечения'], None),
    0xD324: (['загрузка Flags и Radius из физической записи проекции'], None),
    0xD328: (['вычисление отрицательного радиуса для альтернативного состояния контура'], None),
    0xD32B: (["обновление только C' и E', альтернативные B' и D' сохраняются"], None),
    0xD330: (['вычисление X левой границы как CenterX-Radius по модулю байта'], None),
    0xD332: (['построение адреса левого края в HL и E, включающей маски в B'], None),
    0xD335: (['восстановление центральной строки после замены C левой масочной процедурой'], None),
    0xD339: (['вычисление X правой границы как CenterX+Radius по модулю байта'], None),
    0xD33D: (['хвостовое построение правого адреса HL и маски C, возврат сразу внешнему вызывающему'], None),
}


def name_operands(region, function_address, operation):
    if region == 'Controls' and function_address == 0xD320:
        operation = operation.replace('(#D183)', '(@ControlsCircleSetupState.CenterY)')
        operation = operation.replace('(#D184)', '(@ControlsCircleSpanState.CenterX)')
        operation = operation.replace('(#D17F)', '(@ControlsBodyProjection.Value.Flags)')
    return operation
