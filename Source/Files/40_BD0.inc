; -----------------------------------------
; запись 40, BD0.C
; -----------------------------------------
                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)
                ; Маска и пиксели, ширина 6 байтов, высота 84 строк, ссылка BAR на #C000.
                assert $ == #0000
                incbin "../Resources/40_BD0/Sprite0000.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 85 строк, ссылка BAR на #C3F0.
                assert $ == #03F0
                incbin "../Resources/40_BD0/Sprite03F0.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 86 строк, ссылка BAR на #C7EC.
                assert $ == #07EC
                incbin "../Resources/40_BD0/Sprite07EC.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 86 строк, ссылка BAR на #CBF4.
                assert $ == #0BF4
                incbin "../Resources/40_BD0/Sprite0BF4.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 88 строк, ссылка BAR на #CFFC.
                assert $ == #0FFC
                incbin "../Resources/40_BD0/Sprite0FFC.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 88 строк, ссылка BAR на #D41C.
                assert $ == #141C
                incbin "../Resources/40_BD0/Sprite141C.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 94 строк, ссылка BAR на #D83C.
                assert $ == #183C
                incbin "../Resources/40_BD0/Sprite183C.bin"
                ; Маска и пиксели, ширина 8 байтов, высота 65 строк, ссылка BAR на #DD60.
                assert $ == #1D60
                incbin "../Resources/40_BD0/Sprite1D60.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 72 строк, ссылка BAR на #E170.
                assert $ == #2170
                incbin "../Resources/40_BD0/Sprite2170.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 93 строк, ссылка BAR на #E4D0.
                assert $ == #24D0
                incbin "../Resources/40_BD0/Sprite24D0.bin"
                ; Маска и пиксели, ширина 5 байтов, высота 93 строк, ссылка BAR на #E92C.
                assert $ == #292C
                incbin "../Resources/40_BD0/Sprite292C.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 57 строк, ссылка BAR на #ECCE.
                assert $ == #2CCE
                incbin "../Resources/40_BD0/Sprite2CCE.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 60 строк, ссылка BAR на #EF7A.
                assert $ == #2F7A
                incbin "../Resources/40_BD0/Sprite2F7A.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 48 строк, ссылка BAR на #F24A.
                assert $ == #324A
                incbin "../Resources/40_BD0/Sprite324A.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 56 строк, ссылка BAR на #F48A.
                assert $ == #348A
                incbin "../Resources/40_BD0/Sprite348A.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 50 строк, ссылка BAR на #F87A.
                assert $ == #387A
                incbin "../Resources/40_BD0/Sprite387A.bin"
                ; Маска и пиксели, ширина 13 байтов, высота 35 строк, ссылка BAR на #FBFE.
                assert $ == #3BFE
                incbin "../Resources/40_BD0/Sprite3BFE.bin"
                ; Исходный секторный хвост после логического файла, сохранён отдельно.
                assert $ == #3F8C
                ; Физический суффикс выделенных секторов, неиспользуемость не установлена
                ; Документация [границы и сохранение суффиксов](../../Docs/AllocatedSectorSuffixes.md)
                incbin "../Resources/40_BD0/SectorTail.bin"
                assert $ == #4000
