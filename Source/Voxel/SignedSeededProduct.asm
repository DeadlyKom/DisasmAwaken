                module Voxel
                module SignedSeededProduct
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Знаковое табличное произведение с использованием входного IY как младшей части накопителя
; исходная запись 20, файловые смещения #28A1..#2964
; In:
;   HL - первое знаковое слово, BC - второе знаковое слово, IY - исходная младшая часть накопителя
; Out:
;   HL - знаковый результат накопителя, точная формула и проверенный набор входов приведены в Docs/Effects.md
; Corrupt:
;   HL, DE, BC, AF, AF', IY
; Note:
;   входной IY влияет на результат, это не независимое обычное умножение HL и BC
;   инструкции #E909 и #E90B читают IYL и IYH, полученная ранее младшая часть первого произведения отбрасывается
;   младшие шесть битов модуля BC и следующие восемь битов обрабатываются двумя стадиями
;   знак определяется XOR исходных знаков даже при нулевом модуле одного из слов
;   меняется операнд #E913, IX и альтернативные HL, DE, BC не используются
; -----------------------------------------
                ; сохранение знака результата отдельно от модулей входных слов
Entry:          LD A, B
                XOR H
                EX AF, AF'
                BIT 7, H
                JR Z, @Voxel.SignedSeededProduct.PointE8AF                      ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
PointE8AF:      BIT 7, B
                JR Z, @Voxel.SignedSeededProduct.PointE8BA                      ; переход, если флаг Z установлен


                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
PointE8BA:      LD A, C
                RLA
                RL B
                RLA
                RL B
                LD (#E913), A
                EX DE, HL
                XOR A
                LD C, A
                LD H, C
                LD L, C
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8CF                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8CF:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8D7                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8D7:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8DF                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8DF:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8E7                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8E7:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8EF                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8EF:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8F7                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8F7:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE8FF                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE8FF:      ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.PointE907                     ; переход, если флаг Carry сброшен


                ADD HL, DE
                ADC A, C
PointE907:      ADD HL, HL
                EX DE, HL
                ; чтение входного IY вместо младшего результата первой стадии, зависимость накопителя от вызывающего кода
                LD E, IYL
                LD D, IYH
                EX DE, HL
                LD L, A
                LD H, C
                ADC HL, HL
                LD A, #00
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE91B                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE91B:      ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE926                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE926:      ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE931                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE931:      ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE93C                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE93C:      ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE947                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE947:      ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.PointE952                     ; переход, если флаг Carry сброшен


                ADD IY, DE
                ADC HL, BC
PointE952:      ADD IY, IY
                ADC HL, HL
                LD A, IYH
                ADD A, A
                ADC HL, HL
                EX AF, AF'
                RET P                                                           ; выход, если флаг Sign сброшен

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                RET


                endmodule
                endmodule
