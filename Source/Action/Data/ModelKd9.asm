                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C4B2
Kd9:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G04B2_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #08,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G04B2_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #61                                                         ; Component2
                }
G04B2_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #09,                                                        ; Component1
                    #63                                                         ; Component2
                }
G04B2_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1D,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #57                                                         ; Component2
                }
G04B2_04:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #13,                                                        ; Component1
                    #00                                                         ; Component2
                }
G04B2_05:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #32,                                                        ; Component1
                    #0B                                                         ; Component2
                }
G04B2_06:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #14,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G04B2_07:       FActionModelGroup {
                    #40,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #13,                                                        ; Component1
                    #50                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R04B2_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R04B2_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R04B2_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R04B2_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R04B2_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R04B2_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R04B2_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R04B2_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R04B2_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R04B2_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R04B2_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R04B2_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R04B2_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R04B2_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R04B2_0E:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #37,                                                        ; Vertex3
                    #28,                                                        ; Vertex4
                    #5F                                                         ; Vertex5
                }
R04B2_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R04B2_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R04B2_11:       FActionModelPrimitive6 {
                    #26,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #05,                                                        ; Vertex3
                    #0A,                                                        ; Vertex4
                    #5A                                                         ; Vertex5
                }
R04B2_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R04B2_13:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R04B2_14:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R04B2_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R04B2_16:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R04B2_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R04B2_18:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C54F
                endmodule
