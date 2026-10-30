                module Controls
                module RunTemporaryModule
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Сохранение памяти по банкам, распаковка временного модуля и восстановление полётного кода
; исходная запись 23, файловые смещения #0000..#007E
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
Entry:          PUSH IX
                LD (#5E33), SP
                LD A, #16
                LD BC, #7FFD
                OUT (C), A
                EXX
                LD HL, #8C00
                LD DE, #C000
                LD BC, #3400
                LDIR
                EXX
                LD A, #11
                OUT (C), A
                EXX
                LD HL, #C600
                LD BC, #0000
                LD DE, #8000
                PUSH BC
                PUSH DE
                LDIR
                LD DE, #E000
                LD HL, #6000
                LD BC, #2000
                LDIR
                POP HL
                POP BC
                LD DE, #6400
                PUSH DE
                LDIR
                POP HL
                LD D, H
                LD E, L
                CALL #AB23
                LD SP, #6000
                CALL #6500
                DI
                LD BC, #7FFD
                LD A, #16
                OUT (C), A
                EXX
                LD HL, #C000
                LD DE, #8C00
                LD BC, #3400
                LDIR
                EXX
                LD A, #10
                OUT (C), A
                EXX
                CALL @Controls.UnknownD10A.Entry
                EXX
                LD A, #11
                OUT (C), A
                PUSH BC
                CALL @Controls.UnknownC870.Entry
                LD HL, #E000
                LD DE, #6000
                LD BC, #2000
                LDIR
                JP #6000


                endmodule
                endmodule
