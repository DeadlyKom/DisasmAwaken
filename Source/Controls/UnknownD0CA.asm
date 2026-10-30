                module Controls
                module UnknownD0CA
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #10CA..#1109
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
                EXX
                DEC C
                EXX
                OR A
                SBC HL, DE
                JP C, @Controls.UnknownD10A.PointD117                           ; переход, если флаг Carry установлен


                JP Z, @Controls.UnknownD0CA.PointD107                           ; переход, если флаг Z установлен


PointD0D7:      POP HL
                LD A, H
                AND A
                JR Z, @Controls.UnknownCF0B.PointD0C3                           ; переход, если флаг Z установлен


                LD A, #08
PointD0DE:      SLA C
                ADC HL, HL
                JP C, @Controls.UnknownD10A.PointD134                           ; переход, если флаг Carry установлен


                SLA B
                RL E
                RL D
                DEC A
                JR NZ, @Controls.UnknownD0CA.PointD0DE                          ; переход, если флаг Z сброшен


PointD0EE:      LD A, #08
PointD0F0:      ADD HL, HL
                JP C, @Controls.UnknownD10A.PointD134                           ; переход, если флаг Carry установлен


                EX DE, HL
                ADD HL, HL
                EX DE, HL
                DEC A
                JR NZ, @Controls.UnknownD0CA.PointD0F0                          ; переход, если флаг Z сброшен


                LD A, #08
PointD0FC:      SLA H
                JP C, @Controls.UnknownD10A.PointD134                           ; переход, если флаг Carry установлен


                SLA D
                DEC A
                JR NZ, @Controls.UnknownD0CA.PointD0FC                          ; переход, если флаг Z сброшен


                RET


PointD107:      PUSH BC
                LD A, C
                SUB B
                ; JP @Controls.UnknownD10A.Entry, продолжение в UnknownD10A.asm

                endmodule
                endmodule
