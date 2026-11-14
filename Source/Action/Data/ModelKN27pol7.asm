                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CBEC
KN27pol7:       FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0BEC_00:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0BEC_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #64,                                                        ; Component0
                    #00,                                                        ; Component1
                    #47                                                         ; Component2
                }
G0BEC_02:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #31,                                                        ; Component1
                    #6B                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0BEC_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0BEC_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0BEC_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0BEC_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0BEC_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CC11
                endmodule
