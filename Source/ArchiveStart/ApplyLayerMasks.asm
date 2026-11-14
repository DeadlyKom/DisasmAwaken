                module ArchiveStart
                module ApplyLayerMasks
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; применение двадцати общих и двух завершающих масок к одному слою
                ; In:
                ;   заданы координаты сетки, режим объединения, слой, смещение группы и пропуск пары
                ; Out:
                ;   обновлены операнды 22 плиток целевого слоя
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; подключение таблицы масок, координат и счётчика общих плиток
Entry:          LD HL, @ArchiveStartMaskPointers.Cell00
                LD IX, @ArchiveStartTileOffsets.Cell00
                LD A, @ArchiveStartConst.CommonTileCount

                ; объединение очередной маски и проверка числа оставшихся плиток
NextMask:       PUSH AF
                CALL @ArchiveStart.ApplyMaskTile.Entry
                POP AF
                DEC A
                JR NZ, @ArchiveStart.ApplyLayerMasks.NextMask                   ; переход, если остались общие маски, продолжить цикл

                ; выбор завершающей пары масок и координат
EndPairPatch:   LD DE, #0000
                ADD HL, DE
                ADD IX, DE

                ; объединение двух завершающих масок с операндами слоя
                CALL @ArchiveStart.ApplyMaskTile.Entry
                CALL @ArchiveStart.ApplyMaskTile.Entry
                RET

                endmodule
                endmodule
