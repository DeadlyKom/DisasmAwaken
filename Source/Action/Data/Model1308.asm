                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #D308
M1308:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #04                                                         ; ScaleExponent
                }
G1308_00:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #59                                                         ; Component2
                }
G1308_01:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #21,                                                        ; Component0
                    #00,                                                        ; Component1
                    #5A                                                         ; Component2
                }
G1308_02:       FActionModelGroup {
                    #80,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1308_03:       FActionModelGroup {
                    #F0,                                                        ; Mask, комбинации вершин
                    #09,                                                        ; Component0
                    #15,                                                        ; Component1
                    #1B                                                         ; Component2
                }
G1308_04:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #14,                                                        ; Component0
                    #00,                                                        ; Component1
                    #38                                                         ; Component2
                }
G1308_05:       FActionModelGroup {
                    #0F,                                                        ; Mask, комбинации вершин
                    #27,                                                        ; Component0
                    #20,                                                        ; Component1
                    #68                                                         ; Component2
                }
G1308_06:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #47,                                                        ; Component0
                    #00,                                                        ; Component1
                    #66                                                         ; Component2
                }
G1308_07:       FActionModelGroup {
                    #01,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #00,                                                        ; Component1
                    #51                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1308_00:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #00,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1308_01:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1308_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1308_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1308_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #32,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0A,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
R1308_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #37,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1308_06:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #41                                                         ; Vertex2
                }
R1308_07:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #5A                                                         ; Vertex2
                }
R1308_08:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1308_09:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #5F,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1308_0A:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #50                                                         ; Vertex2
                }
R1308_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #4B,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #28                                                         ; Vertex3
                }
R1308_0C:       FActionModelPrimitive3 {
                    #23,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R1308_0D:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1308_0E:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #46,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1308_0F:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #14,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #1E                                                         ; Vertex2
                }
R1308_10:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #41,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1308_11:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #14                                                         ; Vertex2
                }
R1308_12:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #32,                                                        ; Vertex2
                    #37                                                         ; Vertex3
                }
R1308_13:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #0F,                                                        ; Vertex1
                    #0A                                                         ; Vertex2
                }
R1308_14:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #55,                                                        ; Vertex1
                    #37,                                                        ; Vertex2
                    #23                                                         ; Vertex3
                }
R1308_15:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #19,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1308_16:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #19                                                         ; Vertex2
                }
R1308_17:       FActionModelPrimitive3 {
                    #33,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #00                                                         ; Vertex2
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #D398
                endmodule
