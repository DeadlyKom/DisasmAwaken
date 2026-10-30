                module Controls
                module UnknownD515
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1515..#153B
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
Entry:          LD L, C
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
                LD B, A
                LD A, (#D18C)
                AND A
                LD A, B
                LD B, #FF
                INC A
PointD532:      SRL B
                DEC A
                JR NZ, @Controls.UnknownD515.PointD532                          ; переход, если флаг Z сброшен


                LD A, B
                CPL
                LD B, A
                LD E, L
                RET


                endmodule
                endmodule
