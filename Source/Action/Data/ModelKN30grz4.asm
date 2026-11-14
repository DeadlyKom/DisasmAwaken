                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CD8B
KN30grz4:       FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G0D8B_00:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G0D8B_01:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #37,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G0D8B_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #34,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0D8B_03:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #43,                                                        ; Component0
                    #01,                                                        ; Component1
                    #62                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0D8B_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0D8B_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0D8B_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0D8B_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0D8B_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0D8B_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0D8B_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0D8B_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0D8B_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0D8B_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CDC9
                endmodule
