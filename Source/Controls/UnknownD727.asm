                module Controls
                module UnknownD727
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1727..#180E
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
Entry:          LD A, (#D18B)
                AND A
                LD SP, (#D186)
                JR NZ, @Controls.UnknownD727.PointD736                          ; переход, если флаг Z сброшен


                CALL @Controls.UnknownD925.Entry
                JR @Controls.UnknownD609.PointD6C9


PointD736:      CALL @Controls.UnknownD940.Entry
                JR @Controls.UnknownD609.PointD6C9


PointD73B:      LD A, L
                AND #1F
                CP #20
                JR NC, @Controls.UnknownD727.PointD754                          ; переход, если флаг Carry сброшен


                LD A, (#D18B)
                AND A
                JR NZ, @Controls.UnknownD727.PointD74F                          ; переход, если флаг Z сброшен


                LD A, #7F
                CP H
                JR C, @Controls.UnknownD727.PointD756                           ; переход, если флаг Carry установлен


                JR @Controls.UnknownD727.PointD754


PointD74F:      LD A, #8B
                CP H
                JR NC, @Controls.UnknownD727.PointD756                          ; переход, если флаг Carry сброшен


PointD754:      POP AF
                RET


PointD756:      LD (#D186), SP
PointD75A:      LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
                LD D, L
                LD L, E
                LD A, D
                SUB E
                SRL A
                JR NC, @Controls.UnknownD727.PointD773                          ; переход, если флаг Carry сброшен


                LD (#D772), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD773:      CALL @Controls.UnknownCEA4.Entry
                JR NZ, @Controls.UnknownD727.PointD77D                          ; переход, если флаг Z сброшен


                CALL @Controls.UnknownD925.Entry
                JR @Controls.UnknownD727.PointD780


PointD77D:      CALL @Controls.UnknownD940.Entry
PointD780:      EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.UnknownD727.PointD799                          ; переход, если флаг Z сброшен


                SLL C
                JR C, @Controls.UnknownD727.PointD79E                           ; переход, если флаг Carry установлен


PointD78D:      EXX
                ADD HL, BC
                INC C
                EX AF, AF'
                CP C
                JR Z, @Controls.UnknownD727.PointD7A8                           ; переход, если флаг Z установлен


                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
PointD799:      JP NZ, @Controls.UnknownD727.PointD75A                          ; переход, если флаг Z сброшен


                JR @Controls.UnknownD727.PointD7CC


PointD79E:      DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Controls.UnknownD727.PointD7BC                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD727.PointD78D


PointD7A8:      EX AF, AF'
                EXX
                LD A, L
                SUB E
                EXX
                JR Z, @Controls.UnknownD727.PointD7BC                           ; переход, если флаг Z установлен


                JP @Controls.UnknownD609.PointD696


PointD7B2:      EX AF, AF'
                EXX
                LD A, L
                SUB E
                EXX
                JR Z, @Controls.UnknownD727.PointD7BC                           ; переход, если флаг Z установлен


                JP @Controls.UnknownD609.PointD6D7


PointD7BC:      LD SP, (#D186)
                POP AF
                RET


PointD7C2:      DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Controls.UnknownD727.PointD7BC                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD727.PointD7D0


PointD7CC:      SLL C
                JR C, @Controls.UnknownD727.PointD7C2                           ; переход, если флаг Carry установлен


PointD7D0:      EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.UnknownD727.PointD7BC                           ; переход, если флаг Z установлен


                EX AF, AF'
                CP C
                JR Z, @Controls.UnknownD727.PointD7B2                           ; переход, если флаг Z установлен


                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.UnknownD727.PointD7CC                           ; переход, если флаг Z установлен


                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
                LD D, L
                LD L, E
                LD A, D
                SUB E
                SRL A
                JR NC, @Controls.UnknownD727.PointD7FE                          ; переход, если флаг Carry сброшен


                LD (#D7FD), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD7FE:      LD L, D
                SUB #11
                CPL
                LD (#D80E), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                LD SP, HL
PointD80D:      JR @Controls.UnknownD727.PointD80D


                endmodule
                endmodule
