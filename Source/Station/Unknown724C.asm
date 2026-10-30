                module Station
                module Unknown724C
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #14F8..#15EA
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
Entry:          EX DE, HL
                LD HL, #9592
                PUSH HL
                LD A, (#9849)
                PUSH AF
                LD HL, #9400
                PUSH HL
                LD HL, #95F0
                PUSH HL
                LD HL, #988E
                PUSH HL
                LD HL, #EE57
                LD BC, #1800
                LD (#6320), BC
                PUSH DE
                LD A, E
                CALL @Station.PrintAfterCR.Entry
                LD A, #18
                LD (#6321), A
                POP BC
                POP HL
                ADD HL, BC
                EX DE, HL
                SLA C
                RL B
                PUSH BC
                EXX
                POP BC
                POP HL
                ADD HL, BC
                EX DE, HL
                SLA C
                RL B
                POP HL
                ADD HL, BC
                EX DE, HL
                EXX
                POP AF
                LD (#7306), A
                POP HL
                ADD HL, BC
                EX DE, HL
                XOR A
                EX AF, AF'
Point7294:      LD A, (@TextStreamState.Column2X)
                LD (#6320), A
                EX AF, AF'
                INC A
                EX AF, AF'
                LD A, (HL)
                INC HL
                CP #80
                RET Z                                                           ; выход, если флаг Z установлен

                AND A
                JP P, @Station.Unknown724C.Point72A7                            ; переход, если флаг Sign сброшен


                CPL
Point72A7:      AND A
                JR NZ, @Station.Unknown724C.Point72B1                           ; переход, если флаг Z сброшен


                LD A, #2D
                CALL @Station.DrawGlyph.Entry
                JR @Station.Unknown724C.Point72B7


Point72B1:      LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
Point72B7:      JR C, @Station.Unknown724C.Point72BD                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point72BD:      LD A, (@TextStreamState.Column3X)
                LD (#6320), A
                LD A, (DE)
                LD C, A
                INC DE
                LD A, (DE)
                LD B, A
                INC DE
                XOR A
                CALL @Station.PrintWord.Entry
                JR C, @Station.Unknown724C.Point72D3                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point72D3:      LD A, (@TextStreamState.Column4X)
                ADD A, #04
                LD (#6320), A
                EXX
                LD A, #00
                CP (HL)
                INC HL
                JR NC, @Station.Unknown724C.Point72EB                           ; переход, если флаг Carry сброшен


                INC HL
                EXX
                LD A, #2D
                CALL @Station.DrawGlyph.Entry
                JR @Station.Unknown724C.Point72F4


Point72EB:      LD A, (HL)
                INC HL
                EXX
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
Point72F4:      JR C, @Station.Unknown724C.Point72FA                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point72FA:      LD A, (@TextStreamState.Column5X)
                ADD A, #04
                LD (#6320), A
                EXX
                EX DE, HL
                PUSH HL
                LD A, #00
                OR A
                JP M, @Station.Unknown724C.Point731C                            ; переход, если флаг Sign установлен


                CP (HL)
                INC HL
                JR Z, @Station.Unknown724C.Point731C                            ; переход, если флаг Z установлен


                CP (HL)
                INC HL
                JR Z, @Station.Unknown724C.Point731C                            ; переход, если флаг Z установлен


                CP (HL)
                INC HL
                JR Z, @Station.Unknown724C.Point731C                            ; переход, если флаг Z установлен


                CP (HL)
                INC HL
                JR Z, @Station.Unknown724C.Point731C                            ; переход, если флаг Z установлен


                SCF
Point731C:      LD A, #FB
                CALL C, @Station.DrawGlyph.Entry                                ; вызов, если флаг Carry установлен
                POP HL
                JR C, @Station.Unknown724C.Point7328                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point7328:      LD BC, #0004
                ADD HL, BC
                EX DE, HL
                EXX
                LD A, (#AEAB)
                LD C, A
                LD A, (#6321)
                ADD A, #08
                CP C
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD (#6321), A
                JP @Station.Unknown724C.Point7294


                endmodule
                endmodule
