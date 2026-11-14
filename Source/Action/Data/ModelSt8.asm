                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DF76
St8:            FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1F76_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #11,                                                        ; Component1
                    #27                                                         ; Component2
                }
G1F76_01:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #50,                                                        ; Component0
                    #00,                                                        ; Component1
                    #14                                                         ; Component2
                }
G1F76_02:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #2E,                                                        ; Component0
                    #12,                                                        ; Component1
                    #68                                                         ; Component2
                }
G1F76_03:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #04,                                                        ; Component1
                    #4E                                                         ; Component2
                }
G1F76_04:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #13,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #0F                                                         ; Component2
                }
G1F76_05:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #01,                                                        ; Component0
                    #20,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G1F76_06:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #2F,                                                        ; Component0
                    #00,                                                        ; Component1
                    #28                                                         ; Component2
                }
G1F76_07:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #3E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1F76_00:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #6E,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1F76_01:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #64,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R1F76_02:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #73,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1F76_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1F76_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1F76_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1F76_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1F76_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1F76_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1F76_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R1F76_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1F76_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R1F76_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R1F76_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1F76_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R1F76_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1F76_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1F76_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R1F76_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1F76_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
R1F76_14:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1F76_15:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1F76_16:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
R1F76_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #91,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1F76_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
R1F76_19:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1F76_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1F76_1B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R1F76_1C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R1F76_1D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1F76_1E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1F76_1F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1F76_20:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1F76_21:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #8C                                                         ; Vertex2
                }
R1F76_22:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #7D                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E044
                endmodule
