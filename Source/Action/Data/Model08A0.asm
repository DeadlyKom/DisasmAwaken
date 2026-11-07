                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #C8A0
M08A0:          FActionModelHeader {
                    #6B,                                                        ; Unknown00, смысл не установлен
                    #02                                                         ; ScaleExponent
                }
G08A0_00:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #28,                                                        ; Component0
                    #20,                                                        ; Component1
                    #5E                                                         ; Component2
                }
G08A0_01:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #19,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6B                                                         ; Component2
                }
G08A0_02:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #4B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #11                                                         ; Component2
                }
G08A0_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #45,                                                        ; Component0
                    #15,                                                        ; Component1
                    #55                                                         ; Component2
                }
G08A0_04:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #65,                                                        ; Component0
                    #00,                                                        ; Component1
                    #26                                                         ; Component2
                }
G08A0_05:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #45,                                                        ; Component0
                    #44,                                                        ; Component1
                    #1F                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R08A0_00:       FActionModelPrimitive8 {
                    #18,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #73,                                                        ; Vertex3
                    #64,                                                        ; Vertex4
                    #32,                                                        ; Vertex5
                    #2D,                                                        ; Vertex6
                    #5F                                                         ; Vertex7
                }
R08A0_01:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R08A0_02:       FActionModelPrimitive8 {
                    #18,                                                        ; Header, грань
                    #6E,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #7D,                                                        ; Vertex3
                    #5A,                                                        ; Vertex4
                    #28,                                                        ; Vertex5
                    #37,                                                        ; Vertex6
                    #69                                                         ; Vertex7
                }
R08A0_03:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R08A0_04:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R08A0_05:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R08A0_06:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R08A0_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R08A0_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R08A0_09:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R08A0_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #73                                                         ; Vertex2
                }
R08A0_0B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R08A0_0C:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R08A0_0D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #78                                                         ; Vertex2
                }
R08A0_0E:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #78,                                                        ; Vertex1
                    #5F                                                         ; Vertex2
                }
R08A0_0F:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R08A0_10:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R08A0_11:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #64                                                         ; Vertex2
                }
R08A0_12:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R08A0_13:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R08A0_14:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #7D                                                         ; Vertex2
                }
R08A0_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #7D,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R08A0_16:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R08A0_17:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R08A0_18:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R08A0_19:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R08A0_1A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #C935
                endmodule
