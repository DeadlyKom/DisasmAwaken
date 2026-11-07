                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CEF5
M0EF5:          FActionModelHeader {
                    #5C,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G0EF5_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #23,                                                        ; Component1
                    #5C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0EF5_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0EF5_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0EF5_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0EF5_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CF11
                endmodule
