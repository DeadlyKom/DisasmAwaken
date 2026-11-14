                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E51F
StPirat:        FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G251F_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G251F_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #58,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #28                                                         ; Component2
                }
G251F_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R251F_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #32                                                         ; Vertex1
                }
R251F_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #14,                                                        ; Vertex0
                    #19                                                         ; Vertex1
                }
R251F_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #37,                                                        ; Vertex0
                    #3C                                                         ; Vertex1
                }
R251F_03:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #0F                                                         ; Vertex1
                }
R251F_04:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #1E,                                                        ; Vertex0
                    #23                                                         ; Vertex1
                }
R251F_05:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #2D,                                                        ; Vertex0
                    #46                                                         ; Vertex1
                }
R251F_06:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #00,                                                        ; Vertex0
                    #05                                                         ; Vertex1
                }
R251F_07:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #4B,                                                        ; Vertex0
                    #28                                                         ; Vertex1
                }
R251F_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R251F_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R251F_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R251F_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R251F_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R251F_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R251F_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R251F_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R251F_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R251F_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R251F_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R251F_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R251F_14:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R251F_15:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R251F_16:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R251F_17:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R251F_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R251F_19:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R251F_1A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R251F_1B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R251F_1C:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R251F_1D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R251F_1E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R251F_1F:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #73                                                         ; Vertex2
                }
R251F_20:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R251F_21:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E5C1
                endmodule
