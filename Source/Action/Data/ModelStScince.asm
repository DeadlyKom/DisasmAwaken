                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E707
StScince:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G2707_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #00,                                                        ; Component1
                    #1B                                                         ; Component2
                }
G2707_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #07                                                         ; Component2
                }
G2707_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #0A,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2707_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0B,                                                        ; Component0
                    #09,                                                        ; Component1
                    #10                                                         ; Component2
                }
G2707_04:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #12,                                                        ; Component1
                    #11                                                         ; Component2
                }
G2707_05:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #00                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R2707_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R2707_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R2707_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R2707_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R2707_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R2707_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R2707_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R2707_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R2707_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R2707_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R2707_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R2707_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R2707_0C:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R2707_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2707_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R2707_0F:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R2707_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R2707_11:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R2707_12:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R2707_13:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R2707_14:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R2707_15:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R2707_16:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R2707_17:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2707_18:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R2707_19:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R2707_1A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R2707_1B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E7AB
                endmodule
