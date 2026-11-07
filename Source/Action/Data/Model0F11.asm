                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CF11
M0F11:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G0F11_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #3E,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0F11_01:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #26,                                                        ; Component1
                    #36                                                         ; Component2
                }
G0F11_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0F11_03:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0F11_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0F11_05:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #61,                                                        ; Component0
                    #00,                                                        ; Component1
                    #46                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0F11_00:       FActionModelPrimitive5 {
                    #A5,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #2D,                                                        ; Vertex3
                    #0A                                                         ; Vertex4
                }
R0F11_01:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0F11_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0F11_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0F11_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0F11_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0F11_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0F11_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0F11_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0F11_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0F11_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CF61
                endmodule
