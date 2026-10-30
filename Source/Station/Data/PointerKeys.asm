                module PointerKeys
; Документация [опрос ввода](../../../Docs/PointerInputs.md)
; исходные привязки, RowMask выбирает строку, KeyMask проверяет её активные низкие разряды
                assert $ == #99B6
Up:             FKeyBinding { #FB, #01 }                                        ; RowMask, KeyMask для Up
Down:           FKeyBinding { #FD, #01 }                                        ; RowMask, KeyMask для Down
Left:           FKeyBinding { #DF, #02 }                                        ; RowMask, KeyMask для Left
Right:          FKeyBinding { #DF, #01 }                                        ; RowMask, KeyMask для Right
Action2:        FKeyBinding { #7F, #01 }                                        ; RowMask, KeyMask для Action2
Action1:        FKeyBinding { #7F, #04 }                                        ; RowMask, KeyMask для Action1
                assert $ == #99C2
                endmodule
