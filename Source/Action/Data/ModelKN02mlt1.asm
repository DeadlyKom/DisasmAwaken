                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C0A5
KN02mlt1:       FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G00A5_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #46,                                                        ; Component0
                    #34,                                                        ; Component1
                    #24                                                         ; Component2
                }
G00A5_01:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #04,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G00A5_02:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #66                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R00A5_00:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R00A5_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R00A5_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R00A5_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R00A5_04:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C0CC
                endmodule
