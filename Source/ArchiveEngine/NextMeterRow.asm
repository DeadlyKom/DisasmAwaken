                module ArchiveEngine
                module NextMeterRow
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; переход на следующую строку растра с сохранением столбца
                ; In:
                ;   DE - адрес байта в раскладке ULA
                ; Out:
                ;   DE - адрес следующей строки по исходной формуле, граница экрана не ограничивается
                ; Corrupt:
                ;   DE, AF
                ; -----------------------------------------
                ; проверка перехода через последнюю строку текущего знакоместного ряда
Entry:          INC D
                LD A, D
                AND @ArchiveEngineConst.LowPageMask
                RET NZ                                                          ; выход, если следующая строка в том же знакоместном ряду

                ; прибавление одного знакоместного ряда к младшему адресу
                LD A, E
                ADD A, @ArchiveEngineConst.CharRowBytes
                LD E, A
                RET C                                                           ; выход, если перенос уже перевёл адрес в следующую треть экрана

                ; компенсация переноса в старшем байте внутри одной трети экрана
                LD A, D
                SUB @ArchiveEngineConst.MeterHeight
                LD D, A
                RET

                endmodule
                endmodule
