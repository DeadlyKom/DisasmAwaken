                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D7DF
KRYLD:          FActionModelHeader {
                    #60,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G17DF_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #12,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #16                                                         ; Component2
                }
G17DF_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #60,                                                        ; Component0
                    #05,                                                        ; Component1
                    #0A                                                         ; Component2
                }
G17DF_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #0B,                                                        ; Component0
                    #04,                                                        ; Component1
                    #50                                                         ; Component2
                }
G17DF_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #06,                                                        ; Component1
                    #2C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R17DF_00:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R17DF_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R17DF_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R17DF_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R17DF_04:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R17DF_05:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R17DF_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R17DF_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R17DF_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R17DF_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R17DF_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R17DF_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R17DF_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R17DF_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R17DF_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R17DF_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R17DF_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R17DF_11:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R17DF_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D84C
                endmodule
