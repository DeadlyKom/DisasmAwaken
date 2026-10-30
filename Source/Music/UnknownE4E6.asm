                module Music
                module UnknownE4E6
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #09E6..#0A82
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
Entry:          LD BC, #1020
PointE4E9:      LD A, (DE)
                INC DE
                ADD A, B
                JR C, @Music.UnknownE439.PointE4C8                              ; переход, если флаг Carry установлен


                ADD A, C
                JR C, @Music.UnknownE4E6.PointE529                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE439.PointE491                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE439.PointE4A5                              ; переход, если флаг Carry установлен


                ADD A, #60
                JR C, @Music.UnknownE439.PointE489                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE4E6.PointE52D                              ; переход, если флаг Carry установлен


                ADD A, C
                JR C, @Music.UnknownE4E6.PointE511                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE4E6.PointE516                              ; переход, если флаг Carry установлен


                RLA
                LD HL, #DDFE
                ADD A, L
                LD L, A
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                PUSH HL
                JR @Music.UnknownE4E6.PointE4E9


PointE511:      LD (#DF67), A
                JR @Music.UnknownE4E6.PointE4E9


PointE516:      JR Z, @Music.UnknownE439.PointE4D4                              ; переход, если флаг Z установлен


                LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
                JR @Music.UnknownE439.PointE4D4


PointE529:      RET Z                                                           ; выход, если флаг Z установлен

                ADD A, A
                JR @Music.UnknownE439.PointE4DC


PointE52D:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DEF6), BC
                EXX
                LD B, D
                EXX
                JR @Music.UnknownE4E6.Entry


PointE53D:      JR Z, @Music.UnknownE4E6.PointE548                              ; переход, если флаг Z установлен


                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                LD (#E22B), A
                JR @Music.UnknownE583.PointE586


PointE548:      LD (@MusicState.GateCounterC), A
                DEC A
                LD (#E1EE), A
                RET


PointE550:      LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
PointE55F:      LD (#E235), A
                JR @Music.UnknownE583.PointE586


PointE564:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#E276), BC
                XOR A
PointE570:      LD (#E235), A
                XOR A
                LD (#E27A), A
                LD A, (DE)
                INC DE
PointE579:      ADD A, #A0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#E1F5), BC
                ; JP @Music.UnknownE583.Entry, продолжение в UnknownE583.asm

                endmodule
                endmodule
