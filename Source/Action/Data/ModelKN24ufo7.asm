                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D54A
KN24ufo7:       FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G154A_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G154A_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6A,                                                        ; Component0
                    #00,                                                        ; Component1
                    #42                                                         ; Component2
                }
G154A_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2A,                                                        ; Component0
                    #2F,                                                        ; Component1
                    #1C                                                         ; Component2
                }
G154A_03:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #60                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R154A_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R154A_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R154A_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R154A_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R154A_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R154A_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R154A_06:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R154A_07:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D57E
                endmodule
