; -----------------------------------------
; запись 34, BANK1.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/34_BANK1/StripsPrefix.asm"
                assert $ == #1CFE
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                ; Документация [таблицы и сохранённые промежутки](../../Docs/BankArchiveRouteCopies.md)
                assert $ == #1CFE
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1CFE
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/34_BANK1/StripStagingTail.bin"
                assert $ == #1D49
                ; Документация [копия растрового слоя](../../Docs/BankArchiveTileLayers.md)
                assert $ == #1D49
                ; Копия третьего внекаталожного растрового слоя, значения и положение сохранены
                incbin "../Resources/34_BANK1/ArchiveTileLayerCopy.bin"
                assert $ == #1E12
                disp #1E12
                include "../Resources/34_BANK1/ArchiveRouteCopies.asm"
                ent
                assert $ == #1E76
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/34_BANK1/Unclassified1E76_23DA.bin"
                assert $ == #23DA
                include "../Resources/34_BANK1/StripsSuffix.asm"
                assert $ == #4000
