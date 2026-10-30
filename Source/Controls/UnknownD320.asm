                module Controls
                module UnknownD320
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1320..#14CA
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          LD BC, (#D183)
                LD DE, (#D17F)
                LD A, D
                NEG
                EXX
                LD C, A
                LD E, #00
                EXX
                LD A, B
                SUB D
                CALL @Controls.UnknownD515.Entry
                LD A, (#D183)
                LD C, A
                LD A, (#D184)
                ADD A, D
                JP @Controls.UnknownD53C.Entry


PointD340:      LD A, B
                ADD A, #78
                LD B, A
                LD (#D182), A
                XOR A
                JR @Controls.UnknownD320.PointD34E


PointD34A:      LD A, #88
                ADD A, B
                INC A
PointD34E:      EX AF, AF'
                LD A, #78
                ADD A, B
                CALL @Controls.UnknownD609.Entry
                LD (#D185), A
                LD B, A
                LD A, (#D183)
                CALL @Controls.UnknownD208.Entry
                CALL @Controls.UnknownD56C.Entry
                CALL @Controls.UnknownD57B.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1CB.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD1A2.Entry                            ; вызов, если флаг Z сброшен
                LD A, (#D185)
                LD B, A
                LD A, (#D183)
                CALL @Controls.UnknownD211.Entry
                CALL @Controls.UnknownD56C.Entry
                CALL @Controls.UnknownD57B.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1B6.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD18D.Entry                            ; вызов, если флаг Z сброшен
                RET


PointD38C:      LD A, B
                ADD A, #78
                LD B, A
                LD (#D182), A
                XOR A
                JR @Controls.UnknownD320.PointD399


PointD396:      LD A, B
                SUB #77
PointD399:      EX AF, AF'
                LD DE, (#D17F)
                LD A, #78
                ADD A, B
                CALL @Controls.UnknownD609.Entry
                LD (#D185), A
                SUB C
                LD B, A
                BIT 1, E
                JR Z, @Controls.UnknownD320.PointD3C3                           ; переход, если флаг Z установлен


                XOR A
                CALL @Controls.UnknownD211.Entry
                CALL @Controls.UnknownD56C.Entry
                CALL @Controls.UnknownD57B.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1B6.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD18D.Entry                            ; вызов, если флаг Z сброшен
                RET


PointD3C3:      LD A, #5F
                CALL @Controls.UnknownD208.Entry
                CALL @Controls.UnknownD56C.Entry
                CALL @Controls.UnknownD57B.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1CB.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD1A2.Entry                            ; вызов, если флаг Z сброшен
                RET


PointD3DA:      LD A, B
                ADD A, #78
                LD (#D182), A
                LD B, A
                XOR A
                JR @Controls.UnknownD320.PointD3E7


PointD3E4:      LD A, B
                SUB #77
PointD3E7:      EX AF, AF'
                BIT 0, E
                JR Z, @Controls.UnknownD320.PointD3F8                           ; переход, если флаг Z установлен


                CALL @Controls.UnknownD4CB.Entry
                CALL @Controls.UnknownD18D.Entry
                CALL @Controls.UnknownD4CB.Entry
                JP @Controls.UnknownD1A2.Entry


PointD3F8:      CALL @Controls.UnknownD4E4.Entry
                CALL @Controls.UnknownD1B6.Entry
                CALL @Controls.UnknownD4E4.Entry
                JP @Controls.UnknownD1CB.Entry


PointD404:      LD A, B
                ADD A, #78
                LD (#D182), A
                LD B, A
                XOR A
                JR @Controls.UnknownD320.PointD411


PointD40E:      LD A, B
                SUB #77
PointD411:      EX AF, AF'
                LD DE, (#D17F)
                LD A, C
                CALL @Controls.UnknownD609.Entry
                LD (#D185), A
                LD A, C
                EXX
                LD E, A
                LD A, (#D185)
                NEG
                LD C, A
                EXX
                BIT 0, E
                JR Z, @Controls.UnknownD320.PointD459                           ; переход, если флаг Z установлен


                LD A, (#D185)
                CPL
                ADD A, #81
                ADD A, B
                LD C, #00
                BIT 1, E
                JR NZ, @Controls.UnknownD320.PointD43A                          ; переход, если флаг Z сброшен


                LD C, #5F
PointD43A:      CALL @Controls.UnknownD515.Entry
                LD A, (#D18C)
                AND A
                LD A, E
                AND #1F
                CP #1F
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, E
                OR #1F
                LD L, A
                LD C, #FF
                LD A, (#D17F)
                BIT 1, A
                CALL NZ, @Controls.UnknownD18D.Entry                            ; вызов, если флаг Z сброшен
                CALL Z, @Controls.UnknownD1A2.Entry                             ; вызов, если флаг Z установлен
                RET


PointD459:      LD A, (#D185)
                ADD A, #80
                SUB B
                CP #08
                RET C                                                           ; выход, если флаг Carry установлен

                LD C, #00
                BIT 1, E
                JR NZ, @Controls.UnknownD320.PointD46A                          ; переход, если флаг Z сброшен


                LD C, #5F
PointD46A:      CALL @Controls.UnknownD53C.Entry
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD A, (#D18C)
                AND A
                LD B, #00
                LD A, (#D17F)
                BIT 1, A
                CALL NZ, @Controls.UnknownD1B6.Entry                            ; вызов, если флаг Z сброшен
                CALL Z, @Controls.UnknownD1CB.Entry                             ; вызов, если флаг Z установлен
                RET


PointD485:      LD DE, (#D17F)
                LD A, C
                CALL @Controls.UnknownD609.Entry
                LD (#D185), A
                LD A, C
                EXX
                LD E, A
                LD A, (#D185)
                NEG
                LD C, A
                EXX
                XOR A
                BIT 1, E
                JR NZ, @Controls.UnknownD320.PointD4A1                          ; переход, если флаг Z сброшен


                LD A, #5F
PointD4A1:      LD (#D183), A
                LD C, A
                LD A, (#D185)
                LD L, A
                LD A, (#D184)
                SUB L
                CALL @Controls.UnknownD515.Entry
                LD A, (#D183)
                LD C, A
                LD A, (#D185)
                LD L, A
                LD A, (#D184)
                ADD A, L
                CALL @Controls.UnknownD53C.Entry
                LD A, (#D17F)
                BIT 1, A
                CALL NZ, @Controls.UnknownD1DF.Entry                            ; вызов, если флаг Z сброшен
                CALL Z, @Controls.UnknownD1F4.Entry                             ; вызов, если флаг Z установлен
                RET


                endmodule
                endmodule
