; -----------------------------------------
; запись 42, BD2.C
; -----------------------------------------
                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)
                ; Маска и пиксели, ширина 8 байтов, высота 87 строк, ссылка BAR на #C000.
                assert $ == #0000
                incbin "../Resources/42_BD2/Sprite0000.bin"
                ; Маска и пиксели, ширина 10 байтов, высота 82 строк, ссылка BAR на #C570.
                assert $ == #0570
                incbin "../Resources/42_BD2/Sprite0570.bin"
                ; Маска и пиксели, ширина 10 байтов, высота 86 строк, ссылка BAR на #CBD8.
                assert $ == #0BD8
                incbin "../Resources/42_BD2/Sprite0BD8.bin"
                ; Маска и пиксели, ширина 4 байтов, высота 89 строк, ссылка BAR на #D290.
                assert $ == #1290
                incbin "../Resources/42_BD2/Sprite1290.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 80 строк, ссылка BAR на #D558.
                assert $ == #1558
                incbin "../Resources/42_BD2/Sprite1558.bin"
                ; Маска и пиксели, ширина 10 байтов, высота 69 строк, ссылка BAR на #DAF8.
                assert $ == #1AF8
                incbin "../Resources/42_BD2/Sprite1AF8.bin"
                ; Маска и пиксели, ширина 9 байтов, высота 85 строк, ссылка BAR на #E05C.
                assert $ == #205C
                incbin "../Resources/42_BD2/Sprite205C.bin"
                ; Маска и пиксели, ширина 7 байтов, высота 77 строк, ссылка BAR на #E656.
                assert $ == #2656
                incbin "../Resources/42_BD2/Sprite2656.bin"
                ; Маска и пиксели, ширина 8 байтов, высота 81 строк, ссылка BAR на #EA8C.
                assert $ == #2A8C
                incbin "../Resources/42_BD2/Sprite2A8C.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 77 строк, ссылка BAR на #EF9C.
                assert $ == #2F9C
                incbin "../Resources/42_BD2/Sprite2F9C.bin"
                ; Маска и пиксели, ширина 8 байтов, высота 85 строк, ссылка BAR на #F338.
                assert $ == #3338
                incbin "../Resources/42_BD2/Sprite3338.bin"
                ; Маска и пиксели, ширина 6 байтов, высота 88 строк, ссылка BAR на #F888.
                assert $ == #3888
                incbin "../Resources/42_BD2/Sprite3888.bin"
                ; 720 логических байтов без подтверждённой ссылки BAR, формат не назначается.
                assert $ == #3CA8
                incbin "../Resources/42_BD2/UnknownLogicalTail.bin"
                ; Исходный секторный хвост после логического файла, сохранён отдельно.
                assert $ == #3F78
                incbin "../Resources/42_BD2/SectorTail.bin"
                assert $ == #4000
