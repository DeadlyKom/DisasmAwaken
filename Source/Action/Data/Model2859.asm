                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #E859
M2859:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G2859_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #12,                                                        ; Component0
                    #12,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2859_01:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #07,                                                        ; Component0
                    #10,                                                        ; Component1
                    #0F                                                         ; Component2
                }
G2859_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #01,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2859_03:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #0A,                                                        ; Component0
                    #02,                                                        ; Component1
                    #16                                                         ; Component2
                }
G2859_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #55,                                                        ; Component0
                    #16,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2859_05:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #6C,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G2859_06:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #29,                                                        ; Component0
                    #15,                                                        ; Component1
                    #4B                                                         ; Component2
                }
G2859_07:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #35,                                                        ; Component0
                    #00,                                                        ; Component1
                    #59                                                         ; Component2
                }
G2859_08:       FActionModelGroup {
                    #40,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #45,                                                        ; Component1
                    #00                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R2859_00:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R2859_01:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R2859_02:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R2859_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R2859_04:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #91,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R2859_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #9B,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R2859_06:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #8C,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R2859_07:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R2859_08:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R2859_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0E:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #B4                                                         ; Vertex2
                }
R2859_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R2859_10:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R2859_11:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #14                                                         ; Vertex3
                }
R2859_12:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R2859_13:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R2859_14:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R2859_15:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R2859_16:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R2859_17:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R2859_18:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R2859_19:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R2859_1A:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #1E                                                         ; Vertex3
                }
R2859_1B:       FActionModelPrimitive6 {
                    #06,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #32,                                                        ; Vertex3
                    #37,                                                        ; Vertex4
                    #00                                                         ; Vertex5
                }
R2859_1C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #AF,                                                        ; Vertex2
                    #8C                                                         ; Vertex3
                }
R2859_1D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #AF,                                                        ; Vertex1
                    #AA,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R2859_1E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #AA,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R2859_1F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #A5,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R2859_20:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #A5,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R2859_21:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #87,                                                        ; Vertex0
                    #A0,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R2859_22:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #A5,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #A0                                                         ; Vertex3
                }
R2859_23:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #A5,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R2859_24:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #AA,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
R2859_25:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #AA,                                                        ; Vertex1
                    #AF,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R2859_26:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #AF,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R2859_27:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #A0,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R2859_28:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R2859_29:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R2859_2A:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #96                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #E954
                endmodule
