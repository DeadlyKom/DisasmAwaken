                module MouseInput
; Документация [мышь](../../../Docs/MouseInput.md)
; семь независимых байтов флагов и два последних аппаратных счётчика
                assert $ == #6585
State:          FMouseInput {
                    #00,                                                        ; FMouseInput.Action2
                    #00,                                                        ; FMouseInput.Up
                    #00,                                                        ; FMouseInput.Down
                    #00,                                                        ; FMouseInput.Right
                    #00,                                                        ; FMouseInput.Left
                    #00,                                                        ; FMouseInput.Action1
                    #00,                                                        ; FMouseInput.ExtraButton
                    #00,                                                        ; FMouseInput.PreviousX
                    #00                                                         ; FMouseInput.PreviousY
                }
                assert $ == #658E
                endmodule
