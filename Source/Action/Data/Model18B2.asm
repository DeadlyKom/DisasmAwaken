                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D8B2
M18B2:          FActionModelHeader {
                    #01,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
                db #00                                                          ; конец групп компонент
                db #00                                                          ; конец потока примитивов
                assert $ == #D8B6
                endmodule
