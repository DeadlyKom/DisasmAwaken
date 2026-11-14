                module ArchiveStart
                module PrepareLeftLayerUpdate
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; подготовка перерисовки для прежнего выбора левой стороны
                ; In:
                ;   в окне #C000 находится код START, селекторы обеих сторон находятся в своих пределах
                ; Out:
                ;   старый вариант левой стороны обработан, вывод левой полосы временно отключён
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; отключение левой полосы и выбор левой пары завершающих плиток без пропуска
Entry:          LD A, #01
                LD (@ArchiveStart.HandleBankFrame.SkipLeft + 1), A
                LD HL, #0000
                LD (@ArchiveStart.WriteLayerVariant.CoordSkipPatch + 1), HL
                LD (@ArchiveStart.WriteLayerVariant.SourceSkipPatch + 1), HL

                ; вычисление базовых координат и номера варианта, 4 × старший индекс + младший
                LD HL, (@ArchiveStartData.Frame.LeftMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD A, (@ArchiveStartData.Frame.LeftMajor)
                ADD A, A
                ADD A, A
                LD HL, @ArchiveStartData.Frame.LeftMinor
                ADD A, (HL)

                ; JP RedrawLayerSelection, продолжение в RedrawLayerSelection.asm

                endmodule
                endmodule
