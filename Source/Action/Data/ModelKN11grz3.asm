                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C602
KN11grz3:       FActionModelHeader {
                    #68,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G0602_00:       FActionModelGroup {
                    #40,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #63                                                         ; Component2
                }
G0602_01:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #20,                                                        ; Component1
                    #37                                                         ; Component2
                }
G0602_02:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #35,                                                        ; Component0
                    #00,                                                        ; Component1
                    #25                                                         ; Component2
                }
G0602_03:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #00,                                                        ; Component1
                    #68                                                         ; Component2
                }
G0602_04:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #15,                                                        ; Component1
                    #68                                                         ; Component2
                }
G0602_05:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #5A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0602_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0602_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0602_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0602_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0602_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0602_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0602_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0602_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R0602_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0602_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0602_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C64F
                endmodule
