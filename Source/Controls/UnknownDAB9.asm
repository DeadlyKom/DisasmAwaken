                module Controls
                module UnknownDAB9
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1AB9..#1ADD
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
Entry:          LD DE, #0003
                ADD IY, DE
                LD A, (IY + #02)
                AND #7F
                LD D, A
                LD A, (IX + #02)
                AND #7F
                CP #0A
                JR C, @Controls.UnknownDAB9.PointDAD9                           ; переход, если флаг Carry установлен


                CP D
                JR C, @Controls.UnknownDAB9.PointDADC                           ; переход, если флаг Carry установлен


                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, (IX + #01)
                CP (IY + #01)
                JR C, @Controls.UnknownDAB9.PointDADC                           ; переход, если флаг Carry установлен


PointDAD9:      OR #01
                RET


PointDADC:      XOR A
                RET


                endmodule
                endmodule
