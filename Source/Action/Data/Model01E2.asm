                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C1E2
M01E2:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G01E2_00:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #13,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G01E2_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #55,                                                        ; Component0
                    #07,                                                        ; Component1
                    #53                                                         ; Component2
                }
G01E2_02:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #42,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R01E2_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R01E2_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R01E2_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R01E2_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C202
                endmodule
