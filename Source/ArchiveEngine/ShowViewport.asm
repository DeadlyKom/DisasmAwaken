                module ArchiveEngine
                module ShowViewport
                ; Документация [полный фон кадра](../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; -----------------------------------------
                ; вывод рабочего окна сцены снизу вверх в теневой экран
                ; In:
                ;   ViewColumn указывает на первый столбец окна по #7700, VerticalOffset задаёт строку 0..11
                ;   пропуск источника в CopyViewportRows уже настроен
                ; Out:
                ;   перенесены 5844 байта растра, в строках индикаторов сохранены боковые столбцы
                ;   выбрана страница 7, атрибуты не меняются
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; -----------------------------------------
                ; вычисление начала окна из выбранных строки и столбца в фиксированной RAM
Entry:          LD A, @ArchiveEngineConst.ScreenPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD A, (@ArchiveEngineScene.View.VerticalOffset)
                LD DE, (@ArchiveEngineScene.View.RowBytes)
                CALL @ArchiveEngine.MultiplyByteWord.Entry
                LD DE, (@ArchiveEngineScene.View.ViewColumn)
                ADD HL, DE
                LD DE, @ArchiveEngineConst.ScreenBottom

                ; перенос двадцати групп по восемь строк, счётчик групп хранится в AF'
                LD A, @ArchiveEngineConst.ScreenGroups
FullGroup:      EX AF, AF'
                LD A, @ArchiveEngineConst.MeterHeight
                CALL @ArchiveEngine.CopyViewportRows.Entry
                LD A, E
                SUB @ArchiveEngineConst.CharRowBytes
                LD E, A
                JR C, @ArchiveEngine.ShowViewport.CountGroup                    ; переход, если переход в предыдущую треть уже учтён в адресе

                LD A, D
                ADD A, @ArchiveEngineConst.MeterHeight
                LD D, A
CountGroup:     EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.ShowViewport.FullGroup                    ; переход, если остались полные группы строк ниже индикаторов

                ; перенос последних семи строк снизу и сохранение начала строк индикаторов
                LD A, @ArchiveEngineConst.BelowMeters
                CALL @ArchiveEngine.CopyViewportRows.Entry
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                LD (@ArchiveEngineScene.View.MeterGapSource), HL

                ; пропуск десяти строк, в которых полные строки заменены индикаторами
                ADD HL, BC
                ADD HL, BC
                SLA C
                RL B
                SLA C
                RL B
                SLA C
                RL B
                ADD HL, BC

                ; вывод оставшихся пятнадцати полных строк над индикаторами
                LD DE, @ArchiveEngineConst.AboveMeters
                LD A, @ArchiveEngineConst.BelowMeters
                CALL @ArchiveEngine.CopyViewportRows.Entry
                LD DE, @ArchiveEngineConst.ScreenTopGroup
                LD A, @ArchiveEngineConst.MeterHeight
                CALL @ArchiveEngine.CopyViewportRows.Entry

                ; перенос двух байтов между полосами в нижней строке области индикаторов
                LD HL, (@ArchiveEngineScene.View.MeterGapSource)
                LD BC, @ArchiveEngineConst.MeterGapColumn
                ADD HL, BC
                LD DE, @ArchiveEngineConst.MeterGapBottom
                LDI
                LD A, (HL)
                LD (DE), A
                DEC HL
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC

                ; перенос двух байтов в каждой из восьми внутренних строк области
                LD DE, @ArchiveEngineConst.MeterGapMiddle
                LD A, @ArchiveEngineConst.MeterHeight
                LD C, #FF
GapRow:         LDI
                LDI
                DEC DE
                DEC DE
                DEC D
                DEC HL
                DEC HL
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC
                DEC A
                JR NZ, @ArchiveEngine.ShowViewport.GapRow                       ; переход, если остались внутренние строки между полосами

                ; перенос двух байтов верхней строки области индикаторов
                LD DE, @ArchiveEngineConst.MeterGapTop
                LDI
                LDI
                RET

                endmodule
                endmodule
