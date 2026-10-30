                module Help
                module IndexTextLines
; Документация [Help](../../Docs/FunctionDetails/Help.md)
; -----------------------------------------
; Создание таблицы указателей максимум на 1024 строки текста
; исходная запись 8, файловые смещения #0000..#0041
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
                LD HL, #E3E2
                CALL #A390
                LD DE, #0000
                XOR A
                LD (#6320), A
                LD IX, #DB7C
PointDB13:      LD (IX + #00), L
                LD (IX + #01), H
                INC IX
                INC IX
                LD A, #08
                LD (#6321), A
                PUSH DE
                CALL #AD35
                POP DE
                INC DE
                JP NC, @Help.IndexTextLines.PointDB13                           ; переход, если флаг Carry сброшен


                PUSH DE
                PUSH IX
                LD HL, #0400
                OR A
                SBC HL, DE
                ADD HL, HL
                LD B, H
                LD C, L
                POP HL
                LD D, H
                LD E, L
                LD (HL), #00
                INC DE
                DEC BC
                LDIR
                POP DE
                RET


                endmodule
                endmodule
