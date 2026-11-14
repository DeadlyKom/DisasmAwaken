                module ArchiveStart
                module BlendLayerTile
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; объединение восьми растровых строк с операндами одного знакоместа
                ; In:
                ;   DE - D, ряд знакоместа, E, колонка, BC - источник восьми байтов, операнды режима и слоя заданы
                ; Out:
                ;   изменены восемь байтов в операндах LD DE, DE указывает за источником
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; -----------------------------------------
                ; сохранение адреса источника
Entry:          PUSH BC

                ; получение адреса слоя из изменяемого операнда
DestPatch:      LD BC, @ArchiveStartLayerPrograms.Third.Entry

                ; вычисление адреса ряда знакоместа, начало слоя + 339 × Y
                LD A, E
                EX AF, AF'
                LD A, D
                LD DE, @ArchiveStartConst.LayerCellStride
                PUSH BC
                CALL @ArchiveStart.MultiplyByteWord.Entry
                POP BC
                ADD HL, BC

                ; вычисление смещения колонки, 2 × (X AND #FE) + 1 − (X AND 1) + 5
                EX AF, AF'
                LD C, A
                AND #01
                XOR #01
                LD B, A
                LD A, C
                AND #FE
                ADD A, A
                ADD A, B
                ADD A, #05
                LD C, A
                LD B, #00
                ADD HL, BC

                ; восстановление адреса источника и настройка восьми строк с шагом 42 байта
                POP DE
                LD BC, @ArchiveStartConst.LayerLineStride
                LD A, @ArchiveStartConst.TileHeight

                ; перенос исходного байта и переключение на регистр данных
NextRow:        EX AF, AF'
                LD A, (DE)

                ; изменяемый код NOP или CPL
InvertPatch:    NOP

                ; изменяемый код NOP, OR (HL) или AND (HL)
BlendPatch:     OR (HL)

                ; запись операнда и проверка оставшихся строк плитки
                LD (HL), A
                INC DE
                ADD HL, BC
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveStart.BlendLayerTile.NextRow                     ; переход, если остались строки плитки, обработать следующий байт

                RET

                endmodule
                endmodule
