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
                incbin "../Resources/16_SAVE0/Unknown98AC.bin"
                assert $ == #0075
                include "../Resources/16_SAVE0/MissionOffer.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0085
                incbin "../Resources/16_SAVE0/Unknown085.bin"
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
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #01E3
                incbin "../Resources/16_SAVE0/Unknown1E3.bin"
                assert $ == #0200
