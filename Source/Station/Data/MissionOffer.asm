                module MissionOffer
; Документация [генератор предложения](../../../Docs/MissionOffer.md)
                assert $ == #98B0
Entry:          FMissionOfferState {
                    #4B39,                                                      ; FirstWord, исходное значение поля
                    #0006,                                                      ; SecondWord, исходное значение поля
                    #0000,                                                      ; UnknownWord04, исходное значение поля
                    #0000,                                                      ; UnknownWord06, исходное значение поля
                    #0000,                                                      ; UnknownWord08, исходное значение поля
                    #0000,                                                      ; UnknownWord0A, исходное значение поля
                    #03E8,                                                      ; Reward, исходное значение поля
                    #0F,                                                        ; RequiredTonnage, исходное значение поля
                    #01                                                         ; UnknownStatus, исходное значение поля
                }
                assert $ == #98C0
                endmodule
