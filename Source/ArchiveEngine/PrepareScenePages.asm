                module ArchiveEngine
                module PrepareScenePages
                ; Документация [разделение фона](../../Docs/Scene1PixelPairs.md#код-во-внекаталожных-секторах)
                ; -----------------------------------------
                ; настройка окна и копирование исходного фона в две страницы
                ; In:
                ;   scene1po загружен по #7700, селектор страниц настроен
                ; Out:
                ;   операнд AdvanceSource в CopyViewportRows получает шаг 60
                ;   ViewColumn получает #771D, первые 178 строк копируются по #C000 страницы 13
                ;   следующие 25 строк и ещё 92 байта копируются по #C054 страницы 14
                ; Corrupt:
                ;   HL, DE, BC, AF, выбрана страница 14
                ; Note:
                ;   последние 12 байтов фиксированной RAM и 80 прежних байтов страницы 14 участвуют во втором LDIR
                ; -----------------------------------------
                ; расчёт пропуска от конца 32-байтовой части строки до начала следующей
Entry:          LD HL, (@ArchiveEngineScene.View.RowBytes)
                LD DE, @ArchiveEngineConst.WindowNegWidth
                ADD HL, DE
                LD (@ArchiveEngine.CopyViewportRows.AdvanceSource + 1), HL

                ; исходное сложение шага с шириной экрана, результат HL далее замещается
                LD HL, (@ArchiveEngineScene.View.RowBytes)
                LD DE, @ArchiveEngineConst.CharRowBytes
                ADD HL, DE

                ; центрирование окна, вычитание его ширины и деление свободного места пополам
                LD HL, (@ArchiveEngineScene.View.SourceWidth)
                LD DE, @ArchiveEngineConst.WindowNegWidth
                ADD HL, DE
                SRL H
                RR L
                LD DE, @ArchiveEngineConst.ScenePixels
                ADD HL, DE
                LD (@ArchiveEngineScene.View.ViewColumn), HL

                ; перенос 178 полных строк в первую расширенную страницу
                LD BC, @ArchiveEngineConst.SceneHeadBytes
                LD A, @ArchiveEngineConst.SceneHeadPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD HL, @ArchiveEngineConst.ScenePixels
                LD DE, @ArchiveEngineConst.ScreenBitmap
                LDIR

                ; расчёт начала второй части из конечного адреса первой и шага строки
                EX DE, HL
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC
                LD H, HIGH(@ArchiveEngineConst.ScreenBitmap)
                EX DE, HL
                ; перенос остатка и дополнительной строки во вторую страницу
                LD A, @ArchiveEngineConst.SceneTailPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD BC, @ArchiveEngineConst.SceneTailBytes
                LDIR
                RET

                endmodule
                endmodule
