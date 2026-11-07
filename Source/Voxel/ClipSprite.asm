                module Voxel
                module ClipSprite
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
                ; Документация [Отсечение спрайта](../../Docs/VoxelSpriteClipBounds.md)
; -----------------------------------------
; Отсечение прямоугольника по горизонтали 64 и вертикали 24 с расчётом краевых смещений
; исходная запись 21, файловые смещения #007F..#0279
                ; In:
                ;   HL, DE задают знаковые начальные X и Y, BC задаёт высоту в B и ширину в C
                ;   HL' задаёт высоту ресурса в H' и ширину в L', DE' указывает ресурс в банке 3
                ;   таблицы #C0..#C3 и буфер #8000..#8BFF доступны, под SP доступны восемь байтов
                ;   IRQ не вмешиваются, SP на время рисования содержит дробный шаг по X
                ; Out:
                ;   при нулевом размере возврат до любых записей, при пустом пересечении изменяются только операнды отсечения
                ;   при видимом пересечении RasterizeSprite обновляет четыре подстроки на пару кодов
                ;   SP восстановлен перед RET, формулы обоих наборов регистров и индексных регистров приведены в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, перечисленные операнды, буфер и до восьми байтов под исходным SP
                ; Note:
                ;   порядок и значения записей в код, кратность записей в буфер и регистры видимого пути сверены на 32 входах
                ;   41084 сценария раннего возврата сверяют регистры и флаги, кроме R
                ;   значения остаточных слов под SP, точное время и IRQ не входят в проверку
                ;   при нечётной левой границе временная маска первого столбца восстанавливается по окончании рисования
; -----------------------------------------
                ; Проверка нулевой высоты и нулевой ширины.
Entry:          LD A, B
                OR A
                RET Z                                                           ; выход, если высота спрайта равна нулю

                LD A, C
                OR A
                RET Z                                                           ; выход, если ширина спрайта равна нулю

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
                ; Проверка левой границы, загруженный X ранее записан в операнд.
                LD HL, #0000
                LD A, H
                AND A
                JP P, @Voxel.ClipSprite.CheckPositiveX                          ; переход, если X неотрицателен, проверить правую границу


                ADC HL, BC
                RET M                                                           ; выход, если правая граница лежит левее нуля

                RET Z                                                           ; выход, если правая граница совпадает с нулём

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
                JP @Voxel.ClipSprite.CheckRight


CheckPositiveX: RET NZ                                                          ; выход, если старший байт неотрицательного X ненулевой

                LD A, L
                CP #40
                RET NC                                                          ; выход, если X не меньше ширины окна 64

CheckRight:     ADD HL, BC
                LD A, H
                OR A
                LD A, L
                JR NZ, @Voxel.ClipSprite.TrimRight                              ; переход, если правый край перешёл границу байта, ширину отсечь


                CP #41
                JR C, @Voxel.ClipSprite.BeginVertical                           ; переход, если правый край не выходит за 64


TrimRight:      SUB #40
                SUB C
                NEG
                LD C, A
BeginVertical:  LD HL, #0000
                ; Проверка верхней границы по исходному Y из операнда.
                LD D, #00
                LD A, H
                AND A
                JP P, @Voxel.ClipSprite.CheckPositiveY                          ; переход, если Y неотрицателен, проверить нижнюю границу


                ADC HL, DE
                RET M                                                           ; выход, если нижняя граница лежит выше нуля

                RET Z                                                           ; выход, если нижняя граница совпадает с нулём

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
                JP @Voxel.ClipSprite.CheckBottom


CheckPositiveY: RET NZ                                                          ; выход, если старший байт неотрицательного Y ненулевой

                LD A, L
                CP #18
                RET NC                                                          ; выход, если Y не меньше высоты окна 24

CheckBottom:    ADD HL, DE
                LD A, H
                OR A
                LD A, L
                JR NZ, @Voxel.ClipSprite.TrimBottom                             ; переход, если нижний край перешёл границу байта, высоту отсечь


                CP #19
                JR C, @Voxel.ClipSprite.BeginSteps                              ; переход, если нижний край не выходит за 24


TrimBottom:     SUB #18
                SUB E
                NEG
                LD E, A
                ; Начало подготовки шагов ресурса по отсечённым размерам.
BeginSteps:     EXX
                LD A, (#EC9D)
                BIT 0, C
                JR Z, @Voxel.ClipSprite.CheckTopTrim                            ; переход, если слева не было отсечения, оставить исходный X


                XOR A
CheckTopTrim:   BIT 1, C
                EXX
                LD B, A
                LD A, (#ECD2)
                JR Z, @Voxel.ClipSprite.BufferAddress                           ; переход, если сверху не было отсечения, оставить исходный Y


                XOR A
BufferAddress:  SRL A
                LD L, D
                RR L
                LD H, A
                LD IXH, E
                LD E, B
                LD A, E
                LD (#EE17), A
                SRL E
                LD A, #30
                JR NC, @Voxel.ClipSprite.StoreParityOp                          ; переход, если видимый левый край чётный


                INC C
                INC C
                LD A, #38
StoreParityOp:  LD (#EE4A), A
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
                JR NC, @Voxel.ClipSprite.WideStride                             ; переход, если исходная ширина ресурса не меньше 17, использовать шаг 32


                LD A, #10
                JR @Voxel.ClipSprite.SkipTopRows


WideStride:     LD A, #20
SkipTopRows:    LD B, A
                EXX
                LD A, B
                AND A
                JR Z, @Voxel.ClipSprite.CheckLeftTrim                           ; переход, если сверху ничего не отсечено


                LD B, IXL
                CALL @Voxel.Multiply7BitWord.Entry
                LD A, H
                AND A
                JR Z, @Voxel.ClipSprite.CheckLeftTrim                           ; переход, если целое число пропускаемых строк ресурса равно нулю


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
CheckLeftTrim:  EXX
                LD A, #00
                AND A
                JR Z, @Voxel.ClipSprite.SaveStack                               ; переход, если слева ничего не отсечено


                EX DE, HL
                LD HL, #0000
                RLA
                LD C, A
                XOR A
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift1                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift1: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift2                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift2: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift3                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift3: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift4                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift4: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift5                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift5: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.LeftSkipShift6                         ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
LeftSkipShift6: ADD HL, HL
                RLA
                RL C
                JR NC, @Voxel.ClipSprite.ApplyLeftSkip                          ; переход, если текущий разряд среза слева равен нулю, не прибавлять частичное произведение


                ADD HL, DE
                ADC A, #00
ApplyLeftSkip:  EX AF, AF'
                LD A, H
                EXX
                LD L, A
                EX AF, AF'
                LD H, A
                ADD HL, DE
                EX DE, HL
                EXX
                EX DE, HL
SaveStack:      LD A, B
                POP BC
                POP DE
                ; Сохранение настоящего стека, в SP на время рисования помещается шаг по X.
                LD (@VoxelSpriteState.SavedSP), SP
                LD (@VoxelSpriteState.SourceStride), A
                LD SP, HL
                LD B, A
                LD A, IXL
                OR A
                JR Z, @Voxel.ClipSprite.StoreRowStep                            ; переход, если целая часть шага по Y равна нулю


                EX AF, AF'
                LD A, C
                EX AF, AF'
                LD C, B
                LD B, #00
                LD HL, #0000
                RLA
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift1                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift1:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift2                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift2:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift3                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift3:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift4                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift4:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift5                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift5:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.RowStepShift6                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
RowStepShift6:  ADD HL, HL
                RLA
                JR NC, @Voxel.ClipSprite.FinishRowStep                          ; переход, если текущий разряд целого шага Y равен нулю, не прибавлять длину строки


                ADD HL, BC
FinishRowStep:  EX AF, AF'
                LD C, A
                LD A, L
                LD IXL, A
                LD A, H
StoreRowStep:   LD (@VoxelSpriteState.RowStepHigh), A
                LD A, #00
                ADD A, C
                RRA
                LD A, #0F
                JR NC, @Voxel.ClipSprite.StoreRightMask                         ; переход, если исключённый правый край чётный, сохранить полную маску #0F


                LD A, (#EE4A)
                CP #38
                JR Z, @Voxel.ClipSprite.PartialMask                             ; переход, если левый край нечётный, ширину второй раз не округлять


                INC C
PartialMask:    XOR A
StoreRightMask: LD (@VoxelSpriteState.RightMaskFull), A
                LD (@VoxelSpriteState.RightMaskOnly), A
                SRL C
                LD A, #20
                SUB C
                JP NC, @Voxel.ClipSprite.PairEntryIndex                         ; переход, если число занятых пар не превышает 32


                XOR A
PairEntryIndex: LD L, A
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
                ; Вычисленный адрес выбирает начало развёрнутого прохода по строке.
                LD BC, #EE7A
                ADD HL, BC
                LD (@VoxelSpriteState.FirstPair), HL
                JR NC, @Voxel.ClipSprite.SaveMaskPatch                          ; переход без замены маски при чётном X и отсутствии переноса, при нечётном X опкод меняется на JR C


                INC HL
                INC HL
                INC HL
                INC HL
                LD (HL), #00
                DEC HL
SaveMaskPatch:  LD (#EE78), HL
                LD IYL, E
                LD C, E
                LD B, D
                RRA
                LD H, #C3
                LD A, #A9
                JR C, @Voxel.ClipSprite.StoreHalfOp                             ; переход, если число пропускаемых групп нечётное, выбрать страницу #C3


                SET 5, C
                LD H, #C0
                LD A, #E9
StoreHalfOp:    LD (@VoxelSpriteState.RowHalfOp), A
                LD A, H
                LD (@VoxelSpriteState.PalettePage), A
                LD D, #0F
                EXX
                XOR A
                LD B, E
NextRow:        EX AF, AF'
                LD H, B
                LD L, #00
                JP #0000


                endmodule
                endmodule
