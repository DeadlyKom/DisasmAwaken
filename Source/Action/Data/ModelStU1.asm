                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E66B
StU1:           FActionModelHeader {
                    #6D,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G266B_00:       FActionModelGroup {
                    #11,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G266B_01:       FActionModelGroup {
                    #3C,                                                        ; Mask, комбинации вершин
                    #30,                                                        ; Component0
                    #10,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G266B_02:       FActionModelGroup {
                    #3C,                                                        ; Mask, комбинации вершин
                    #25,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G266B_03:       FActionModelGroup {
                    #14,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #28,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G266B_04:       FActionModelGroup {
                    #3C,                                                        ; Mask, комбинации вершин
                    #22,                                                        ; Component0
                    #15,                                                        ; Component1
                    #1E                                                         ; Component2
                }
G266B_05:       FActionModelGroup {
                    #3C,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #19                                                         ; Component2
                }
G266B_06:       FActionModelGroup {
                    #24,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #27,                                                        ; Component1
                    #3A                                                         ; Component2
                }
G266B_07:       FActionModelGroup {
                    #88,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G266B_08:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #3E,                                                        ; Component1
                    #00                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R266B_00:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #82,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #87                                                         ; Vertex2
                }
R266B_01:       FActionModelPrimitive3 {
                    #A3,                                                        ; Header, линия
                    #7D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #78                                                         ; Vertex2
                }
R266B_02:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #87,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R266B_03:       FActionModelPrimitive4 {
                    #A4,                                                        ; Header, линия
                    #78,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #7D,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R266B_04:       FActionModelPrimitive5 {
                    #A5,                                                        ; Header, линия
                    #7D,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #82,                                                        ; Vertex3
                    #7D                                                         ; Vertex4
                }
R266B_05:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R266B_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R266B_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R266B_08:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R266B_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R266B_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #6E                                                         ; Vertex3
                }
R266B_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R266B_0C:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R266B_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R266B_0E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R266B_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R266B_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R266B_11:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R266B_12:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R266B_13:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R266B_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R266B_15:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R266B_16:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R266B_17:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R266B_18:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E707
                endmodule
