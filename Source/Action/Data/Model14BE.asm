                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D4BE
M14BE:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G14BE_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2D,                                                        ; Component0
                    #10,                                                        ; Component1
                    #00                                                         ; Component2
                }
G14BE_01:       FActionModelGroup {
                    #A0,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #26,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G14BE_02:       FActionModelGroup {
                    #55,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #58,                                                        ; Component1
                    #2D                                                         ; Component2
                }
G14BE_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #0E                                                         ; Component2
                }
G14BE_04:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #16,                                                        ; Component0
                    #10,                                                        ; Component1
                    #32                                                         ; Component2
                }
G14BE_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #18,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #6D                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R14BE_00:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R14BE_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R14BE_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R14BE_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R14BE_04:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R14BE_05:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R14BE_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R14BE_07:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R14BE_08:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R14BE_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R14BE_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R14BE_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R14BE_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R14BE_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R14BE_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R14BE_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R14BE_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R14BE_11:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R14BE_12:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R14BE_13:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R14BE_14:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R14BE_15:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R14BE_16:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R14BE_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D54A
                endmodule
