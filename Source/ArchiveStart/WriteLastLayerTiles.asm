                module ArchiveStart
                module WriteLastLayerTiles
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; запись двух завершающих плиток выбранной стороны
                ; In:
                ;   BC - указатель сразу после двадцати общих плиток, смещение варианта уже прибавлено
                ; Out:
                ;   операнды двух знакомест слоя изменены, DE указывает за второй плиткой
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; применение пропусков стороны к указателю растров и пар координат
Entry:          LD IX, @ArchiveStartTileOffsets.LeftEnd0
                LD HL, (@ArchiveStart.WriteLayerVariant.SourceSkipPatch + 1)
                ADD HL, BC
                LD B, H
                LD C, L
                LD DE, (@ArchiveStart.WriteLayerVariant.CoordSkipPatch + 1)
                ADD IX, DE

                ; запись первой плитки и передача следующего адреса второй плитке
                CALL @ArchiveStart.ApplyOffsetTile.Entry
                LD B, D
                LD C, E
                CALL @ArchiveStart.ApplyOffsetTile.Entry
                RET

                endmodule
                endmodule
