                module Controls
                module UnknownD95F
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #195F..#197D
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
Entry:          CALL @Controls.UnknownCF0B.Entry
                AND A
                RET Z                                                           ; выход, если флаг Z установлен

                PUSH IX
                LD IX, #9B24
                PUSH IY
                LD IY, #9B1B
                CALL @Controls.UnknownDAB9.Entry
                CALL NZ, @Controls.UnknownDAB9.Entry                            ; вызов, если флаг Z сброшен
                CALL NZ, @Controls.UnknownDAB9.Entry                            ; вызов, если флаг Z сброшен
                POP IY
                POP IX
                RET


                endmodule
                endmodule
