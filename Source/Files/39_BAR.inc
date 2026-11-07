; -----------------------------------------
; запись 39, BAR.C
; -----------------------------------------
                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)
                assert $ == #0000
                include "../Resources/39_BAR/PoseSequences.asm"
                ; Исходный секторный хвост после логического файла, сохранён отдельно.
                assert $ == #0C04
                incbin "../Resources/39_BAR/SectorTail.bin"
                assert $ == #0D00
