                module Station
                module DrawSpanRow
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Запись левого края, заданного числа средних байтов и правого края с переходом на следующую пиксельную строку
; исходная запись 4, файловые смещения #617B..#61BF
; In:
;   HL - адрес левого крайнего байта, DE - D левый образец и E средний образец, BC - C правый образец
;   StationRaster.SpanSkip - чётное смещение 2*(30-N), где N от нуля до 30, участок назначения помещается в строке и не перекрывает код или CPU-стек
;   LeftCode содержит #2C72 либо #0000, RightCode содержит #71 либо #00, изменяемый код подготовлен до входа
; Out:
;   HL - L сохранён, H увеличен на один без переноса дальше, AF - A прежний L, F от INC прежнего H с сохранённым входным Carry
; Corrupt:
;   HL, AF
; Note:
;   при включённых краях записаны N+2 байта в порядке D, затем N копий E, затем C
;   два NOP в LeftCode отменяют и левую запись, и первый шаг L, нулевой RightCode отменяет правую запись
;   в общем случае пишутся N плюс число включённых краёв байтов, порядок оставшихся частей сохраняется
;   развёрнутый блок содержит 30 пар LD (HL),E и INC L, изменяемый JR пропускает лишние пары
;   DE, BC, альтернативные и индексные регистры сохраняются, SP восстанавливается
;   H увеличивается для следующей пиксельной строки внутри знакоместа, переход к следующей строке знакомест отдельно выполняет NextCharRow
; -----------------------------------------
                ; сохранение исходной колонки в A и начало записи левого края полосы
Entry:          LD A, L
                LD (HL), D
                INC L
                ; пропуск лишних пар записи по настроенному SpanSkip, исходное смещение ноль выводит 30 средних байтов
                JR @Station.DrawSpanRow.Middle

Middle:         LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                LD (HL), E
                INC L
                ; запись правого края после выбранного числа средних байтов
                LD (HL), C
                ; возврат к исходной колонке перед переходом к следующей пиксельной строке знакоместа
                LD L, A
                INC H
                RET

                endmodule
                endmodule
