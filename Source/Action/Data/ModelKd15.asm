                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C6EA
Kd15:           FActionModelHeader {
                    #67,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #04                                                         ; ScaleExponent
                }
G06EA_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #23,                                                        ; Component0
                    #0A,                                                        ; Component1
                    #28                                                         ; Component2
                }
G06EA_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #38                                                         ; Component2
                }
G06EA_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #1D,                                                        ; Component0
                    #02,                                                        ; Component1
                    #50                                                         ; Component2
                }
G06EA_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #11,                                                        ; Component0
                    #0A,                                                        ; Component1
                    #5E                                                         ; Component2
                }
G06EA_04:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #01,                                                        ; Component1
                    #67                                                         ; Component2
                }
G06EA_05:       FActionModelGroup {
                    #AA,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #16,                                                        ; Component1
                    #25                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R06EA_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R06EA_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R06EA_02:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R06EA_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R06EA_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R06EA_05:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R06EA_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R06EA_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R06EA_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R06EA_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R06EA_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R06EA_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R06EA_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R06EA_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R06EA_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R06EA_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R06EA_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R06EA_11:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R06EA_12:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R06EA_13:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R06EA_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R06EA_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R06EA_16:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R06EA_17:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R06EA_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R06EA_19:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R06EA_1A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R06EA_1B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R06EA_1C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R06EA_1D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R06EA_1E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C78D
                endmodule
