                module Voxel
                module Multiply7BitWord
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Умножение младших семи битов A на BC с результатом HL modulo #10000
; исходная запись 21, файловые смещения #0D31..#0D56
; In:
;   BC - беззнаковое слово, AF - A множитель, учитываются только биты 6..0
; Out:
;   HL - ((A AND #7F) * BC) modulo #10000
; Corrupt:
;   HL, AF
; Note:
;   старший бит A пропускается двумя первыми RLA, это не полное умножение восьмибитного A
;   DE, BC, альтернативные и индексные регистры сохраняются
;   развёрнутый сдвиговый алгоритм содержит семь условных добавлений BC
;   результат ограничен 16 битами, переносы сверх HL в результат не включаются
; -----------------------------------------
                ; расчёт произведения по битам 6..0 A, старший бит множителя пропускается
Entry:          LD HL, #0000
                RLA
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF939                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF939:      ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF93E                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF93E:      ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF943                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF943:      ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF948                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF948:      ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF94D                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF94D:      ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.PointF952                        ; переход, если флаг Carry сброшен


                ADD HL, BC
PointF952:      ADD HL, HL
                RLA
                RET NC                                                          ; выход, если флаг Carry сброшен

                ADD HL, BC
                RET


                endmodule
                endmodule
