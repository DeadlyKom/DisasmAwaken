                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D864
ROKET:          FActionModelHeader {
                    #52,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #01                                                         ; ScaleExponent
                }
G1864_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #4E,                                                        ; Component1
                    #1A                                                         ; Component2
                }
G1864_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #4B                                                         ; Component2
                }
G1864_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #17,                                                        ; Component1
                    #1A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1864_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1864_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R1864_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R1864_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1864_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R1864_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R1864_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1864_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R1864_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R1864_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1864_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1864_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1864_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1864_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D8B2
                endmodule
