                module ActionTailModelPointers
                ; Документация [дополнительные указатели OBJECT3D](../../../Docs/ActionModelTail.md)
                ; Авторские пары в физическом порядке: IST16, IST_PIRAT, IPRISON, IST_U1, IST_U2, IST_SCINCE, IGIP_PL
                assert $ == #9F00
                ; -----------------------------------------
                ; исходная физическая запись Offset00
Offset00:       FObjectDataPointer {
                    @ActionModels.St16                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset02
Offset02:       FObjectDataPointer {
                    @ActionModels.St16                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset04
Offset04:       FObjectDataPointer {
                    @ActionModels.StPirat                                       ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset06
Offset06:       FObjectDataPointer {
                    @ActionModels.StPirat                                       ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset08
Offset08:       FObjectDataPointer {
                    @ActionModels.Prison                                        ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset0A
Offset0A:       FObjectDataPointer {
                    @ActionModels.Prison                                        ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset0C
Offset0C:       FObjectDataPointer {
                    @ActionModels.StU1                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset0E
Offset0E:       FObjectDataPointer {
                    @ActionModels.StU1                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset10
Offset10:       FObjectDataPointer {
                    @ActionModels.StU2                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset12
Offset12:       FObjectDataPointer {
                    @ActionModels.StU2                                          ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset14
Offset14:       FObjectDataPointer {
                    @ActionModels.StScince                                      ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset16
Offset16:       FObjectDataPointer {
                    @ActionModels.StScince                                      ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset18
Offset18:       FObjectDataPointer {
                    @ActionModels.GipPl                                         ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                ; -----------------------------------------
                ; исходная физическая запись Offset1A
Offset1A:       FObjectDataPointer {
                    @ActionModels.GipPl                                         ; Target, адрес начала дополнительного потока OBJECT3D банка 4
                }
                assert $ == #9F1C
                endmodule
