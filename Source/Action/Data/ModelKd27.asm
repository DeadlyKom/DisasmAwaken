                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CC11
Kd27:           FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0C11_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0C11_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #29                                                         ; Component2
                }
G0C11_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #61,                                                        ; Component0
                    #00,                                                        ; Component1
                    #48                                                         ; Component2
                }
G0C11_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #19,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0C11_04:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #34,                                                        ; Component1
                    #38                                                         ; Component2
                }
G0C11_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #12,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0C11_06:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #00,                                                        ; Component1
                    #06                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0C11_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #0F,                                                        ; Vertex0
                    #50                                                         ; Vertex1
                }
R0C11_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #0A,                                                        ; Vertex0
                    #55                                                         ; Vertex1
                }
R0C11_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0C11_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0C11_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0C11_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0C11_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0C11_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0C11_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0C11_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0C11_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0C11_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0C11_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0C11_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0C11_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0C11_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0C11_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0C11_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CC7D
                endmodule
