                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C78D
KN16trg4:       FActionModelHeader {
                    #60,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G078D_00:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #26,                                                        ; Component0
                    #23,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G078D_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1F,                                                        ; Component0
                    #45,                                                        ; Component1
                    #2E                                                         ; Component2
                }
G078D_02:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #37,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G078D_03:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #17,                                                        ; Component1
                    #60                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R078D_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R078D_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R078D_02:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #23,                                                        ; Vertex3
                    #1E,                                                        ; Vertex4
                    #0A                                                         ; Vertex5
                }
R078D_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R078D_04:       FActionModelPrimitive6 {
                    #36,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05,                                                        ; Vertex3
                    #14,                                                        ; Vertex4
                    #28                                                         ; Vertex5
                }
R078D_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R078D_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C7C6
                endmodule
