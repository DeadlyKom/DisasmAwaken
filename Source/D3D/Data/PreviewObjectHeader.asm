                module PreviewObjectHeader
                ; Документация [физические поля и потребители](../../../Docs/FinalSyncAndPreviewRecord.md)
                assert $ == #CDC0
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewObjectHeader {
                    #0000,                                                      ; First, первая координата исходной записи, прочитана первым POP
                    #0000,                                                      ; Second, вторая координата исходной записи, прочитана вторым POP
                    #05DC,                                                      ; Third, третья координата исходной записи, управление принимает значения 512..4095
                    #00                                                         ; ModelOffset, байтовое смещение пары указателей модели, устанавливается SetupPreviewModel
                }
                assert $ == #CDC7
                endmodule
