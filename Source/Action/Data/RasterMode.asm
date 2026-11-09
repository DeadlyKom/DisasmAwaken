                module ActionRasterMode
                ; Документация [физическое состояние линии](../../../Docs/ActionRasterWorkData.md)
                assert $ == #8D4E
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FLineRasterMode {
                    #00,                                                        ; PixelOpcode, полный байт A1 для AND, B1 для OR либо A9 для XOR
                    #00                                                         ; BranchOpcode, полный байт 30 для JR NC либо 38 для JR C
                }
                assert $ == #8D50
                endmodule
