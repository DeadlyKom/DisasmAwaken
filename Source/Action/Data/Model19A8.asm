                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D9A8
M19A8:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G19A8_00:       FActionModelGroup {
                    #91,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #02,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G19A8_01:       FActionModelGroup {
                    #0E,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #18,                                                        ; Component1
                    #29                                                         ; Component2
                }
G19A8_02:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #6C,                                                        ; Component1
                    #26                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R19A8_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R19A8_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R19A8_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R19A8_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R19A8_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R19A8_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R19A8_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R19A8_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R19A8_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R19A8_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R19A8_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R19A8_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D9E8
                endmodule
