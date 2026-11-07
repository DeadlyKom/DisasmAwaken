                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D8BA
M18BA:          FActionModelHeader {
                    #28,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G18BA_00:       FActionModelGroup {
                    #71,                                                        ; Mask, комбинации вершин
                    #28,                                                        ; Component0
                    #28,                                                        ; Component1
                    #28                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R18BA_00:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R18BA_01:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R18BA_02:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R18BA_03:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D8D2
                endmodule
