                module Controls
                module UnknownD53C
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #153C..#156B
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
Entry:          PUSH AF
                LD A, B
                LD (#D18A), A
                POP AF
                LD L, C
                LD C, A
                LD H, #04
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                SRL C
                SRL C
                SRL C
                LD B, #00
                ADD HL, BC
                AND #07
                SUB #08
                NEG
                LD C, A
                LD A, (#D18C)
                AND A
                LD A, C
                LD C, #00
PointD562:      SLL C
                DEC A
                JR NZ, @Controls.UnknownD53C.PointD562                          ; переход, если флаг Z сброшен


                LD A, (#D18A)
                LD B, A
                RET


                endmodule
                endmodule
