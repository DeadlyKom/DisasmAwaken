                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C000
M0000:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0000_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #13,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0000_01:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #17                                                         ; Component2
                }
G0000_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #50,                                                        ; Component0
                    #2F,                                                        ; Component1
                    #30                                                         ; Component2
                }
G0000_03:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #37,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0000_00:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0000_01:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0000_02:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0000_03:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0000_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0000_05:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0000_06:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0000_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0000_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0000_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C040
                endmodule
