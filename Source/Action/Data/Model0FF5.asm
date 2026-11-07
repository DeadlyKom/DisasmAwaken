                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CFF5
M0FF5:          FActionModelHeader {
                    #4C,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G0FF5_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #36,                                                        ; Component1
                    #15                                                         ; Component2
                }
G0FF5_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #4C,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #48                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0FF5_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R0FF5_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0FF5_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R0FF5_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0FF5_04:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0FF5_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0FF5_06:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0FF5_07:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0FF5_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0FF5_09:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R0FF5_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0FF5_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0FF5_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R0FF5_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D047
                endmodule
