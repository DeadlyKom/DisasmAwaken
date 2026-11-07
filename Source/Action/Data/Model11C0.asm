                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D1C0
M11C0:          FActionModelHeader {
                    #5F,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G11C0_00:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #5A                                                         ; Component2
                }
G11C0_01:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #2E,                                                        ; Component1
                    #00                                                         ; Component2
                }
G11C0_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #3F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #5F                                                         ; Component2
                }
G11C0_03:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #50,                                                        ; Component0
                    #00,                                                        ; Component1
                    #12                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R11C0_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R11C0_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R11C0_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R11C0_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R11C0_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R11C0_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R11C0_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R11C0_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R11C0_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D1F9
                endmodule
