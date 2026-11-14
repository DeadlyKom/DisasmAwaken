                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CF61
micKd2:         FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #01                                                         ; ScaleExponent
                }
G0F61_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #3C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #20                                                         ; Component2
                }
G0F61_01:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #26,                                                        ; Component1
                    #36                                                         ; Component2
                }
G0F61_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0F61_03:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0F61_04:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0F61_00:       FActionModelPrimitive7 {
                    #A7,                                                        ; Header, линия
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #05,                                                        ; Vertex3
                    #2D,                                                        ; Vertex4
                    #28,                                                        ; Vertex5
                    #00                                                         ; Vertex6
                }
R0F61_01:       FActionModelPrimitive7 {
                    #A7,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F,                                                        ; Vertex3
                    #32,                                                        ; Vertex4
                    #2D,                                                        ; Vertex5
                    #0A                                                         ; Vertex6
                }
R0F61_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0F61_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0F61_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0F61_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0F61_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CFA2
                endmodule
