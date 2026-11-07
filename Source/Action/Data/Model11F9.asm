                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D1F9
M11F9:          FActionModelHeader {
                    #69,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G11F9_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #1B                                                         ; Component2
                }
G11F9_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #53,                                                        ; Component0
                    #00,                                                        ; Component1
                    #25                                                         ; Component2
                }
G11F9_02:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G11F9_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #27                                                         ; Component2
                }
G11F9_04:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #41,                                                        ; Component0
                    #00,                                                        ; Component1
                    #66                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R11F9_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R11F9_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R11F9_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R11F9_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R11F9_04:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R11F9_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R11F9_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R11F9_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R11F9_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R11F9_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R11F9_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R11F9_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R11F9_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R11F9_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R11F9_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D254
                endmodule
