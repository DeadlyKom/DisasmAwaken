                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D103
KN03grz1:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G1103_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #15,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1103_01:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1103_02:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #3A,                                                        ; Component0
                    #15,                                                        ; Component1
                    #41                                                         ; Component2
                }
G1103_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #21,                                                        ; Component1
                    #4D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1103_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1103_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1103_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1103_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1103_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1103_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1103_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1103_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1103_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1103_09:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #14,                                                        ; Vertex3
                    #2D,                                                        ; Vertex4
                    #32                                                         ; Vertex5
                }
R1103_0A:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41,                                                        ; Vertex3
                    #1E,                                                        ; Vertex4
                    #14                                                         ; Vertex5
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D150
                endmodule
