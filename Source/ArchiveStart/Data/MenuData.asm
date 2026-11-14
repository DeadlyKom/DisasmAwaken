                module ArchiveStartData
                ; Документация [режимы страниц и фазы](../../../Docs/BankStripArchiveConsumer.md)
Page:           FArchiveStartPaging {
                    #00,                                                        ; CurrentCode
                    #00,                                                        ; Visible, основной экран
                    #00,                                                        ; IrqSavedCode
                    #00,                                                        ; NextVisible
                    #08,                                                        ; Bank0
                    #09,                                                        ; Bank1
                    #0A,                                                        ; Bank2
                    #0B,                                                        ; Bank3
                    #0C,                                                        ; Bank4
                    #0D,                                                        ; Bank5
                    #00                                                         ; DefaultCode
                }
Frame:          FArchiveStartFrame {
                    #00,                                                        ; LeftMinor
                    #00,                                                        ; LeftMajor
                    #03,                                                        ; RightMinor
                    #00,                                                        ; RightMajor
                    #00,                                                        ; LeftKeyLatch
                    #00,                                                        ; RightKeyLatch
                    #00,                                                        ; StripPhase
                    #00                                                         ; LayerPhase
                }
                endmodule

                module ArchiveStartFileKeys
Choose1:        FTrDosFileKey { { "choose1 " }, #43 }                           ; первый экран, страница 5
Choose2:        FTrDosFileKey { { "choose2 " }, #43 }                           ; второй экран, страница 7
                endmodule
