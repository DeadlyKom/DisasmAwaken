                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D622
M1622:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G1622_00:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #27,                                                        ; Component1
                    #68                                                         ; Component2
                }
G1622_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #57,                                                        ; Component0
                    #00,                                                        ; Component1
                    #41                                                         ; Component2
                }
G1622_02:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #00,                                                        ; Component1
                    #39                                                         ; Component2
                }
G1622_03:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1622_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #31,                                                        ; Component0
                    #12,                                                        ; Component1
                    #15                                                         ; Component2
                }
G1622_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1622_00:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1622_01:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1622_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1622_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1622_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1622_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1622_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1622_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1622_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1622_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1622_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1622_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1622_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1622_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R1622_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1622_0F:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1622_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D683
                endmodule
