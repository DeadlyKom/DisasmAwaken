                module ActionPlayerPanelWord
                ; Документация [исходное объявление PLAYER](../../../Docs/ActionPanelPhysicalData.md#архивное-объявление-player)
                assert $ == #A78D
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FArchivedPlayerPanelWord {
                    #0000                                                       ; Value, исходное слово после ACTION, текущий потребитель неизвестен
                }
                assert $ == #A78F
                endmodule
