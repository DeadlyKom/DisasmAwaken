                module ActionBoot
                module BuildReciprocalTable
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Создание двух страниц таблицы через двоичное деление
; исходная запись 17, файловые смещения #01D2..#0211
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
Entry:          LD HL, #9100
                XOR A
                LD E, A
                LD D, A
                LD (HL), A
                INC H
                LD (HL), #F0
                DEC H
                INC L
Point439B:      LD (HL), D
                INC H
                LD (HL), A
                DEC H
                EX AF, AF'
                PUSH HL
                PUSH DE
                LD DE, #74E9
                LD C, L
                SRL C
                RR D
                XOR A
                LD HL, #B8AA
                EXX
                LD H, A
                LD L, A
                LD B, #10
Point43B3:      EXX
                ADD HL, HL
                ADC A, A
                SBC HL, DE
                SBC A, C
                JR NC, @ActionBoot.BuildReciprocalTable.Point43BD               ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
Point43BD:      EXX
                CCF
                RL L
                RL H
                DJNZ @ActionBoot.BuildReciprocalTable.Point43B3

                POP DE
                EX AF, AF'
                ADD HL, DE
                ADC A, B
                EX DE, HL
                POP HL
                INC L
                JR NZ, @ActionBoot.BuildReciprocalTable.Point439B               ; переход, если флаг Z сброшен


                RET


                endmodule
                endmodule
