                module Intro
                module FillBitmap
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Заполнение 128 экранных строк байтом C с учётом адресации Spectrum
; исходная запись 3, файловые смещения #0767..#07C0
; In:
;   BC - C значение заполнения bitmap
; Out:
;   HL - #5000, B - 0, E - #E0, первые 128 экранных строк #4000..#4FFF заполнены C
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   D, C, индексные и альтернативные регистры сохраняются, атрибуты не затрагиваются
;   на каждую строку приходится 32 записи, переход к строке учитывает экранную раскладку Spectrum
; -----------------------------------------
Entry:          LD HL, #4000
                LD B, #80
Point6A6C:      LD E, L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                LD L, E
                INC H
                LD A, H
                AND #07
                JP NZ, @Intro.FillBitmap.Point6ABE                              ; переход, если следующая строка остаётся внутри восьмистрочного знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Intro.FillBitmap.Point6ABE                               ; переход, если переход к следующему знакоместу переполнил L


                LD A, H
                SUB #08
                LD H, A
Point6ABE:      DJNZ @Intro.FillBitmap.Point6A6C

                RET


                endmodule
                endmodule
