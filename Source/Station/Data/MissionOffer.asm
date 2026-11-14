                module MissionOffer
                ; Документация [генератор предложения](../../../Docs/MissionOffer.md)
                ; [Условная запись промежуточных слов через LANG](../../../Docs/MissionOffer.md#условный-писатель-через-lang)
                assert $ == #98B0
Entry:          FMissionOfferState {
                    #4B39,                                                      ; FirstWord, исходное значение поля
                    #0006,                                                      ; SecondWord, исходное значение поля
                    #0000,                                                      ; UnknownWord04, при Cursor=99A4 первое слово ключа CenterContractMap, исходное назначение неизвестно
                    #0000,                                                      ; UnknownWord06, при Cursor=99A4 второе слово ключа CenterContractMap, исходное назначение неизвестно
                    #0000,                                                      ; UnknownWord08, при Cursor=99A5 первое слово ключа CenterContractMap, исходное назначение неизвестно
                    #0000,                                                      ; UnknownWord0A, при Cursor=99A5 второе слово ключа CenterContractMap, исходное назначение неизвестно
                    #03E8,                                                      ; Reward, исходное значение поля
                    #0F,                                                        ; RequiredTonnage, исходное значение поля
                    #01                                                         ; MessageIndex, исходное значение поля
                }
                assert $ == #98C0
                endmodule
