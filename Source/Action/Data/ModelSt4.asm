                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DCEC
St4:            FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1CEC_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #08,                                                        ; Component0
                    #08,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G1CEC_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #11,                                                        ; Component0
                    #10,                                                        ; Component1
                    #10                                                         ; Component2
                }
G1CEC_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #08,                                                        ; Component1
                    #08                                                         ; Component2
                }
G1CEC_03:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #0B,                                                        ; Component0
                    #27,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1CEC_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1CEC_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1CEC_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R1CEC_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1CEC_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R1CEC_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1CEC_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1CEC_07:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1CEC_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1CEC_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1CEC_0A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1CEC_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1CEC_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1CEC_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1CEC_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R1CEC_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1CEC_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1CEC_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R1CEC_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1CEC_13:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1CEC_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1CEC_15:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R1CEC_16:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1CEC_17:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1CEC_18:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1CEC_19:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DD82
                endmodule
