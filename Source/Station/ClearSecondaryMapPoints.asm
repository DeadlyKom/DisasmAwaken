                module Station
                module ClearSecondaryMapPoints
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Очистка первых байтов второго списка до точного маркера 80 и обновление панелей
; исходная запись 4, файловые смещения #1F10..#1F29
; In:
;   в B достижим именно первый байт 80 по шагу FStoredMapPoint, для другого отрицательного маркера этот проход не имеет такого договора
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
;   действует договор RefreshSecondaryListPanels, обратное чтение до положительного байта доступно даже при пустом результате
; Out:
;   Pending=1, Cursor сначала установлен к началу B, каждый первый байт до точного 80 заменён FF
;   остальные четыре байта всех записей, сам ограничитель и A не меняются
;   далее выполнены нормализация B и общий рисунок, конечные результаты соответствуют RefreshSecondaryListPanels
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, первые байты B, Cursor, порядок и Pending
; Note:
;   это точное сравнение CP 80, коды 7F,81..FE сами по себе не заканчивают очистку
;   после очистки нормализатор сначала читает назад и лишь потом ограничивает адрес снизу, предшествующая читаемая память является обязательным условием
; -----------------------------------------
                ; запрос обновления планет перед очисткой B
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; установка Cursor к началу второго списка до прохода очистки
                LD HL, @StoredMapPointsB.Point00
                LD (@SecondaryPointState.Cursor), HL
                LD BC, FStoredMapPoint
                ; проверка именно маркера 80, остальные отрицательные коды здесь не заканчивают проход
ClearNext:      LD A, (HL)
                CP @StoredPointConst.EndMarker
                JR Z, @Station.ClearSecondaryMapPoints.Refresh                  ; переход, если первый байт равен ровно 80, закончить очистку и нормализовать B

                ; освобождение только первого байта очередной записи
                LD (HL), @StoredPointConst.Empty
                ; расчёт адреса следующей пятибайтовой записи B
                ADD HL, BC
                JR @Station.ClearSecondaryMapPoints.ClearNext

Refresh:        JR @Station.RefreshSecondaryListPanels.Entry

                endmodule
                endmodule
