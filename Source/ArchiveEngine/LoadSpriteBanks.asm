                module ArchiveEngine
                module LoadSpriteBanks
                ; Документация [загрузка страниц масок](../../Docs/FighterAssets.md#вывод-и-чтение-секторов)
                ; -----------------------------------------
                ; последовательная загрузка BD0..BD3 в расширенные страницы 8..11
                ; In:
                ;   селектор страниц по #4FB6 уже настроен, TR-DOS и диск доступны
                ; Out:
                ;   HL - адрес сразу после первой таблицы ключей
                ;   BC - B равен нулю, C сохранён
                ;   AF - A равен 4, статус последнего чтения по #5D0F
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', дополнительно состояние TR-DOS согласно ПЗУ
                ; Note:
                ;   значение A перед выбором страницы сохраняется на стеке независимо от результата TR-DOS
                ;   последнее увеличение даёт 4, внешние границы цикла определяет B
                ; -----------------------------------------
                ; подготовка указателя и числа файлов, индекс одновременно выбирает страницу
Entry:          LD A, @ArchiveEngineConst.FirstSprite
                LD HL, @ArchiveBdKeys.Bd0
                LD B, @ArchiveEngineConst.SpriteBankCount

                ; перенос очередного ключа и сохранение указателя на следующий
LoadNext:       PUSH BC
                EX AF, AF'
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                PUSH HL
                EX AF, AF'
                PUSH AF
                ; выбор страницы по индексу и загрузка масок в банковое окно
                CALL @ArchiveEngine.SelectSpritePage.Entry
                LD C, @TrDos.LoadFile
                LD HL, @ArchiveEngineConst.SpriteData
                LD A, @ArchiveEngineConst.LoadByName
                CALL @TrDos.Dispatch
                ; восстановление счётчиков после файловой операции
                POP AF
                INC A
                POP HL
                POP BC
                DJNZ @ArchiveEngine.LoadSpriteBanks.LoadNext

                RET

                endmodule
                endmodule
