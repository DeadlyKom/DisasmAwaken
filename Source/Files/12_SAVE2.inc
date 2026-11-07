; -----------------------------------------
; запись 12, SAVE2.s
; логическая длина 512, полный секторный размер 512
; -----------------------------------------
                ; Документация [состояние слота](../../Docs/SavedStateLayout.md)
                assert $ == #0000
                include "../Resources/12_SAVE2/StationTimer.asm"
                assert $ == #0004
                include "../Resources/12_SAVE2/CurrentSignature.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0009
                assert $ == #0009
                include "../Resources/12_SAVE2/SelectedMapKey.asm"
                assert $ == #000E
                include "../Resources/12_SAVE2/PlayerSaveHeader.asm"
                assert $ == #0017
                include "../Resources/12_SAVE2/OwnedCargoRows.asm"
                assert $ == #0053
                include "../Resources/12_SAVE2/EquipmentQuantityCodes.asm"
                assert $ == #0071
                ; Четыре соседних байта сохраняют неизвестный смысл.
                incbin "../Resources/12_SAVE2/Unknown98AC.bin"
                assert $ == #0075
                include "../Resources/12_SAVE2/MissionOffer.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0085
                incbin "../Resources/12_SAVE2/Unknown085.bin"
                assert $ == #00CF
                include "../Resources/12_SAVE2/StoredMapPoints.asm"
                assert $ == #0135
                include "../Resources/12_SAVE2/StoredMapOrder.asm"
                assert $ == #0140
                include "../Resources/12_SAVE2/MapAuxiliaryPoints.asm"
                assert $ == #0168
                include "../Resources/12_SAVE2/MapAuxiliaryCodes.asm"
                assert $ == #0173
                include "../Resources/12_SAVE2/InterfaceChoices.asm"
                assert $ == #017B
                include "../Resources/12_SAVE2/PointerKeys.asm"
                assert $ == #0187
                include "../Resources/12_SAVE2/InterfaceColors.asm"
                assert $ == #018D
                include "../Resources/12_SAVE2/ControlOptions.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #01E3
                incbin "../Resources/12_SAVE2/Unknown1E3.bin"
                assert $ == #0200
