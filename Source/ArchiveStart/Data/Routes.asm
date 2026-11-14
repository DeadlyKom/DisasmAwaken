                module ArchiveStartRoutes
                ; Документация [рабочие маршруты](../../../Docs/BankStripArchiveConsumer.md#таблицы-и-вывод)
LeftIndex:      db #FF                                                          ; первый шаг индекса оборачивается в 0
RightIndex:     db #FF                                                          ; первый шаг индекса оборачивается в 0

                ; Пустой исходный буфер левого маршрута, заполняется из таблицы C000.
Left:           FArchiveBankStripRoute {
                    #00,                                                        ; BankIndex
                    #00,                                                        ; FrameCount
                    #0000,                                                      ; Staged00
                    #0000,                                                      ; Staged01
                    #0000,                                                      ; Staged02
                    #0000,                                                      ; Staged03
                    #0000,                                                      ; Staged04
                    #0000,                                                      ; Staged05
                    #0000,                                                      ; Staged06
                    #0000,                                                      ; Staged07
                    #0000,                                                      ; Staged08
                    #0000,                                                      ; Staged09
                    #0000,                                                      ; Staged10
                    #0000,                                                      ; Staged11
                    #0000,                                                      ; Direct00
                    #0000,                                                      ; Direct01
                    #0000,                                                      ; Direct02
                    #0000,                                                      ; Direct03
                    #0000,                                                      ; Direct04
                    #0000,                                                      ; Direct05
                    #0000,                                                      ; Direct06
                    #0000,                                                      ; Direct07
                    #0000,                                                      ; Direct08
                    #0000,                                                      ; Direct09
                    #0000,                                                      ; Direct10
                    #0000                                                       ; Direct11
                }

                ; Пустой исходный буфер правого маршрута, заполняется из таблицы C000.
Right:          FArchiveBankStripRoute {
                    #00,                                                        ; BankIndex
                    #00,                                                        ; FrameCount
                    #0000,                                                      ; Staged00
                    #0000,                                                      ; Staged01
                    #0000,                                                      ; Staged02
                    #0000,                                                      ; Staged03
                    #0000,                                                      ; Staged04
                    #0000,                                                      ; Staged05
                    #0000,                                                      ; Staged06
                    #0000,                                                      ; Staged07
                    #0000,                                                      ; Staged08
                    #0000,                                                      ; Staged09
                    #0000,                                                      ; Staged10
                    #0000,                                                      ; Staged11
                    #0000,                                                      ; Direct00
                    #0000,                                                      ; Direct01
                    #0000,                                                      ; Direct02
                    #0000,                                                      ; Direct03
                    #0000,                                                      ; Direct04
                    #0000,                                                      ; Direct05
                    #0000,                                                      ; Direct06
                    #0000,                                                      ; Direct07
                    #0000,                                                      ; Direct08
                    #0000,                                                      ; Direct09
                    #0000,                                                      ; Direct10
                    #0000                                                       ; Direct11
                }

                endmodule
