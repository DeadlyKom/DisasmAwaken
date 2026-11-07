                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E0B0
M20B0:          FActionModelHeader {
                    #6B,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G20B0_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #2C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #68                                                         ; Component2
                }
G20B0_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #0A                                                         ; Component2
                }
G20B0_02:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #34                                                         ; Component2
                }
G20B0_03:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #55,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G20B0_04:       FActionModelGroup {
                    #44,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #55                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R20B0_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R20B0_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R20B0_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R20B0_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R20B0_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R20B0_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R20B0_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R20B0_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R20B0_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R20B0_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R20B0_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R20B0_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R20B0_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R20B0_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R20B0_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R20B0_0F:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R20B0_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R20B0_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R20B0_12:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R20B0_13:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R20B0_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R20B0_15:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R20B0_16:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R20B0_17:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R20B0_18:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R20B0_19:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R20B0_1A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R20B0_1B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R20B0_1C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R20B0_1D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R20B0_1E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R20B0_1F:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R20B0_20:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R20B0_21:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E152
                endmodule
