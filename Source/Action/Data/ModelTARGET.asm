                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D8B2
                ; Авторский пакет TARGET, хвост после ограничителей подключён отдельно.
TARGET:         FActionModelHeader {
                    #01,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #01                                                         ; ScaleExponent
                }
                db #00                                                          ; конец групп компонент
                db #00                                                          ; конец потока примитивов
                assert $ == #D8B6
                endmodule
