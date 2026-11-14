                module ActionParameterSet
                ; Документация [поля очереди и параметров](../../../Docs/ActionQueueParameterPhysicalData.md)
                ; LegacyHitPower [архивный потребитель и нынешнее чтение](../../../Docs/ActionLegacyHitPower.md)
                assert $ == #9BA4
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FActionParameterSet {
                    #00,                                                        ; Link1ABaseLimit, поле 00, базовый порог связи 1A при сброшенном бите 3 LinkFlags, адрес изменяемого операнда F79C
                    #00,                                                        ; LegacyHitPower, архивная мощность лазера по игроку PMLPI, текущий ApplyParameterSet читает без применения
                    #00,                                                        ; OtherLinkLimit, поле 02, порог для LinkedIndex, отличного от 1A, адрес изменяемого операнда F798
                    #00,                                                        ; RegenPhaseStep, поле 03, шаг фазы восстановления первой шкалы, адрес изменяемого операнда A968
                    #00,                                                        ; PairedLineStep, поле 04, шаг фазового допуска RequestPairedAimLines, адрес изменяемого операнда 63B9
                    #00,                                                        ; ThirdGaugeStep, поле 05, шаг фазы повышения третьей шкалы, адрес изменяемого операнда A8B5
                    #00,                                                        ; SpawnLowAndBias, общий начальный SpawnLowLimit и база пересчёта SpawnBiasBase
                    #00,                                                        ; Class0RLimit, поле 07, изменяемый операнд CP аппаратного R в ConfigureClass0Link, адрес изменяемого операнда 6615
                    #00,                                                        ; RandomLowLimit, поле 08, изменяемый операнд CP младшего байта Stream10 в FindFilteredRecordOr26, адрес изменяемого операнда E6E7
                    #00,                                                        ; LinkedRLimit, поле 09, порог R обратной связи в CheckAndToggleLinkedOverlay, адрес изменяемого операнда E823
                    #00,                                                        ; Class3RLimit, поле 0A, изменяемый операнд CP аппаратного R в ConfigureClass3Link, адрес изменяемого операнда 65E5
                    #00,                                                        ; SavedLowLimit, поле 0B, нижний предел младшего байта сохранённого слова с верхним байтом 23, адрес изменяемого операнда 79A4
                    #00,                                                        ; SpawnValueMask, поле 0C, маска OR кандидата EffectReserve в обоих создателях, адрес изменяемого операнда 7E07
                    #00,                                                        ; SpawnValueCap, поле 0D, исключённый верхний предел EffectReserve, ноль даёт FF, адрес изменяемого операнда 7E09
                    #00                                                         ; SpawnField11, поле 0E, значение Unknown11 после непересекающихся случайных масок, адрес изменяемого операнда 7DE4
                }
                assert $ == #9BB3
                endmodule
