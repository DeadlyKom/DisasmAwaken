                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C202
M0202:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0202_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #13,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0202_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #55,                                                        ; Component0
                    #07,                                                        ; Component1
                    #53                                                         ; Component2
                }
G0202_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #3D,                                                        ; Component0
                    #2F,                                                        ; Component1
                    #3B                                                         ; Component2
                }
G0202_03:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #2D,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0202_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #16,                                                        ; Component0
                    #32,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0202_05:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #03,                                                        ; Component1
                    #65                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0202_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0202_01:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #1E,                                                        ; Vertex3
                    #19                                                         ; Vertex4
                }
R0202_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0202_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0202_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0202_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0202_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0202_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R0202_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0202_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0202_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C251
                endmodule
