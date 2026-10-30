                module Intro
                module SelectTexturePointerRow
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Выбор строки #F000 + 16*A для генерируемого переноса #A800
; исходная запись 3, файловые смещения #0953..#0961
; In:
;   AF - A индекс строки указателей от 0 до 255
; Out:
;   HL - #F000 + 16*A, DE - #F000, операнд #6BB2 содержит HL
; Corrupt:
;   HL, DE, AF
; Note:
;   A сохраняется, меняются флаги от ADD HL,HL и ADD HL,DE, остальные регистры сохраняются
; -----------------------------------------
                ; расчёт адреса строки таблицы указателей, HL равен #F000 плюс 16*A
Entry:          LD L, A
                LD H, #00
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD DE, #F000
                ADD HL, DE
                LD (#6BB2), HL
                RET


                endmodule
                endmodule
