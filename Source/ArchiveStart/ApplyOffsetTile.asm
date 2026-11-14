                module ArchiveStart
                module ApplyOffsetTile
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; перевод смещения в координаты плитки и вызов объединения
                ; In:
                ;   HL - сохраняемый указатель, BC - адрес растра, IX - очередная пара смещений
                ; Out:
                ;   HL сохранён, DE указывает за восемью строками источника, IX продвинут на одну пару
                ; Corrupt:
                ;   DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; сложение смещений плитки с базовыми координатами сетки
Entry:          LD A, (@ArchiveStartLayerWork.OriginX)
                ADD A, (IX+#00)
                INC IX
                LD E, A
                LD A, (@ArchiveStartLayerWork.OriginY)
                ADD A, (IX+#00)
                INC IX
                LD D, A
                PUSH HL

                ; прибавление изменяемого смещения к адресу источника и объединение восьми строк
MaskOffsetPatch:LD HL, #0000
                ADD HL, BC
                LD B, H
                LD C, L
                CALL @ArchiveStart.BlendLayerTile.Entry
                POP HL
                RET

                endmodule
                endmodule
