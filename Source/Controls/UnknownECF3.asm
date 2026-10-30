                module Controls
                module UnknownECF3
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #1215..#1249
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
Entry:          CP #64
                JR C, @Controls.UnknownECF3.PointED0A                           ; переход, если флаг Carry установлен


                LD C, #00
                LD B, #64
                SUB B
PointECFC:      INC C
                SUB B
                JR NC, @Controls.UnknownECF3.PointECFC                          ; переход, если флаг Carry сброшен


                ADD A, B
                LD B, A
                LD A, C
                ADD A, #30
                PUSH BC
                CALL @Controls.UnknownEFC4.Entry
                POP AF
PointED0A:      LD B, A
                CP #0A
                LD C, #00
                JR C, @Controls.UnknownECF3.PointED1B                           ; переход, если флаг Carry установлен


                LD B, #0A
                SUB B
PointED14:      INC C
                SUB B
                JP NC, @Controls.UnknownECF3.PointED14                          ; переход, если флаг Carry сброшен


                ADD A, B
                LD B, A
PointED1B:      LD A, C
                ADD A, #30
                PUSH BC
                CALL @Controls.UnknownEFC4.Entry
                POP AF
                ADD A, #30
                JP @Controls.UnknownEFC4.Entry


                endmodule
                endmodule
