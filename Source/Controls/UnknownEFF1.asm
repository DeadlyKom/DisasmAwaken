                module Controls
                module UnknownEFF1
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #1513..#15B5
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
Entry:          BIT 0, C
                LD B, #F0
                JR NZ, @Controls.UnknownEFF1.PointEFF9                          ; переход, если флаг Z сброшен


                LD B, #0F
PointEFF9:      EX AF, AF'
                RRA
                JR NC, @Controls.UnknownEFF1.PointF001                          ; переход, если флаг Carry сброшен


                LD A, C
                XOR #01
                LD C, A
PointF001:      BIT 0, C
                LD C, B
                JR NZ, @Controls.UnknownEFF1.PointF059                          ; переход, если флаг Z сброшен


                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                RET


PointF059:      LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                RET


                endmodule
                endmodule
