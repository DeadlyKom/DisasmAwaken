                module Controls
                module UnknownCAB3
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0AB3..#0AE2
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
Entry:          LD HL, #C500
PointCAB6:      CALL @Controls.UnknownCA8D.Entry
                CP #01
                JR NC, @Controls.UnknownCAB3.PointCABF                          ; переход, если флаг Carry сброшен


                ADD A, #02
PointCABF:      CP #FE
                JR C, @Controls.UnknownCAB3.PointCAC5                           ; переход, если флаг Carry установлен


                SUB #02
PointCAC5:      EX AF, AF'
                CALL @Controls.UnknownCA8D.Entry
                AND #7F
                CP #01
                JR NC, @Controls.UnknownCAB3.PointCAD1                          ; переход, если флаг Carry сброшен


                ADD A, #02
PointCAD1:      CP #5F
                JR C, @Controls.UnknownCAB3.PointCAD7                           ; переход, если флаг Carry установлен


                SUB #40
PointCAD7:      LD (HL), A
                INC L
                EX AF, AF'
                LD (HL), A
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCAB3.PointCAB6                           ; переход, если флаг Carry установлен


                RET


                endmodule
                endmodule
