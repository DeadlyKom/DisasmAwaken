; -----------------------------------------
; запись 36, BANK3.C
; логическая длина 16384, полный секторный размер 16384
; -----------------------------------------
                assert $ == #0000
                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)
                assert $ == #0000
                include "../Resources/36_BANK3/StripsPrefix.asm"
                assert $ == #1B66
                ; Unknown, содержимое промежутка не объявляется неиспользуемым
                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #1B66
                ; Исходные байты, которые фиксированный LDIR читает за концом растра полосы
                incbin "../Resources/36_BANK3/StripStagingTail.bin"
                assert $ == #1BD5
                ; Unknown, дальнейшие чтения промежутка этой трассой не установлены
                incbin "../Resources/36_BANK3/Unclassified1BD5_221E.bin"
                assert $ == #221E
                include "../Resources/36_BANK3/StripsSuffix.asm"
                assert $ == #4000
