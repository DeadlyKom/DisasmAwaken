                module MapAuxiliaryCodes
; Документация [общие коды и смежная граница](../../../Docs/AuxiliaryMapPoints.md)
                assert $ == #99A3
                ; ActiveCode и CompletionCode совпадают с ячейками состояния миссии
                ; Unknown02..Unknown10 сохранены, карта читает их как числовые управляющие коды
State:          FMapMarkerCodes { #00, #00, #01, #01, #01, #01, #01, #01, #01, #01, #00 }
                ; следующий байт принадлежит InterfaceChoices и служит отрицательной границей исходного снимка
                assert $ == #99AE
                endmodule
