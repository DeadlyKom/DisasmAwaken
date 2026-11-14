                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D479
KN20ufo5:       FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G1479_00:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #26,                                                        ; Component1
                    #61                                                         ; Component2
                }
G1479_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #52,                                                        ; Component1
                    #04                                                         ; Component2
                }
G1479_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1B,                                                        ; Component0
                    #28,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G1479_03:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #2F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #28                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1479_00:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1479_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1479_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1479_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1479_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1479_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1479_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1479_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1479_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1479_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1479_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D4BE
                endmodule
