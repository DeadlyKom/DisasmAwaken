; -----------------------------------------
; запись 38, BANK5.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/38_BANK5/StripsPrefix.asm"
                assert $ == #1D16
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                assert $ == #1D16
                ; Unknown, оставшаяся часть промежутка сохраняется буквально
                ; Документация [таблицы и сохранённые промежутки](../../Docs/BankArchiveRouteCopies.md)
                assert $ == #1D16
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1D16
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/38_BANK5/StripStagingTail.bin"
                assert $ == #1D61
                ; Документация [копия растрового слоя](../../Docs/BankArchiveTileLayers.md)
                assert $ == #1D61
                ; Копия третьего внекаталожного растрового слоя, значения и положение сохранены
                incbin "../Resources/38_BANK5/ArchiveTileLayerCopy.bin"
                assert $ == #1E12
                disp #1E12
                include "../Resources/38_BANK5/ArchiveRouteCopies.asm"
                ent
                assert $ == #2006
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/38_BANK5/Unclassified2006_221E.bin"
                assert $ == #221E
                include "../Resources/38_BANK5/StripsAdditional.asm"
                assert $ == #265C
                include "../Resources/38_BANK5/PartialStripCopy.asm"
                assert $ == #26B0
                include "../Resources/38_BANK5/StripsSuffix.asm"
                assert $ == #4000
