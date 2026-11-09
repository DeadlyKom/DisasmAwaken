                module ActionPolygonScratch
                ; Документация [временный кадр заливки](../../../Docs/ActionPolygonFill.md)
                assert $ == #FFDE
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPolygonEdgeScratch {
                    #00,                                                        ; Row, младший байт PUSH HL, текущая строка из D
                    #00                                                         ; MaskPage, старший байт PUSH HL, текущая страница масок из H
                }
                assert $ == #FFE0
                endmodule
