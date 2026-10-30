                module Controls
                module UnknownD10A
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #110A..#1164
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
Entry:          POP BC
                JR C, @Controls.UnknownD10A.PointD117                           ; переход, если флаг Carry установлен


                JR Z, @Controls.UnknownD10A.PointD117                           ; переход, если флаг Z установлен


                JP @Controls.UnknownD0CA.PointD0D7


PointD112:      SET 2, B
                JP @Controls.UnknownD10A.PointD11D


PointD117:      EXX
                DEC C
                JR NZ, @Controls.UnknownD10A.PointD112                          ; переход, если флаг Z сброшен


                SET 3, B
PointD11D:      INC C
                EXX
                POP HL
                LD A, #17
PointD122:      SLA C
                ADC HL, HL
                PUSH AF
                SLA B
                RL E
                RL D
                JR C, @Controls.UnknownD10A.PointD15B                           ; переход, если флаг Carry установлен


                POP AF
                DEC A
                JR NZ, @Controls.UnknownD10A.PointD122                          ; переход, если флаг Z сброшен


                RET


PointD134:      SLA B
                RL E
                RL D
                PUSH AF
                SCF
                RR H
                RR L
                POP AF
                JR C, @Controls.UnknownD10A.PointD14A                           ; переход, если флаг Carry установлен


                PUSH HL
                OR A
                SBC HL, DE
                JR NC, @Controls.UnknownD10A.PointD152                          ; переход, если флаг Carry сброшен


                POP HL
PointD14A:      SCF
                RR D
                OR A
                SBC HL, DE
                JR @Controls.UnknownD10A.PointD163


PointD152:      POP HL
                POP AF
PointD154:      XOR A
                RET


PointD156:      SCF
                RR H
                JR @Controls.UnknownD10A.PointD160


PointD15B:      POP AF
                JR C, @Controls.UnknownD10A.PointD156                           ; переход, если флаг Carry установлен


                RR H
PointD160:      SCF
                RR D
PointD163:      LD A, H
                LD B, D
                ; JP @Controls.UnknownD165.Entry, продолжение в UnknownD165.asm

                endmodule
                endmodule
