                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C329
Kd7:            FActionModelHeader {
                    #65,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #04                                                         ; ScaleExponent
                }
G0329_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #10,                                                        ; Component1
                    #19                                                         ; Component2
                }
G0329_01:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #00,                                                        ; Component1
                    #46                                                         ; Component2
                }
G0329_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #10,                                                        ; Component0
                    #00,                                                        ; Component1
                    #65                                                         ; Component2
                }
G0329_03:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #61                                                         ; Component2
                }
G0329_04:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0329_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #16,                                                        ; Component1
                    #25                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0329_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R0329_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R0329_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #23                                                         ; Vertex2
                }
R0329_03:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R0329_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R0329_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R0329_06:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R0329_07:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R0329_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R0329_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R0329_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R0329_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R0329_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R0329_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0329_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0329_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R0329_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R0329_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R0329_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R0329_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R0329_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R0329_15:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R0329_16:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R0329_17:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R0329_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C3AE
                endmodule
