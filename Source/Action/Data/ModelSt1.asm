                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DAAA
St1:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1AAA_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #08,                                                        ; Component0
                    #08,                                                        ; Component1
                    #65                                                         ; Component2
                }
G1AAA_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #14,                                                        ; Component1
                    #0A                                                         ; Component2
                }
G1AAA_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #10                                                         ; Component2
                }
G1AAA_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #08,                                                        ; Component1
                    #08                                                         ; Component2
                }
G1AAA_04:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #6C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1AAA_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #BE,                                                        ; Vertex1
                    #C3,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1AAA_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #B4,                                                        ; Vertex0
                    #B9,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1AAA_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #B4,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #C3                                                         ; Vertex3
                }
R1AAA_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R1AAA_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1AAA_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #A5,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1AAA_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #AA,                                                        ; Vertex0
                    #AF,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1AAA_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1AAA_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R1AAA_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #AA,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #A5                                                         ; Vertex3
                }
R1AAA_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #B9,                                                        ; Vertex2
                    #BE                                                         ; Vertex3
                }
R1AAA_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1AAA_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #AF,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
R1AAA_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1AAA_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1AAA_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1AAA_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #91,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R1AAA_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1AAA_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R1AAA_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1AAA_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
R1AAA_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R1AAA_16:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1AAA_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1AAA_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1AAA_19:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R1AAA_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R1AAA_1B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1AAA_1C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1AAA_1D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R1AAA_1E:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1AAA_1F:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1AAA_20:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R1AAA_21:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1AAA_22:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1AAA_23:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1AAA_24:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #B9,                                                        ; Vertex0
                    #B4,                                                        ; Vertex1
                    #C3,                                                        ; Vertex2
                    #BE                                                         ; Vertex3
                }
R1AAA_25:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #AF,                                                        ; Vertex0
                    #AA,                                                        ; Vertex1
                    #A5,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DB80
                endmodule
