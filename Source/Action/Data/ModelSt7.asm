                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DEAC
St7:            FActionModelHeader {
                    #6B,                                                        ; BoundMantissa, мантисса границы близости и проекции
                    #05                                                         ; ScaleExponent
                }
G1EAC_00:       FActionModelGroup {
                    #33,                                                        ; Mask, комбинации вершин
                    #33,                                                        ; Component0
                    #00,                                                        ; Component1
                    #57                                                         ; Component2
                }
G1EAC_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #6B,                                                        ; Component0
                    #00,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1EAC_02:       FActionModelGroup {
                    #05,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #0F,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1EAC_03:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #16,                                                        ; Component1
                    #27                                                         ; Component2
                }
G1EAC_04:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1EAC_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #2E,                                                        ; Component0
                    #17,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1EAC_06:       FActionModelGroup {
                    #FF,                                                        ; Mask, комбинации вершин
                    #0D,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #11                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1EAC_00:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1EAC_01:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1EAC_02:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R1EAC_03:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1EAC_04:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #2D                                                         ; Vertex2
                }
R1EAC_05:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #2D,                                                        ; Vertex0
                    #1E,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R1EAC_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
R1EAC_07:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1EAC_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1EAC_09:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1EAC_0A:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1EAC_0B:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1EAC_0C:       FActionModelPrimitive6 {
                    #06,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #82,                                                        ; Vertex1
                    #87,                                                        ; Vertex2
                    #5F,                                                        ; Vertex3
                    #8C,                                                        ; Vertex4
                    #91                                                         ; Vertex5
                }
R1EAC_0D:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #82,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #87                                                         ; Vertex3
                }
R1EAC_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #87,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #73                                                         ; Vertex3
                }
R1EAC_0F:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #8C                                                         ; Vertex3
                }
R1EAC_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #8C,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #91                                                         ; Vertex3
                }
R1EAC_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #91,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #6E,                                                        ; Vertex2
                    #5A                                                         ; Vertex3
                }
R1EAC_12:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #82                                                         ; Vertex3
                }
R1EAC_13:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #37                                                         ; Vertex2
                }
R1EAC_14:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R1EAC_15:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1EAC_16:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #3C                                                         ; Vertex2
                }
R1EAC_17:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #73                                                         ; Vertex2
                }
R1EAC_18:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1EAC_19:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1A:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #0F,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1B:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1C:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1D:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1E:       FActionModelPrimitive3 {
                    #13,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1EAC_1F:       FActionModelPrimitive6 {
                    #06,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #96,                                                        ; Vertex1
                    #9B,                                                        ; Vertex2
                    #50,                                                        ; Vertex3
                    #78,                                                        ; Vertex4
                    #7D                                                         ; Vertex5
                }
R1EAC_20:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #4B,                                                        ; Vertex2
                    #9B                                                         ; Vertex3
                }
R1EAC_21:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #9B,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #64,                                                        ; Vertex2
                    #50                                                         ; Vertex3
                }
R1EAC_22:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #78                                                         ; Vertex3
                }
R1EAC_23:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #7D,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1EAC_24:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #28,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #7D                                                         ; Vertex3
                }
R1EAC_25:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #96,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #69,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DF76
                endmodule
