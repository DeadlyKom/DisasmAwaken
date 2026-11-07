                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C3F1
M03F1:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G03F1_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #38,                                                        ; Component0
                    #00,                                                        ; Component1
                    #30                                                         ; Component2
                }
G03F1_01:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G03F1_02:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #24,                                                        ; Component1
                    #00                                                         ; Component2
                }
G03F1_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #13,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G03F1_04:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #13,                                                        ; Component1
                    #40                                                         ; Component2
                }
G03F1_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1F,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R03F1_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R03F1_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R03F1_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R03F1_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R03F1_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R03F1_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R03F1_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R03F1_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R03F1_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R03F1_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R03F1_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R03F1_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R03F1_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R03F1_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R03F1_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R03F1_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R03F1_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C454
                endmodule
