                module ArchiveEngine
                module CollectCombatInput
                ; Документация [клавиши и выбор действия](../../Docs/FighterAssets.md#клавиши-и-выбор-действия)
                ; -----------------------------------------
                ; опрос клавиш и накопление двух групп битов для каждого бойца в IRQ
                ; In:
                ;   физические таблицы портов и масок готовы, текущая сторона известна
                ; Out:
                ;   биты нажатых клавиш добавлены к накопителям обеих записей
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; Note:
                ;   первое чтение #7FFE выполняется отдельно, его значение не участвует в формировании битов
                ; -----------------------------------------
Entry:          LD BC, @ArchiveEngineConst.InitialKeyPort
                IN A, (C)
                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.PollFighterKeys.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.PollFighterKeys.Entry
                RET

                endmodule
                endmodule
