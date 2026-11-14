                module ActionPlayerMoney
                ; Документация [перенос полей игрока](../../../Docs/ActionTransferredPlayerFields.md)
                assert $ == #9BD0
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FActionPlayerMoney {
                    #FDE8                                                       ; Money, копия суммы игрока из состояния станции
                }
                assert $ == #9BD2
                endmodule
