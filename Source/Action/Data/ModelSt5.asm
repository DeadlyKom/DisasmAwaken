                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DD82
St5:            FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1D82_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #34                                                         ; Component2
                }
G1D82_01:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G1D82_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #54,                                                        ; Component0
                    #00,                                                        ; Component1
                    #27                                                         ; Component2
                }
G1D82_03:       FActionModelGroup {
                    #02,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #55                                                         ; Component2
                }
G1D82_04:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #0A                                                         ; Component2
                }
G1D82_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #09                                                         ; Component2
                }
G1D82_06:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #15                                                         ; Component2
                }
G1D82_07:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0C,                                                        ; Component0
                    #1F,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1D82_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1D82_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1D82_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1D82_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1D82_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1D82_05:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1D82_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1D82_07:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1D82_08:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1D82_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1D82_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1D82_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R1D82_0C:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1D82_0D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1D82_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1D82_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1D82_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1D82_11:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R1D82_12:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1D82_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1D82_14:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R1D82_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1D82_16:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1D82_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DE12
                endmodule
