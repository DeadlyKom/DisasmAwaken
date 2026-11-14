                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CCA5
Kd28:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0CA5_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0CA5_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #21,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0CA5_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #00,                                                        ; Component1
                    #30                                                         ; Component2
                }
G0CA5_03:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #18,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0CA5_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #12,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0CA5_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0CA5_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0CA5_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0CA5_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0CA5_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0CA5_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0CA5_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0CA5_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0CA5_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0CA5_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CCEB
                endmodule
