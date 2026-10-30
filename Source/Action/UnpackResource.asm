                module Action
                module UnpackResource
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Полётная копия распаковщика ресурсов с обработкой ссылок
; исходная запись 17, файловые смещения #4B23..#4C37
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
Entry:          PUSH DE
                PUSH HL
                INC HL
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                DEC BC
                EX DE, HL
                ADD HL, BC
                EX DE, HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                DEC BC
                POP HL
                ADD HL, BC
                SBC HL, DE
                ADD HL, DE
                JR C, @Action.UnpackResource.PointAB3C                          ; переход, если флаг Carry установлен


                LD D, H
                LD E, L
PointAB3C:      LDDR
                EX DE, HL
                POP DE
                LD C, #0C
                ADD HL, BC
                PUSH HL
                POP IX
                LD A, #03
PointAB48:      DEC HL
                LD B, (HL)
                DEC HL
                LD C, (HL)
                PUSH BC
                DEC A
                JR NZ, @Action.UnpackResource.PointAB48                         ; переход, если флаг Z сброшен


                LD B, A
                EXX
                LD D, #BF
                LD C, #10
                CALL @Action.UnknownAC38.Entry
PointAB59:      LD A, (IX + #00)
                INC IX
                EXX
PointAB5F:      LD (DE), A
                INC DE
PointAB61:      EXX
PointAB62:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointAB68

                CALL @Action.UnknownAC38.Entry
PointAB68:      JR C, @Action.UnpackResource.PointAB59                          ; переход, если флаг Carry установлен


                LD E, #01
PointAB6C:      LD A, #80
PointAB6E:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointAB74

                CALL @Action.UnknownAC38.Entry
PointAB74:      RLA
                JR C, @Action.UnpackResource.PointAB6E                          ; переход, если флаг Carry установлен


                CP #03
                JR C, @Action.UnpackResource.PointAB80                          ; переход, если флаг Carry установлен


                ADD A, E
                LD E, A
                XOR C
                JR NZ, @Action.UnpackResource.PointAB6C                         ; переход, если флаг Z сброшен


PointAB80:      ADD A, E
                CP #04
                JR Z, @Action.UnpackResource.PointABE7                          ; переход, если флаг Z установлен


                ADC A, #FF
                CP #02
                EXX
PointAB8A:      LD C, A
PointAB8B:      EXX
                LD A, #BF
                JR C, @Action.UnpackResource.PointABA5                          ; переход, если флаг Carry установлен


PointAB90:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointAB96

                CALL @Action.UnknownAC38.Entry
PointAB96:      RLA
                JR C, @Action.UnpackResource.PointAB90                          ; переход, если флаг Carry установлен


                JR Z, @Action.UnpackResource.PointABA0                          ; переход, если флаг Z установлен


                INC A
                ADD A, D
                JR NC, @Action.UnpackResource.PointABA7                         ; переход, если флаг Carry сброшен


                SUB D
PointABA0:      INC A
                JR NZ, @Action.UnpackResource.PointABB0                         ; переход, если флаг Z сброшен


                LD A, #EF
PointABA5:      RRCA
                CP A
PointABA7:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointABAD

                CALL @Action.UnknownAC38.Entry
PointABAD:      RLA
                JR C, @Action.UnpackResource.PointABA7                          ; переход, если флаг Carry установлен


PointABB0:      EXX
                LD H, #FF
                JR Z, @Action.UnpackResource.PointABBE                          ; переход, если флаг Z установлен


                LD H, A
                INC A
                LD A, (IX + #00)
                INC IX
                JR Z, @Action.UnpackResource.PointABC9                          ; переход, если флаг Z установлен


PointABBE:      LD L, A
                ADD HL, DE
                LDIR
PointABC2:      JR @Action.UnpackResource.PointAB61


PointABC4:      EXX
                RRC D
                JR @Action.UnpackResource.PointAB62


PointABC9:      CP #E0
                JR C, @Action.UnpackResource.PointABBE                          ; переход, если флаг Carry установлен


                RLCA
                XOR C
                INC A
                JR Z, @Action.UnpackResource.PointABC4                          ; переход, если флаг Z установлен


                SUB #10
PointABD4:      LD L, A
                LD C, A
                LD H, #FF
                ADD HL, DE
                LDI
                LD A, (IX + #00)
                INC IX
                LD (DE), A
                INC HL
                INC DE
                LD A, (HL)
                JP @Action.UnpackResource.PointAB5F


PointABE7:      LD A, #80
PointABE9:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointABEF

                CALL @Action.UnknownAC38.Entry
PointABEF:      ADC A, A
                JR NZ, @Action.UnpackResource.PointAC16                         ; переход, если флаг Z сброшен


                JR C, @Action.UnpackResource.PointABE9                          ; переход, если флаг Carry установлен


                LD A, #FC
                JR @Action.UnpackResource.PointAC19


PointABF8:      LD B, A
                LD C, (IX + #00)
                INC IX
                CCF
                JR @Action.UnpackResource.PointAB8B


PointAC01:      CP #0F
                JR C, @Action.UnpackResource.PointABF8                          ; переход, если флаг Carry установлен


                JR NZ, @Action.UnpackResource.PointAB8A                         ; переход, если флаг Z сброшен


                LD B, #03
                EX DE, HL
PointAC0A:      POP DE
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                DJNZ @Action.UnpackResource.PointAC0A

                LD HL, #2758
                EXX
                RET


PointAC16:      SBC A, A
                LD A, #EF
PointAC19:      ADD HL, HL
                DJNZ @Action.UnpackResource.PointAC1F

                CALL @Action.UnknownAC38.Entry
PointAC1F:      RLA
                JR C, @Action.UnpackResource.PointAC19                          ; переход, если флаг Carry установлен


                EXX
                JR NZ, @Action.UnpackResource.PointABD4                         ; переход, если флаг Z сброшен


                BIT 7, A
                JR Z, @Action.UnpackResource.PointAC01                          ; переход, если флаг Z установлен


                SUB #EA
                ADD A, A
                LD B, A
PointAC2D:      LD A, (IX + #00)
                INC IX
                LD (DE), A
                INC DE
                DJNZ @Action.UnpackResource.PointAC2D

                JR @Action.UnpackResource.PointABC2


                endmodule
                endmodule
