                module ArchiveStart
                module FillLayerAttributes
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; заполнение 21 ряда по 20 атрибутов текущим цветом слоя
                ; In:
                ;   AF - A, байт атрибута, экранная страница отображена в #C000
                ; Out:
                ;   записаны колонки 6..25 в рядах 3..23, SP восстановлен
                ; Corrupt:
                ;   HL, DE, BC, AF, временно SP
                ; Note:
                ;   десять PUSH записывают справа налево два одинаковых байта за раз
                ; -----------------------------------------
                ; сохранение стека и подготовка пары одинаковых атрибутов
Entry:          LD (@ArchiveStart.FillLayerAttributes.RestoreStack + 1), SP
                LD D, A
                LD E, A
                LD HL, @ArchiveStartConst.LayerAttrRight
                LD BC, @ArchiveStartConst.ScreenRowBytes
                LD A, @ArchiveStartConst.LayerAttrRows

                ; перенос SP к правому краю ряда и заполнение двадцати байтов
WriteRow:       LD SP, HL
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE

                ; переход к следующему ряду и проверка числа оставшихся рядов
                ADD HL, BC
                DEC A
                JR NZ, @ArchiveStart.FillLayerAttributes.WriteRow               ; переход, если остались ряды атрибутов

RestoreStack:   LD SP, #0000
                RET

                endmodule
                endmodule
