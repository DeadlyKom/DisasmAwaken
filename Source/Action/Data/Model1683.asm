                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D683
M1683:          FActionModelHeader {
                    #78,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G1683_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #2C,                                                        ; Component0
                    #16,                                                        ; Component1
                    #2A                                                         ; Component2
                }
G1683_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #78,                                                        ; Component0
                    #01,                                                        ; Component1
                    #0F                                                         ; Component2
                }
G1683_02:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #66                                                         ; Component2
                }
G1683_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #15,                                                        ; Component1
                    #4E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1683_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1683_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1683_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1683_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1683_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1683_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1683_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1683_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1683_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1683_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1683_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1683_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1683_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1683_0D:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23,                                                        ; Vertex3
                    #00,                                                        ; Vertex4
                    #41                                                         ; Vertex5
                }
R1683_0E:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #50,                                                        ; Vertex3
                    #0F,                                                        ; Vertex4
                    #14                                                         ; Vertex5
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D6E0
                endmodule
