                module ActionBoot
                module BuildProjectionTable
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Создание таблицы в #9300 с вычислением через сдвиги и сложение
; исходная запись 17, файловые смещения #0198..#01D1
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
Entry:          LD IX, #9300
                LD HL, #0000
Point435C:      LD A, H
                BIT 7, L
                JR Z, @ActionBoot.BuildProjectionTable.Point4362                ; переход, если флаг Z установлен


                INC A
Point4362:      LD (IX + #00), A
                XOR A
                EXX
                LD L, A
                LD H, A
                LD E, A
                LD BC, #00B2
                EXX
                LD BC, #1801
Point4371:      RR C
                RR H
                RR L
                EXX
                JR NC, @ActionBoot.BuildProjectionTable.Point437D               ; переход, если флаг Carry сброшен


                ADD HL, BC
                ADC A, #01
Point437D:      RRA
                RR H
                RR L
                EXX
                DJNZ @ActionBoot.BuildProjectionTable.Point4371

                LD A, C
                RRA
                EXX
                LD H, L
                LD L, A
                INC IXL
                JR NZ, @ActionBoot.BuildProjectionTable.Point435C               ; переход, если флаг Z сброшен


                RET


                endmodule
                endmodule
