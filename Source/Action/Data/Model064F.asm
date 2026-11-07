                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C64F
M064F:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G064F_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #23,                                                        ; Component1
                    #30                                                         ; Component2
                }
G064F_01:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #41,                                                        ; Component0
                    #00,                                                        ; Component1
                    #16                                                         ; Component2
                }
G064F_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #16,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G064F_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #1A,                                                        ; Component1
                    #4F                                                         ; Component2
                }
G064F_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #00,                                                        ; Component1
                    #4E                                                         ; Component2
                }
G064F_05:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G064F_06:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #32,                                                        ; Component0
                    #00,                                                        ; Component1
                    #2E                                                         ; Component2
                }
G064F_07:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #43                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R064F_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R064F_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R064F_02:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R064F_03:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R064F_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R064F_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R064F_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R064F_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R064F_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R064F_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R064F_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R064F_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R064F_0C:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R064F_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R064F_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R064F_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R064F_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R064F_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R064F_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R064F_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R064F_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R064F_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R064F_16:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R064F_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R064F_18:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C6EA
                endmodule
