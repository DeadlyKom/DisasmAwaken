                module Station
                module SkipCrRecords
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [поиск и выбор текстовой записи](../../Docs/TextSelection.md)
; -----------------------------------------
; Пропуск A+1 ограничителей CR с восстановлением LF в операнде поиска
; исходная запись 4, файловые смещения #4380..#438F
; In:
;   HL - начало поиска, память читаема в пределах всех повторов CPIR
;   BC - младший байт C участвует в первом лимите поиска #FF00 OR C
;   AF - A определяет число ограничителей A+1, включая 256 при A=#FF, Carry сохраняется
;   для SkipLfRecords TextSelectState.Separator обычно равен LF, SkipCrRecords временно задаёт CR
; Out:
;   HL - позиция после последнего найденного ограничителя либо после исчерпанного прохода CPIR
;   DE и BC восстановлены, SkipCrRecords записывает LF в Separator перед возвратом
;   AF - F=#42 OR входной Carry, A=LF после SkipCrRecords либо текущий операнд Separator после SkipLfRecords
; Corrupt:
;   HL, AF
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   поиск не проверяет успех CPIR, финальный Z=1 сформирован DEC E и не доказывает найденный ограничитель
;   лимит BC не перезагружается для каждого ограничителя, после исчерпания следующий CPIR с BC=0 сканирует 65536 байтов
;   SkipCrRecords не сохраняет произвольный прежний Separator, восстановление всегда записывает LF
; -----------------------------------------
                ; сохранение индекса и Carry перед временной заменой ограничителя поиска
Entry:          PUSH AF
                ; выбор CR для временного режима поиска записей
                LD A, @TextConst.CarriageReturn
                LD (@TextSelectState.Separator), A
                POP AF
                CALL @Station.SkipLfRecords.Entry
                ; восстановление именно LF, произвольный прежний операнд не сохраняется
                LD A, @TextConst.LineFeed
                LD (@TextSelectState.Separator), A
                RET

                endmodule
                endmodule
