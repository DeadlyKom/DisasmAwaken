                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E044
St9:            FActionModelHeader {
                    #68,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G2044_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #00,                                                        ; Component1
                    #46                                                         ; Component2
                }
G2044_01:       FActionModelGroup {
                    #02,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #05,                                                        ; Component1
                    #66                                                         ; Component2
                }
G2044_02:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #0E                                                         ; Component2
                }
G2044_03:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #16,                                                        ; Component0
                    #00,                                                        ; Component1
                    #09                                                         ; Component2
                }
G2044_04:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #1F                                                         ; Component2
                }
G2044_05:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #1F,                                                        ; Component1
                    #0F                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R2044_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R2044_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R2044_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R2044_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R2044_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R2044_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R2044_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R2044_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R2044_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R2044_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R2044_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R2044_0B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R2044_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R2044_0D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R2044_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R2044_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R2044_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R2044_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R2044_12:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R2044_13:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E0B0
                endmodule
