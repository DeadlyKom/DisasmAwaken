                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CDC9
Kd30:           FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G0DC9_00:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G0DC9_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #00,                                                        ; Component1
                    #44                                                         ; Component2
                }
G0DC9_02:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #3D,                                                        ; Component1
                    #51                                                         ; Component2
                }
G0DC9_03:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G0DC9_04:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #23,                                                        ; Component0
                    #00,                                                        ; Component1
                    #68                                                         ; Component2
                }
G0DC9_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #2C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0DC9_06:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #21,                                                        ; Component1
                    #66                                                         ; Component2
                }
G0DC9_07:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #4A,                                                        ; Component0
                    #01,                                                        ; Component1
                    #62                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0DC9_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0DC9_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0DC9_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0DC9_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0DC9_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0DC9_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0DC9_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0DC9_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R0DC9_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R0DC9_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0DC9_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0DC9_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0DC9_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R0DC9_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0DC9_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0DC9_0F:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0DC9_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CE36
                endmodule
