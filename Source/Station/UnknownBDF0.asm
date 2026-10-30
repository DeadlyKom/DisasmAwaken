                module Station
                module UnknownBDF0
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #5DF0..#5E1A
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
Entry:          CP #21
                JR C, @Station.UnknownBDF0.PointBDF8                            ; переход, если флаг Carry установлен


                CALL @Station.DrawGlyph.Entry
                RET


PointBDF8:      SUB #1E
                ADD A, A
                ADD A, A
                PUSH HL
                PUSH DE
                LD L, A
                LD H, #00
                LD DE, #BE1B
                ADD HL, DE
                LD A, (HL)
                INC HL
                CALL @Station.DrawGlyph.Entry
                LD A, (HL)
                INC HL
                CALL @Station.DrawGlyph.Entry
                LD A, (HL)
                INC HL
                CALL @Station.DrawGlyph.Entry
                LD A, (HL)
                CALL @Station.DrawGlyph.Entry
                POP DE
                POP HL
                RET


                endmodule
                endmodule
