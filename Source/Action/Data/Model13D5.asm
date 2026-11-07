                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D3D5
M13D5:          FActionModelHeader {
                    #6C,                                                        ; Unknown00, смысл не установлен
                    #03                                                         ; ScaleExponent
                }
G13D5_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #2C,                                                        ; Component1
                    #6A                                                         ; Component2
                }
G13D5_01:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2F,                                                        ; Component0
                    #14,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G13D5_02:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #15,                                                        ; Component1
                    #26                                                         ; Component2
                }
G13D5_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #05,                                                        ; Component0
                    #05,                                                        ; Component1
                    #6C                                                         ; Component2
                }
G13D5_04:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #1A,                                                        ; Component0
                    #0D,                                                        ; Component1
                    #53                                                         ; Component2
                }
G13D5_05:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #1C,                                                        ; Component1
                    #41                                                         ; Component2
                }
G13D5_06:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #15,                                                        ; Component1
                    #27                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R13D5_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R13D5_01:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R13D5_02:       FActionModelPrimitive4 {
                    #44,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R13D5_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R13D5_04:       FActionModelPrimitive8 {
                    #48,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #19,                                                        ; Vertex3
                    #05,                                                        ; Vertex4
                    #00,                                                        ; Vertex5
                    #14,                                                        ; Vertex6
                    #23                                                         ; Vertex7
                }
R13D5_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R13D5_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R13D5_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #55                                                         ; Vertex2
                }
R13D5_08:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R13D5_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #7D                                                         ; Vertex2
                }
R13D5_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R13D5_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #78                                                         ; Vertex2
                }
R13D5_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R13D5_0D:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R13D5_0E:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #41                                                         ; Vertex3
                }
R13D5_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R13D5_10:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #87                                                         ; Vertex2
                }
R13D5_11:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #82,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R13D5_12:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R13D5_13:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R13D5_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R13D5_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R13D5_16:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R13D5_17:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R13D5_18:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #82                                                         ; Vertex2
                }
R13D5_19:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #73,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #46,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R13D5_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R13D5_1B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D479
                endmodule
