                module ArchiveStart
                module RebuildLayerMasks
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; пересчёт масок в трёх слоях после обновления маршрута
                ; In:
                ;   HL - слой, в котором следует восстановить видимую маску, начало сетки уже вычислено
                ; Out:
                ;   стирающие маски применены к трём слоям, основной растр маски объединён через OR с выбранным слоем
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; сохранение выделенного слоя и настройка стирания второй группой масок
Entry:          PUSH HL
                LD A, @ArchiveStartConst.OpAndAtHL
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A
                LD A, @ArchiveStartConst.OpComplement
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD HL, @ArchiveStartConst.MaskVariantSize
                LD (@ArchiveStart.ApplyOffsetTile.MaskOffsetPatch + 1), HL

                ; проверка равенства двух пар селекторов
                LD BC, (@ArchiveStartData.Frame.LeftMinor)
                LD HL, (@ArchiveStartData.Frame.RightMinor)
                OR A
                SBC HL, BC
                JR Z, @ArchiveStart.RebuildLayerMasks.EqualSelectors            ; переход, если пары селекторов совпадают, стереть только завершающие маски

                ; стирание полных масок в третьем, первом и втором слое
                LD HL, @ArchiveStartLayerPrograms.Third.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                LD HL, @ArchiveStartLayerPrograms.First.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry

                ; восстановление основного растра маски в выбранном слое через OR
                POP HL
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD A, @ArchiveStartConst.OpOrAtHL
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A
                XOR A
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD HL, #0000
                LD (@ArchiveStart.ApplyOffsetTile.MaskOffsetPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                RET

                ; стирание только завершающей пары в третьем, первом и втором слое
EqualSelectors: LD HL, @ArchiveStartLayerPrograms.Third.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyEndMasks.Entry
                LD HL, @ArchiveStartLayerPrograms.First.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyEndMasks.Entry
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyEndMasks.Entry

                ; восстановление основного растра маски в выбранном слое через OR
                POP HL
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD A, @ArchiveStartConst.OpOrAtHL
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A
                XOR A
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD HL, #0000
                LD (@ArchiveStart.ApplyOffsetTile.MaskOffsetPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                RET

                endmodule
                endmodule
