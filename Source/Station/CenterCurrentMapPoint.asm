                module Station
                module CenterCurrentMapPoint
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Чтение двух слов текущего ключа перед общим выбором и центрированием карты
; исходная запись 4, файловые смещения #1FB4..#1FBF
; In:
;   SignatureInput.Entry содержит читаемые FirstWord и SecondWord текущего ключа
;   действуют договоры SelectMapPoint и ReadStoredMapVariant, первый список имеет достижимое совпадение либо конец
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   Pending=1, DE получает текущее FirstWord, HL текущее SecondWord, затем последовательный вход CenterKeyAndRefreshMap
;   текущий Variant входного пятибайтового ключа не читается, выбор варианта происходит заново из A по общему договору
;   конечные результаты соответствуют CenterKeyAndRefreshMap
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, MapSelection, начало карты и Pending
; Note:
;   порядок INCLUDE с общим банковым входом жёсткий, новой инструкции перехода не добавлено
; -----------------------------------------
                ; запрос отложенного обновления планет до выбора текущего ключа
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; чтение FirstWord и SecondWord текущего ключа без его Variant
                LD DE, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD HL, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                ; JP @Station.CenterKeyAndRefreshMap.Entry, продолжение в CenterKeyAndRefreshMap.asm

                endmodule
                endmodule
