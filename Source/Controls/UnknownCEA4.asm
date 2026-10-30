                module Controls
                module UnknownCEA4
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0EA4..#0EB4
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
Entry:          LD L, D
                ADD A, A
                JR Z, @Controls.UnknownCECF.PointCEF4                           ; переход, если флаг Z установлен


                PUSH HL
                ADD A, A
                SUB #3E
                NEG
                LD (#CEB4), A
                LD A, IXL
PointCEB3:      JR @Controls.UnknownCEA4.PointCEB3


                endmodule
                endmodule
