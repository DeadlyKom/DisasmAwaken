                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C454
KN09mlt2:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0454_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #08,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0454_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #60                                                         ; Component2
                }
G0454_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #06,                                                        ; Component1
                    #5C                                                         ; Component2
                }
G0454_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1D,                                                        ; Component0
                    #18,                                                        ; Component1
                    #45                                                         ; Component2
                }
G0454_04:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #10                                                         ; Component2
                }
G0454_05:       FActionModelGroup {
                    #3F,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #32,                                                        ; Component1
                    #0B                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0454_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0454_01:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0454_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0454_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R0454_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0454_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R0454_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0454_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0454_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0454_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R0454_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0454_0B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0454_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0454_0D:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C4B2
                endmodule
