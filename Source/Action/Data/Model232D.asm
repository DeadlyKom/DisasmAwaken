                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E32D
M232D:          FActionModelHeader {
                    #54,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G232D_00:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #54,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #45                                                         ; Component2
                }
G232D_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #3C,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #33                                                         ; Component2
                }
G232D_02:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #13,                                                        ; Component0
                    #2B,                                                        ; Component1
                    #13                                                         ; Component2
                }
G232D_03:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #04,                                                        ; Component0
                    #2E,                                                        ; Component1
                    #10                                                         ; Component2
                }
G232D_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #24,                                                        ; Component0
                    #00,                                                        ; Component1
                    #20                                                         ; Component2
                }
G232D_05:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #22                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R232D_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R232D_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R232D_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R232D_03:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #28,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R232D_04:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #37,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R232D_05:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #3C,                                                        ; Vertex0
                    #50                                                         ; Vertex1
                }
R232D_06:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #55                                                         ; Vertex1
                }
R232D_07:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R232D_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R232D_09:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #46,                                                        ; Vertex0
                    #5A                                                         ; Vertex1
                }
R232D_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R232D_0B:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #5F,                                                        ; Vertex0
                    #4B                                                         ; Vertex1
                }
R232D_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R232D_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R232D_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R232D_0F:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R232D_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R232D_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R232D_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R232D_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R232D_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R232D_15:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R232D_16:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R232D_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R232D_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R232D_19:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R232D_1A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R232D_1B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R232D_1C:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R232D_1D:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E3D3
                endmodule
