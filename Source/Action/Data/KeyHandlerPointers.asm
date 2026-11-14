                module ActionKeyHandlerPointers
                ; Документация [частичный диспетчер клавиш](../../../Docs/ActionKeyDispatchPrefix.md)
                assert $ == #7017
                ; -----------------------------------------
                ; исходная физическая запись Index00
Index00:        FKeyHandlerPointer {
                    @Action.RequestYNegative.Entry                              ; Target, запрос уменьшения Y с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index01
Index01:        FKeyHandlerPointer {
                    @Action.RequestYPositive.Entry                              ; Target, запрос увеличения Y с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index02
Index02:        FKeyHandlerPointer {
                    @Action.RequestXNegative.Entry                              ; Target, запрос уменьшения X с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index03
Index03:        FKeyHandlerPointer {
                    @Action.RequestXPositive.Entry                              ; Target, запрос увеличения X с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index04
Index04:        FKeyHandlerPointer {
                    @Action.RequestTurnNegative.Entry                           ; Target, запрос уменьшения поворота с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index05
Index05:        FKeyHandlerPointer {
                    @Action.RequestTurnPositive.Entry                           ; Target, запрос увеличения поворота с накопителем повтора
                }
                ; -----------------------------------------
                ; исходная физическая запись Index06
Index06:        FKeyHandlerPointer {
                    @Action.RequestAimOrCollectTarget.Entry                     ; Target, запрос прицельных линий либо притягивание и сбор захваченного объекта по режиму силового луча
                }
                ; -----------------------------------------
                ; исходная физическая запись Index07
Index07:        FKeyHandlerPointer {
                    @Action.IncreaseGaugeWord.Entry                             ; Target, набор скорости с исходной проверкой ограничения
                }
                ; -----------------------------------------
                ; исходная физическая запись Index08
Index08:        FKeyHandlerPointer {
                    @Action.DecreaseGaugeWord.Entry                             ; Target, сброс скорости с исходной проверкой бита 4 отрицательного слова
                }
                ; -----------------------------------------
                ; исходная физическая запись Index09
Index09:        FKeyHandlerPointer {
                    @Action.QueueDiagnosticCounters.Entry                        ; Target, бортовой компьютер из списка настроек, ставит счётчики в очередь
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0A
Index0A:        FKeyHandlerPointer {
                    @Action.ToggleTargetRequest.Entry                           ; Target, переключение младшего бита запроса наведения с двумя сообщениями
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0B
Index0B:        FKeyHandlerPointer {
                    @Action.ClearMissileTargets.Entry                           ; Target, снятие трёх захватов ракет с задержкой повторной команды и сообщением
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0C
Index0C:        FKeyHandlerPointer {
                    @Action.RequestMissile0.Entry                               ; Target, условный запрос по соответствующему захвату
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0D
Index0D:        FKeyHandlerPointer {
                    @Action.RequestMissile1.Entry                               ; Target, условный запрос по соответствующему захвату
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0E
Index0E:        FKeyHandlerPointer {
                    @Action.RequestMissile2.Entry                               ; Target, условный запрос по соответствующему захвату
                }
                ; -----------------------------------------
                ; исходная физическая запись Index0F
Index0F:        FKeyHandlerPointer {
                    @Action.RequestBoost.Entry                                  ; Target, запрос ускорения с проверкой классов и квантованных старших байтов координат
                }
                ; -----------------------------------------
                ; исходная физическая запись Index10
Index10:        FKeyHandlerPointer {
                    @Action.ToggleFreeFlightMode.Entry                          ; Target, условная смена опкода координатного обновления с сообщением о свободном полёте
                }
                ; -----------------------------------------
                ; исходная физическая запись Index11
Index11:        FKeyHandlerPointer {
                    @Action.CycleTargetOverlayMode.Entry                        ; Target, смена режима отображения целей при наличии системы наведения
                }
                ; -----------------------------------------
                ; исходная физическая запись Index12
Index12:        FKeyHandlerPointer {
                    @Action.RequestStationReturn.Entry                          ; Target, однократная команда возврата к станции с переходом в банковый подготовитель загрузки
                }
                ; -----------------------------------------
                ; исходная физическая запись Index13
Index13:        FKeyHandlerPointer {
                    @Action.ToggleTractorMode.Entry                             ; Target, переключение режима силового луча и запроса наведения со снятием захватов
                }
                ; -----------------------------------------
                ; исходная физическая запись Index14
Index14:        FKeyHandlerPointer {
                    @Action.ActivateAntimissileSystem.Entry                     ; Target, поиск первой ракеты класса 11 с целью 1A, установка признаков противоракетной обработки и вывод сегмента
                }
                ; -----------------------------------------
                ; исходная физическая запись Index15
Index15:        FKeyHandlerPointer {
                    @Action.EjectCargo.Entry                                    ; Target, выброс первого ненулевого байта из начала пар груза с сообщением независимо от размещения
                }
                ; -----------------------------------------
                ; исходная физическая запись Index16
Index16:        FKeyHandlerPointer {
                    @Action.EjectMine.Entry                                     ; Target, списание одной мины и попытка создания помеченной записи класса 19
                }
                ; -----------------------------------------
                ; исходная физическая запись Index17
Index17:        FKeyHandlerPointer {
                    @Action.RequestHyperJump.Entry                              ; Target, проверка гиперследа, списание выбранного запаса и перенос пятибайтового контекста перед перезагрузкой ACTION
                }
                ; -----------------------------------------
                ; исходная физическая запись Index18
Index18:        FKeyHandlerPointer {
                    @Action.IgnoreKey.Entry                                     ; Target, адрес обработчика в общей RAM, назначение описывается отдельно для каждой цели
                }
                ; -----------------------------------------
                ; исходная физическая запись Index19
Index19:        FKeyHandlerPointer {
                    @Action.ToggleViewDirection.Entry                           ; Target, разворот базиса, обновление точек и согласованная смена трёх опкодных пар направления вида
                }
                assert $ == #704B
                endmodule
