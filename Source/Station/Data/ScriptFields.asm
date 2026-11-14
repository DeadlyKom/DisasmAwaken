                module StationScriptFields
                ; Документация [режимы и ресурс LANG](../../../Docs/StationScriptFields.md)
                assert $ == #9A3B
ModeM08:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM09:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM10:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM11:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM12:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM13:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeM14:        FScriptModeByte {
                    #00                                                         ; исходный байт режима m
                }
ModeE00:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE01:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE02:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE03:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE04:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE05:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
ModeE06:        FScriptModeByte {
                    #00                                                         ; исходный байт режима e
                }
Group01:        FScriptGroupStart {
                    #FF                                                         ; первый разделитель групп
                }
Record01:       FScriptRecordStart {
                    #FE                                                         ; первый разделитель записей
                }
Payload01:      db #00, #00, #00                                                ; байты до следующего разделителя записей
Record02:       FScriptRecordStart {
                    #FE                                                         ; второй разделитель записей
                }
Payload02:      db #00, #00                                                     ; байты до следующего разделителя групп
Group02:        FScriptGroupStart {
                    #FF                                                         ; второй разделитель групп
                }
Record03:       FScriptRecordStart {
                    #FE                                                         ; разделитель записи после второй группы
                }
Payload03:      db #00, #00, #00, #00, #00                                      ; исходные байты до EmptyCallback
                assert $ == #9A58
                endmodule
