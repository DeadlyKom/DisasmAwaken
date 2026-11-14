                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E2B9
St13:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G22B9_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #1B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G22B9_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G22B9_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #00                                                         ; Component2
                }
G22B9_03:       FActionModelGroup {
                    #AA,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #16,                                                        ; Component1
                    #2F                                                         ; Component2
                }
G22B9_04:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R22B9_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R22B9_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R22B9_02:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #37,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R22B9_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R22B9_04:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #3C,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R22B9_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R22B9_06:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R22B9_07:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R22B9_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R22B9_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R22B9_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R22B9_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R22B9_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R22B9_0D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R22B9_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R22B9_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R22B9_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R22B9_11:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R22B9_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R22B9_13:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E32D
                endmodule
