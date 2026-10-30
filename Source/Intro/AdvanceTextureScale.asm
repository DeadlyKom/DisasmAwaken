                module Intro
                module AdvanceTextureScale
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Начальное нарастание масштаба и последующий циклический выбор из таблицы #6C62
; исходная запись 3, файловые смещения #0921..#0952
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   первый счётчик начинается с #A1, уменьшается до единицы и остаётся на ней
;   до окончания этой фазы второй счётчик растёт до 63, индекс равен 39 плюс половина счётчика
;   после неё третий счётчик идёт по циклу 40 значений, индекс равен 56 плюс байт таблицы #6C62
;   процедура завершается общим SelectTexturePointerRow, а не собственным RET
; -----------------------------------------
                ; проверка завершения начального изменения масштаба по счётчику в операнде
Entry:          LD A, #A1
                DEC A
                JR NZ, @Intro.AdvanceTextureScale.Point6C27                     ; переход, если первый счётчик после уменьшения не равен нулю


                INC A
Point6C27:      LD (#6C22), A
                DEC A
                JR Z, @Intro.AdvanceTextureScale.Point6C3E                      ; переход, если первый счётчик достиг единицы и нужен табличный масштаб


                LD A, #00
                INC A
                BIT 6, A
                JR Z, @Intro.AdvanceTextureScale.Point6C35                      ; переход, если второй счётчик ещё не достиг 64


                DEC A
Point6C35:      LD (#6C2E), A
                SRL A
                ADD A, #27
                JR @Intro.SelectTexturePointerRow.Entry


Point6C3E:      LD A, #00
                INC A
                CP #28
                JR NZ, @Intro.AdvanceTextureScale.Point6C46                     ; переход, если индекс циклического масштаба ещё не достиг 40


                SUB A
Point6C46:      LD (#6C3F), A
                LD E, A
                LD D, #00
                LD HL, #6C62
                ADD HL, DE
                LD A, (HL)
                ADD A, #38
                ; JP @Intro.SelectTexturePointerRow.Entry, продолжение в SelectTexturePointerRow.asm

                endmodule
                endmodule
