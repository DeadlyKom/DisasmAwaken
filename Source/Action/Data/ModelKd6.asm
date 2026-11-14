                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C271
Kd6:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0271_00:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #4F,                                                        ; Component0
                    #2F,                                                        ; Component1
                    #26                                                         ; Component2
                }
G0271_01:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #34,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G0271_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0271_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #15,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0271_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0271_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0271_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0271_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0271_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0271_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0271_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0271_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0271_08:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0271_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0271_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R0271_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0271_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C2BE
                endmodule
