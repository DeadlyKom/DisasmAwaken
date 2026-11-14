                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #CA40
Kd22:           FActionModelHeader {
                    #67,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #04                                                         ; ScaleExponent
                }
G0A40_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #12,                                                        ; Component0
                    #0A,                                                        ; Component1
                    #4E                                                         ; Component2
                }
G0A40_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1C,                                                        ; Component0
                    #17,                                                        ; Component1
                    #24                                                         ; Component2
                }
G0A40_02:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #16,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #35                                                         ; Component2
                }
G0A40_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0E,                                                        ; Component0
                    #09,                                                        ; Component1
                    #44                                                         ; Component2
                }
G0A40_04:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #20,                                                        ; Component0
                    #00,                                                        ; Component1
                    #1B                                                         ; Component2
                }
G0A40_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #1E,                                                        ; Component0
                    #17,                                                        ; Component1
                    #42                                                         ; Component2
                }
G0A40_06:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #26,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G0A40_07:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #00,                                                        ; Component1
                    #54                                                         ; Component2
                }
G0A40_08:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #44                                                         ; Component2
                }
G0A40_09:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #0C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #67                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R0A40_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #82                                                         ; Vertex2
                }
R0A40_01:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R0A40_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R0A40_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R0A40_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R0A40_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R0A40_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R0A40_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R0A40_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0A40_09:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R0A40_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R0A40_0B:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0A40_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R0A40_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R0A40_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0A40_0F:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R0A40_10:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R0A40_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #A5,                                                        ; Vertex1
                    #8C                                                         ; Vertex2
                }
R0A40_12:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #82                                                         ; Vertex2
                }
R0A40_13:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R0A40_14:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R0A40_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #96                                                         ; Vertex2
                }
R0A40_16:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #7D                                                         ; Vertex2
                }
R0A40_17:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R0A40_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R0A40_19:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R0A40_1A:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #A5,                                                        ; Vertex1
                    #A0,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R0A40_1B:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #A5,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #96,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #CAEE
                endmodule
