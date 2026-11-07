                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C935
M0935:          FActionModelHeader {
                    #69,                                                        ; Unknown00, смысл не установлен
                    #04                                                         ; ScaleExponent
                }
G0935_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #13,                                                        ; Component0
                    #00,                                                        ; Component1
                    #2D                                                         ; Component2
                }
G0935_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #00,                                                        ; Component1
                    #16                                                         ; Component2
                }
G0935_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #15,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0935_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #06,                                                        ; Component0
                    #14,                                                        ; Component1
                    #17                                                         ; Component2
                }
G0935_04:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #62                                                         ; Component2
                }
G0935_05:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #00,                                                        ; Component1
                    #59                                                         ; Component2
                }
G0935_06:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #69                                                         ; Component2
                }
G0935_07:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #3A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0935_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R0935_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0935_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R0935_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0935_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0935_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0935_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0935_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0935_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0935_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R0935_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0935_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0935_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0935_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R0935_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R0935_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R0935_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R0935_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R0935_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0935_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R0935_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R0935_15:       FActionModelPrimitive5 {
                    #15,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41,                                                        ; Vertex3
                    #1E                                                         ; Vertex4
                }
R0935_16:       FActionModelPrimitive5 {
                    #15,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37,                                                        ; Vertex3
                    #28                                                         ; Vertex4
                }
R0935_17:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0935_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R0935_19:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0935_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0935_1B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C9D7
                endmodule
