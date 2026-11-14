                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D5E2
KN23ufo6:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G15E2_00:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #27,                                                        ; Component1
                    #68                                                         ; Component2
                }
G15E2_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #57,                                                        ; Component0
                    #00,                                                        ; Component1
                    #41                                                         ; Component2
                }
G15E2_02:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #00,                                                        ; Component1
                    #39                                                         ; Component2
                }
G15E2_03:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G15E2_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2E,                                                        ; Component0
                    #12,                                                        ; Component1
                    #11                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R15E2_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R15E2_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R15E2_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R15E2_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R15E2_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R15E2_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R15E2_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R15E2_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R15E2_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R15E2_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D622
                endmodule
