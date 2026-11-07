                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D398
M1398:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G1398_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #21,                                                        ; Component1
                    #66                                                         ; Component2
                }
G1398_01:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #1F,                                                        ; Component0
                    #16,                                                        ; Component1
                    #32                                                         ; Component2
                }
G1398_02:       FActionModelGroup {
                    #40,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G1398_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #2D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1398_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1398_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1398_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1398_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1398_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1398_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1398_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1398_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1398_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D3D5
                endmodule
