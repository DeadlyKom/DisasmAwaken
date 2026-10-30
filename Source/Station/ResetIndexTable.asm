                module Station
                module ResetIndexTable
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [CellMap.md](../../Docs/CellMap.md)
; -----------------------------------------
; Заполнение #0080 байт таблицы #8500 значением #FF
; исходная запись 4, файловые смещения #3ED7..#3EEA
; In:
;   StationState.ItemIndex длиной #0080 байт доступна для записи, CPU-стек не перекрывает её
; Out:
;   #8500..#857F заполнены #FF, #8580..#85FF не изменены, A сохранён, H, N и PV сброшены
;   S, Z и Carry сохранены, бит 3 F получает бит 3 суммы (A+#FF) по модулю 256, бит 5 F получает бит 1 той же суммы
; Corrupt:
;   AF, только F
; Note:
;   первый #FF распространяется на оставшиеся 127 байтов через перекрывающийся LDIR
;   HL, DE, BC, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   инициализация охватывает 64 двухбайтовые пары, хотя InvalidateItemIndex может просматривать 128 пар, отличие сохранено
; -----------------------------------------
Entry:          PUSH HL
                PUSH DE
                PUSH BC
                ; подготовка исходной инициализации первых 128 байтов индексной таблицы
                LD HL, @StationState.ItemIndex
                LD DE, @StationState.ItemIndex + 1
                LD BC, @StationTables.IndexInitTail
                ; запись первого свободного байта для последующего распространения
                LD (HL), @ItemIndexConst.FreeHigh
                ; заполнение остальных 127 байтов, вторая половина страницы не затрагивается
                LDIR
                POP BC
                POP DE
                POP HL
                RET

                endmodule
                endmodule
