                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C54F
M054F:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G054F_00:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G054F_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #60,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #31                                                         ; Component2
                }
G054F_02:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #31,                                                        ; Component1
                    #6A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R054F_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R054F_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R054F_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R054F_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C56F
                endmodule
