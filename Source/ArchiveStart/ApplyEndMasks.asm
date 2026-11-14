                module ArchiveStart
                module ApplyEndMasks
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; применение двух завершающих масок выбранной стороны
                ; In:
                ;   заданы координаты сетки, режим объединения, слой, смещение группы и пропуск пары
                ; Out:
                ;   обновлены операнды двух плиток целевого слоя, указатели продвинуты за обработанную пару
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; выбор завершающей пары указателей масок и соответствующих координат
Entry:          LD HL, @ArchiveStartMaskPointers.LeftEnd0
                LD IX, @ArchiveStartTileOffsets.LeftEnd0
                LD DE, (@ArchiveStart.ApplyLayerMasks.EndPairPatch + 1)
                ADD HL, DE
                ADD IX, DE

                ; объединение двух масок с операндами текущего слоя
                CALL @ArchiveStart.ApplyMaskTile.Entry
                CALL @ArchiveStart.ApplyMaskTile.Entry
                RET

                endmodule
                endmodule
