                module ActionModels
                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)
                assert $ == #DB80
M1B80:          FActionModelHeader {
                    #6D,                                                        ; Unknown00, смысл не установлен
                    #05                                                         ; ScaleExponent
                }
G1B80_00:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #18,                                                        ; Component0
                    #21,                                                        ; Component1
                    #20                                                         ; Component2
                }
G1B80_01:       FActionModelGroup {
                    #20,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #22,                                                        ; Component1
                    #06                                                         ; Component2
                }
G1B80_02:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #52,                                                        ; Component0
                    #15,                                                        ; Component1
                    #2D                                                         ; Component2
                }
G1B80_03:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #63,                                                        ; Component0
                    #15,                                                        ; Component1
                    #18                                                         ; Component2
                }
G1B80_04:       FActionModelGroup {
                    #03,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #17,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1B80_05:       FActionModelGroup {
                    #30,                                                        ; Mask, комбинации вершин
                    #5C,                                                        ; Component0
                    #0B,                                                        ; Component1
                    #20                                                         ; Component2
                }
G1B80_06:       FActionModelGroup {
                    #01,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #0C,                                                        ; Component1
                    #6D                                                         ; Component2
                }
G1B80_07:       FActionModelGroup {
                    #01,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #05,                                                        ; Component1
                    #00                                                         ; Component2
                }
G1B80_08:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #53,                                                        ; Component0
                    #11,                                                        ; Component1
                    #4B                                                         ; Component2
                }
G1B80_09:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #61,                                                        ; Component0
                    #12,                                                        ; Component1
                    #3A                                                         ; Component2
                }
G1B80_0A:       FActionModelGroup {
                    #0C,                                                        ; Mask, комбинации вершин
                    #58,                                                        ; Component0
                    #05,                                                        ; Component1
                    #3F                                                         ; Component2
                }
G1B80_0B:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #17,                                                        ; Component0
                    #1D,                                                        ; Component1
                    #0D                                                         ; Component2
                }
G1B80_0C:       FActionModelGroup {
                    #08,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #1E,                                                        ; Component1
                    #15                                                         ; Component2
                }
G1B80_0D:       FActionModelGroup {
                    #C0,                                                        ; Mask, комбинации вершин
                    #0F,                                                        ; Component0
                    #0E,                                                        ; Component1
                    #58                                                         ; Component2
                }
G1B80_0E:       FActionModelGroup {
                    #10,                                                        ; Mask, комбинации вершин
                    #00,                                                        ; Component0
                    #01,                                                        ; Component1
                    #55                                                         ; Component2
                }
                db #00                                                          ; конец групп компонент
R1B80_00:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #28,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1B80_01:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #05,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #2D,                                                        ; Vertex2
                    #19                                                         ; Vertex3
                }
R1B80_02:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #23,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1B80_03:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #32                                                         ; Vertex3
                }
R1B80_04:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #32,                                                        ; Vertex1
                    #14,                                                        ; Vertex2
                    #0A                                                         ; Vertex3
                }
R1B80_05:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #0A,                                                        ; Vertex1
                    #0F,                                                        ; Vertex2
                    #2D                                                         ; Vertex3
                }
R1B80_06:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #19,                                                        ; Vertex0
                    #2D,                                                        ; Vertex1
                    #0F                                                         ; Vertex2
                }
R1B80_07:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #1E,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #32                                                         ; Vertex2
                }
R1B80_08:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #23,                                                        ; Vertex0
                    #37,                                                        ; Vertex1
                    #28                                                         ; Vertex2
                }
R1B80_09:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #64,                                                        ; Vertex1
                    #69                                                         ; Vertex2
                }
R1B80_0A:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #5F,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1B80_0B:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #78,                                                        ; Vertex2
                    #3C                                                         ; Vertex3
                }
R1B80_0C:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #55,                                                        ; Vertex2
                    #4B                                                         ; Vertex3
                }
R1B80_0D:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #3C,                                                        ; Vertex0
                    #69,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #55                                                         ; Vertex3
                }
R1B80_0E:       FActionModelPrimitive4 {
                    #24,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #3C,                                                        ; Vertex1
                    #5A,                                                        ; Vertex2
                    #46                                                         ; Vertex3
                }
R1B80_0F:       FActionModelPrimitive4 {
                    #34,                                                        ; Header, грань
                    #50,                                                        ; Vertex0
                    #5A,                                                        ; Vertex1
                    #3C,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1B80_10:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #78,                                                        ; Vertex0
                    #73,                                                        ; Vertex1
                    #6E                                                         ; Vertex2
                }
R1B80_11:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #5F,                                                        ; Vertex0
                    #6E,                                                        ; Vertex1
                    #73,                                                        ; Vertex2
                    #64                                                         ; Vertex3
                }
R1B80_12:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #55,                                                        ; Vertex0
                    #41,                                                        ; Vertex1
                    #4B                                                         ; Vertex2
                }
R1B80_13:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #64,                                                        ; Vertex0
                    #4B,                                                        ; Vertex1
                    #41,                                                        ; Vertex2
                    #69                                                         ; Vertex3
                }
R1B80_14:       FActionModelPrimitive3 {
                    #43,                                                        ; Header, грань
                    #5A,                                                        ; Vertex0
                    #50,                                                        ; Vertex1
                    #46                                                         ; Vertex2
                }
R1B80_15:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #69,                                                        ; Vertex0
                    #46,                                                        ; Vertex1
                    #50,                                                        ; Vertex2
                    #5F                                                         ; Vertex3
                }
R1B80_16:       FActionModelPrimitive3 {
                    #03,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #00,                                                        ; Vertex1
                    #05                                                         ; Vertex2
                }
R1B80_17:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #14,                                                        ; Vertex1
                    #1E,                                                        ; Vertex2
                    #00                                                         ; Vertex3
                }
R1B80_18:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #00,                                                        ; Vertex0
                    #23,                                                        ; Vertex1
                    #28,                                                        ; Vertex2
                    #05                                                         ; Vertex3
                }
R1B80_19:       FActionModelPrimitive4 {
                    #14,                                                        ; Header, грань
                    #0A,                                                        ; Vertex0
                    #05,                                                        ; Vertex1
                    #19,                                                        ; Vertex2
                    #0F                                                         ; Vertex3
                }
                db #00                                                          ; конец потока примитивов
                assert $ == #DC3A
                endmodule
