                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D28A
M128A:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G128A_00:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #18,                                                        ; Component1
                    #14                                                         ; Component2
                }
G128A_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #08,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G128A_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #4B,                                                        ; Component0
                    #26,                                                        ; Component1
                    #18                                                         ; Component2
                }
G128A_03:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #20,                                                        ; Component1
                    #09                                                         ; Component2
                }
G128A_04:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G128A_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #3F,                                                        ; Component0
                    #18,                                                        ; Component1
                    #48                                                         ; Component2
                }
G128A_06:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #6D,                                                        ; Component0
                    #06,                                                        ; Component1
                    #00                                                         ; Component2
                }
G128A_07:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #2A,                                                        ; Component1
                    #62                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R128A_00:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R128A_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R128A_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R128A_03:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R128A_04:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R128A_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R128A_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R128A_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R128A_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R128A_09:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R128A_0A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R128A_0B:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R128A_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R128A_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R128A_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R128A_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R128A_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R128A_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R128A_12:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R128A_13:       FActionModelPrimitive5 {
                    #25,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28,                                                        ; Vertex3
                    #3C                                                         ; Vertex4
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D308
                endmodule
