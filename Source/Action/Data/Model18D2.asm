                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D8D2
M18D2:          FActionModelHeader {
                    #3E,                                                        ; Unknown00, смысл не установлен
                    #01                                                         ; ScaleExponent
                }
G18D2_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #32,                                                        ; Component1
                    #2D                                                         ; Component2
                }
G18D2_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #32,                                                        ; Component1
                    #3E                                                         ; Component2
                }
G18D2_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1B,                                                        ; Component0
                    #32,                                                        ; Component1
                    #2D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R18D2_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R18D2_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R18D2_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R18D2_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R18D2_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R18D2_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R18D2_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R18D2_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R18D2_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R18D2_09:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R18D2_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R18D2_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R18D2_0C:       FActionModelPrimitive8 {
                    #18,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37,                                                        ; Vertex3
                    #0F,                                                        ; Vertex4
                    #14,                                                        ; Vertex5
                    #3C,                                                        ; Vertex6
                    #41                                                         ; Vertex7
                }
R18D2_0D:       FActionModelPrimitive8 {
                    #28,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B,                                                        ; Vertex3
                    #23,                                                        ; Vertex4
                    #00,                                                        ; Vertex5
                    #28,                                                        ; Vertex6
                    #2D                                                         ; Vertex7
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D930
                endmodule
