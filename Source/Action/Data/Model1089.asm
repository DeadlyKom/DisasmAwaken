                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D089
M1089:          FActionModelHeader {
                    #48,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G1089_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #41,                                                        ; Component0
                    #37,                                                        ; Component1
                    #18                                                         ; Component2
                }
G1089_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #18,                                                        ; Component1
                    #48                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1089_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1089_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1089_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1089_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1089_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1089_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1089_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1089_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1089_08:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1089_09:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1089_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1089_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1089_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1089_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D0DB
                endmodule
