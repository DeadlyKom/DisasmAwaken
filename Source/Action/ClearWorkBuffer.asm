                module Action
                module ClearWorkBuffer
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Заполнение #0C00 байт до #8C00 значением #FF через стек с восстановлением SP
; исходная запись 17, файловые смещения #710A..#712B
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
Entry:          LD (#D129), SP
                LD SP, #8C00
                LD HL, #FFFF
                LD B, #60
PointD116:      PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                DJNZ @Action.ClearWorkBuffer.PointD116

                LD SP, #0000
                RET


                endmodule
                endmodule
