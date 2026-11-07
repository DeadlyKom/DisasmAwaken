                module Voxel
                module SignedSeededProduct
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
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
                JR Z, @Voxel.SignedSeededProduct.CheckBCSign                    ; переход, если первый множитель неотрицателен, его модуль уже готов


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
CheckBCSign:    BIT 7, B
                JR Z, @Voxel.SignedSeededProduct.SplitMagnitude                 ; переход, если второй множитель неотрицателен, его модуль уже готов


                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
SplitMagnitude: LD A, C
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
                JR NC, @Voxel.SignedSeededProduct.UpperShift1                   ; переход, если разряд 13 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift1:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift2                   ; переход, если разряд 12 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift2:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift3                   ; переход, если разряд 11 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift3:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift4                   ; переход, если разряд 10 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift4:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift5                   ; переход, если разряд 9 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift5:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift6                   ; переход, если разряд 8 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift6:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift7                   ; переход, если разряд 7 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift7:    ADD HL, HL
                ADC A, A
                RL B
                JR NC, @Voxel.SignedSeededProduct.UpperShift8                   ; переход, если разряд 6 модуля BC нулевой, слагаемое DE пропускается


                ADD HL, DE
                ADC A, C
UpperShift8:    ADD HL, HL
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
                JR NC, @Voxel.SignedSeededProduct.LowerShift1                   ; переход, если разряд 5 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift1:    ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.LowerShift2                   ; переход, если разряд 4 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift2:    ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.LowerShift3                   ; переход, если разряд 3 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift3:    ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.LowerShift4                   ; переход, если разряд 2 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift4:    ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.LowerShift5                   ; переход, если разряд 1 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift5:    ADD IY, IY
                ADC HL, HL
                RLA
                JR NC, @Voxel.SignedSeededProduct.LowerShift6                   ; переход, если разряд 0 модуля BC нулевой, слагаемое DE пропускается


                ADD IY, DE
                ADC HL, BC
LowerShift6:    ADD IY, IY
                ADC HL, HL
                LD A, IYH
                ADD A, A
                ADC HL, HL
                EX AF, AF'
                RET P                                                           ; выход, если знаки исходных множителей совпадают, отрицание результата не требуется

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
