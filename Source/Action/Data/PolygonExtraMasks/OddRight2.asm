                module ActionExtraMaskOddRight2
                ; Документация [дополнительные пары AND/OR](../../../../Docs/ActionPolygonExtraMaskPairs.md)
                assert $ == #8D5C
                ; -----------------------------------------
                ; исходная физическая запись Mode6
Mode6:          FPolygonLiteralEdgeMask {
                    #00,                                                        ; AndMask, буквальный операнд AND краевого байта в исходном состоянии
                    #00                                                         ; OrMask, буквальный операнд OR краевого байта в исходном состоянии
                }
                ; -----------------------------------------
                ; исходная физическая запись Mode7
Mode7:          FPolygonLiteralEdgeMask {
                    #00,                                                        ; AndMask, буквальный операнд AND краевого байта в исходном состоянии
                    #00                                                         ; OrMask, буквальный операнд OR краевого байта в исходном состоянии
                }
                assert $ == #8D60
                endmodule
