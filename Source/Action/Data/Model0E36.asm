                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CE36
M0E36:          FActionModelHeader {
                    #6B,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G0E36_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0E36_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #25,                                                        ; Component1
                    #67                                                         ; Component2
                }
G0E36_02:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #38,                                                        ; Component0
                    #00,                                                        ; Component1
                    #37                                                         ; Component2
                }
G0E36_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2B,                                                        ; Component0
                    #14,                                                        ; Component1
                    #63                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0E36_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0E36_01:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #00,                                                        ; Vertex3
                    #05,                                                        ; Vertex4
                    #23                                                         ; Vertex5
                }
R0E36_02:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F,                                                        ; Vertex3
                    #23,                                                        ; Vertex4
                    #05                                                         ; Vertex5
                }
R0E36_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0E36_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0E36_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0E36_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0E36_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0E36_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0E36_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0E36_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0E36_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CE82
                endmodule
