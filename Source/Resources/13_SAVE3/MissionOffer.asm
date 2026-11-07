                module Save3MissionOffer
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0075
Entry:          FMissionOfferState {
                    #4B39,                                                      ; FMissionOfferState.FirstWord, значение дискового слота
                    #0006,                                                      ; FMissionOfferState.SecondWord, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord04, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord06, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord08, значение дискового слота
                    #0000,                                                      ; FMissionOfferState.UnknownWord0A, значение дискового слота
                    #03E8,                                                      ; FMissionOfferState.Reward, значение дискового слота
                    #0F,                                                        ; FMissionOfferState.RequiredTonnage, значение дискового слота
                    #01                                                         ; FMissionOfferState.MessageIndex, значение дискового слота
                }
                assert $ == #0085
                endmodule
