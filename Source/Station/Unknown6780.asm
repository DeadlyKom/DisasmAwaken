                module Station
                module Unknown6780
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #0A2C..#0A54
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
Entry:          LD HL, #9A58
                LD (#9A89), HL
                LD DE, (#7A16)
                CALL @Station.DropItemDraw.Entry
                LD DE, (#6878)
                CALL @Station.DropItemDraw.Entry
                LD DE, (#6946)
                CALL @Station.DropItemDraw.Entry
                LD DE, (#7A56)
                CALL @Station.DropItemDraw.Entry
                LD DE, (#7A83)
                JP @Station.DropItemDraw.Entry


                endmodule
                endmodule
