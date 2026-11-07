                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C3AE
M03AE:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G03AE_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #38,                                                        ; Component0
                    #00,                                                        ; Component1
                    #35                                                         ; Component2
                }
G03AE_01:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G03AE_02:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #00                                                         ; Component2
                }
G03AE_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2B,                                                        ; Component0
                    #13,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R03AE_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R03AE_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R03AE_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R03AE_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R03AE_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R03AE_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R03AE_06:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R03AE_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R03AE_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R03AE_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R03AE_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C3F1
                endmodule
