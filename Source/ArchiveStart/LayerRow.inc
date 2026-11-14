                ; Один исходный ряд экранного слоя, слова перечисляются от правого края.
                MACRO ArchiveLayerRow w0, w1, w2, w3, w4, w5, w6, w7, w8, w9
                LD SP, HL
                LD DE, w0
                PUSH DE
                LD DE, w1
                PUSH DE
                LD DE, w2
                PUSH DE
                LD DE, w3
                PUSH DE
                LD DE, w4
                PUSH DE
                LD DE, w5
                PUSH DE
                LD DE, w6
                PUSH DE
                LD DE, w7
                PUSH DE
                LD DE, w8
                PUSH DE
                LD DE, w9
                PUSH DE
                INC H
                ENDM
