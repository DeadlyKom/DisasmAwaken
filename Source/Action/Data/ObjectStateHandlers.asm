                module ActionObjectStateHandlers
                ; Документация [выбор обработчика состояния](../../../Docs/ActionObjectStateDispatch.md)
                assert $ == #EF50
                ; -----------------------------------------
                ; исходная физическая запись State00
State00:        FObjectStateHandler {
                    @Action.StepIdleObjectOffset.Entry                          ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State01
State01:        FObjectStateHandler {
                    @Action.StepSelectedWideVector.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State02
State02:        FObjectStateHandler {
                    @Action.HandleLinkedTargetState.Entry                       ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State03
State03:        FObjectStateHandler {
                    @Action.UpdateLinkedOrNearPhase.Entry                       ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State04
State04:        FObjectStateHandler {
                    @Action.StepFastRecordPhases.Entry                          ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State05
State05:        FObjectStateHandler {
                    @Action.HandleLinkedPhaseState.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State06
State06:        FObjectStateHandler {
                    @Action.StartSmallRecordEffect.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State07
State07:        FObjectStateHandler {
                    @Action.StepTimedRecordDecay.Entry                          ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State08
State08:        FObjectStateHandler {
                    @Action.ApproachTargetRecordAndResolve.Entry                ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State09
State09:        FObjectStateHandler {
                    @Action.UpdatePreferredClass18.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0A
State0A:        FObjectStateHandler {
                    @Action.SweepClass17AndPrepareSpawn.Entry                   ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0B
State0B:        FObjectStateHandler {
                    @Action.SpawnPeriodicClass3Record.Entry                     ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0C
State0C:        FObjectStateHandler {
                    @Action.HandleClass18Proximity.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0D
State0D:        FObjectStateHandler {
                    @Action.HandleSelectedRecordProximity.Entry                 ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0E
State0E:        FObjectStateHandler {
                    @Action.HandleLinkedRecordProximity.Entry                   ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State0F
State0F:        FObjectStateHandler {
                    @Action.UpdatePhaseAndNearVector.Entry                      ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State10
State10:        FObjectStateHandler {
                    @Action.StepTimedLinkedOverlay.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State11
State11:        FObjectStateHandler {
                    @Action.StepTimedPhasePattern.Entry                         ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State12
State12:        FObjectStateHandler {
                    @Action.AcquireLinkAndApplyOffsets.Entry                    ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State13
State13:        FObjectStateHandler {
                    @Action.AdvanceObjectPhaseWait.Entry                        ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State14
State14:        FObjectStateHandler {
                    @Action.AdvanceObjectOffsetRise.Entry                       ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                ; -----------------------------------------
                ; исходная физическая запись State15
State15:        FObjectStateHandler {
                    @Action.AdvanceObjectOffsetFall.Entry                       ; Handler, исходный адрес обработчика состояния, проверка цели выполняется отдельно
                }
                assert $ == #EF7C
                endmodule
