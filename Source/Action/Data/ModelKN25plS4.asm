                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CAEE
KN25plS4:       FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0AEE_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0AEE_01:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #32,                                                        ; Component1
                    #21                                                         ; Component2
                }
G0AEE_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #56,                                                        ; Component0
                    #00,                                                        ; Component1
                    #59                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0AEE_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0AEE_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0AEE_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0AEE_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0AEE_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CB13
                endmodule
