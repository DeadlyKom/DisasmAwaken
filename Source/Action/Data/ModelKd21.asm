                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C9F7
Kd21:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G09F7_00:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #12,                                                        ; Component0
                    #20,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G09F7_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #5C,                                                        ; Component0
                    #21,                                                        ; Component1
                    #32                                                         ; Component2
                }
G09F7_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #58,                                                        ; Component0
                    #20,                                                        ; Component1
                    #00                                                         ; Component2
                }
G09F7_03:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #21,                                                        ; Component1
                    #67                                                         ; Component2
                }
G09F7_04:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #14,                                                        ; Component1
                    #61                                                         ; Component2
                }
G09F7_05:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #1F,                                                        ; Component0
                    #14,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R09F7_00:       FActionModelPrimitive2 {
                    #82,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #19                                                         ; Vertex1
                }
R09F7_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #0F,                                                        ; Vertex0
                    #14                                                         ; Vertex1
                }
R09F7_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R09F7_03:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #28,                                                        ; Vertex0
                    #32                                                         ; Vertex1
                }
R09F7_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R09F7_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R09F7_06:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #2D,                                                        ; Vertex0
                    #37                                                         ; Vertex1
                }
R09F7_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R09F7_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R09F7_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R09F7_0A:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #0A,                                                        ; Vertex3
                    #1E,                                                        ; Vertex4
                    #23                                                         ; Vertex5
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CA40
                endmodule
