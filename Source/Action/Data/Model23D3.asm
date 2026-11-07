                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E3D3
M23D3:          FActionModelHeader {
                    #6B,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G23D3_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #3C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #69                                                         ; Component2
                }
G23D3_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #0B                                                         ; Component2
                }
G23D3_02:       FActionModelGroup {
                    #CC,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #38                                                         ; Component2
                }
G23D3_03:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #69,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G23D3_04:       FActionModelGroup {
                    #44,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #66                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R23D3_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #0F,                                                        ; Vertex0
                    #46                                                         ; Vertex1
                }
R23D3_01:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #4B,                                                        ; Vertex0
                    #0A                                                         ; Vertex1
                }
R23D3_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #00                                                         ; Vertex1
                }
R23D3_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R23D3_04:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #05,                                                        ; Vertex0
                    #3C                                                         ; Vertex1
                }
R23D3_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R23D3_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R23D3_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R23D3_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R23D3_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R23D3_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R23D3_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R23D3_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R23D3_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R23D3_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R23D3_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R23D3_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R23D3_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R23D3_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R23D3_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R23D3_14:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R23D3_15:       FActionModelPrimitive4 {
                    #04,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R23D3_16:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R23D3_17:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R23D3_18:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R23D3_19:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R23D3_1A:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R23D3_1B:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R23D3_1C:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R23D3_1D:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E469
                endmodule
