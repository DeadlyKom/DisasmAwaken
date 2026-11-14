                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CD10
Kd29:           FActionModelHeader {
                    #6C,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #02                                                         ; ScaleExponent
                }
G0D10_00:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G0D10_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #5B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0D10_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #29,                                                        ; Component1
                    #57                                                         ; Component2
                }
G0D10_03:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #33,                                                        ; Component1
                    #38                                                         ; Component2
                }
G0D10_04:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #68,                                                        ; Component0
                    #00,                                                        ; Component1
                    #3C                                                         ; Component2
                }
G0D10_05:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #58,                                                        ; Component0
                    #00,                                                        ; Component1
                    #19                                                         ; Component2
                }
G0D10_06:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #18,                                                        ; Component0
                    #1F,                                                        ; Component1
                    #6C                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0D10_00:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #3C,                                                        ; Vertex0
                    #0A                                                         ; Vertex1
                }
R0D10_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0D10_02:       FActionModelPrimitive2 {
                    #A2,                                                        ; Header, линия
                    #41,                                                        ; Vertex0
                    #0F                                                         ; Vertex1
                }
R0D10_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0D10_04:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R0D10_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0D10_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0D10_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0D10_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R0D10_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0D10_0A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0D10_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0D10_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0D10_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0D10_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R0D10_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R0D10_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R0D10_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R0D10_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0D10_13:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0D10_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CD8B
                endmodule
