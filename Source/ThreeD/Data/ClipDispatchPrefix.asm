                module ThreeDClipDispatchPrefix
                ; Документация [адресные байты и рабочие ячейки CF00](../../../Docs/ClipDispatchPrefixData.md)
                assert $ == #CF00
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FClipDispatchPrefix {
                    #D3,                                                        ; AppendPointLow, младший байт адреса AppendSecondClipPoint.Entry
                    #E4,                                                        ; ToRightLow, младший байт адреса ClipInsideToRight.Entry
                    #88,                                                        ; ToLeftLow, младший байт адреса ClipInsideToLeft.Entry
                    #00,                                                        ; CornerBlock, нулевой байт разрешает запись углов, любой ненулевой запрещает
                    #3D,                                                        ; ToBottomLow, младший байт адреса ClipInsideToBottom.Entry
                    #7B,                                                        ; ToBottomRLow, младший байт адреса ClipInsideToBottomRight.Entry
                    #95,                                                        ; ToBottomLLow, младший байт адреса ClipInsideToBottomLeft.Entry
                    #00                                                         ; SeenFlags, отметки TL, TR, BL, BR в битах 3..0, обработчики углов сохраняют 7..4
                }
                assert $ == #CF08
                endmodule
