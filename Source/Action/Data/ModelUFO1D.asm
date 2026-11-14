                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DA1E
UFO1D:          FActionModelHeader {
                    #3C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G1A1E_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #3B,                                                        ; Component0
                    #32,                                                        ; Component1
                    #3C                                                         ; Component2
                }
G1A1E_01:       FActionModelGroup {
                    #3F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G1A1E_02:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #21,                                                        ; Component1
                    #30                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1A1E_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A1E_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1A1E_02:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1A1E_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R1A1E_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1A1E_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A1E_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1A1E_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1A1E_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1A1E_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1A1E_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1A1E_0B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1A1E_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1A1E_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1A1E_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DA6B
                endmodule
