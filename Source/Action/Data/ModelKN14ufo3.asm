                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D254
KN14ufo3:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G1254_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #23,                                                        ; Component0
                    #08,                                                        ; Component1
                    #68                                                         ; Component2
                }
G1254_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #29,                                                        ; Component1
                    #02                                                         ; Component2
                }
G1254_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #3D,                                                        ; Component0
                    #14,                                                        ; Component1
                    #5E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1254_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1254_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1254_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1254_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1254_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1254_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1254_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1254_07:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D28A
                endmodule
