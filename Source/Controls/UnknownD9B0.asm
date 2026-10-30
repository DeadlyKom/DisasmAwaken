                module Controls
                module UnknownD9B0
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #19B0..#19DD
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
Entry:          LD E, A
                LD D, #00
                LD HL, #D97E
                EX AF, AF'
                AND A
                JR Z, @Controls.UnknownD9B0.PointD9BD                           ; переход, если флаг Z установлен


                LD HL, #D987
PointD9BD:      ADD HL, DE
                LD A, (HL)
                AND #07
                LD B, A
                LD A, (HL)
                AND #F8
                LD HL, #D990
PointD9C8:      LD (HL), A
                INC HL
                SRA A
                DJNZ @Controls.UnknownD9B0.PointD9C8

                LD B, E
PointD9CF:      LD (HL), A
                INC HL
                DJNZ @Controls.UnknownD9B0.PointD9CF

                LD HL, #D987
                ADD HL, DE
                LD A, (HL)
                AND #F8
                LD (#D990), A
                RET


                endmodule
                endmodule
