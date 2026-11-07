                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D780
M1780:          FActionModelHeader {
                    #60,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G1780_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #12,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #16                                                         ; Component2
                }
G1780_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #60,                                                        ; Component0
                    #05,                                                        ; Component1
                    #0A                                                         ; Component2
                }
G1780_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #0B,                                                        ; Component0
                    #04,                                                        ; Component1
                    #50                                                         ; Component2
                }
G1780_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #2C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1780_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1780_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1780_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1780_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1780_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R1780_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1780_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1780_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1780_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1780_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1780_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1780_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1780_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1780_0D:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #55,                                                        ; Vertex3
                    #0F,                                                        ; Vertex4
                    #14                                                         ; Vertex5
                }
R1780_0E:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #05,                                                        ; Vertex3
                    #1E,                                                        ; Vertex4
                    #23                                                         ; Vertex5
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D7DF
                endmodule
