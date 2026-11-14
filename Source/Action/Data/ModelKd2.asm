                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C0CC
Kd2:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G00CC_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #3E                                                         ; Component2
                }
G00CC_01:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #29,                                                        ; Component0
                    #06,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G00CC_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #2F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G00CC_03:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G00CC_04:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #14,                                                        ; Component1
                    #3A                                                         ; Component2
                }
G00CC_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #1F,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #58                                                         ; Component2
                }
G00CC_06:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #2A,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #6A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R00CC_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R00CC_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #28,                                                        ; Vertex0
                    #5A                                                         ; Vertex1
                }
R00CC_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #2D,                                                        ; Vertex0
                    #5F                                                         ; Vertex1
                }
R00CC_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R00CC_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R00CC_05:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R00CC_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R00CC_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R00CC_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R00CC_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R00CC_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R00CC_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R00CC_0C:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41,                                                        ; Vertex3
                    #28                                                         ; Vertex4
                }
R00CC_0D:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #2D,                                                        ; Vertex3
                    #3C                                                         ; Vertex4
                }
R00CC_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R00CC_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R00CC_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R00CC_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C140
                endmodule
