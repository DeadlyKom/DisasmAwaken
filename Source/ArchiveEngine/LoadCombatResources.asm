                module ArchiveEngine
                module LoadCombatResources
                ; Документация [порядок запросов](../../Docs/ArchiveMenuHandoff.md#исполнение)
                ; -----------------------------------------
                ; загрузка масок, рабочего фона и двух таблиц шагов бойцов
                ; In:
                ;   операнд SelectPage.Dispatch настроен, TR-DOS и диск доступны
                ; Out:
                ;   BD0..BD3 в страницах 8..11, scene1po по #7700, BAR по #C000 и #D000 страницы 0
                ;   статус последней загрузки BAR по #5D0F, выбран экран страницы 7 и окно страницы 0
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', дополнительно состояние TR-DOS согласно ПЗУ
                ; Note:
                ;   все вызовы идут последовательно, между ними нет проверки дискового статуса
                ; -----------------------------------------
Entry:          CALL @ArchiveEngine.LoadSpriteBanks.Entry
                CALL @ArchiveEngine.LoadScenePixels.Entry
                CALL @ArchiveEngine.LoadAnimationSteps.Entry
                RET

                endmodule
                endmodule
