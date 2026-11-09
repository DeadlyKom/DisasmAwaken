; -----------------------------------------
; запись 43, BD3.C
; -----------------------------------------
                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)
                ; Маска и пиксели, ширина 7 байтов, высота 90 строк, ссылка BAR на #C000.
                assert $ == #0000
                incbin "../Resources/43_BD3/Sprite0000.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 105 строк, ссылка BAR на #C4EC.
                assert $ == #04EC
                incbin "../Resources/43_BD3/Sprite04EC.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 42 строк, ссылка BAR на #C9D8.
                assert $ == #09D8
                incbin "../Resources/43_BD3/Sprite09D8.bin"
                ; Маска и пиксели, ширина 12 байтов, высота 40 строк, ссылка BAR на #CBD0.
                assert $ == #0BD0
                incbin "../Resources/43_BD3/Sprite0BD0.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 54 строк, ссылка BAR на #CF90.
                assert $ == #0F90
                incbin "../Resources/43_BD3/Sprite0F90.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 74 строк, ссылка BAR на #D284.
                assert $ == #1284
                incbin "../Resources/43_BD3/Sprite1284.bin"
                ; Маска и пиксели, ширина 8 байтов, высота 86 строк, ссылка BAR на #D690.
                assert $ == #1690
                incbin "../Resources/43_BD3/Sprite1690.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 86 строк, ссылка BAR на #DBF0.
                assert $ == #1BF0
                incbin "../Resources/43_BD3/Sprite1BF0.bin"
                ; Маска и пиксели, ширина 11 байтов, высота 81 строк, ссылка BAR на #E1FC.
                assert $ == #21FC
                incbin "../Resources/43_BD3/Sprite21FC.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 87 строк, ссылка BAR на #E8F2.
                assert $ == #28F2
                incbin "../Resources/43_BD3/Sprite28F2.bin"
                ; Исходный секторный хвост после логического файла, сохранён отдельно.
                assert $ == #2F10
                ; Физический суффикс выделенных секторов, неиспользуемость не установлена
                ; Документация [границы и сохранение суффиксов](../../Docs/AllocatedSectorSuffixes.md)
                incbin "../Resources/43_BD3/SectorTail.bin"
                assert $ == #3000
