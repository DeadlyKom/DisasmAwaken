                module Station
                module SelectSecondaryListCursor
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Установка курсора второго списка на первую совпавшую с выбранным ключом запись
; исходная запись 4, файловые смещения #1FE0..#1FFE
; In:
;   MapSelection задаёт четыре байта ключа, B удовлетворяет FindSecondaryMapPoint
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   Pending=1, первый совпавший ключ B найден настоящим банковым поиском независимо от Variant
;   при отсутствии возврат до рисунка, Cursor не меняется, Sign=1 и A отрицательный не-FF маркер, остальные результаты по FindSecondaryMapPoint и возврату банка
;   при совпадении адрес DE уменьшен на три к началу записи, Cursor получает этот адрес, затем выполнен общий рисунок RefreshStoredMapPanels
;   таблица порядка и Layout этим путём не пересчитываются, сами записи A,B не меняются
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, Cursor и Pending
; Note:
;   это установка курсора B, а не копирование записи в выбранный ключ или немедленное центрирование
; -----------------------------------------
                ; запрос обновления планет до проверки наличия выбранного ключа B
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; выбор KARTA для поиска первой совпавшей записи второго списка
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                CALL @Map.FindSecondaryMapPoint.Entry
                ; сохранение AF поиска вокруг возврата станционного банка
                EX AF, AF'
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                RET M                                                           ; выход, если выбранного ключа нет в B, Cursor и рисунок не менять

                ; расчёт начала совпавшей записи уменьшением адреса старшего SecondWord на три
                DEC DE
                DEC DE
                DEC DE
                ; обновление Cursor найденным адресом без пересчёта порядка
                LD (@SecondaryPointState.Cursor), DE
                JP @Station.RefreshStoredMapPanels.Entry

                endmodule
                endmodule
