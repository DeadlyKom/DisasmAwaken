                module ArchiveStart
                module WriteLayerVariant
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; запись двадцати общих и двух завершающих плиток варианта
                ; In:
                ;   BC - начало 192-байтового варианта, целевой слой и режим объединения уже записаны
                ; Out:
                ;   изменены операнды 22 знакомест, DE указывает за последней плиткой
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; подключение первой пары смещений и счётчика общих плиток
Entry:          LD IX, @ArchiveStartTileOffsets.Cell00
                LD A, @ArchiveStartConst.CommonTileCount

                ; запись плитки, обновление указателя источника и проверка счётчика
NextCommon:     PUSH AF
                CALL @ArchiveStart.ApplyOffsetTile.Entry
                LD B, D
                LD C, E
                POP AF
                DEC A
                JR NZ, @ArchiveStart.WriteLayerVariant.NextCommon               ; переход, если остались общие плитки, продолжить запись

                ; прибавление пропуска растров перед двумя завершающими плитками
SourceSkipPatch:LD HL, #0000
                ADD HL, BC
                LD B, H
                LD C, L

                ; прибавление пропуска пар координат для правой стороны
CoordSkipPatch: LD DE, #0000
                ADD IX, DE

                ; запись двух завершающих плиток
                CALL @ArchiveStart.ApplyOffsetTile.Entry
                LD B, D
                LD C, E
                CALL @ArchiveStart.ApplyOffsetTile.Entry
                RET

                endmodule
                endmodule
