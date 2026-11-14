                module ArchiveStart
                module PrepareRightLayerUpdate
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; подготовка перерисовки для прежнего выбора правой стороны
                ; In:
                ;   в окне #C000 находится код START, селекторы обеих сторон находятся в своих пределах
                ; Out:
                ;   старый вариант правой стороны обработан, вывод правой полосы временно отключён
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; отключение правой полосы и выбор правой пары завершающих плиток
Entry:          LD A, #01
                LD (@ArchiveStart.HandleBankFrame.SkipRight + 1), A
                LD HL, @ArchiveStartConst.RightCoordSkip
                LD (@ArchiveStart.WriteLayerVariant.CoordSkipPatch + 1), HL
                LD HL, @ArchiveStartConst.RightTileSkip
                LD (@ArchiveStart.WriteLayerVariant.SourceSkipPatch + 1), HL

                ; вычисление базовых координат и номера варианта, 4 × старший индекс + младший
                LD HL, (@ArchiveStartData.Frame.RightMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD A, (@ArchiveStartData.Frame.RightMajor)
                ADD A, A
                ADD A, A
                LD HL, @ArchiveStartData.Frame.RightMinor
                ADD A, (HL)
                JR @ArchiveStart.RedrawLayerSelection.Entry

                endmodule
                endmodule
