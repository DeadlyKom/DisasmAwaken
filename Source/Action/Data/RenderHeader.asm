                module ActionRenderHeader
                ; Документация [заголовок текущей модели](../../../Docs/ActionRenderHeaderPhysicalData.md)
                assert $ == #9B8D
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FRenderHeaderState {
                    #00,                                                        ; ModeBits, бит 0 задаёт одноосный расчёт, RenderSceneFrame пишет 00 либо 01
                    #00                                                         ; ModelByteOffset, байтовое смещение слова указателя модели в таблице OBJECT3D
                }
                assert $ == #9B8F
                endmodule
