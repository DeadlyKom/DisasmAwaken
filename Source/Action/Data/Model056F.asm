                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C56F
M056F:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G056F_00:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #15,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G056F_01:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #45,                                                        ; Component0
                    #00,                                                        ; Component1
                    #2B                                                         ; Component2
                }
G056F_02:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #18,                                                        ; Component0
                    #03,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G056F_03:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #28,                                                        ; Component1
                    #3D                                                         ; Component2
                }
G056F_04:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #01                                                         ; Component2
                }
G056F_05:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #27,                                                        ; Component1
                    #1F                                                         ; Component2
                }
G056F_06:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #03,                                                        ; Component1
                    #3F                                                         ; Component2
                }
G056F_07:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #01,                                                        ; Component1
                    #22                                                         ; Component2
                }
G056F_08:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #3E,                                                        ; Component0
                    #20,                                                        ; Component1
                    #00                                                         ; Component2
                }
G056F_09:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #31,                                                        ; Component1
                    #4B                                                         ; Component2
                }
G056F_0A:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #67,                                                        ; Component0
                    #03,                                                        ; Component1
                    #0E                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R056F_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R056F_01:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R056F_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #46,                                                        ; Vertex0
                    #64                                                         ; Vertex1
                }
R056F_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R056F_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R056F_05:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #4B,                                                        ; Vertex0
                    #69                                                         ; Vertex1
                }
R056F_06:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R056F_07:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #28,                                                        ; Vertex3
                    #32,                                                        ; Vertex4
                    #1E                                                         ; Vertex5
                }
R056F_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R056F_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R056F_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R056F_0B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R056F_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R056F_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R056F_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R056F_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R056F_10:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R056F_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R056F_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R056F_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R056F_14:       FActionModelPrimitive6 {
                    #16,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5A,                                                        ; Vertex3
                    #5F,                                                        ; Vertex4
                    #55                                                         ; Vertex5
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C602
                endmodule
