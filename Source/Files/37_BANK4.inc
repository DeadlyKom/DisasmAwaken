; -----------------------------------------
; запись 37, BANK4.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/37_BANK4/StripsPrefix.asm"
                assert $ == #1B4E
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                assert $ == #1B4E
                ; Unknown, оставшаяся часть промежутка сохраняется буквально
                ; Документация [таблицы и сохранённые промежутки](../../Docs/BankArchiveRouteCopies.md)
                assert $ == #1B4E
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1B4E
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/37_BANK4/StripStagingTail.bin"
                assert $ == #1BB7
                ; Документация [копия растрового слоя](../../Docs/BankArchiveTileLayers.md)
                assert $ == #1BB7
                ; Копия третьего внекаталожного растрового слоя, значения и положение сохранены
                incbin "../Resources/37_BANK4/ArchiveTileLayerCopy.bin"
                assert $ == #1E12
                disp #1E12
                include "../Resources/37_BANK4/ArchiveRouteCopies.asm"
                ent
                assert $ == #1FA2
                ; Unknown, соседние байты не объявляются свободными
                incbin "../Resources/37_BANK4/Unclassified1FA2_221E.bin"
                assert $ == #221E
                include "../Resources/37_BANK4/StripsAdditional.asm"
                assert $ == #265C
                include "../Resources/37_BANK4/PartialStripCopy.asm"
                assert $ == #27A0
                include "../Resources/37_BANK4/StripsSuffix.asm"
                assert $ == #4000
