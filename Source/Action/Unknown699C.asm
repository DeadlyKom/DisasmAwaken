                module Action
                module Unknown699C
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0BD9..#0BFA
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
Entry:          LD A, (#9B71)
                OR A
                JP P, @Action.Unknown699C.Point69A4                             ; переход, если флаг Sign сброшен


                CPL
Point69A4:      LD L, A
                LD A, (#9B74)
                OR A
                JP P, @Action.Unknown699C.Point69AD                             ; переход, если флаг Sign сброшен


                CPL
Point69AD:      CP L
                JR C, @Action.Unknown699C.Point69B1                             ; переход, если флаг Carry установлен


                LD L, A
Point69B1:      LD A, (#9B77)
                OR A
                JP P, @Action.Unknown699C.Point69B9                             ; переход, если флаг Sign сброшен


                CPL
Point69B9:      CP L
                JR C, @Action.Unknown699C.Point69BD                             ; переход, если флаг Carry установлен


                LD L, A
Point69BD:      RET


                endmodule
                endmodule
