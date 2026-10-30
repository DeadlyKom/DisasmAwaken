                module Station
                module RemoveFoundSecondaryPoint
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Сдвиг физического остатка второго списка на одну запись и освобождение последней записи
; исходная запись 4, файловые смещения #1ED0..#1EF5
; In:
;   DE - адрес старшего байта SecondWord совпавшей записи B, как от FindSecondaryMapPoint, по шагу пять достижим первый байт 7F..FE
;   доступен FSecondaryDeleteFrame и договор RefreshSecondaryListPanels
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   адрес удаляемой записи получен уменьшением DE на три, немедленный следующий конец не копируется
;   иначе LDIR переносит физический диапазон от следующей записи до байта перед концом на пять байтов влево, пустоты FF тоже переносятся
;   первый байт последней освобождённой записи становится FF, оставшиеся четыре байта этой записи сохраняются, сам конец остаётся на месте
;   дальнейшее последовательное исполнение идёт в RefreshSecondaryListPanels, окончательные результаты соответствуют её договору
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, физические записи B, Cursor и порядок
; Note:
;   FSecondaryDeleteFrame содержит NextRecord и RemovedRecord поверх исходного адреса возврата
;   удаляется одна физическая позиция, это не общий уплотнитель всех FF, Variant при поиске не сравнивается
;   этот самостоятельный вход не ставит Pending, вызывающий ToggleSecondaryMapPoint уже поставил его
; -----------------------------------------
                ; расчёт начала удаляемой записи из адреса старшего байта SecondWord
Entry:          DEC DE
                DEC DE
                DEC DE
                LD H, D
                LD L, E
                ; расчёт следующей записи для проверки немедленного конца
                LD BC, FStoredMapPoint
                ADD HL, BC
                ; проверка первого байта после удаляемой записи, 7F..FE не переносятся
                LD A, (HL)
                INC A
                JP M, @Station.RemoveFoundSecondaryPoint.ClearLast              ; переход, если следующая запись уже содержит первый байт 7F..FE, освободить текущую без переноса

                ; создание FSecondaryDeleteFrame с адресами RemovedRecord и NextRecord
                PUSH DE
                PUSH HL
                ; расчёт следующего адреса физического остатка, пустоты также входят в перенос
FindEnd:        ADD HL, BC
                ; проверка конца после INC очередного первого байта
                LD A, (HL)
                INC A
                JP P, @Station.RemoveFoundSecondaryPoint.FindEnd                ; переход, если первый байт 00..7E либо FF, продолжить поиск конца физического остатка

                ; восстановление NextRecord и расчёт длины переноса до байта перед концом
                POP DE
                OR A
                SBC HL, DE
                LD B, H
                LD C, L
                ; выбор NextRecord источником и RemovedRecord приёмником сдвига на пять байтов влево
                EX DE, HL
                POP DE
                ; перенос физического остатка LDIR без отдельного удаления пустот
                LDIR
                ; расчёт начала последней освобождаемой записи от позиции конца
ClearLast:      LD BC, @StoredPointConst.PreviousRecord
                ADD HL, BC
                ; освобождение только первого байта, затем последовательное продолжение нормализации и рисунка
                LD (HL), @StoredPointConst.Empty
                ; JP @Station.RefreshSecondaryListPanels.Entry, продолжение в RefreshSecondaryListPanels.asm

                endmodule
                endmodule
