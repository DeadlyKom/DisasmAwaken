                module Controls
                module UnknownD340
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1340..#14CA
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
Entry:          LD A, B
                ADD A, #78
                LD B, A
                LD (#D182), A
                XOR A
                JR @Controls.UnknownD340.PointD34E


PointD34A:      LD A, #88
                ADD A, B
                INC A
PointD34E:      EX AF, AF'
                LD A, #78
                ADD A, B
                CALL @Controls.SqrtSquareDiff.Entry
                LD (#D185), A
                LD B, A
                LD A, (#D183)
                CALL @Controls.FillInteriorRowsUp.Entry
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1CB.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD1A2.Entry                            ; вызов, если флаг Z сброшен
                LD A, (#D185)
                LD B, A
                LD A, (#D183)
                CALL @Controls.FillInteriorRowsDown.Entry
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
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
                JR @Controls.UnknownD340.PointD399


PointD396:      LD A, B
                SUB #77
PointD399:      EX AF, AF'
                LD DE, (#D17F)
                LD A, #78
                ADD A, B
                CALL @Controls.SqrtSquareDiff.Entry
                LD (#D185), A
                SUB C
                LD B, A
                BIT 1, E
                JR Z, @Controls.UnknownD340.PointD3C3                           ; переход, если флаг Z установлен


                XOR A
                CALL @Controls.FillInteriorRowsDown.Entry
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (#D17F)
                BIT 0, A
                CALL Z, @Controls.UnknownD1B6.Entry                             ; вызов, если флаг Z установлен
                CALL NZ, @Controls.UnknownD18D.Entry                            ; вызов, если флаг Z сброшен
                RET


PointD3C3:      LD A, #5F
                CALL @Controls.FillInteriorRowsUp.Entry
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
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
                JR @Controls.UnknownD340.PointD3E7


PointD3E4:      LD A, B
                SUB #77
PointD3E7:      EX AF, AF'
                BIT 0, E
                JR Z, @Controls.UnknownD340.PointD3F8                           ; переход, если флаг Z установлен


                CALL @Controls.PrepareCircleRightClip.Entry
                CALL @Controls.UnknownD18D.Entry
                CALL @Controls.PrepareCircleRightClip.Entry
                JP @Controls.UnknownD1A2.Entry


PointD3F8:      CALL @Controls.PrepareCircleLeftClip.Entry
                CALL @Controls.UnknownD1B6.Entry
                CALL @Controls.PrepareCircleLeftClip.Entry
                JP @Controls.UnknownD1CB.Entry


PointD404:      LD A, B
                ADD A, #78
                LD (#D182), A
                LD B, A
                XOR A
                JR @Controls.UnknownD340.PointD411


PointD40E:      LD A, B
                SUB #77
PointD411:      EX AF, AF'
                LD DE, (#D17F)
                LD A, C
                CALL @Controls.SqrtSquareDiff.Entry
                LD (#D185), A
                LD A, C
                EXX
                LD E, A
                LD A, (#D185)
                NEG
                LD C, A
                EXX
                BIT 0, E
                JR Z, @Controls.UnknownD340.PointD459                           ; переход, если флаг Z установлен


                LD A, (#D185)
                CPL
                ADD A, #81
                ADD A, B
                LD C, #00
                BIT 1, E
                JR NZ, @Controls.UnknownD340.PointD43A                          ; переход, если флаг Z сброшен


                LD C, #5F
PointD43A:      CALL @Controls.BuildLeftSpanMask.Entry
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
                JR NZ, @Controls.UnknownD340.PointD46A                          ; переход, если флаг Z сброшен


                LD C, #5F
PointD46A:      CALL @Controls.BuildRightSpanMask.Entry
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
                CALL @Controls.SqrtSquareDiff.Entry
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
                JR NZ, @Controls.UnknownD340.PointD4A1                          ; переход, если флаг Z сброшен


                LD A, #5F
PointD4A1:      LD (#D183), A
                LD C, A
                LD A, (#D185)
                LD L, A
                LD A, (#D184)
                SUB L
                CALL @Controls.BuildLeftSpanMask.Entry
                LD A, (#D183)
                LD C, A
                LD A, (#D185)
                LD L, A
                LD A, (#D184)
                ADD A, L
                CALL @Controls.BuildRightSpanMask.Entry
                LD A, (#D17F)
                BIT 1, A
                CALL NZ, @Controls.UnknownD1DF.Entry                            ; вызов, если флаг Z сброшен
                CALL Z, @Controls.UnknownD1F4.Entry                             ; вызов, если флаг Z установлен
                RET


                endmodule
                endmodule
