                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E152
St11:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G2152_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #00,                                                        ; Component1
                    #54                                                         ; Component2
                }
G2152_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #62,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2152_02:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #23                                                         ; Component2
                }
G2152_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #1D                                                         ; Component2
                }
G2152_04:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2152_05:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #38,                                                        ; Component0
                    #00,                                                        ; Component1
                    #61                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R2152_00:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #19,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R2152_01:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #00,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R2152_02:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R2152_03:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #14,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R2152_04:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #05,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R2152_05:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R2152_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2152_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R2152_08:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #0F,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R2152_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R2152_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R2152_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2152_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R2152_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R2152_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R2152_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R2152_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R2152_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R2152_12:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R2152_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R2152_14:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E1CB
                endmodule
