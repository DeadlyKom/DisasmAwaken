                module ArchiveEngineIrqStack
                ; Документация [кадровое прерывание и стек](../../../Docs/ArchiveEngineStartup.md#прерывание)
Value:          FArchiveEngineIrqStack {
                    #0000,                                                      ; AtmOutputEntry, место адреса #2A53 для RET из ПЗУ
                    #0000,                                                      ; AtmAFOrReturn, место AF и затем возврата из ПЗУ
                    #0000,                                                      ; PagingHLOrAF, HL для ATM-2 или AF для Scorpion
                    #0000,                                                      ; PagingSavedBC, место PUSH BC по #4FB4
                    #0000,                                                      ; NestedReturn, возврат в служебную процедуру
                    #0000,                                                      ; ServiceReturn, возврат в обработчик
                    #0000,                                                      ; AltAF
                    #0000,                                                      ; AltBC
                    #0000,                                                      ; AltDE
                    #0000,                                                      ; AltHL
                    #0000,                                                      ; SavedAF
                    #0000,                                                      ; SavedBC
                    #0000,                                                      ; SavedDE
                    #0000,                                                      ; SavedHL
                    #0000                                                       ; SavedIX
                }
                endmodule
