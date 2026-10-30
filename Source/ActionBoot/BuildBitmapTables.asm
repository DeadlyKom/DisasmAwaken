                module ActionBoot
                module BuildBitmapTables
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Создание таблиц строк и битовых масок для рисования
; исходная запись 17, файловые смещения #0212..#023C
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
Entry:          LD HL, #9400
                LD DE, #8000
                LD BC, #0020
Point43D8:      LD (HL), D
                INC H
                LD (HL), E
                DEC H
                EX DE, HL
                ADD HL, BC
                EX DE, HL
                INC L
                JR NZ, @ActionBoot.BuildBitmapTables.Point43D8                  ; переход, если флаг Z сброшен


                INC H
                INC H
                LD A, #80
                EX AF, AF'
                XOR A
Point43E8:      LD B, #08
Point43EA:      LD (HL), A
                EX AF, AF'
                INC H
                LD (HL), A
                RRCA
                DEC H
                EX AF, AF'
                INC L
                DJNZ @ActionBoot.BuildBitmapTables.Point43EA

                INC A
                CP #20
                JR C, @ActionBoot.BuildBitmapTables.Point43E8                   ; переход, если флаг Carry установлен


                RET


                endmodule
                endmodule
