                module Station
                module UnknownAA3D
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #4A3D..#4A4E
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          CALL @Station.GenerateMissionOffer.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem31.Entry
                CALL @Station.DrawItem32.Entry
                CALL @Station.DrawItem00.Entry
                JP @Station.EndScreenUpdate.Entry


                endmodule
                endmodule
