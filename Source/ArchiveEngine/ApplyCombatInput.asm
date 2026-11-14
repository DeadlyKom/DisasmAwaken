                module ArchiveEngine
                module ApplyCombatInput
                ; Документация [клавиши и выбор действия](../../Docs/FighterAssets.md#клавиши-и-выбор-действия)
                ; -----------------------------------------
                ; применение накопленного ввода обоих бойцов к запросам действий
                ; In:
                ;   записи бойцов содержат запросы, клавиши и указатели таблиц правил
                ; Out:
                ;   для каждого бойца клавиши потреблены, запрос заменён при совпадении правила
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
Entry:          LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.SelectFighterAction.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.SelectFighterAction.Entry
                RET

                endmodule
                endmodule
