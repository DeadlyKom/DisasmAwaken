                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D6E0
KOBRAD:         FActionModelHeader {
                    #78,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G16E0_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #2C,                                                        ; Component0
                    #16,                                                        ; Component1
                    #31                                                         ; Component2
                }
G16E0_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #4F,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #21                                                         ; Component2
                }
G16E0_02:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #78,                                                        ; Component0
                    #01,                                                        ; Component1
                    #0F                                                         ; Component2
                }
G16E0_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #08,                                                        ; Component0
                    #07,                                                        ; Component1
                    #64                                                         ; Component2
                }
G16E0_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #4E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R16E0_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R16E0_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R16E0_02:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R16E0_03:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R16E0_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R16E0_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R16E0_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R16E0_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R16E0_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R16E0_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R16E0_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R16E0_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R16E0_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R16E0_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R16E0_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R16E0_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R16E0_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R16E0_11:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R16E0_12:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R16E0_13:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R16E0_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R16E0_15:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R16E0_16:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R16E0_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R16E0_18:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R16E0_19:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R16E0_1A:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R16E0_1B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D780
                endmodule
