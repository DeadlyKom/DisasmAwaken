# Рисование глифа станции

[DrawGlyph](../Source/Station/DrawGlyph.asm) по #AE8D получает восьмибитный
код символа в A. Его ширина берётся из #8900, восемь строк из #8A00.
[Исходные ресурсы и измерители](Font.md) описаны отдельно.

## Курсор и ограничения

Относительный Y должен быть строго меньше TextWindow.Height.
Следующая позиция CursorX, сумма прежней позиции и ширины символа,
должна помещаться в байт и быть строго меньше Width. Равенство границе
является отказом. После этих двух проверок CursorX обновляется.
Последующие проверки физического начала уже не отменяют продвижение.

Физические X и Y получаются прибавлением исходных относительных координат
к знаковым началам окна. Ненулевой отрицательный старший байт пропускает
весь глиф с успешным статусом. Неотрицательный ненулевой старший байт
возвращает ошибку координаты. Частичного отсечения слева или сверху нет.
Физический верхний Y должен быть меньше 185, чтобы поместились восемь строк.
Относительная Height ограничивает начало глифа, не весь его прямоугольник.
Например, Height=1 допускает восемь строк глифа с относительным Y=0.

| Результат | AF | CursorX |
| --- | --- | --- |
| Рисование, допустимый отрицательный пропуск или режим без пикселей | #0045 | Ширина принята |
| Положительный выход X за байтовую координату | #0044 | Ширина уже принята |
| Положительный выход Y за байтовую координату | #0100 | Ширина уже принята |
| Физический верхний Y не меньше 185 | A=1, F от CP(Y,185) | Ширина уже принята |
| Относительный Y достиг Height | A=2, F от AND относительного Y | Без изменения |
| Ширина переполнила байт или достигла Width | A=3, F от AND байтовой суммы | Без изменения |

Коды A именованы в GlyphStatus. Значение A=0 различается по Carry.
Отказы реализованы входами
[GlyphHeightError](../Source/Station/GlyphHeightError.asm),
[GlyphWidthError](../Source/Station/GlyphWidthError.asm),
[GlyphOriginXError](../Source/Station/GlyphOriginXError.asm),
[GlyphOriginYError](../Source/Station/GlyphOriginYError.asm) и
[GlyphBottomError](../Source/Station/GlyphBottomError.asm).
Они используют уже созданный FGlyphFrame.

## Таблица двух участков

Адрес первой строки берётся из страниц #82 и #83, горизонтальный вклад
из #84. Выбор процедуры определяется сдвигом X AND 7, признаком
крайней колонки X SHR 3 = 31 и младшими тремя битами Y.

Индекс равен (2*сдвиг + признак_крайней_колонки)*8 + (Y AND 7).
Адрес записи равен #9200 + 4*индекс.
[GlyphRoutes.asm](../Source/Station/Data/GlyphRoutes.asm) содержит все 128
физических FGlyphRoute с именованными целями двух слов.

First выбирает первый участок. При Y, кратном восьми, он выводит все
восемь строк, AfterWrap равен нулю и не читается. При остатке Y от 1 до 7
первый участок выводит 8-Y строк, корректирует адрес следующего знакоместа
и выбирает AfterWrap для последних Y строк. Один изменяемый JP по #AF09
получает обе цели последовательно. Слово адреса по #AF0A именовано
GlyphState.DispatchTarget.

Для каждого байта строки сдвиг S даёт первый вклад, байт SHR S.
Вторая часть равна младшему байту байт SHL (8-S). Обе части объединяются
с bitmap через XOR. Для крайней колонки второй байт не записывается,
пиксели правее X=255 отсекаются. При S=0 второй вклад не требуется,
две группы таблицы ссылаются на одно ядро.

| Сдвиг | Обычный участок | Крайний байт |
| --- | --- | --- |
| 0 | [DrawGlyphShift0](../Source/Station/DrawGlyphShift0.asm) | То же ядро |
| 1 | [DrawGlyphShift1](../Source/Station/DrawGlyphShift1.asm) | [DrawGlyphEdge1](../Source/Station/DrawGlyphEdge1.asm) |
| 2 | [DrawGlyphShift2](../Source/Station/DrawGlyphShift2.asm) | [DrawGlyphEdge2](../Source/Station/DrawGlyphEdge2.asm) |
| 3 | [DrawGlyphShift3](../Source/Station/DrawGlyphShift3.asm) | [DrawGlyphEdge3](../Source/Station/DrawGlyphEdge3.asm) |
| 4 | [DrawGlyphShift4](../Source/Station/DrawGlyphShift4.asm) | [DrawGlyphEdge4](../Source/Station/DrawGlyphEdge4.asm) |
| 5 | [DrawGlyphShift5](../Source/Station/DrawGlyphShift5.asm) | [DrawGlyphEdge5](../Source/Station/DrawGlyphEdge5.asm) |
| 6 | [DrawGlyphShift6](../Source/Station/DrawGlyphShift6.asm) | [DrawGlyphEdge6](../Source/Station/DrawGlyphEdge6.asm) |
| 7 | [DrawGlyphShift7](../Source/Station/DrawGlyphShift7.asm) | [DrawGlyphEdge7](../Source/Station/DrawGlyphEdge7.asm) |

Дополнительные входы RowsN выводят последние N строк развёрнутого ядра.
SplitGlyphShiftN и SplitGlyphEdgeN выводят префикс до границы знакоместа.
Их Entry начинает с семи строк, дополнительные RowsN сокращают префикс.
После увеличений H адрес исправляется прибавлением 32 к L. При переносе
H уже соответствует следующей трети, без переноса из H вычитается восемь.
Затем через EXX возвращается указатель второго слова записи.

## Кадр регистров

FGlyphFrame создаётся исходными PUSH. Отдельная память для него не выделяется.

| Смещение от SP | Поле |
| --- | --- |
| #00 | SavedAFAlt |
| #02 | SavedHLAlt |
| #04 | SavedBCAlt |
| #06 | SavedDEAlt |
| #08 | SavedHL |
| #0A | SavedBC |
| #0C | SavedDE |
| #0E | ReturnAddress |

[ReturnGlyph](../Source/Station/ReturnGlyph.asm) по #B514 формирует AF=#0045.
Вход Status по #B516 сохраняет переданный статус. Затем восстанавливаются
оба набора общих регистров и альтернативный AF, RET снимает адрес возврата.
Потреблено #10 байт от начала кадра. IX, IY, I и IFF сохраняются.
Во внутренних контрактах Corrupt перечисляет рабочие наборы относительно
внутреннего входа, которые заменяются сохранёнными значениями FGlyphFrame.
Самостоятельный CALL внутренних участков без этого кадра недопустим.

## Режим без пикселей

[SkipJustifyRow](../Source/Station/SkipJustifyRow.asm) временно меняет три байта
начиная с #AED5 на JP ReturnGlyph.Entry. Проверки и продвижение CursorX
сохраняются, пиксельная часть и запись DispatchTarget пропускаются.
Для возобновления возвращаются #68, #48 и #26. Последний байт является
только началом LD H,nn, прежний операнд #82 по #AED8 не меняется.
Исходные константы именованы в GlyphOpcode, поле изменения в GlyphState.KernelPrefix.

## Текстовая строка

[AdvanceTextRow](../Source/Station/AdvanceTextRow.asm) по #AE55 вычисляет
следующий Y=(CursorY+8) AND #FF. Если он меньше Height, CursorY обновляется,
CursorX обнуляется, AF=#0044. Иначе курсор сохраняется, A содержит следующий Y,
Carry установлен. BC возвращает Height и вычисленный Y, HL и DE сохраняются.
Байтовое переполнение сохранено, 250 при добавлении восьми даёт 2.
Все 65536 пар проверены в
[TextRowVerification.json](../Tools/Disasm/Reports/TextRowVerification.json).

## Проверка

[CheckGlyphRenderer.py](../Tools/Disasm/Research/CheckGlyphRenderer.py) сверил
36768 исходных глифов и положений с независимым XOR по отдельным пикселям.
Проверены все коды, все 128 записей таблицы, правый край и границы третей.
Дополнительно проверены 32768 случаев со всеми 256 значениями байта строки,
исходный шрифт содержит только 40 различных байтов рисунка.
Ещё 32 случая охватывают отказы, отрицательные начала, восстановление
нулевой физической координаты и временный режим без рисования.

Сверяются оба набора регистров, AF, стек, курсор, обе цели JP и вся область
bitmap с атрибутами. Журнал записей допускает только bitmap, кадр стека,
CursorX и два байта DispatchTarget.
Отчёт [GlyphRenderVerification.json](../Tools/Disasm/Reports/GlyphRenderVerification.json).
Модель работает без IRQ и нативного запуска. Другие неизвестные изменения
инструкций в ходе игры не подтверждены.

Трасса классифицировала 1065 инструкций из прежних двоичных промежутков.
22 байта #BBA8..#BBBD относятся к отдельному числовому входу PrintMin4,
разобранному позднее в [NumberOutput](NumberOutput.md). Перенос 38 процедур и
128 записей выполнен через отдельную копию, 31 предыдущий файл сохранён
в истории. Отчёт [GlyphReleaseVerification.json](../Tools/Disasm/Reports/GlyphReleaseVerification.json).

## Связанные исходники

| Вход | Процедура |
| --- | --- |
| #AF36 | [Station.SplitGlyphShift0](../Source/Station/SplitGlyphShift0.asm) |
| #AFE0 | [Station.SplitGlyphShift1](../Source/Station/SplitGlyphShift1.asm) |
| #B089 | [Station.SplitGlyphEdge1](../Source/Station/SplitGlyphEdge1.asm) |
| #B152 | [Station.SplitGlyphShift2](../Source/Station/SplitGlyphShift2.asm) |
| #B220 | [Station.SplitGlyphEdge2](../Source/Station/SplitGlyphEdge2.asm) |
| #B30F | [Station.SplitGlyphShift3](../Source/Station/SplitGlyphShift3.asm) |
| #B402 | [Station.SplitGlyphEdge3](../Source/Station/SplitGlyphEdge3.asm) |
| #B521 | [Station.SplitGlyphShift4](../Source/Station/SplitGlyphShift4.asm) |
| #B631 | [Station.SplitGlyphEdge4](../Source/Station/SplitGlyphEdge4.asm) |
| #B735 | [Station.SplitGlyphShift5](../Source/Station/SplitGlyphShift5.asm) |
| #B828 | [Station.SplitGlyphEdge5](../Source/Station/SplitGlyphEdge5.asm) |
| #B90D | [Station.SplitGlyphShift6](../Source/Station/SplitGlyphShift6.asm) |
| #B9E3 | [Station.SplitGlyphEdge6](../Source/Station/SplitGlyphEdge6.asm) |
| #BAA9 | [Station.SplitGlyphShift7](../Source/Station/SplitGlyphShift7.asm) |
| #BB62 | [Station.SplitGlyphEdge7](../Source/Station/SplitGlyphEdge7.asm) |

## Составной Corrupt входа DrawGlyph

Сохранение HL, DE, BC, альтернативных и индексных регистров не
означает отсутствия записей. Собственный вход DrawGlyph записывает
семь сохранённых слов, 14 байтов под внешним адресом возврата.
Это поля FGlyphFrame без его ReturnAddress. При допустимой ширине
меняется TextWindow.CursorX, CursorY этим входом сохраняется.
При фактическом рисовании меняются выбранные байты bitmap и
двухбайтовый GlyphState.DispatchTarget. При раннем отказе либо
режиме без пикселей соответствующие записи могут отсутствовать.
AF и R меняются, точное число M1 зависит от достигнутого пути.
Эти эффекты явно перечислены в Corrupt исходника, прежние
ограничения отдельных моделей и статусы всех выходов сохраняются.

## Записи продвижения строки

AdvanceTextRow не вызывает дочерние процедуры и не выполняет PUSH.
Его Corrupt включает BC, AF, R и курсоры TextWindow.CursorX и CursorY.
При принятой новой строке записываются Y и нулевой X, при отказе оба
курсора сохраняются. Эта процедура сама не пишет bitmap и не создаёт
временную рамку стека, внешний RET только читает адрес возврата.

## Общие выходы и снятие кадра

ReturnGlyph.Entry формирует успех 0045, Status передаёт готовый AF.
Пять внутренних входов отказа затем используют тот же выход.
Он читает семь сохранённых слов FGlyphFrame и внешний адрес возврата,
SP увеличивается на 16. Обычный AF задаёт статус, альтернативный AF
восстанавливается из кадра, поэтому эти два источника не объединяются.
Сам выход и входы отказов не пишут RAM и не рисуют пиксели.

[Дополнительный режим модели](../Tools/Disasm/Research/CheckGlyphRenderer.py)
`--return-entries` проверяет исходные инструкции этих семи входов.
Выполнено 458240 случаев, все допустимые входные A и F, включая
255 ненулевых A для двух входов физического начала. Сохранённые слова
задаются различимыми значениями, проверены регистры, статус, SP,
PC и R. Наблюдатель записей проверен положительным контролем CPU.
Во всех случаях сам проверяемый код не записывал RAM, кадр сохранился.

| Вход | Приращение младших семи разрядов R в M1 |
| --- | ---: |
| ReturnGlyph.Status | 11 |
| ReturnGlyph.Entry | 13 |
| GlyphHeightError | 14 |
| GlyphWidthError | 14 |
| GlyphOriginXError | 15 |
| GlyphOriginYError | 15 при отрицательном A, иначе 16 |
| GlyphBottomError | 13 |

Старший бит R сохраняется. Результаты относятся к исходным опкодам
и подготовленному доступному кадру. Полное произведение сохранённых
слов, произвольные перекрытия стека, IRQ, нативный запуск и сборка
не проверялись. Самостоятельный CALL без FGlyphFrame остаётся
недопустимым способом использования этих внутренних входов.
[Отчёт](../Tools/Disasm/Reports/GlyphReturnEntriesVerification.json).
