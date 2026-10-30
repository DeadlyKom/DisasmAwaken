                module Music
                module UnknownE439
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #0939..#09E5
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
PointE43C:      LD A, (DE)
                INC DE
                ADD A, B
                JR C, @Music.UnknownE2CB.PointE41B                              ; переход, если флаг Carry установлен


                ADD A, C
                JR C, @Music.UnknownE439.PointE475                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE2CB.PointE3E4                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE2CB.PointE3F8                              ; переход, если флаг Carry установлен


                ADD A, #60
                JR C, @Music.UnknownE2CB.PointE3DC                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE439.PointE479                              ; переход, если флаг Carry установлен


                ADD A, #30
                JR C, @Music.UnknownE439.PointE462                              ; переход, если флаг Carry установлен


                RLA
                LD HL, #DDDE
                ADD A, L
                LD L, A
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                PUSH HL
                JR @Music.UnknownE439.PointE43C


PointE462:      JR Z, @Music.UnknownE2CB.PointE427                              ; переход, если флаг Z установлен


                LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
                JR @Music.UnknownE2CB.PointE427


PointE475:      RET Z                                                           ; выход, если флаг Z установлен

                ADD A, A
                JR @Music.UnknownE2CB.PointE42F


PointE479:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DE68), BC
                EXX
                LD B, D
                EXX
                JR @Music.UnknownE439.Entry


PointE489:      LD (#DEDB), A
                XOR A
                LD B, #01
                JR @Music.UnknownE439.PointE49E


PointE491:      JR Z, @Music.UnknownE439.PointE49C                              ; переход, если флаг Z установлен


                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                LD (#DEEB), A
                JR @Music.UnknownE4E6.PointE4E9


PointE49C:      LD A, #2F
PointE49E:      LD (#DED6), A
                EXX
                LD H, D
                EXX
                RET


PointE4A5:      JR Z, @Music.UnknownE439.PointE4C0                              ; переход, если флаг Z установлен


                DEC A
                JR NZ, @Music.UnknownE439.PointE4B1                             ; переход, если флаг Z сброшен


                LD A, (DE)
                LD (#E39F), A
                INC DE
                JR @Music.UnknownE4E6.PointE4E9


PointE4B1:      LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
PointE4C0:      LD (#DEFC), A
                EXX
                LD B, D
                EXX
                JR @Music.UnknownE4E6.PointE4E9


PointE4C8:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DEF6), BC
                XOR A
PointE4D4:      LD (#DEFC), A
                EXX
                LD B, D
                EXX
                LD A, (DE)
                INC DE
PointE4DC:      ADD A, #A0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#DEE0), BC
                ; JP @Music.UnknownE4E6.Entry, продолжение в UnknownE4E6.asm

                endmodule
                endmodule
