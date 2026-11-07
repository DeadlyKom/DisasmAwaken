                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DC3A
M1C3A:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G1C3A_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #56,                                                        ; Component0
                    #1B,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1C3A_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #2E,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #46                                                         ; Component2
                }
G1C3A_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #01,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1C3A_03:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #35,                                                        ; Component0
                    #02,                                                        ; Component1
                    #5B                                                         ; Component2
                }
G1C3A_04:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0C,                                                        ; Component0
                    #15,                                                        ; Component1
                    #46                                                         ; Component2
                }
G1C3A_05:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #0A                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1C3A_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1C3A_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1C3A_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1C3A_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1C3A_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1C3A_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1C3A_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1C3A_07:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #A5                                                         ; Vertex3
                }
R1C3A_08:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #A5,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R1C3A_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1C3A_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1C3A_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #91,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #A5                                                         ; Vertex3
                }
R1C3A_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #A0,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R1C3A_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #A0,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R1C3A_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #A5,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
R1C3A_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #8C,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1C3A_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R1C3A_11:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #91,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1C3A_12:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1C3A_13:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1C3A_14:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R1C3A_15:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1C3A_16:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1C3A_17:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1C3A_18:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1C3A_19:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1C3A_1A:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1C3A_1B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1C3A_1C:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1C3A_1D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DCEC
                endmodule
