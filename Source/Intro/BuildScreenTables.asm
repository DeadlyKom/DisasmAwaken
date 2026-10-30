                module Intro
                module BuildScreenTables
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Построение таблиц адресов экранных строк и зеркальной половины таблицы
; исходная запись 3, файловые смещения #06B6..#06FD
; In:
;   #6400..#647F содержат исходную половину таблицы координат
; Out:
;   HL - #6080, DE - #6180, B - 0, половина #6481..#64FF отражена, экранные адреса подготовлены
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   байт #6480 не перезаписывается, C и индексные регистры сохраняются
;   в #6000 и #6100 задаются только поля экранных адресов, другие поля заполняют следующие стадии
; -----------------------------------------
Entry:          LD HL, #647F
                LD DE, #6481
Point69BC:      LD A, (HL)
                LD (DE), A
                DEC L
                INC E
                JR NZ, @Intro.BuildScreenTables.Point69BC                       ; переход, если зеркальная половина таблицы ещё не заполнена


                LD HL, #6000
                LD DE, #4000
                LD B, #10
Point69CA:      INC L
                INC L
                LD (HL), E
                INC L
                LD (HL), D
                INC L
                INC L
                INC L
                LD (HL), E
                INC L
                LD A, D
                ADD A, #04
                LD (HL), A
                INC L
                LD A, E
                ADD A, #20
                LD E, A
                JR NC, @Intro.BuildScreenTables.Point69E3                       ; переход, если переход к следующему знакоместу не переполнил E


                LD A, D
                ADD A, #08
                LD D, A
Point69E3:      DJNZ @Intro.BuildScreenTables.Point69CA

                LD HL, #6000
                LD DE, #6100
                LD B, #20
Point69ED:      INC L
                INC L
                INC E
                INC E
                LD A, (HL)
                LD (DE), A
                INC L
                INC E
                LD A, (HL)
                ADD A, #02
                LD (DE), A
                INC L
                INC E
                DJNZ @Intro.BuildScreenTables.Point69ED

                RET


                endmodule
                endmodule
