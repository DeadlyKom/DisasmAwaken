                module ArchiveEngine
                module SwitchSceneTail
                ; Документация [восстановление прямоугольника](../../Docs/Scene1PixelPairs.md#восстановление-фона-под-бойцом)
                ; -----------------------------------------
                ; перевод указателя копии фона с первой страницы на начало второй
                ; In:
                ;   HL - указатель строки 178 в продолжении первой страницы
                ; Out:
                ;   HL - #C054 плюс прежний горизонтальный отступ, выбрана страница 14
                ;   AF сохранён
                ; Corrupt:
                ;   HL, BC, AF', банковое окно
                ; -----------------------------------------
                ; пересчёт адреса источника и выбор второй страницы фона
Entry:          EX AF, AF'
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC
                LD H, HIGH(@ArchiveEngineConst.ScreenBitmap)
                LD A, @ArchiveEngineConst.SceneTailPage
                CALL @ArchiveEngine.SelectPage.Entry
                EX AF, AF'
                RET

                endmodule
                endmodule
