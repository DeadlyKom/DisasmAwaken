                module Station
                module RefreshSecondaryListPanels
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Нормализация курсора и таблицы порядка B перед общим рисунком карты и сведений
; исходная запись 4, файловые смещения #1EF6..#1F05
; In:
;   действует договор Map.RefreshSecondaryPointOrder, обратный поиск от SecondaryPointState.Cursor достигает положительного байта
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   сначала нормализован Cursor, пересчитано количество B и плотная таблица смещений, старшая тетрада Layout сохранена
;   после SelectRamBank выбрана страница станции, далее хвостовой переход в RefreshStoredMapPanels, её результаты являются конечными
;   старый экран скопирован в банк 7, условно нарисованы сведения, затем безусловно рамка и содержимое основной карты
;   TextWindow в конце относится к основной карте, прежнее окно и стиль не восстанавливаются
;   при обычном успешном рисунке A=10, F=44, ScreenRequest=0, ClipRequest=0, SectorRequest=1, CurrentPage=10
;   HL, DE, BC и альтернативные пары соответствуют DrawMapPanel, AF' рабочий от указателя, IX рабочий по договору карты
;   IY, I и IFF сохраняются инструкциями при договоре HALT, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, SecondaryPointState.Cursor и StoredMapOrder
; Note:
;   сам этот вход не ставит Pending, оригинальные 7F,FF,80 обрабатываются по отдельному договору нормализатора
;   отдельная проверка 88 общих рисунков включает все количества B от нуля до десяти и два исходных экранных бита
; -----------------------------------------
                ; выбор KARTA для нормализации курсора и таблицы порядка B
Entry:          LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; исходный пересчёт Cursor, количества и плотных смещений, включая обратный поиск ниже начала
                CALL @Map.RefreshSecondaryPointOrder.Entry
                ; возврат станции перед хвостовым общим рисунком
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                JP @Station.RefreshStoredMapPanels.Entry

                endmodule
                endmodule
