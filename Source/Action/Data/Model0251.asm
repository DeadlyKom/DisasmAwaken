                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C251
M0251:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0251_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #22,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0251_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0251_02:       FActionModelGroup {
                    #01,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #15,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0251_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0251_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0251_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0251_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C271
                endmodule
