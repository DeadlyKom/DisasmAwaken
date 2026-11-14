                module ArchiveStart
                module CalculateLayerOrigin
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; вычисление начала сетки плиток для пары селекторов
                ; In:
                ;   HL - H, старший индекс 0..2, L, младший индекс 0..3
                ; Out:
                ;   записаны координаты X = 5 × (3 − L) и Y = 7 × H, L получает 3 − L
                ; Corrupt:
                ;   HL, AF
                ; -----------------------------------------
                ; вычисление горизонтального начала по убыванию младшего индекса
Entry:          LD A, #03
                SUB L
                LD L, A
                ADD A, A
                ADD A, A
                ADD A, L
                LD (@ArchiveStartLayerWork.OriginX), A

                ; вычисление вертикального начала по возрастанию старшего индекса
                LD A, H
                ADD A, A
                ADD A, A
                ADD A, A
                SUB H
                LD (@ArchiveStartLayerWork.OriginY), A
                RET

                endmodule
                endmodule
