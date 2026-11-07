; -----------------------------------------
; запись 41, BD1.C
; -----------------------------------------
                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)
                ; Маска и пиксели, ширина 7 байтов, высота 91 строк, ссылка BAR на #C000.
                assert $ == #0000
                incbin "../Resources/41_BD1/Sprite0000.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 90 строк, ссылка BAR на #C4FA.
                assert $ == #04FA
                incbin "../Resources/41_BD1/Sprite04FA.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 91 строк, ссылка BAR на #C9E6.
                assert $ == #09E6
                incbin "../Resources/41_BD1/Sprite09E6.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 88 строк, ссылка BAR на #CEE0.
                assert $ == #0EE0
                incbin "../Resources/41_BD1/Sprite0EE0.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 88 строк, ссылка BAR на #D3B0.
                assert $ == #13B0
                incbin "../Resources/41_BD1/Sprite13B0.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 89 строк, ссылка BAR на #D880.
                assert $ == #1880
                incbin "../Resources/41_BD1/Sprite1880.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 89 строк, ссылка BAR на #DD5E.
                assert $ == #1D5E
                incbin "../Resources/41_BD1/Sprite1D5E.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 88 строк, ссылка BAR на #E23C.
                assert $ == #223C
                incbin "../Resources/41_BD1/Sprite223C.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 88 строк, ссылка BAR на #E70C.
                assert $ == #270C
                incbin "../Resources/41_BD1/Sprite270C.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 57 строк, ссылка BAR на #EBDC.
                assert $ == #2BDC
                incbin "../Resources/41_BD1/Sprite2BDC.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 50 строк, ссылка BAR на #EE88.
                assert $ == #2E88
                incbin "../Resources/41_BD1/Sprite2E88.bin"
                ; Маска и пиксели, ширина 5 байтов, высота 42 строк, ссылка BAR на #F0E0.
                assert $ == #30E0
                incbin "../Resources/41_BD1/Sprite30E0.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 33 строк, ссылка BAR на #F284.
                assert $ == #3284
                incbin "../Resources/41_BD1/Sprite3284.bin"
                ; Маска и пиксели, ширина 5 байтов, высота 42 строк, ссылка BAR на #F410.
                assert $ == #3410
                incbin "../Resources/41_BD1/Sprite3410.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 32 строк, ссылка BAR на #F5B4.
                assert $ == #35B4
                incbin "../Resources/41_BD1/Sprite35B4.bin"
                ; Маска и пиксели, ширина 10 байтов, высота 56 строк, ссылка BAR на #F734.
                assert $ == #3734
                incbin "../Resources/41_BD1/Sprite3734.bin"
                ; Маска и пиксели, ширина 10 байтов, высота 45 строк, ссылка BAR на #FB94.
                assert $ == #3B94
                incbin "../Resources/41_BD1/Sprite3B94.bin"
                ; Исходный секторный хвост после логического файла, сохранён отдельно.
                assert $ == #3F18
                incbin "../Resources/41_BD1/SectorTail.bin"
                assert $ == #4000
