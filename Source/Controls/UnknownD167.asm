                module Controls
                module UnknownD167
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1167..#117C
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
Entry:          LD D, #FE
PointD169:      SLA E
                RLA
                JR C, @Controls.UnknownD167.PointD176                           ; переход, если флаг Carry установлен


                CP B
                JR NC, @Controls.UnknownD167.PointD176                          ; переход, если флаг Carry сброшен


                SLA D
                RET NC                                                          ; выход, если флаг Carry сброшен

                JR @Controls.UnknownD167.PointD169


PointD176:      SUB B
                SCF
                RL D
                RET NC                                                          ; выход, если флаг Carry сброшен

                JR @Controls.UnknownD167.PointD169


                endmodule
                endmodule
