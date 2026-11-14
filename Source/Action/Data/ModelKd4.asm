                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C167
Kd4:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0167_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #09,                                                        ; Component0
                    #14,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0167_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0167_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #61                                                         ; Component2
                }
G0167_03:       FActionModelGroup {
                    #AA,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G0167_04:       FActionModelGroup {
                    #55,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #3E,                                                        ; Component1
                    #4B                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0167_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R0167_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0167_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0167_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0167_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0167_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0167_06:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0167_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0167_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0167_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0167_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0167_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0167_0C:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0167_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R0167_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R0167_0F:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #23,                                                        ; Vertex3
                    #14,                                                        ; Vertex4
                    #50                                                         ; Vertex5
                }
R0167_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R0167_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0167_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R0167_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0167_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C1E2
                endmodule
