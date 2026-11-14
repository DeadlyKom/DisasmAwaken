                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CE82
Kd31:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G0E82_00:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #14,                                                        ; Component1
                    #54                                                         ; Component2
                }
G0E82_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #3C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #35                                                         ; Component2
                }
G0E82_02:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0E82_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2B,                                                        ; Component0
                    #14,                                                        ; Component1
                    #5B                                                         ; Component2
                }
G0E82_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #18,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0E82_05:       FActionModelGroup {
                    #40,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #19,                                                        ; Component1
                    #24                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0E82_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0E82_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0E82_02:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0E82_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0E82_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0E82_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0E82_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0E82_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0E82_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0E82_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0E82_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0E82_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0E82_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0E82_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0E82_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0E82_0F:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0E82_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0E82_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0E82_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0E82_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0E82_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CEF5
                endmodule
