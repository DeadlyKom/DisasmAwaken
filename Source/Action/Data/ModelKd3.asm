                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D150
Kd3:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #03                                                         ; ScaleExponent
                }
G1150_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #15,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1150_01:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #06,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1150_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #16,                                                        ; Component0
                    #25,                                                        ; Component1
                    #50                                                         ; Component2
                }
G1150_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #3B,                                                        ; Component0
                    #14,                                                        ; Component1
                    #3C                                                         ; Component2
                }
G1150_04:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #25,                                                        ; Component1
                    #2C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1150_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1150_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1150_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1150_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1150_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1150_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1150_06:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37,                                                        ; Vertex3
                    #55,                                                        ; Vertex4
                    #5A                                                         ; Vertex5
                }
R1150_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1150_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1150_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1150_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1150_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1150_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1150_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1150_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1150_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1150_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1150_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D1C0
                endmodule
