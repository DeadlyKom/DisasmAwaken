                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E7AB
StU2:           FActionModelHeader {
                    #69,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G27AB_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #69,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #2A                                                         ; Component2
                }
G27AB_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0C,                                                        ; Component0
                    #10,                                                        ; Component1
                    #14                                                         ; Component2
                }
G27AB_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #69,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #00                                                         ; Component2
                }
G27AB_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #2C,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #67                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R27AB_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R27AB_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R27AB_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R27AB_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R27AB_04:       FActionModelPrimitive4 {
                    #84,                                                        ; Header, линия
                    #73,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R27AB_05:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #7D,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R27AB_06:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R27AB_07:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #87,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R27AB_08:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #69,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R27AB_09:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R27AB_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R27AB_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R27AB_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R27AB_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R27AB_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R27AB_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R27AB_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R27AB_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R27AB_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R27AB_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R27AB_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R27AB_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R27AB_16:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R27AB_17:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R27AB_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R27AB_19:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R27AB_1A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R27AB_1B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R27AB_1C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R27AB_1D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R27AB_1E:       FActionModelPrimitive6 {
                    #36,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #5A,                                                        ; Vertex3
                    #19,                                                        ; Vertex4
                    #1E                                                         ; Vertex5
                }
R27AB_1F:       FActionModelPrimitive6 {
                    #36,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #5F,                                                        ; Vertex3
                    #0F,                                                        ; Vertex4
                    #00                                                         ; Vertex5
                }
R27AB_20:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R27AB_21:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E859
                endmodule
