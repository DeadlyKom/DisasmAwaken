                module Controls
                module BuildBodyProjection
                ; Документация [алгоритм и проверка](../../Docs/ControlsBodyProjection.md)
                ; -----------------------------------------
                ; Выбор глубины, кодирование двух смещений и расчёт радиуса проекции
                ; исходная запись 22, банк 1, смещения #0F0B..#10C9
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают
                ;   банк 1 выбран, Mode задаёт режим, Component0..2 содержат знак и 23-битный модуль
                ;   на CPU-стеке внешний возврат, шесть байтов под ним доступны временным CALL и PUSH
                ; Out:
                ;   при успехе A=1, OffsetX, OffsetY, Flags и Radius записаны, точные HL, DE, BC, F описаны в документации
                ;   при отказе A=0, F=44, ранее выполненные записи глубины и OffsetX сохраняются
                ;   B' содержит накопленные флаги, C'=3 до отношений, 2 после первого, 1 после второго
                ;   SP=входной SP+2, оба отказа отношений возвращают сразу вызывающему проекции
                ;   HL', DE', AF', IX, IY сохраняются, I, IM, IFF и страница не меняются
                ;   R и значения временных байтов CPU-стека моделью не доказаны, прерывания не исполнялись
                ; Corrupt:
                ;   HL, DE, BC, AF, BC', R, проекция, знак выбранной глубины и шесть временных байтов стека
                ; Note:
                ;   Mode=0 или 1 выбирает Component2 как глубину, остальные значения выбирают Component0
                ;   положительная глубина требуется для Mode=0 и Mode>=3, отрицательная для Mode=1 и Mode=2
                ;   LoadLowWords является внутренним входом нормализатора отношения, обычный CALL туда недопустим
                ;   полное декартово произведение компонент не перебрано, числовые формулы и границы проверки приведены в документации
                ; -----------------------------------------
                ; Создание накопителя направлений и двух признаков N<=Q в альтернативном B.
Entry:          EXX
                LD BC, @ControlsProjectConst.FirstCoord
                EXX
                LD A, (@ControlsSmallBodiesState.Mode)
                AND A
                JP NZ, @Controls.BuildBodyProjection.CheckMode1                 ; переход, если Mode отличается от нуля, проверяется следующий режим

                ; Проверка требуемого знака глубины режима 0.
                LD A, (@ActionComponentWork.Component2.High)
                BIT @ControlsProjectConst.SignBit, A
                JP NZ, @Controls.ContinueProjectionRatio.RejectProject          ; переход, если Component2 отрицателен, режим 0 отвергает проекцию

                AND @ControlsProjectConst.HighMask
                ; Обновление глубины до вычисления смещений, последующий отказ эту запись не откатывает.
                LD (@ActionComponentWork.Component2.High), A
                LD HL, (@ActionComponentWork.Component2.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component0.Middle)
                LD A, (@ActionComponentWork.Component2.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component0.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR NZ, @Controls.BuildBodyProjection.ProjectAxisX               ; переход, если Component0 отрицателен, направление XPlus не устанавливается

                EXX
                SET @ControlsProjectConst.XPlusBit, B
                EXX
                ; Расчёт кода горизонтального отношения, отказ снимает возврат этого CALL.
ProjectAxisX:   AND @ControlsProjectConst.HighMask
                LD H, A
                CALL @Controls.EncodeProjectionRatio.Entry
                LD A, D
                LD (@ControlsBodyProjection.Value.OffsetX), A
                LD HL, (@ActionComponentWork.Component2.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component1.Middle)
                LD A, (@ActionComponentWork.Component2.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component1.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR NZ, @Controls.BuildBodyProjection.ProjectAxisY               ; переход, если Component1 отрицателен, направление YMinus не устанавливается

                EXX
                SET @ControlsProjectConst.YMinusBit, B
                EXX
                ; Расчёт вертикального отношения после уже записанного OffsetX.
ProjectAxisY:   AND @ControlsProjectConst.HighMask
                LD H, A
                CALL @Controls.EncodeProjectionRatio.Entry
                LD A, D
                LD (@ControlsBodyProjection.Value.OffsetY), A
                EXX
                LD A, B
                EXX
                LD (@ControlsBodyProjection.Value.Flags), A
                LD A, (@ActionComponentWork.Component2.High)
                AND A
                JR NZ, @Controls.BuildBodyProjection.RadiusDepth2               ; переход, если старший байт глубины ненулевой, требуется масштабирование радиуса

                LD HL, @ControlsProjectConst.DepthLimit
                LD DE, (@ActionComponentWork.Component2.Low)
                SBC HL, DE
                JR C, @Controls.BuildBodyProjection.RadiusDepth2                ; переход, если глубина больше A000, радиус рассчитывается по старшему слову

                LD A, @ControlsProjectConst.RadiusMax
                JR @Controls.BuildBodyProjection.StoreDepth2

                ; Расчёт радиуса по старшему слову глубины, исходная дальняя проверка при 23-битном модуле недостижима.
RadiusDepth2:   LD HL, @ControlsProjectConst.DepthLimit
                LD DE, (@ActionComponentWork.Component2.Middle)
                OR A
                SBC HL, DE
                JP C, @Controls.ContinueProjectionRatio.RejectProject           ; переход, если старшее слово глубины больше A000, проекция отвергается

                LD A, (@ActionComponentWork.Component2.High)
                AND A
                JR Z, @Controls.BuildBodyProjection.ByteRadius2                 ; переход, если старший байт глубины нулевой, используется байтовый делитель

                LD B, A
                LD A, (@ActionComponentWork.Component2.Middle)
                LD C, A
                XOR A
                LD E, @ControlsProjectConst.RadiusScale
                ; Расчёт нормализованных коэффициентов радиуса с сохранением исходных усечений.
ScaleRadius2:   SLA C
                RL B
                JR C, @Controls.BuildBodyProjection.DivideRadius2               ; переход, если старший разряд знаменателя вышел в Carry, нормализация завершена

                SLA E
                RLA
                JR @Controls.BuildBodyProjection.ScaleRadius2

DivideRadius2:  SCF
                RR B
                CALL @Controls.DivideWordByByte.Entry
                LD A, D
                JR @Controls.BuildBodyProjection.StoreDepth2

ByteRadius2:    LD A, (@ActionComponentWork.Component2.Middle)
                LD B, A
                LD A, @ControlsProjectConst.RadiusScale
                CALL @Controls.DivideByteFraction.Entry
                LD A, D
StoreDepth2:    JP @Controls.BuildBodyProjection.StoreRadius

                ; Проверка режима с отрицательной Component2.
CheckMode1:     DEC A
                JR NZ, @Controls.BuildBodyProjection.CheckMode2                 ; переход, если Mode отличается от единицы, проверяется следующий режим

                LD A, (@ActionComponentWork.Component2.High)
                BIT @ControlsProjectConst.SignBit, A
                JP Z, @Controls.ContinueProjectionRatio.RejectProject           ; переход, если Component2 неотрицателен, режим 1 отвергает проекцию

                AND @ControlsProjectConst.HighMask
                LD (@ActionComponentWork.Component2.High), A
                LD HL, (@ActionComponentWork.Component2.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component0.Middle)
                LD A, (@ActionComponentWork.Component2.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component0.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR Z, @Controls.BuildBodyProjection.UseDepth2X                  ; переход, если Component0 неотрицателен, обратное направление XPlus не устанавливается

                AND @ControlsProjectConst.HighMask
                LD H, A
                EXX
                SET @ControlsProjectConst.XPlusBit, B
                EXX
UseDepth2X:     JP @Controls.BuildBodyProjection.ProjectAxisX

                ; Проверка режима с отрицательной Component0.
CheckMode2:     DEC A
                JP NZ, @Controls.BuildBodyProjection.PositiveDepth0             ; переход, если Mode отличается от двух, используется положительная Component0

                LD A, (@ActionComponentWork.Component0.High)
                BIT @ControlsProjectConst.SignBit, A
                JP Z, @Controls.ContinueProjectionRatio.RejectProject           ; переход, если Component0 неотрицателен, режим 2 отвергает проекцию

                AND @ControlsProjectConst.HighMask
                LD (@ActionComponentWork.Component0.High), A
                LD HL, (@ActionComponentWork.Component0.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component2.Middle)
                LD A, (@ActionComponentWork.Component0.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component2.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR NZ, @Controls.BuildBodyProjection.ProjectAxisZ               ; переход, если Component2 отрицателен, направление XPlus не устанавливается

                EXX
                SET @ControlsProjectConst.XPlusBit, B
                EXX
                ; Расчёт горизонтального отношения Component2 к Component0.
ProjectAxisZ:   AND @ControlsProjectConst.HighMask
                LD H, A
                CALL @Controls.EncodeProjectionRatio.Entry
                LD A, D
                LD (@ControlsBodyProjection.Value.OffsetX), A
                LD HL, (@ActionComponentWork.Component0.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component1.Middle)
                LD A, (@ActionComponentWork.Component0.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component1.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR NZ, @Controls.BuildBodyProjection.ProjectAxisY0              ; переход, если Component1 отрицателен, направление YMinus не устанавливается

                EXX
                SET @ControlsProjectConst.YMinusBit, B
                EXX
                ; Расчёт вертикального отношения Component1 к Component0.
ProjectAxisY0:  AND @ControlsProjectConst.HighMask
                LD H, A
                CALL @Controls.EncodeProjectionRatio.Entry
                LD A, D
                LD (@ControlsBodyProjection.Value.OffsetY), A
                EXX
                LD A, B
                EXX
                LD (@ControlsBodyProjection.Value.Flags), A
                LD A, (@ActionComponentWork.Component0.High)
                AND A
                JR NZ, @Controls.BuildBodyProjection.RadiusDepth0               ; переход, если старший байт глубины ненулевой, требуется масштабирование радиуса

                LD HL, @ControlsProjectConst.DepthLimit
                LD DE, (@ActionComponentWork.Component0.Low)
                SBC HL, DE
                JR C, @Controls.BuildBodyProjection.RadiusDepth0                ; переход, если глубина больше A000, радиус рассчитывается по старшему слову

                LD A, @ControlsProjectConst.RadiusMax
                JR @Controls.BuildBodyProjection.StoreDepth0

                ; Расчёт радиуса по Component0, дальний отказ недостижим для модуля не больше 7FFFFF.
RadiusDepth0:   LD HL, @ControlsProjectConst.DepthLimit
                LD DE, (@ActionComponentWork.Component0.Middle)
                OR A
                SBC HL, DE
                JP C, @Controls.ContinueProjectionRatio.RejectProject           ; переход, если старшее слово глубины больше A000, проекция отвергается

                LD A, (@ActionComponentWork.Component0.High)
                AND A
                JR Z, @Controls.BuildBodyProjection.ByteRadius0                 ; переход, если старший байт глубины нулевой, используется байтовый делитель

                LD B, A
                LD A, (@ActionComponentWork.Component0.Middle)
                LD C, A
                XOR A
                LD E, @ControlsProjectConst.RadiusScale
                ; Расчёт нормализованного делителя радиуса для глубины Component0.
ScaleRadius0:   SLA C
                RL B
                JR C, @Controls.BuildBodyProjection.DivideRadius0               ; переход, если старший разряд знаменателя вышел в Carry, нормализация завершена

                SLA E
                RLA
                JP @Controls.BuildBodyProjection.ScaleRadius0

DivideRadius0:  SCF
                RR B
                CALL @Controls.DivideWordByByte.Entry
                LD A, D
                JR @Controls.BuildBodyProjection.StoreDepth0

ByteRadius0:    LD A, (@ActionComponentWork.Component0.Middle)
                LD B, A
                LD A, @ControlsProjectConst.RadiusScale
                CALL @Controls.DivideByteFraction.Entry
                LD A, D
StoreDepth0:    JP @Controls.BuildBodyProjection.StoreRadius

                ; Проверка положительной глубины Component0 для всех остальных значений Mode.
PositiveDepth0: LD A, (@ActionComponentWork.Component0.High)
                BIT @ControlsProjectConst.SignBit, A
                JP NZ, @Controls.ContinueProjectionRatio.RejectProject          ; переход, если Component0 отрицателен, режим не меньше трёх отвергает проекцию

                LD HL, (@ActionComponentWork.Component0.Middle)
                EX DE, HL
                LD HL, (@ActionComponentWork.Component2.Middle)
                LD A, (@ActionComponentWork.Component0.Low)
                LD B, A
                LD A, (@ActionComponentWork.Component2.Low)
                LD C, A
                LD A, H
                BIT @ControlsProjectConst.SignBit, A
                JR Z, @Controls.BuildBodyProjection.UseDepth0X                  ; переход, если Component2 неотрицателен, обратное направление XPlus не устанавливается

                EXX
                SET @ControlsProjectConst.XPlusBit, B
                EXX
UseDepth0X:     JP @Controls.BuildBodyProjection.ProjectAxisZ

                ; Обновление радиуса завершает успешную проекцию, F остаётся от расчёта.
StoreRadius:    LD (@ControlsBodyProjection.Value.Radius), A
                LD A, @ControlsProjectConst.ProjectionOK
                RET

                ; Преобразование младших байтов в слова для внешней нормализации, внутренний вход отношения.
LoadLowWords:   LD H, L
                LD L, C
                LD D, E
                LD E, B
                JP @Controls.EncodeProjectionRatio.ShiftLowWords

                endmodule
                endmodule
