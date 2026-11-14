; -----------------------------------------
; запись 11, SAVE1.s
; логическая длина 512, полный секторный размер 512
; -----------------------------------------
                ; Документация [состояние слота](../../Docs/SavedStateLayout.md)
                assert $ == #0000
                include "../Resources/11_SAVE1/StationTimer.asm"
                assert $ == #0004
                include "../Resources/11_SAVE1/CurrentSignature.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0009
                assert $ == #0009
                include "../Resources/11_SAVE1/SelectedMapKey.asm"
                assert $ == #000E
                include "../Resources/11_SAVE1/PlayerSaveHeader.asm"
                assert $ == #0017
                include "../Resources/11_SAVE1/OwnedCargoRows.asm"
                assert $ == #0053
                include "../Resources/11_SAVE1/EquipmentQuantityCodes.asm"
                assert $ == #0071
                ; Четыре соседних байта сохраняют неизвестный смысл.
                ; Документация [таблицы и сохранённые промежутки](../../Docs/EquipmentPhysicalTables.md)
                assert $ == #0071
                disp #0071
                include "../Resources/11_SAVE1/PrimaryQuantityTail.asm"
                ent
                assert $ == #0075
                include "../Resources/11_SAVE1/MissionOffer.asm"
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
                include "../Resources/11_SAVE1/NewsTransfer.asm"
                ent
                assert $ == #008B
                disp #008B
                include "../Resources/11_SAVE1/OrderCompatibleSlots.asm"
                ent
                assert $ == #00BB
                disp #00BB
                include "../Resources/11_SAVE1/SecondaryQuantities.asm"
                ent
                assert $ == #00C9
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/11_SAVE1/Unclassified00C9_00CB.bin"
                assert $ == #00CB
                disp #00CB
                include "../Resources/11_SAVE1/TransitionCounter.asm"
                ent
                assert $ == #00CC
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/11_SAVE1/Unclassified00CC_00CD.bin"
                assert $ == #00CD
                disp #00CD
                include "../Resources/11_SAVE1/MeasuredDistance.asm"
                ent
                assert $ == #00CE
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/11_SAVE1/Unclassified00CE_00CF.bin"
                assert $ == #00CF
                include "../Resources/11_SAVE1/StoredMapPoints.asm"
                assert $ == #0135
                include "../Resources/11_SAVE1/StoredMapOrder.asm"
                assert $ == #0140
                include "../Resources/11_SAVE1/MapAuxiliaryPoints.asm"
                assert $ == #0168
                include "../Resources/11_SAVE1/MapAuxiliaryCodes.asm"
                assert $ == #0173
                include "../Resources/11_SAVE1/InterfaceChoices.asm"
                assert $ == #017B
                include "../Resources/11_SAVE1/PointerKeys.asm"
                assert $ == #0187
                include "../Resources/11_SAVE1/InterfaceColors.asm"
                assert $ == #018D
                include "../Resources/11_SAVE1/ControlOptions.asm"
                assert $ == #01E3
                ; Хвост исходного состояния перед переносом в ACTION
                incbin "../Resources/11_SAVE1/InitialTransferTrailer.bin"
                assert $ == #0200
