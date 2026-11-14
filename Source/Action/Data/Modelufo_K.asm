                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D047
ufo_K:          FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #01                                                         ; ScaleExponent
                }
G1047_00:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1047_01:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #60,                                                        ; Component1
                    #4B                                                         ; Component2
                }
G1047_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #40,                                                        ; Component0
                    #00,                                                        ; Component1
                    #3F                                                         ; Component2
                }
G1047_03:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #42,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1047_04:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1047_00:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1047_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1047_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1047_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1047_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1047_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1047_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1047_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1047_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1047_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D089
                endmodule
