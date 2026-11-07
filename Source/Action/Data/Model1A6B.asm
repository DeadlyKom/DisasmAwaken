                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DA6B
M1A6B:          FActionModelHeader {
                    #44,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G1A6B_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #3B,                                                        ; Component0
                    #32,                                                        ; Component1
                    #3C                                                         ; Component2
                }
G1A6B_01:       FActionModelGroup {
                    #3F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G1A6B_02:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #24,                                                        ; Component1
                    #44                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1A6B_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A6B_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1A6B_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1A6B_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1A6B_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A6B_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A6B_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1A6B_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1A6B_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1A6B_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1A6B_0A:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A,                                                        ; Vertex3
                    #0F                                                         ; Vertex4
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DAAA
                endmodule
