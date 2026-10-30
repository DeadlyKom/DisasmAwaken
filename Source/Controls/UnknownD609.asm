                module Controls
                module UnknownD609
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1609..#1716
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
Entry:          PUSH BC
                PUSH DE
                PUSH HL
                PUSH AF
                LD A, D
                CALL @Controls.UnknownD30B.Entry
                LD H, D
                LD L, E
                POP AF
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                LD B, #80
                XOR A
                LD (#D188), HL
PointD61F:      LD HL, (#D188)
                ADD A, B
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                JR NC, @Controls.UnknownD609.PointD62B                          ; переход, если флаг Carry сброшен


                SUB B
PointD62B:      SRL B
                JR NC, @Controls.UnknownD609.PointD61F                          ; переход, если флаг Carry сброшен


                POP HL
                POP DE
                POP BC
                RET


PointD633:      LD A, E
                SUB L
                JR NC, @Controls.UnknownD609.PointD649                          ; переход, если флаг Carry сброшен


                LD A, (#D18B)
                AND A
                JR NZ, @Controls.UnknownD609.PointD644                          ; переход, если флаг Z сброшен


                LD A, #7F
                CP H
                JR C, @Controls.UnknownD609.PointD64B                           ; переход, если флаг Carry установлен


                JR @Controls.UnknownD609.PointD649


PointD644:      LD A, #8B
                CP H
                JR NC, @Controls.UnknownD609.PointD64B                          ; переход, если флаг Carry сброшен


PointD649:      POP AF
                RET


PointD64B:      LD (#D186), SP
PointD64F:      LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
                LD D, L
                LD L, E
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.UnknownD609.PointD673                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D672), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD673:      CALL @Controls.UnknownCEA4.Entry
                JR NZ, @Controls.UnknownD609.PointD67E                          ; переход, если флаг Z сброшен


                CALL @Controls.UnknownD925.Entry
                JP @Controls.UnknownD609.PointD681


PointD67E:      CALL @Controls.UnknownD940.Entry
PointD681:      EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.UnknownD609.PointD69A                          ; переход, если флаг Z сброшен


                SCF
                RR B
                JR C, @Controls.UnknownD609.PointD69F                           ; переход, если флаг Carry установлен


PointD68F:      SLL C
                JR C, @Controls.UnknownD609.PointD6A8                           ; переход, если флаг Carry установлен


PointD693:      EXX
                ADD HL, BC
                INC C
PointD696:      ADD HL, BC
                BIT 7, H
                EXX
PointD69A:      JP NZ, @Controls.UnknownD609.PointD64F                          ; переход, если флаг Z сброшен


                JR @Controls.UnknownD609.PointD6C9


PointD69F:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD609.PointD6B1                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD609.PointD68F


PointD6A8:      DEC L
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD609.PointD6B1                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD609.PointD693


PointD6B1:      LD SP, (#D186)
                POP AF
                RET


PointD6B7:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD609.PointD6B1                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD609.PointD6CE


PointD6C0:      DEC L
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD609.PointD6B1                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD609.PointD6D2


PointD6C9:      SCF
                RR B
                JR C, @Controls.UnknownD609.PointD6B7                           ; переход, если флаг Carry установлен


PointD6CE:      SLL C
                JR C, @Controls.UnknownD609.PointD6C0                           ; переход, если флаг Carry установлен


PointD6D2:      EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.UnknownD609.PointD6B1                           ; переход, если флаг Z установлен


PointD6D7:      ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.UnknownD609.PointD6C9                           ; переход, если флаг Z установлен


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
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.UnknownD609.PointD706                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D705), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD706:      LD L, D
                SUB #11
                CPL
                LD (#D716), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                LD SP, HL
                JR @Controls.UnknownD727.Entry


                endmodule
                endmodule
