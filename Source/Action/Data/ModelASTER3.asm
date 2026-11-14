                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D9E8
ASTER3:         FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G19E8_00:       FActionModelGroup {
                    #91,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #32,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G19E8_01:       FActionModelGroup {
                    #3E,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #18,                                                        ; Component1
                    #29                                                         ; Component2
                }
G19E8_02:       FActionModelGroup {
                    #02,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #6C,                                                        ; Component1
                    #27                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R19E8_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R19E8_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R19E8_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R19E8_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R19E8_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R19E8_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R19E8_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R19E8_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R19E8_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DA1E
                endmodule
