                module Save5MissionOffer
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0075
Entry:          FMissionOfferState {
                    #0000,                                                      ; FMissionOfferState.FirstWord, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.SecondWord, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord04, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord06, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord08, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord0A, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.Reward, значение дискового слота
                    #00,                                                        ; FMissionOfferState.RequiredTonnage, значение дискового слота
                    #00                                                         ; FMissionOfferState.MessageIndex, значение дискового слота
                }
                assert $ == #0085
                endmodule
