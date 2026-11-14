                module ArchiveEngine
                module LoadAnimationSteps
                ; Документация [загрузка таблиц шагов](../../Docs/FighterAssets.md#вывод-и-чтение-секторов)
                ; -----------------------------------------
                ; загрузка двух экземпляров BAR в одну страницу для двух бойцов
                ; In:
                ;   селектор страниц по #4FB6 уже настроен, TR-DOS и диск доступны
                ; Out:
                ;   таблицы BAR по #C000 и #D000 страницы 0, статус второго чтения по #5D0F
                ; Corrupt:
                ;   HL, DE, BC, AF, дополнительно состояние TR-DOS согласно ПЗУ
                ; Note:
                ;   после первой загрузки код сразу готовит второй ключ, отдельной проверки статуса нет
                ; -----------------------------------------
                ; выбор общей страницы и загрузка первой таблицы шагов
Entry:          LD A, @ArchiveEngineConst.BarPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD HL, @ArchiveBarKeys.FirstFighter
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, @ArchiveEngineConst.FirstBar
                LD C, @TrDos.LoadFile
                LD A, @ArchiveEngineConst.LoadByName
                CALL @TrDos.Dispatch

                ; загрузка второй таблицы шагов со своим физическим ключом BAR
                LD HL, @ArchiveBarKeys.SecondFighter
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, @ArchiveEngineConst.SecondBar
                LD C, @TrDos.LoadFile
                LD A, @ArchiveEngineConst.LoadByName
                CALL @TrDos.Dispatch
                RET

                endmodule
                endmodule
