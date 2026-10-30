                module Controls
                module UnknownCAE3
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0AE3..#0AFF
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
Entry:          LD BC, #C500
PointCAE6:      LD H, #94
                LD A, (BC)
                LD L, A
                INC C
                LD A, (BC)
                INC C
                LD E, A
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, E
                ADD A, (HL)
                LD E, A
                INC H
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                LD A, C
                CP #46
                JP C, @Controls.UnknownCAE3.PointCAE6                           ; переход, если флаг Carry установлен


                RET


                endmodule
                endmodule
