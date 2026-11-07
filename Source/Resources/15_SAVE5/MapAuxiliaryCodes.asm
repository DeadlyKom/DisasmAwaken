                module Save5MapAuxiliaryCodes
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0168
State:          FMapMarkerCodes {
                    #00,                                                        ; FMapMarkerCodes.ActiveCode, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.CompletionCode, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown02, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown03, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown04, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown05, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown06, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown07, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown08, значение дискового слота
                    #00,                                                        ; FMapMarkerCodes.Unknown09, значение дискового слота
                    #00                                                         ; FMapMarkerCodes.Unknown10, значение дискового слота
                }
                assert $ == #0173
                endmodule
