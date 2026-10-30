                module ThreeD
                module UnknownCAB3
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 19, файловые смещения #0AB3..#0AE2
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
Entry:          SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                SUB IXH
                JP PO, @ThreeD.UnknownCAB3.PointCAD6                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAB3.PointCAD6                            ; переход, если флаг P/V сброшен


                DEC A
PointCAD6:      LD (#CB3C), A
                LD A, IYH
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                ; JP @ThreeD.UnknownCAE3.Entry, продолжение в UnknownCAE3.asm

                endmodule
                endmodule
