; -----------------------------------------
; запись 35, BANK2.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/35_BANK2/StripsPrefix.asm"
                assert $ == #1CB6
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                ; Документация [таблицы и сохранённые промежутки](../../Docs/BankArchiveRouteCopies.md)
                assert $ == #1CB6
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1CB6
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/35_BANK2/StripStagingTail.bin"
                assert $ == #1D07
                ; Документация [копия растрового слоя](../../Docs/BankArchiveTileLayers.md)
                assert $ == #1D07
                ; Копия третьего внекаталожного растрового слоя, значения и положение сохранены
                incbin "../Resources/35_BANK2/ArchiveTileLayerCopy.bin"
                assert $ == #1E12
                disp #1E12
                include "../Resources/35_BANK2/ArchiveRouteCopies.asm"
                ent
                assert $ == #1EDA
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/35_BANK2/Unclassified1EDA_242E.bin"
                assert $ == #242E
                include "../Resources/35_BANK2/StripsSuffix.asm"
                assert $ == #4000
