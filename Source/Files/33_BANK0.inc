; -----------------------------------------
; запись 33, BANK0.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/33_BANK0/StripsPrefix.asm"
                assert $ == #1C92
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1C92
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/33_BANK0/StripStagingTail.bin"
                assert $ == #1CE3
                ; Документация [копия растрового слоя](../../Docs/BankArchiveTileLayers.md)
                assert $ == #1CE3
                ; Копия третьего внекаталожного растрового слоя, значения и положение сохранены
                incbin "../Resources/33_BANK0/ArchiveTileLayerCopy.bin"
                assert $ == #1DF7
                ; Unknown, последующие байты остаются отдельно
                incbin "../Resources/33_BANK0/Unclassified1DF7_1E40.bin"
                assert $ == #1E40
                include "../Resources/33_BANK0/StripsSuffix.asm"
                assert $ == #4000
