                module Controls
                module UnknownCECF
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0ECF..#0EF8
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
Entry:          DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                POP HL
PointCEF4:      LD A, (#D18B)
                AND A
                RET


                endmodule
                endmodule
