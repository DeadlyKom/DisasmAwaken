                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CB7A
Kd26:           FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0B7A_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0B7A_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #23                                                         ; Component2
                }
G0B7A_02:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0B7A_03:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6A,                                                        ; Component0
                    #08,                                                        ; Component1
                    #3D                                                         ; Component2
                }
G0B7A_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1D,                                                        ; Component0
                    #10,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0B7A_05:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #29,                                                        ; Component1
                    #52                                                         ; Component2
                }
G0B7A_06:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #69,                                                        ; Component0
                    #07,                                                        ; Component1
                    #26                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0B7A_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #1E,                                                        ; Vertex0
                    #46                                                         ; Vertex1
                }
R0B7A_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #19,                                                        ; Vertex0
                    #41                                                         ; Vertex1
                }
R0B7A_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0B7A_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R0B7A_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0B7A_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0B7A_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0B7A_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0B7A_08:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37,                                                        ; Vertex3
                    #0A                                                         ; Vertex4
                }
R0B7A_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0B7A_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0B7A_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0B7A_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0B7A_0D:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0B7A_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0B7A_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0B7A_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0B7A_11:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0B7A_12:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0B7A_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CBEC
                endmodule
