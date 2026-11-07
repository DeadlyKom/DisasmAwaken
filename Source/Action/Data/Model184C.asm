                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D84C
M184C:          FActionModelHeader {
                    #24,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G184C_00:       FActionModelGroup {
                    #17,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #1F,                                                        ; Component1
                    #24                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R184C_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R184C_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R184C_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R184C_03:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D864
                endmodule
