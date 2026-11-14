                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CC7D
KN28plS5:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0C7D_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0C7D_01:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0C7D_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #57,                                                        ; Component0
                    #00,                                                        ; Component1
                    #36                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0C7D_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0C7D_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0C7D_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0C7D_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0C7D_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0C7D_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CCA5
                endmodule
