                module ActionBoot
                module RelocateBootstrap
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Подготовка экранов и перенос #01FA байт загрузчика в #4200
; исходная запись 17, файловые смещения #0000..#0042
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
Entry:          XOR A
                OUT (#FE), A
                LD BC, #7FFD
                LD A, #17
                OUT (C), A
                EXX
                LD HL, #C000
                LD DE, #C001
                LD BC, #1AFF
                LD (HL), L
                LDIR
                EXX
                LD A, #18
                OUT (C), A
                LD HL, #4000
                LD DE, #4001
                LD BC, #1800
                LD (HL), L
                LDIR
                LD (HL), #38
                LD BC, #0180
                LDIR
                LD (HL), #07
                LD BC, #017F
                LDIR
                LD HL, #6043
                LD DE, #4200
                PUSH DE
                LD BC, #01FA
                LDIR
                RET


                endmodule
                endmodule
