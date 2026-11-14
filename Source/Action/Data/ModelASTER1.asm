                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D930
ASTER1:         FActionModelHeader {
                    #59,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #04                                                         ; ScaleExponent
                }
G1930_00:       FActionModelGroup {
                    #5A,                                                        ; Mask, комбинации вершин
                    #4A,                                                        ; Component0
                    #2D,                                                        ; Component1
                    #1D                                                         ; Component2
                }
G1930_01:       FActionModelGroup {
                    #A5,                                                        ; Mask, комбинации вершин
                    #2B,                                                        ; Component0
                    #3C,                                                        ; Component1
                    #3D                                                         ; Component2
                }
G1930_02:       FActionModelGroup {
                    #41,                                                        ; Mask, комбинации вершин
                    #11,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #53                                                         ; Component2
                }
G1930_03:       FActionModelGroup {
                    #09,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #59,                                                        ; Component1
                    #04                                                         ; Component2
                }
G1930_04:       FActionModelGroup {
                    #84,                                                        ; Mask, комбинации вершин
                    #55,                                                        ; Component0
                    #04,                                                        ; Component1
                    #18                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1930_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1930_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1930_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1930_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1930_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1930_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1930_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1930_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1930_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1930_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1930_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1930_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1930_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1930_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1930_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1930_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R1930_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R1930_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1930_12:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1930_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1930_14:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1930_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1930_16:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1930_17:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D9A8
                endmodule
