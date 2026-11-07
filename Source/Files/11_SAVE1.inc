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
                incbin "../Resources/11_SAVE1/Unknown98AC.bin"
                assert $ == #0075
                include "../Resources/11_SAVE1/MissionOffer.asm"
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #0085
                incbin "../Resources/11_SAVE1/Unknown085.bin"
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
                ; Неизвестные поля сохранены, нули не считаются свободным местом.
                assert $ == #01E3
                incbin "../Resources/11_SAVE1/Unknown1E3.bin"
                assert $ == #0200
