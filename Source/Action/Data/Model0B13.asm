                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CB13
M0B13:          FActionModelHeader {
                    #6B,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0B13_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0B13_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #11,                                                        ; Component0
                    #32,                                                        ; Component1
                    #44                                                         ; Component2
                }
G0B13_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #00,                                                        ; Component1
                    #5C                                                         ; Component2
                }
G0B13_03:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #4F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #35                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0B13_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #23,                                                        ; Vertex0
                    #19                                                         ; Vertex1
                }
R0B13_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0B13_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #28,                                                        ; Vertex0
                    #1E                                                         ; Vertex1
                }
R0B13_03:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0B13_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0B13_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0B13_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0B13_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0B13_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0B13_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0B13_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CB52
                endmodule
