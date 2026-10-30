                module Controls
                module UnknownCE16
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0E16..#0E5C
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
Entry:          LD A, #00
                XOR #01
                LD (#CE17), A
                LD C, #00
                JR NZ, @Controls.UnknownCE16.PointCE3F                          ; переход, если флаг Z сброшен


                LD A, R
PointCE23:      CP C
                JR C, @Controls.UnknownCE16.PointCE2A                           ; переход, если флаг Carry установлен


                SUB C
                JP @Controls.UnknownCE16.PointCE23


PointCE2A:      CP #5E
                JR C, @Controls.UnknownCE16.PointCE30                           ; переход, если флаг Carry установлен


                LD A, #5E
PointCE30:      ADD A, #00
                LD E, A
                LD A, R
                ADD A, #80
                CP #FE
                JR C, @Controls.UnknownCE16.PointCE3D                           ; переход, если флаг Carry установлен


                SUB #01
PointCE3D:      LD D, A
                RET


PointCE3F:      LD A, R
PointCE41:      CP C
                JR C, @Controls.UnknownCE16.PointCE48                           ; переход, если флаг Carry установлен


                SUB C
                JP @Controls.UnknownCE16.PointCE41


PointCE48:      CP #5E
                JR C, @Controls.UnknownCE16.PointCE4E                           ; переход, если флаг Carry установлен


                LD A, #5E
PointCE4E:      SUB #5F
                NEG
                LD E, A
                LD A, R
                CP #01
                JR NC, @Controls.UnknownCE16.PointCE5B                          ; переход, если флаг Carry сброшен


                ADD A, #01
PointCE5B:      LD D, A
                RET


                endmodule
                endmodule
