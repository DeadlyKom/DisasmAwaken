                module Controls
                module UnknownEC59
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #117B..#11A1
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
Entry:          PUSH HL
                PUSH BC
                PUSH AF
                LD HL, #EC80
                LD B, #10
PointEC61:      LD A, (HL)
                DEC A
                JR Z, @Controls.UnknownEC59.PointEC77                           ; переход, если флаг Z установлен


                INC A
                JR Z, @Controls.UnknownEC59.PointEC70                           ; переход, если флаг Z установлен


                INC HL
                INC HL
                DJNZ @Controls.UnknownEC59.PointEC61

PointEC6C:      POP AF
                POP BC
                POP HL
                RET


PointEC70:      LD HL, #EC80
                DJNZ @Controls.UnknownEC59.PointEC61

                JR @Controls.UnknownEC59.PointEC6C


PointEC77:      LD (HL), D
                INC HL
                LD (HL), E
                INC HL
                LD (#EC5D), HL
                JR @Controls.UnknownEC59.PointEC6C


                endmodule
                endmodule
