                module Voxel
                module ClipSprite
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Отсечение прямоугольника по горизонтали 64 и вертикали 24 с расчётом краевых смещений
; исходная запись 21, файловые смещения #007F..#0279
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
Entry:          LD A, B
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, C
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                XOR A
                LD (#ED7E), A
                LD (#EC9D), HL
                LD (#ECD2), DE
                LD IYL, C
                LD IYH, B
                LD E, B
                EXX
                LD BC, #0000
                EXX
                LD B, #00
                LD HL, #0000
                LD A, H
                AND A
                JP P, @Voxel.ClipSprite.PointECBC                               ; переход, если флаг Sign сброшен


                ADC HL, BC
                RET M                                                           ; выход, если флаг Sign установлен

                RET Z                                                           ; выход, если флаг Z установлен

                LD A, L
                LD HL, #0000
                LD B, C
                LD C, A
                SUB B
                LD B, L
                NEG
                EXX
                LD (#ED7E), A
                SET 0, C
                EXX
                JP @Voxel.ClipSprite.PointECC1


PointECBC:      RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, L
                CP #40
                RET NC                                                          ; выход, если флаг Carry сброшен

PointECC1:      ADD HL, BC
                LD A, H
                OR A
                LD A, L
                JR NZ, @Voxel.ClipSprite.PointECCB                              ; переход, если флаг Z сброшен


                CP #41
                JR C, @Voxel.ClipSprite.PointECD1                               ; переход, если флаг Carry установлен


PointECCB:      SUB #40
                SUB C
                NEG
                LD C, A
PointECD1:      LD HL, #0000
                LD D, #00
                LD A, H
                AND A
                JP P, @Voxel.ClipSprite.PointECF1                               ; переход, если флаг Sign сброшен


                ADC HL, DE
                RET M                                                           ; выход, если флаг Sign установлен

                RET Z                                                           ; выход, если флаг Z установлен

                LD A, L
                LD HL, #0000
                LD D, E
                LD E, A
                SUB D
                LD D, L
                NEG
                EXX
                LD B, A
                SET 1, C
                EXX
                JP @Voxel.ClipSprite.PointECF6


PointECF1:      RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, L
                CP #18
                RET NC                                                          ; выход, если флаг Carry сброшен

PointECF6:      ADD HL, DE
                LD A, H
                OR A
                LD A, L
                JR NZ, @Voxel.ClipSprite.PointED00                              ; переход, если флаг Z сброшен


                CP #19
                JR C, @Voxel.ClipSprite.PointED06                               ; переход, если флаг Carry установлен


PointED00:      SUB #18
                SUB E
                NEG
                LD E, A
PointED06:      EXX
                LD A, (#EC9D)
                BIT 0, C
                JR Z, @Voxel.ClipSprite.PointED0F                               ; переход, если флаг Z установлен


                XOR A
PointED0F:      BIT 1, C
                EXX
                LD B, A
                LD A, (#ECD2)
                JR Z, @Voxel.ClipSprite.PointED19                               ; переход, если флаг Z установлен


                XOR A
PointED19:      SRL A
                LD L, D
                RR L
                LD H, A
                LD IXH, E
                LD E, B
                LD A, E
                LD (#EE17), A
                SRL E
                LD A, #30
                JR NC, @Voxel.ClipSprite.PointED30                              ; переход, если флаг Carry сброшен


                INC C
                INC C
                LD A, #38
PointED30:      LD (#EE4A), A
                ADD HL, DE
                SET 7, H
                EX DE, HL
                PUSH DE
                PUSH BC
                EXX
                LD A, L
                EXX
                LD B, A
                LD E, IYL
                CALL @Voxel.Divide7BitFixed.Entry
                EX DE, HL
                EXX
                LD A, H
                EXX
                LD E, IYH
                PUSH HL
                CALL @Voxel.Divide7BitFixed.Entry
                POP HL
                LD A, E
                LD IXL, D
                EXX
                LD C, A
                EXX
                LD A, B
                CP #11
                JR NC, @Voxel.ClipSprite.PointED5C                              ; переход, если флаг Carry сброшен


                LD A, #10
                JR @Voxel.ClipSprite.PointED5E


PointED5C:      LD A, #20
PointED5E:      LD B, A
                EXX
                LD A, B
                AND A
                JR Z, @Voxel.ClipSprite.PointED7C                               ; переход, если флаг Z установлен


                LD B, IXL
                CALL @Voxel.Multiply7BitWord.Entry
                LD A, H
                AND A
                JR Z, @Voxel.ClipSprite.PointED7C                               ; переход, если флаг Z установлен


                LD B, A
                EXX
                LD A, B
                EXX
                PUSH BC
                LD C, A
                LD A, B
                LD B, #00
                CALL @Voxel.Multiply7BitWord.Entry
                POP BC
                ADD HL, DE
                EX DE, HL
PointED7C:      EXX
                LD A, #00
                AND A
                JR Z, @Voxel.ClipSprite.PointEDD0                               ; переход, если флаг Z установлен


                EX DE, HL
                LD HL, #0000
                RLA
                LD C, A
                XOR A
                RL C
                JR NC, @Voxel.ClipSprite.PointED90                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointED90:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointED99                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointED99:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointEDA2                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointEDA2:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointEDAB                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointEDAB:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointEDB4                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointEDB4:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointEDBD                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointEDBD:      ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.PointEDC6                              ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, #00
PointEDC6:      EX AF, AF'
                LD A, H
                EXX
                LD L, A
                EX AF, AF'
                LD H, A
                ADD HL, DE
                EX DE, HL
                EXX
                EX DE, HL
PointEDD0:      LD A, B
                POP BC
                POP DE
                LD (#F92A), SP
                LD (#F910), A
                LD SP, HL
                LD B, A
                LD A, IXL
                OR A
                JR Z, @Voxel.ClipSprite.PointEE13                               ; переход, если флаг Z установлен


                EX AF, AF'
                LD A, C
                EX AF, AF'
                LD C, B
                LD B, #00
                LD HL, #0000
                RLA
                RLA
                JR NC, @Voxel.ClipSprite.PointEDEF                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEDEF:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEDF4                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEDF4:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEDF9                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEDF9:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEDFE                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEDFE:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEE03                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEE03:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEE08                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEE08:      ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.PointEE0D                              ; переход, если флаг Carry сброшен


                ADD HL, BC
PointEE0D:      EX AF, AF'
                LD C, A
                LD A, L
                LD IXL, A
                LD A, H
PointEE13:      LD (#F918), A
                LD A, #00
                ADD A, C
                RRA
                LD A, #0F
                JR NC, @Voxel.ClipSprite.PointEE27                              ; переход, если флаг Carry сброшен


                LD A, (#EE4A)
                CP #38
                JR Z, @Voxel.ClipSprite.PointEE26                               ; переход, если флаг Z установлен


                INC C
PointEE26:      XOR A
PointEE27:      LD (#F8B5), A
                LD (#F8DB), A
                SRL C
                LD A, #20
                SUB C
                JP NC, @Voxel.ClipSprite.PointEE36                              ; переход, если флаг Carry сброшен


                XOR A
PointEE36:      LD L, A
                LD H, #00
                LD C, L
                LD B, H
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                LD BC, #EE7A
                ADD HL, BC
                LD (#F921), HL
                JR NC, @Voxel.ClipSprite.PointEE53                              ; переход, если флаг Carry сброшен


                INC HL
                INC HL
                INC HL
                INC HL
                LD (HL), #00
                DEC HL
PointEE53:      LD (#EE78), HL
                LD IYL, E
                LD C, E
                LD B, D
                RRA
                LD H, #C3
                LD A, #A9
                JR C, @Voxel.ClipSprite.PointEE67                               ; переход, если флаг Carry установлен


                SET 5, C
                LD H, #C0
                LD A, #E9
PointEE67:      LD (#F905), A
                LD A, H
                LD (#F907), A
                LD D, #0F
                EXX
                XOR A
                LD B, E
                EX AF, AF'
                LD H, B
                LD L, #00
                JP #0000


                endmodule
                endmodule
