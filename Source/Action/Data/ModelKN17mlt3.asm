                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C845
KN17mlt3:       FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0845_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #36,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #57                                                         ; Component2
                }
G0845_01:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #00,                                                        ; Component1
                    #66                                                         ; Component2
                }
G0845_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #45,                                                        ; Component0
                    #13,                                                        ; Component1
                    #53                                                         ; Component2
                }
G0845_03:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #1B                                                         ; Component2
                }
G0845_04:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #45,                                                        ; Component0
                    #44,                                                        ; Component1
                    #1C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0845_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0845_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0845_02:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0845_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0845_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0845_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0845_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0845_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R0845_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0845_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0845_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0845_0B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0845_0C:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0845_0D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R0845_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C8A0
                endmodule
