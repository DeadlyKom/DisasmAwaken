                module Intro
                module LoadStation
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Переносимая завершающая стадия, поиск STATIONF.C и чтение #C0 секторов
; исходная запись 3, файловые смещения #02B7..#0314
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
Entry:          CALL #6E31
                LD A, #1F
                LD BC, #7FFD
                OUT (C), A
                LD HL, #D800
                LD DE, #D801
                LD BC, #02FF
                LD (HL), L
                LDIR
                LD HL, #4000
                LD DE, #C000
                LD BC, #1B00
                LDIR
                DI
                LD SP, #5FFF
                LD A, #3F
                LD I, A
                IM 1
                LD A, #18
                LD BC, #7FFD
                OUT (C), A
                LD IY, #5C3A
                LD HL, #6615
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD C, #0A
                CALL @TrDos.Dispatch
                LD A, C
                LD C, #08
                CALL @TrDos.Dispatch
                LD HL, #6300
                PUSH HL
                LD HL, #6000
                LD DE, (#5CEB)
                LD B, #C0
                LD C, #05
                JP @TrDos.Dispatch


                endmodule
                endmodule
