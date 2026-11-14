                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C7C6
Kd16:           FActionModelHeader {
                    #68,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G07C6_00:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #1B,                                                        ; Component0
                    #1F,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G07C6_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #4C,                                                        ; Component1
                    #33                                                         ; Component2
                }
G07C6_02:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #33,                                                        ; Component1
                    #32                                                         ; Component2
                }
G07C6_03:       FActionModelGroup {
                    #0A,                                                        ; Mask, комбинации вершин
                    #26,                                                        ; Component0
                    #25,                                                        ; Component1
                    #38                                                         ; Component2
                }
G07C6_04:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #2C                                                         ; Component2
                }
G07C6_05:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #5D                                                         ; Component2
                }
G07C6_06:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #03,                                                        ; Component0
                    #11,                                                        ; Component1
                    #68                                                         ; Component2
                }
G07C6_07:       FActionModelGroup {
                    #50,                                                        ; Mask, комбинации вершин
                    #0C,                                                        ; Component0
                    #30,                                                        ; Component1
                    #4A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R07C6_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R07C6_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R07C6_02:       FActionModelPrimitive2 {
                    #82,                                                        ; Header, линия
                    #1E,                                                        ; Vertex0
                    #50                                                         ; Vertex1
                }
R07C6_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R07C6_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R07C6_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R07C6_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R07C6_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R07C6_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R07C6_09:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #23,                                                        ; Vertex0
                    #55                                                         ; Vertex1
                }
R07C6_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R07C6_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R07C6_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R07C6_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R07C6_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R07C6_0F:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R07C6_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R07C6_11:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R07C6_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R07C6_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R07C6_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C845
                endmodule
