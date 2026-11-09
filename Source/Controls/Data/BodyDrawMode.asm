                module ControlsBodyDrawMode
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #CEF9
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FBodyDrawMode {
                    #00                                                         ; Mode, режим малого рисователя, поддерживаются полные коды 0..3
                }
                assert $ == #CEFA
                endmodule
