                module Music
                module UnknownE2CB
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #07CB..#0938
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
Entry:          LD A, #00
PointE2CD:      LD (@MusicState.SlideCounterC), A
PointE2D0:      EX AF, AF'
PointE2D1:      LD (#DC0A), A
                LD A, #00
                DEC A
                JP M, @Music.UnknownE2CB.PointE2EB                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE2CB.PointE2E8                             ; переход, если флаг Z сброшен


                DEC A
                LD HL, #E1EE
                XOR (HL)
                LD (HL), A
                LD A, #00
                JR NZ, @Music.UnknownE2CB.PointE2E8                             ; переход, если флаг Z сброшен


                LD A, #00
PointE2E8:      LD (@MusicState.GateCounterC), A
PointE2EB:      EXX
                LD A, L
                LD DE, #0000
                LD HL, #0000
                ADD A, L
                LD L, A
                ADD HL, DE
                LD (#DC0B), HL
                LD A, #00
                DEC A
                JP M, @Music.UnknownE2CB.PointE30D                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE2CB.PointE30A                             ; переход, если флаг Z сброшен


                LD HL, #0000
                ADD HL, DE
                LD (#E2EE), HL
                LD A, #00
PointE30A:      LD (#E2FA), A
PointE30D:      LD SP, #0000
                LD DE, #FFBF
                LD BC, #FFFD
                LD HL, #DC00
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD A, IXH
                LD (#DFE9), A
                ADD A, (HL)
                LD B, E
                OUT (C), A
                INC L
                LD B, D
                OUT (C), L
                LD A, IXL
                LD B, E
                OUT (C), A
                INC L
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD B, D
                OUT (C), L
                LD B, E
                OUTI
                LD A, (HL)
                OR A
                JR Z, @Music.UnknownE2CB.PointE37C                              ; переход, если флаг Z установлен


                LD B, D
                OUT (C), L
                LD B, E
                OUT (C), A
                LD (HL), #00
PointE37C:      LD A, #03
                DEC A
                LD (#E37D), A
                JR Z, @Music.UnknownE2CB.PointE3BA                              ; переход, если флаг Z установлен


                DEC A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD HL, #DC0E
                DEC (HL)
                LD DE, #0618
                LD H, E
                LD B, E
                EXX
                JR NZ, @Music.UnknownE2CB.PointE3A3                             ; переход, если флаг Z сброшен


                LD DE, #0000
                LD H, #DB
                CALL @Music.UnknownE4E6.Entry
                LD (#E393), DE
                LD A, #00
                LD (#DC0E), A
PointE3A3:      LD A, #01
                DJNZ @Music.UnknownE2CB.PointE3A9

                LD A, #22
PointE3A9:      LD (#DEBC), A
                EXX
                LD A, B
                LD (#DEEF), A
                LD A, H
                LD (#DEBF), A
                LD A, E
                LD (#DF00), A
                RET


PointE3BA:      INC A
                LD (#DE1F), A
                LD HL, #DC0F
                DEC (HL)
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD DE, #0000
                LD H, #DB
                CALL @Music.UnknownE583.Entry
                LD (#E3C4), DE
                LD A, #00
                LD (#DC0F), A
                DEC B
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD H, B
                LD L, B
                LD (#E296), HL
                RET


PointE3DC:      LD (#DE4D), A
                XOR A
                LD B, #01
                JR @Music.UnknownE2CB.PointE3F1


PointE3E4:      JR Z, @Music.UnknownE2CB.PointE3EF                              ; переход, если флаг Z установлен


                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                LD (#DE5D), A
                JR @Music.UnknownE439.PointE43C


PointE3EF:      LD A, #2F
PointE3F1:      LD (#DE48), A
                EXX
                LD H, D
                EXX
                RET


PointE3F8:      JR Z, @Music.UnknownE2CB.PointE413                              ; переход, если флаг Z установлен


                DEC A
                JR NZ, @Music.UnknownE2CB.PointE404                             ; переход, если флаг Z сброшен


                LD A, (DE)
                LD (#DFC9), A
                INC DE
                JR @Music.UnknownE439.PointE43C


PointE404:      LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
PointE413:      LD (#DE6E), A
                EXX
                LD B, D
                EXX
                JR @Music.UnknownE439.PointE43C


PointE41B:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DE68), BC
                XOR A
PointE427:      LD (#DE6E), A
                EXX
                LD B, D
                EXX
                LD A, (DE)
                INC DE
PointE42F:      ADD A, #A0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DE52), BC
                ; JP @Music.UnknownE439.Entry, продолжение в UnknownE439.asm

                endmodule
                endmodule
