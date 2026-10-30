                module Voxel
                module Divide7BitFixed
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
                JR C, @Voxel.Divide7BitFixed.PointF978                          ; переход, если флаг Carry установлен


                SLL L
                JR C, @Voxel.Divide7BitFixed.PointF97F                          ; переход, если флаг Carry установлен


                SLL L
                JR C, @Voxel.Divide7BitFixed.PointF986                          ; переход, если флаг Carry установлен


                SLL L
                JR C, @Voxel.Divide7BitFixed.PointF98D                          ; переход, если флаг Carry установлен


                SLL L
                JR C, @Voxel.Divide7BitFixed.PointF994                          ; переход, если флаг Carry установлен


                SLL L
                JR C, @Voxel.Divide7BitFixed.PointF99B                          ; переход, если флаг Carry установлен


                SLL L
                JP @Voxel.Divide7BitFixed.PointF9A2


PointF978:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF97D                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF97D:      RL L
PointF97F:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF984                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF984:      RL L
PointF986:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF98B                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF98B:      RL L
PointF98D:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF992                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF992:      RL L
PointF994:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF999                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF999:      RL L
PointF99B:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9A0                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9A0:      RL L
PointF9A2:      RLA
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9A7                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9A7:      RL L
                LD C, L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9AF                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9AF:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9B6                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9B6:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9BD                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9BD:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9C4                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9C4:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9CB                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9CB:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9D2                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9D2:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9D9                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9D9:      RL L
                ADD A, A
                SBC A, E
                JR NC, @Voxel.Divide7BitFixed.PointF9E0                         ; переход, если флаг Carry сброшен


                ADD A, E
PointF9E0:      RL L
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
