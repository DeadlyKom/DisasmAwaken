                module Station
                module Unknown7096
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1342..#13FF
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
                LD HL, #2000
                LD (#6320), HL
                LD HL, #EC4C
                PUSH DE
                LD A, E
                CALL @Station.PrintAfterCR.Entry
                LD A, #20
                LD (#6321), A
                POP HL
                ADD HL, HL
                LD B, H
                LD C, L
                LD HL, #9555
                ADD HL, BC
                EX DE, HL
                LD HL, #9852
                ADD HL, BC
                XOR A
                EX AF, AF'
Point70B9:      LD A, (@TextStreamState.Column2X)
                LD (#6320), A
                LD A, (DE)
                INC A
                RET Z                                                           ; выход, если флаг Z установлен

                EX AF, AF'
                INC A
                EX AF, AF'
                DEC A
                AND #7F
                JR NZ, @Station.Unknown7096.Point70D1                           ; переход, если флаг Z сброшен


                LD A, #2D
                CALL @Station.DrawGlyph.Entry
                JR @Station.Unknown7096.Point70D7


Point70D1:      LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
Point70D7:      JR C, @Station.Unknown7096.Point70DD                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point70DD:      LD A, (DE)
                INC DE
                RLA
                JR NC, @Station.Unknown7096.Point70EC                           ; переход, если флаг Carry сброшен


                LD A, #6D
                LD (#6320), A
                LD A, #FE
                CALL @Station.DrawGlyph.Entry
Point70EC:      LD A, (@TextStreamState.Column3X)
                LD (#6320), A
                LD A, (DE)
                INC DE
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
                JR C, @Station.Unknown7096.Point7100                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point7100:      LD A, (@TextStreamState.Column4X)
                LD (#6320), A
                LD A, (HL)
                AND #7F
                INC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                JR NZ, @Station.Unknown7096.Point7115                           ; переход, если флаг Z сброшен


                LD A, #2D
                CALL @Station.DrawGlyph.Entry
                JR @Station.Unknown7096.Point711B


Point7115:      LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
Point711B:      JR C, @Station.Unknown7096.Point7121                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point7121:      LD A, (HL)
                INC HL
                RLA
                JR NC, @Station.Unknown7096.Point7130                           ; переход, если флаг Carry сброшен


                LD A, #86
                LD (#6320), A
                LD A, #FE
                CALL @Station.DrawGlyph.Entry
Point7130:      LD A, (@TextStreamState.Column5X)
                LD (#6320), A
                LD C, (HL)
                LD B, #00
                INC HL
                CALL @Station.Print4DigitCore.Entry
                JR C, @Station.Unknown7096.Point7143                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point7143:      LD A, (#AEAB)
                LD C, A
                LD A, (#6321)
                ADD A, #08
                CP C
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD (#6321), A
                JP @Station.Unknown7096.Point70B9


                endmodule
                endmodule
