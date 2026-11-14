                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CCEB
KN29pol6:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0CEB_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0CEB_01:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #33,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0CEB_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #00,                                                        ; Component1
                    #47                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0CEB_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0CEB_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0CEB_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0CEB_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0CEB_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CD10
                endmodule
