                module Voxel
                module Divide7BitFixed
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Деление младших семи битов A на E с восемью дробными битами, подтверждённый делитель 1..128
; исходная запись 21, файловые смещения #0D57..#0DE8
; In:
;   DE - E делитель от 1 до 128, AF - A числитель, используются только биты 6..0
; Out:
;   DE - floor(((исходный A AND #7F) * 256) / исходный E), A равен D
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   H и B сохраняются, L и C содержат инвертированные байты частного
;   все 32768 сочетаний A=0..255 и E=1..128 сверены с формулой
;   делители 129..255 проверены отдельно и не включены в контракт, встречаются отличия
;   нулевой делитель не поддержан контрактом
;   SLL наполняет младший регистр единицами и пропускает старший бит исходного A
;   семь разрядов целой части и восемь дробных получают последовательным вычитанием E
;   при заёме вычитание отменяется, в регистр частного сдвигается инвертированный разряд
;   в конце два байта инвертируются через CPL и возвращаются в DE
;   при A=2 и E=171 оригинал возвращает 3 вместо математического 2, исходные команды не исправляются
; -----------------------------------------
                ; подготовка частного с восемью дробными битами, контракт делителя ограничен 1..128
Entry:          LD L, A
                XOR A
                SLL L
                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit6                        ; переход, если бит 6 числителя установлен, начать деление с этого разряда


                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit5                        ; переход, если бит 5 числителя установлен, начать деление с этого разряда


                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit4                        ; переход, если бит 4 числителя установлен, начать деление с этого разряда


                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit3                        ; переход, если бит 3 числителя установлен, начать деление с этого разряда


                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit2                        ; переход, если бит 2 числителя установлен, начать деление с этого разряда


                SLL L
                JR C, @Voxel.Divide7BitFixed.IntegerBit1                        ; переход, если бит 1 числителя установлен, начать деление с этого разряда


                SLL L
                JP @Voxel.Divide7BitFixed.IntegerBit0


IntegerBit6:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt6                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt6:      RL L
IntegerBit5:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt5                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt5:      RL L
IntegerBit4:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt4                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt4:      RL L
IntegerBit3:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt3                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt3:      RL L
IntegerBit2:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt2                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt2:      RL L
IntegerBit1:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt1                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt1:      RL L
IntegerBit0:    RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreInt0                         ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreInt0:      RL L
                LD C, L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac7                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac7:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac6                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac6:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac5                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac5:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac4                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac4:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac3                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac3:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac2                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac2:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac1                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac1:     RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.StoreFrac0                        ; переход, если пробное вычитание E не дало заёма, сохранить новый остаток


                ADD A, E
StoreFrac0:     RL L
                ; преобразование инвертированных разрядов частного в возвращаемое слово DE
                LD A, L
                CPL
                LD E, A
                LD A, C
                CPL
                LD D, A
                RET


                endmodule
                endmodule
