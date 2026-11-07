                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C040
M0040:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0040_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #35,                                                        ; Component0
                    #23,                                                        ; Component1
                    #57                                                         ; Component2
                }
G0040_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #11,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0040_02:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #17                                                         ; Component2
                }
G0040_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #50,                                                        ; Component0
                    #2F,                                                        ; Component1
                    #30                                                         ; Component2
                }
G0040_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #37,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0040_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0040_01:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0040_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0040_03:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0040_04:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0040_05:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0040_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0040_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0040_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0040_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R0040_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0040_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0040_0C:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0040_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0040_0E:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0040_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0040_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C0A5
                endmodule
