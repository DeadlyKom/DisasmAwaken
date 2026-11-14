; -----------------------------------------
; запись 16, SAVE0.s
; логическая длина 512, полный секторный размер 512
; -----------------------------------------
                ; Документация [состояние слота](../../Docs/SavedStateLayout.md)
                assert $ == #0000
                include "../Resources/16_SAVE0/StationTimer.asm"
                assert $ == #0004
                include "../Resources/16_SAVE0/CurrentSignature.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0009
                assert $ == #0009
                include "../Resources/16_SAVE0/SelectedMapKey.asm"
                assert $ == #000E
                include "../Resources/16_SAVE0/PlayerSaveHeader.asm"
                assert $ == #0017
                include "../Resources/16_SAVE0/OwnedCargoRows.asm"
                assert $ == #0053
                include "../Resources/16_SAVE0/EquipmentQuantityCodes.asm"
                assert $ == #0071
                ; Четыре соседних байта сохраняют неизвестный смысл.
                ; Документация [таблицы и сохранённые промежутки](../../Docs/EquipmentPhysicalTables.md)
                assert $ == #0071
                disp #0071
                include "../Resources/16_SAVE0/PrimaryQuantityTail.asm"
                ent
                assert $ == #0075
                include "../Resources/16_SAVE0/MissionOffer.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0085
                ; Документация [таблицы и сохранённые промежутки](../../Docs/MapDistanceAndRenderState.md)
                assert $ == #0085
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [таблицы и сохранённые промежутки](../../Docs/StationTransportTradeTables.md)
                assert $ == #0085
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [таблицы и сохранённые промежутки](../../Docs/StationOrderCompatibleSlots.md)
                assert $ == #0085
                ; Документация [перенос тела NEWS](../../Docs/StationNewsTransfer.md)
                assert $ == #0085
                disp #0085
                include "../Resources/16_SAVE0/NewsTransfer.asm"
                ent
                assert $ == #008B
                disp #008B
                include "../Resources/16_SAVE0/OrderCompatibleSlots.asm"
                ent
                assert $ == #00BB
                disp #00BB
                include "../Resources/16_SAVE0/SecondaryQuantities.asm"
                ent
                assert $ == #00C9
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/16_SAVE0/Unclassified00C9_00CB.bin"
                assert $ == #00CB
                disp #00CB
                include "../Resources/16_SAVE0/TransitionCounter.asm"
                ent
                assert $ == #00CC
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/16_SAVE0/Unclassified00CC_00CD.bin"
                assert $ == #00CD
                disp #00CD
                include "../Resources/16_SAVE0/MeasuredDistance.asm"
                ent
                assert $ == #00CE
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/16_SAVE0/Unclassified00CE_00CF.bin"
                assert $ == #00CF
                include "../Resources/16_SAVE0/StoredMapPoints.asm"
                assert $ == #0135
                include "../Resources/16_SAVE0/StoredMapOrder.asm"
                assert $ == #0140
                include "../Resources/16_SAVE0/MapAuxiliaryPoints.asm"
                assert $ == #0168
                include "../Resources/16_SAVE0/MapAuxiliaryCodes.asm"
                assert $ == #0173
                include "../Resources/16_SAVE0/InterfaceChoices.asm"
                assert $ == #017B
                include "../Resources/16_SAVE0/PointerKeys.asm"
                assert $ == #0187
                include "../Resources/16_SAVE0/InterfaceColors.asm"
                assert $ == #018D
                include "../Resources/16_SAVE0/ControlOptions.asm"
                assert $ == #01E3
                ; Хвост исходного состояния перед переносом в ACTION
                incbin "../Resources/16_SAVE0/InitialTransferTrailer.bin"
                assert $ == #0200
