                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E5C1
Prison:         FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G25C1_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #08,                                                        ; Component0
                    #08,                                                        ; Component1
                    #65                                                         ; Component2
                }
G25C1_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #11,                                                        ; Component1
                    #11                                                         ; Component2
                }
G25C1_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #08,                                                        ; Component1
                    #08                                                         ; Component2
                }
G25C1_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #22,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R25C1_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R25C1_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R25C1_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R25C1_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R25C1_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R25C1_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R25C1_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R25C1_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R25C1_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R25C1_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R25C1_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R25C1_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R25C1_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R25C1_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R25C1_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R25C1_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R25C1_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R25C1_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R25C1_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R25C1_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R25C1_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R25C1_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R25C1_16:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R25C1_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R25C1_18:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R25C1_19:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #8C                                                         ; Vertex3
                }
R25C1_1A:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R25C1_1B:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R25C1_1C:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R25C1_1D:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E66B
                endmodule
