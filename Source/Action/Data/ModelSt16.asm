                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E469
St16:           FActionModelHeader {
                    #65,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G2469_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #53,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #49                                                         ; Component2
                }
G2469_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #13,                                                        ; Component1
                    #65                                                         ; Component2
                }
G2469_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #47,                                                        ; Component0
                    #13,                                                        ; Component1
                    #16                                                         ; Component2
                }
G2469_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R2469_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #9B,                                                        ; Vertex2
                    #8C                                                         ; Vertex3
                }
R2469_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R2469_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R2469_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R2469_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
R2469_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R2469_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R2469_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R2469_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2469_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R2469_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R2469_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R2469_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R2469_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R2469_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R2469_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R2469_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R2469_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2469_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R2469_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R2469_14:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R2469_15:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R2469_16:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R2469_17:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R2469_18:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R2469_19:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2469_1A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R2469_1B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R2469_1C:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R2469_1D:       FActionModelPrimitive5 {
                    #E5,                                                        ; Header, линия
                    #9B,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #96,                                                        ; Vertex3
                    #9B                                                         ; Vertex4
                }
R2469_1E:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #91,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R2469_1F:       FActionModelPrimitive5 {
                    #E5,                                                        ; Header, линия
                    #87,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #82,                                                        ; Vertex3
                    #87                                                         ; Vertex4
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E51F
                endmodule
