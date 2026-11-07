                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D57E
M157E:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G157E_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #2A,                                                        ; Component0
                    #00,                                                        ; Component1
                    #1F                                                         ; Component2
                }
G157E_01:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G157E_02:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #11                                                         ; Component2
                }
G157E_03:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G157E_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #30,                                                        ; Component1
                    #2B                                                         ; Component2
                }
G157E_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #3E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R157E_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R157E_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R157E_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R157E_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R157E_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R157E_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R157E_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R157E_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R157E_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R157E_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R157E_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R157E_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R157E_0C:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R157E_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R157E_0E:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R157E_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R157E_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R157E_11:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D5E2
                endmodule
