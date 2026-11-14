                module ArchiveStart
                module RedrawLayerSelection
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; обновление операндов растровых слоёв для прежнего варианта
                ; In:
                ;   AF - A, номер варианта 0..11, базовые координаты и пропуски пары уже записаны
                ; Out:
                ;   при разных селекторах записаны общие и завершающие плитки, при равных записана пара плиток и стёрта маска
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; вычисление смещения варианта как 256 × A / 2 + 256 × A / 4, то есть 192 × A
Entry:          LD H, A
                LD L, #00
                SRL H
                RR L
                LD D, H
                LD E, L
                SRL H
                RR L
                ADD HL, DE
                LD (@ArchiveStartLayerWork.VariantOffset), HL

                ; замена обоих кодов объединения на NOP для прямой записи прежнего растра
                XOR A
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A

                ; проверка равенства двух пар селекторов
                LD BC, (@ArchiveStartData.Frame.LeftMinor)
                LD HL, (@ArchiveStartData.Frame.RightMinor)
                OR A
                SBC HL, BC
                JR Z, @ArchiveStart.RedrawLayerSelection.EqualSelectors         ; переход, если селекторы обеих сторон совпадают, обновить только завершающие плитки

                ; запись полного варианта на первый слой
                LD HL, @ArchiveStartLayerPrograms.First.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.First
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLayerVariant.Entry

                ; запись полного варианта на второй слой
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.Second
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLayerVariant.Entry

                ; запись полного варианта на третий слой
                LD HL, @ArchiveStartLayerPrograms.Third.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.Third
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLayerVariant.Entry
                RET

                ; запись двух завершающих плиток на первый слой
EqualSelectors: LD HL, @ArchiveStartLayerPrograms.First.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.First + @ArchiveStartConst.CommonTileBytes
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLastLayerTiles.Entry

                ; запись двух завершающих плиток на второй слой
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.Second + @ArchiveStartConst.CommonTileBytes
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLastLayerTiles.Entry

                ; запись двух завершающих плиток на третий слой
                LD HL, @ArchiveStartLayerPrograms.Third.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                LD BC, @ArchiveStartLayers.Third + @ArchiveStartConst.CommonTileBytes
                LD HL, (@ArchiveStartLayerWork.VariantOffset)
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.WriteLastLayerTiles.Entry

                ; проверка стороны изменения для выбора слоя и пары стирающих масок
                LD A, (@ArchiveStartSelector.Side)
                OR A
                JR NZ, @ArchiveStart.RedrawLayerSelection.EraseSecond           ; переход, если меняется правая сторона, стереть маску во втором слое

                ; для левой стороны выбор базовых координат общего варианта и правой пары масок
                LD HL, (@ArchiveStartData.Frame.RightMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD HL, @ArchiveStartConst.RightCoordSkip
                LD (@ArchiveStart.ApplyLayerMasks.EndPairPatch + 1), HL

                ; включение CPL и AND со вторым набором масок, стирание в третьем слое
                LD A, @ArchiveStartConst.OpAndAtHL
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A
                LD A, @ArchiveStartConst.OpComplement
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD HL, @ArchiveStartConst.MaskVariantSize
                LD (@ArchiveStart.ApplyOffsetTile.MaskOffsetPatch + 1), HL
                LD HL, @ArchiveStartLayerPrograms.Third.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                RET

                ; для правой стороны выбор базовых координат общего варианта и левой пары масок
EraseSecond:    LD HL, (@ArchiveStartData.Frame.RightMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD HL, #0000
                LD (@ArchiveStart.ApplyLayerMasks.EndPairPatch + 1), HL

                ; включение CPL и AND со вторым набором масок, стирание во втором слое
                LD A, @ArchiveStartConst.OpAndAtHL
                LD (@ArchiveStart.BlendLayerTile.BlendPatch), A
                LD A, @ArchiveStartConst.OpComplement
                LD (@ArchiveStart.BlendLayerTile.InvertPatch), A
                LD HL, @ArchiveStartConst.MaskVariantSize
                LD (@ArchiveStart.ApplyOffsetTile.MaskOffsetPatch + 1), HL
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                LD (@ArchiveStart.BlendLayerTile.DestPatch + 1), HL
                CALL @ArchiveStart.ApplyLayerMasks.Entry
                RET

                endmodule
                endmodule
