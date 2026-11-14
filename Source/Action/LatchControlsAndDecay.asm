                module Action
                module LatchControlsAndDecay
                ; Физические входы [управления и зерно](../../Docs/ActionInputContextData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionControlDecay.md)
                ; -----------------------------------------
                ; Фиксация запросов управления и фазовое приближение трёх знаковых величин к нулю
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #1192..#1253
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают, сохраняемые части зависят от падающего фронта Request
                ;   Request и SkipDetail содержат текущий и предыдущий общие запросы, X/Y/TurnPrev и Next задают защёлки каналов
                ;   X/Y/TurnPhase содержат полные байты кольцевой фазы, XControl, YControl, TurnControl содержат signed8
                ;   операнды стабильны при чтении, на падающем фронте доступны процедуры и конечный список ReleaseBoostDebrisRecords банка 0
                ;   перенесённый ACTION банка 5 доступен, CPU-стек допускает шесть дополнительных байтов и внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL=0088, D=14, BC=0040 и IY указывает маркер только при Request=0 и прежнем SkipDetail не ноль
                ;   иначе HL, DE, B и IY сохраняются, C=прежний SkipDetail
                ;   E, альтернативные регистры и IX сохраняются, I, IM, IFF и 7FFD сохраняются, SP=входной SP+2
                ;   SkipDetail получает прежний Request, Request обнулён, каждый Prev получает соответствующий Next
                ;   канал со старым Prev не ноль пропущен, остальные сбрасывают пару операндов, вращают Phase и при прежнем бите 0 равном единице сдвигают signed8 к нулю
                ;   на падающем фронте освобождён класс 14, LimitWord и SpeedWord равны 0088, SixthRequest=1
                ;   AF определяется последним каналом, точные формулы и R приведены в документации
                ; Corrupt:
                ;   HL и D только на падающем фронте, BC, AF, IY только на падающем фронте, R, существующие операнды, поля освобождённых записей и шесть временных байтов стека
                ; Note:
                ;   ветвление использует старый Prev, хотя новое Next уже записано, это исходная задержка одного вызова
                ;   Phase является восьмибитным циклическим сдвигом, для исходного 92 затухание допускают три из восьми фаз при непрерывном разрешении
                ;   переход signed8 от FF к нулю использует XOR и возвращает F=44, нулевой неизменяемый канал после AND возвращает F=54
                ;   462929 сценариев проверили все пары общих запросов, фаз и значений, старых и новых запретов каждого канала
                ;   проверены настоящие дочерние процедуры, все позиции класса 14 в трёх состояниях, регистры включая R, RAM и записи стека
                ;   проверка использует банк 0 для настоящего освобождения, полное произведение входов, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Проверка текущего общего запроса Request, прежнее значение SkipDetail загружается в C до его обновления.
Entry:          LD A, #00
                OR A
                LD C, #00
                ; Обновление SkipDetail текущим запросом без изменения флагов проверки Request.
                LD (@ActionProjectionClipState.SkipDetail), A
                JR NZ, @Action.LatchControlsAndDecay.ClearRequest               ; переход, если Request ненулевой, пропустить обработку падающего фронта

                ; Проверка прежнего общего запроса, падение существует только при прежнем ненулевом C.
                CP C
                JR NC, @Action.LatchControlsAndDecay.ClearRequest               ; переход, если прежний запрос также нулевой, падающего фронта нет

                ; Освобождение всех активных записей класса 14 настоящим повторным поиском.
                CALL @Action.ReleaseBoostDebrisRecords.Entry
                ; Обновление исходного ограничивающего слова и рабочего SpeedWord значением 0088.
                LD HL, @ActionControlDecayConst.ResetWord
                LD (@ActionControlDecayState.LimitWord), HL
                LD HL, @ActionControlDecayConst.ResetWord
                LD (@ActionPanelGaugesState.SpeedWord), HL
                ; Создание запроса перерисовки шестой шкалы после сброса SpeedWord.
                LD A, @ActionControlDecayConst.RequestOn
                LD (@ActionPanelGaugesState.SixthRequest), A
                ; Обнуление накопленного общего Request, SkipDetail сохраняет его значение до следующего вызова.
ClearRequest:   XOR A
                LD (@ActionControlDecayState.Request), A
                ; Проверка старого XPrev, затем запись XNext для следующего вызова без замены проверяемых флагов.
                LD A, #00
                OR A
                LD A, #00
                LD (@ActionControlDecayState.XPrev), A
                JR NZ, @Action.LatchControlsAndDecay.LatchY                     ; переход, если старый XPrev ненулевой, пропустить затухание канала

                ; Обновление двух исходных байтов накопления клавиатурных обработчиков канала X.
                LD A, @ActionControlDecayConst.XYReset
                LD (@ActionControlDecayState.XStep0), A
                LD (@ActionControlDecayState.XStep1), A
                ; Расчёт следующей кольцевой XPhase, исходный литерал 92 является изменяемым операндом.
                LD A, @ActionControlDecayConst.PhaseSeed
                RRCA
                LD (@ActionControlDecayState.XPhase), A
                JR NC, @Action.LatchControlsAndDecay.LatchY                     ; переход, если прежний бит 0 фазы нулевой, в этом вызове затухание запрещено

                ; Проверка текущего знакового управления X, нулевое значение не записывается повторно.
                LD A, (@ControlsPointMotionState.XControl)
                AND A
                JR Z, @Action.LatchControlsAndDecay.LatchY                      ; переход, если управление уже нулевое, сохранить его без записи

                JP P, @Action.LatchControlsAndDecay.ReduceX                     ; переход, если управление положительное, уменьшить его на единицу

                ; Расчёт шага отрицательного signed8 к нулю, FF требует отдельного обнуления через XOR.
                ADD A, @ActionControlDecayConst.StepUnit
                JP M, @Action.LatchControlsAndDecay.StoreX                      ; переход, если результат прибавления ещё отрицательный, записать его

                XOR A
                JP @Action.LatchControlsAndDecay.StoreX

                ; Расчёт шага положительного signed8 к нулю.
ReduceX:        SUB @ActionControlDecayConst.StepUnit
                JP P, @Action.LatchControlsAndDecay.StoreX                      ; переход, если результат вычитания неотрицательный, записать его

                XOR A
                ; Обновление соответствующего байта управления с сохранением флагов выбранного арифметического пути.
StoreX:         LD (@ControlsPointMotionState.XControl), A
                ; Проверка старого YPrev, затем запись YNext для следующего вызова без замены проверяемых флагов.
LatchY:         LD A, #00
                OR A
                LD A, #00
                LD (@ActionControlDecayState.YPrev), A
                JR NZ, @Action.LatchControlsAndDecay.LatchTurn                  ; переход, если старый YPrev ненулевой, пропустить затухание канала

                ; Обновление двух исходных байтов накопления клавиатурных обработчиков канала Y.
                LD A, @ActionControlDecayConst.XYReset
                LD (@ActionControlDecayState.YStep0), A
                LD (@ActionControlDecayState.YStep1), A
                ; Расчёт следующей кольцевой YPhase, исходный литерал 92 является изменяемым операндом.
                LD A, @ActionControlDecayConst.PhaseSeed
                RRCA
                LD (@ActionControlDecayState.YPhase), A
                JR NC, @Action.LatchControlsAndDecay.LatchTurn                  ; переход, если прежний бит 0 фазы нулевой, в этом вызове затухание запрещено

                ; Проверка текущего знакового управления Y, нулевое значение не записывается повторно.
                LD A, (@ControlsPointMotionState.YControl)
                AND A
                JR Z, @Action.LatchControlsAndDecay.LatchTurn                   ; переход, если управление уже нулевое, сохранить его без записи

                JP P, @Action.LatchControlsAndDecay.ReduceY                     ; переход, если управление положительное, уменьшить его на единицу

                ; Расчёт шага отрицательного signed8 к нулю, FF требует отдельного обнуления через XOR.
                ADD A, @ActionControlDecayConst.StepUnit
                JP M, @Action.LatchControlsAndDecay.StoreY                      ; переход, если результат прибавления ещё отрицательный, записать его

                XOR A
                JP @Action.LatchControlsAndDecay.StoreY

                ; Расчёт шага положительного signed8 к нулю.
ReduceY:        SUB @ActionControlDecayConst.StepUnit
                JP P, @Action.LatchControlsAndDecay.StoreY                      ; переход, если результат вычитания неотрицательный, записать его

                XOR A
                ; Обновление соответствующего байта управления с сохранением флагов выбранного арифметического пути.
StoreY:         LD (@ControlsPointMotionState.YControl), A
                ; Проверка старого TurnPrev, затем запись TurnNext для следующего вызова без замены проверяемых флагов.
LatchTurn:      LD A, #00
                OR A
                LD A, #00
                LD (@ActionControlDecayState.TurnPrev), A
                RET NZ                                                          ; выход, если старый TurnPrev ненулевой, пропустить затухание канала

                ; Обновление двух исходных байтов накопления клавиатурных обработчиков канала Turn.
                LD A, @ActionControlDecayConst.TurnReset
                LD (@ActionControlDecayState.TurnStep0), A
                LD (@ActionControlDecayState.TurnStep1), A
                ; Расчёт следующей кольцевой TurnPhase, исходный литерал 92 является изменяемым операндом.
                LD A, @ActionControlDecayConst.PhaseSeed
                RRCA
                LD (@ActionControlDecayState.TurnPhase), A
                RET NC                                                          ; выход, если прежний бит 0 фазы нулевой, в этом вызове затухание запрещено

                ; Проверка текущего знакового управления Turn, нулевое значение не записывается повторно.
                LD A, (@ControlsPointMotionState.TurnControl)
                AND A
                RET Z                                                           ; выход, если управление уже нулевое, сохранить его без записи

                JP P, @Action.LatchControlsAndDecay.ReduceTurn                  ; переход, если управление положительное, уменьшить его на единицу

                ; Расчёт шага отрицательного signed8 к нулю, FF требует отдельного обнуления через XOR.
                ADD A, @ActionControlDecayConst.StepUnit
                JP M, @Action.LatchControlsAndDecay.StoreTurn                   ; переход, если результат прибавления ещё отрицательный, записать его

                XOR A
                JP @Action.LatchControlsAndDecay.StoreTurn

                ; Расчёт шага положительного signed8 к нулю.
ReduceTurn:     SUB @ActionControlDecayConst.StepUnit
                JP P, @Action.LatchControlsAndDecay.StoreTurn                   ; переход, если результат вычитания неотрицательный, записать его

                XOR A
                ; Обновление соответствующего байта управления с сохранением флагов выбранного арифметического пути.
StoreTurn:      LD (@ControlsPointMotionState.TurnControl), A
                RET

                endmodule
                endmodule
