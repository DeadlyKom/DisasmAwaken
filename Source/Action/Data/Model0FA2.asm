                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CFA2
M0FA2:          FActionModelHeader {
                    #60,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G0FA2_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #41,                                                        ; Component0
                    #00,                                                        ; Component1
                    #40                                                         ; Component2
                }
G0FA2_01:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #23,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0FA2_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #3C                                                         ; Component2
                }
G0FA2_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #37,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #57                                                         ; Component2
                }
G0FA2_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #3F,                                                        ; Component0
                    #04,                                                        ; Component1
                    #60                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0FA2_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #05                                                         ; Vertex1
                }
R0FA2_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #3C,                                                        ; Vertex0
                    #00                                                         ; Vertex1
                }
R0FA2_02:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #2D,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0FA2_03:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0FA2_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0FA2_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0FA2_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0FA2_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0FA2_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0FA2_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0FA2_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0FA2_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0FA2_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0FA2_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0FA2_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CFF5
                endmodule
