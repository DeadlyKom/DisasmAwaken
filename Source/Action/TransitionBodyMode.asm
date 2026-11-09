                module Action
                module TransitionBodyMode
                ; Документация [алгоритм и проверка](../../Docs/ActionBodyModeTransition.md)
                ; -----------------------------------------
                ; Переключение режима тела и изменение старших слов рабочего вектора
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0964..#09BC
                ; In:
                ;   FirstMode, Stream14 и три старших слова вектора доступны, банк 0 выбран
                ;   стек в общей RAM, генератору доступны четыре временных байта, IRQ не вмешиваются
                ; Out:
                ;   Entry возвращается сразу при режиме 2, иначе устанавливает режим 1 и сбрасывает Stream14 перед CheckRandom
                ;   CheckRandom продвигает Stream14 и только на слове #8746 выставляет режим 2 и три слова #6000, затем передаёт управление на #688A
                ;   LowerWords вычитает #0030 из трёх старших слов и передаёт управление на #679B
                ; Corrupt:
                ;   HL, BC, AF, HL', DE', BC', R, поля режима, SpawnLowLimit, состояние потока, вектор и временные слова по достигнутому пути
                ; Note:
                ;   младшие байты компонент не затрагиваются, старшие слова изменяются по модулю #10000
                ;   66816 сценариев сверяют локальные границы, а оба продолжения описаны отдельно
                ; -----------------------------------------
                ; Проверка режима перед начальным сбросом потока.
Entry:          LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                CP #02
                RET Z                                                           ; выход, если уже включён режим 2

                ; Установка режима 1 и начального состояния потока 14.
                LD A, #01
                LD (@ActionGlyphIndicatorState.Control.FirstMode), A
                LD HL, #1527
                LD (@ActionRandomStreams.Stream14.LowWord), HL
                LD A, #13
                LD (@ActionRandomStreams.Stream14.FoldByte), A
                LD A, #FF
                LD (@ActionApplyParametersState.SpawnLowLimit), A
                ; Продвижение потока и проверка слова перехода в режим 2.
CheckRandom:    CALL @Action.NextRandomWord14.Entry
                LD A, H
                CP #87
                JP NZ, @Action.UpdateBodyMotion.MoveWideVectors                 ; переход, если старший байт слова отличается от #87

                LD A, L
                CP #46
                JP NZ, @Action.UpdateBodyMotion.MoveWideVectors                 ; переход, если младший байт слова отличается от #46

                ; Установка режима 2 и трёх начальных старших слов.
                LD A, #02
                LD (@ActionGlyphIndicatorState.Control.FirstMode), A
                LD HL, #6000
                LD (@ActionTransformWorkVector.Value.Component0.LowWord + 1), HL
                LD (@ActionTransformWorkVector.Value.Component1.LowWord + 1), HL
                LD (@ActionTransformWorkVector.Value.Component2.LowWord + 1), HL
                JP @Action.UpdateBodyMotion.MoveWideVectors

                ; Вычитание #0030 из старших слов с сохранением младших байтов.
LowerWords:     LD HL, (@ActionTransformWorkVector.Value.Component0.LowWord + 1)
                LD BC, #FFD0
                ADD HL, BC
                LD (@ActionTransformWorkVector.Value.Component0.LowWord + 1), HL
                LD HL, (@ActionTransformWorkVector.Value.Component2.LowWord + 1)
                ADD HL, BC
                LD (@ActionTransformWorkVector.Value.Component2.LowWord + 1), HL
                LD HL, (@ActionTransformWorkVector.Value.Component1.LowWord + 1)
                ADD HL, BC
                LD (@ActionTransformWorkVector.Value.Component1.LowWord + 1), HL
                JP @Action.UpdateBodyMotion.SubtractMotion

                endmodule
                endmodule
