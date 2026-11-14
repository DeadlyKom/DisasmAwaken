                module ArchiveEngine
                module RestoreFighterBackground
                ; Документация [восстановление прямоугольника](../../Docs/Scene1PixelPairs.md#восстановление-фона-под-бойцом)
                ; -----------------------------------------
                ; копирование исходного фона поверх предыдущего прямоугольника бойца
                ; In:
                ;   IX - запись с предыдущими адресом, шириной, высотой, ориентацией и Y
                ;   прямоугольник в пределах сцены, начальная строка 0..178, ширина и высота ненулевые
                ;   фон уже разделён на страницы 13 и 14, селектор настроен
                ; Out:
                ;   прямоугольник в рабочем растре восстановлен, выбрана страница последней строки
                ;   LastRow содержит исключённую границу строк
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', банковое окно
                ; Note:
                ;   переключение происходит только при равенстве строки 178, отдельный старт со строки 179 этим входом не покрывается
                ; -----------------------------------------
                ; выбор первой страницы и загрузка прежнего адреса назначения
Entry:          LD A, @ArchiveEngineConst.SceneHeadPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD E, (IX + @FArchiveEngineFighter.PreviousAddress.Low)
                LD D, (IX + @FArchiveEngineFighter.PreviousAddress.High)

                ; проверка ориентации, у зеркального кадра адрес хранится у правого края
                LD A, (IX + @FArchiveEngineFighter.PreviousMirror)
                OR A
                JR Z, @ArchiveEngine.RestoreFighterBackground.MapSource         ; переход, если адрес уже у левого края

                ; перевод адреса к левому краю по ширине прежнего кадра
                LD C, (IX + @FArchiveEngineFighter.PreviousWidth)
                LD B, #00
                DEC C
                EX DE, HL
                OR A
                SBC HL, BC
                LD D, H
                LD E, L

                ; расчёт адреса копии фона по смещению внутри рабочего растра
MapSource:      LD L, E
                LD A, @ArchiveEngineConst.ScenePageDelta
                ADD A, D
                LD H, A

                ; вычисление первой и исключённой последней строк прямоугольника
                LD A, (IX + @FArchiveEngineFighter.PreviousY)
                LD C, A
                LD A, (@ArchiveEngineScene.View.SpriteYBias)
                ADD A, C
                LD C, A
                LD A, (IX + @FArchiveEngineFighter.PreviousHeight)
                ADD A, C
                LD (@ArchiveEngine.RestoreFighterBackground.LastRow + 1), A
                LD A, C

                ; проверка перехода к первой строке второй страницы фона
CheckPage:      CP @ArchiveEngineConst.SceneSplitRow
                CALL Z, @ArchiveEngine.SwitchSceneTail.Entry                    ; вызов, если текущая строка равна 178

                ; перенос видимых байтов строки с сохранением индекса строки в AF'
                EX AF, AF'
                LD B, (IX + @FArchiveEngineFighter.PreviousWidth)
                LD C, #FF
CopyByte:       LDI
                DJNZ @ArchiveEngine.RestoreFighterBackground.CopyByte

                ; продвижение обоих адресов через неперенесённый остаток строки
                LD A, (@ArchiveEngineScene.View.RowBytes)
                SUB (IX + @FArchiveEngineFighter.PreviousWidth)
                LD C, A
                LD B, #00
                EX DE, HL
                ADD HL, BC
                EX DE, HL
                ADD HL, BC

                ; проверка исключённой границы после увеличения номера строки
                EX AF, AF'
                INC A
LastRow:        CP #00                                                          ; исходный ноль, граница записывается на входе
                JR C, @ArchiveEngine.RestoreFighterBackground.CheckPage         ; переход, если остались строки прямоугольника

                RET

                endmodule
                endmodule
