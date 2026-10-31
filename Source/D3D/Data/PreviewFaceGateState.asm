                module PreviewFaceGateState
                ; Документация [код предыдущей ориентации](../../../Docs/PreviewFaceStream.md)
                assert $ == #C27B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewFaceGateState {
                    #00                                                         ; RejectCode, нуль после принятой ориентации, один после отвергнутой, читатель проверяет весь байт
                }
                assert $ == #C27C
                endmodule
