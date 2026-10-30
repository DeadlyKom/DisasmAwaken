                module Music
                module UnknownE583
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #0A83..#0B0B
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
PointE586:      LD A, (DE)
                INC DE
                ADD A, B
                JR C, @Music.UnknownE4E6.PointE564                              ; переход, если флаг Carry установлен


                ADD A, C
                JR C, @Music.UnknownE583.PointE5D1                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE4E6.PointE53D                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE583.PointE5B2                              ; переход, если флаг Carry установлен


                ADD A, #60
                JR C, @Music.UnknownE583.PointE5E6                              ; переход, если флаг Carry установлен


                ADD A, B
                JR C, @Music.UnknownE583.PointE5D5                              ; переход, если флаг Carry установлен


                ADD A, #30
                JR C, @Music.UnknownE583.PointE5BE                              ; переход, если флаг Carry установлен


                LD HL, #DE1E
                RLA
                ADD A, L
                LD L, A
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                PUSH HL
                LD A, (#E2B9)
                LD (#E6EC), A
                JR @Music.UnknownE583.PointE586


PointE5B2:      JR Z, @Music.UnknownE4E6.PointE55F                              ; переход, если флаг Z установлен


                DEC A
                JR NZ, @Music.UnknownE4E6.PointE550                             ; переход, если флаг Z сброшен


                LD A, (DE)
                LD (#E3D0), A
                INC DE
                JR @Music.UnknownE583.PointE586


PointE5BE:      JR Z, @Music.UnknownE4E6.PointE570                              ; переход, если флаг Z установлен


                LD (#DF48), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (#DF50), A
                LD A, #10
                JR @Music.UnknownE4E6.PointE570


PointE5D1:      RET Z                                                           ; выход, если флаг Z установлен

                ADD A, A
                JR @Music.UnknownE4E6.PointE579


PointE5D5:      ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (#E276), BC
                XOR A
                LD (#E27A), A
                JR @Music.UnknownE583.Entry


PointE5E6:      LD (#E2B9), A
                XOR A
                LD H, A
                LD L, A
                LD (#E1F9), A
                LD (#E23C), A
                LD (#E253), A
                LD (#E27A), A
                LD (@MusicState.SlideCounterC), A
                LD (#E1EE), A
                LD (@MusicState.GateCounterC), A
                LD (#E26A), HL
                LD A, #10
                LD (#E20F), A
                LD B, #01
                RET


                endmodule
                endmodule
