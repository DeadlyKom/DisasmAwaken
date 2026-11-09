                module ActionExtraMaskOddLeft1
                ; Документация [дополнительные пары AND/OR](../../../../Docs/ActionPolygonExtraMaskPairs.md)
                assert $ == #8D2E
                ; -----------------------------------------
                ; исходная физическая запись Mode7
Mode7:          FPolygonLiteralEdgeMask {
                    #00,                                                        ; AndMask, буквальный операнд AND краевого байта в исходном состоянии
                    #00                                                         ; OrMask, буквальный операнд OR краевого байта в исходном состоянии
                }
                assert $ == #8D30
                endmodule
