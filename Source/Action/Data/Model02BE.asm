                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C2BE
M02BE:          FActionModelHeader {
                    #56,                                                        ; Unknown00, смысл не установлен
                    #04                                                         ; ScaleExponent
                }
G02BE_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #19                                                         ; Component2
                }
G02BE_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #00,                                                        ; Component1
                    #56                                                         ; Component2
                }
G02BE_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #0B,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #55                                                         ; Component2
                }
G02BE_03:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G02BE_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #10,                                                        ; Component1
                    #25                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R02BE_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R02BE_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R02BE_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R02BE_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R02BE_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R02BE_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R02BE_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R02BE_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R02BE_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R02BE_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R02BE_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R02BE_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R02BE_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R02BE_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R02BE_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R02BE_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R02BE_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R02BE_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R02BE_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C329
                endmodule
