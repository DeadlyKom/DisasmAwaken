                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C140
KN04trg1:       FActionModelHeader {
                    #69,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0140_00:       FActionModelGroup {
                    #02,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0140_01:       FActionModelGroup {
                    #55,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #3E,                                                        ; Component1
                    #55                                                         ; Component2
                }
G0140_02:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0140_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0140_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0140_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0140_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0140_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C167
                endmodule
