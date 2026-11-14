                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DE12
St6:            FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1E12_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #29,                                                        ; Component0
                    #00,                                                        ; Component1
                    #64                                                         ; Component2
                }
G1E12_01:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #29                                                         ; Component2
                }
G1E12_02:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #31,                                                        ; Component0
                    #16,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1E12_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #13,                                                        ; Component1
                    #29                                                         ; Component2
                }
G1E12_04:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #34,                                                        ; Component1
                    #00                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1E12_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1E12_01:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1E12_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1E12_03:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1E12_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R1E12_05:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1E12_06:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #4B,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1E12_07:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #50,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1E12_08:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #32,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R1E12_09:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #3C,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1E12_0A:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #5F,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R1E12_0B:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #2D,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1E12_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1E12_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R1E12_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R1E12_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1E12_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1E12_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1E12_12:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1E12_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1E12_14:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1E12_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1E12_16:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1E12_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1E12_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1E12_19:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1E12_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R1E12_1B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DEAC
                endmodule
