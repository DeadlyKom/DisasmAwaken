                module Controls
                module DrawLargeCircle
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleDispatch.md)
                ; -----------------------------------------
                ; Выбор и рисование большого кругового тела по спроецированным смещениям
                ; исходная запись 22, банк 1, смещения #1236..#130A
                ; In:
                ;   FBodyProjection.Value задаёт OffsetX, OffsetY, Flags и Radius не меньше 9
                ;   два изменяемых байта D240 задают рисунок и XOR-чередование, код и растр банка 1 доступны
                ;   CPU-стек содержит внешний возврат и допускает четырнадцать временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL, DE, BC, AF и альтернативные пары содержат результат выбранной ветви или проверки допуска
                ;   WorkX, WorkY, CenterX и CenterY готовятся из проекции, дочерняя ветвь может дополнить рабочие поля
                ;   IX загружается из Pattern, IXL затем меняется после обработанных строк, IY, I, IM, IFF и страница сохраняются
                ;   на раннем возврате растр сохранён, иначе он содержит результат выбранной ветви, SP=входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, R, рабочая запись, растр, изменяемые операнды и четырнадцать временных байтов CPU-стека
                ; Note:
                ;   флаги допуска отношений сохраняют Carry независимых сравнений координат, Exchange AF выбирает ось
                ;   угловое сравнение квадратов учитывает сохранённый заём после вычитания 48 из OffsetY
                ;   307200 сценариев до границы передачи и 6589 полных проходов с изменённым рисунком сверяют все 11 выходов
                ;   сверены регистры кроме R, восемь физических банков и кратность непиксельных записей, полный набор входов не исчерпан
                ; -----------------------------------------
                ; Чтение проекции и сохранение исходных смещений в рабочей записи.
Entry:          LD BC, (@ControlsBodyProjection.Value.OffsetY)
                LD (@ControlsCircleWork.Value.WorkY), BC
                ; Загрузка рисунка и XOR-чередования из изменяемого операнда Pattern по D240.
                LD IX, #0000
                LD DE, (@ControlsBodyProjection.Value.Flags)
                ; Расчёт центра Y по знаку YMinus с байтовым оборачиванием.
                LD A, @ControlsLargeCircleConst.HalfHeight
                BIT @ControlsProjectConst.YMinusBit, E
                JR NZ, @Controls.DrawLargeCircle.FinishCenterY                  ; переход, если YMinus установлен, вычесть OffsetY из 48

                ADD A, C
                ADD A, C
FinishCenterY:  SUB C
                LD (@ControlsCircleWork.Value.CenterY), A
                ; Расчёт центра X по знаку XPlus с байтовым оборачиванием.
                LD A, @ControlsLargeCircleConst.CenterX
                BIT @ControlsProjectConst.XPlusBit, E
                JR Z, @Controls.DrawLargeCircle.FinishCenterX                   ; переход, если XPlus сброшен, вычесть OffsetX из 128

                ADD A, B
                ADD A, B
FinishCenterX:  SUB B
                LD (@ControlsCircleWork.Value.CenterX), A
                ; Проверка вертикального порога и допуска отношения, BIT сохраняет Carry сравнения.
                LD A, C
                CP @ControlsLargeCircleConst.HalfHeight
                BIT @ControlsProjectConst.YWithinBit, E
                EX AF, AF'
                ; Проверка горизонтального порога и допуска отношения после сохранения вертикальной проверки в AF prime.
                LD A, B
                CP @ControlsHorizontalCircleConst.OffsetLimit
                BIT @ControlsProjectConst.XWithinBit, E
                JR Z, @Controls.DrawLargeCircle.XRatioRejected                  ; переход, если XWithinBit сброшен, проверить немедленный горизонтальный отказ

                JR NC, @Controls.DrawLargeCircle.CheckOutsideY                  ; переход, если OffsetX не меньше 120, проверить вертикаль для внешнего X

                EX AF, AF'
                JR Z, @Controls.DrawLargeCircle.YRatioRejected                  ; переход, если YWithinBit сброшен, проверить немедленный вертикальный отказ

                JR NC, @Controls.DrawLargeCircle.OutsideY                       ; переход, если OffsetY не меньше 48, рассчитать вертикальное сечение

                JR @Controls.DrawLargeCircle.BothInside

YRatioRejected: RET NC                                                          ; выход, если OffsetY не меньше 48 при сброшенном YWithinBit

                JR @Controls.DrawLargeCircle.OutsideY

XRatioRejected: RET NC                                                          ; выход, если OffsetX не меньше 120 при сброшенном XWithinBit

CheckOutsideY:  EX AF, AF'
                JR Z, @Controls.DrawLargeCircle.BothRatioCheck                  ; переход, если YWithinBit сброшен, проверить вертикальный отказ для внешнего X

                JR NC, @Controls.DrawLargeCircle.OutsideBoth                    ; переход, если OffsetY не меньше 48, рассчитать угловое сечение

                JR @Controls.DrawLargeCircle.OutsideX

BothRatioCheck: RET NC                                                          ; выход, если OffsetY не меньше 48 при сброшенном YWithinBit

                JR @Controls.DrawLargeCircle.OutsideBoth

                ; Расчёт дальнего горизонтального края для проверки полного внутреннего круга.
BothInside:     LD A, B
                ADD A, D
                JR C, @Controls.DrawLargeCircle.OppositeX                       ; переход, если сумма OffsetX и Radius переполнила байт, проверить противоположный край

                CP @ControlsHorizontalCircleConst.OffsetLimit
                JP C, @Controls.DrawInteriorCircle.Entry                        ; переход, если OffsetX плюс Radius меньше 120, рисовать внутренний круг

                ; Расчёт расстояния до противоположного горизонтального края.
OppositeX:      LD A, D
                SUB B
                JR C, @Controls.DrawLargeCircle.SelectXClip                     ; переход, если Radius меньше OffsetX, выбрать одностороннее отсечение

                CP @ControlsHorizontalCircleConst.OffsetLimit
SelectXClip:    JP C, @Controls.DrawHorizontallyClippedCircle.InsideEntry       ; переход, если разность меньше 120 либо отрицательна, рисовать одностороннее отсечение

                JP @Controls.DrawFullWidthCircle.InsideXEntry

                ; Преобразование WorkX к расстоянию от боковой границы.
OutsideX:       LD A, B
                SUB @ControlsHorizontalCircleConst.OffsetLimit
                LD B, A
                LD (@ControlsCircleWork.Value.WorkX), A
                ; Проверка оставшейся ширины после вычитания внешнего WorkX из Radius.
                LD A, D
                SUB B
                RET C                                                           ; выход, если Radius меньше WorkX

                RET Z                                                           ; выход, если Radius равен WorkX и остаточная ширина нулевая

                SUB @ControlsLargeCircleConst.FullWidth
                JP NC, @Controls.DrawFullWidthCircle.Entry                      ; переход, если остаточная ширина не меньше 240, рисовать полную полосу

                JP @Controls.DrawHorizontallyClippedCircle.Entry

                ; Преобразование WorkY к расстоянию от вертикальной границы.
OutsideY:       LD A, C
                SUB @ControlsLargeCircleConst.HalfHeight
                LD C, A
                LD (@ControlsCircleWork.Value.WorkY), A
                ; Проверка допуска вертикального сечения по радиусу.
                LD A, D
                SUB C
                RET C                                                           ; выход, если Radius меньше WorkY

                ; Расчёт квадрата горизонтального радиуса сечения как Radius² минус WorkY².
                LD A, D
                CALL @Controls.ReadByteSquare.Entry
                LD H, D
                LD L, E
                LD A, C
                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                ; Сравнение с квадратом ближнего горизонтального плеча.
                LD A, @ControlsHorizontalCircleConst.OffsetLimit
                SUB B
                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                JP C, @Controls.DrawVerticalCircleSlice.Entry                   ; переход, если сечение не достигает ближнего края, рисовать вертикальное сечение без бокового отсечения

                ; Восстановление разности квадратов для сравнения с дальним плечом.
                ADD HL, DE
                LD A, @ControlsHorizontalCircleConst.OffsetLimit
                ADD A, B
                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                JP NC, @Controls.DrawFullWidthCircleSlice.InsideXEntry          ; переход, если сечение достигает дальнего края, рисовать полноширинное сечение

                JP @Controls.DrawCornerCircleSlice.InsideXEntry

                ; Преобразование обеих осей к расстояниям от границ, заём WorkY сохраняется для первого SBC.
OutsideBoth:    LD A, B
                SUB @ControlsHorizontalCircleConst.OffsetLimit
                LD B, A
                LD A, C
                SUB @ControlsLargeCircleConst.HalfHeight
                LD C, A
                LD (@ControlsCircleWork.Value.WorkY), BC
                ; Расчёт остатка Radius² минус WorkY² с учётом исходного займа.
                LD A, D
                CALL @Controls.ReadByteSquare.Entry
                LD H, D
                LD L, E
                LD A, C
                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                RET C                                                           ; выход, если вычитание квадрата WorkY с заёмом дало отрицательный остаток

                ; Проверка пересечения остаточного сечения с ближним углом.
                LD A, B
                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                RET C                                                           ; выход, если остаток меньше квадрата WorkX

                ; Восстановление остатка и расчёт дальнего углового плеча WorkX плюс 248.
                ADD HL, DE
                LD A, B
                ADD A, @ControlsLargeCircleConst.FarCornerX
                JR C, @Controls.DrawLargeCircle.CornerPartial                   ; переход, если дальнее плечо не помещается в байт, рисовать угловое сечение

                CALL @Controls.ReadByteSquare.Entry
                SBC HL, DE
                JP NC, @Controls.DrawFullWidthCircleSlice.Entry                 ; переход, если остаток не меньше квадрата дальнего плеча, рисовать полноширинное сечение

CornerPartial:  JP @Controls.DrawCornerCircleSlice.Entry

                endmodule
                endmodule
