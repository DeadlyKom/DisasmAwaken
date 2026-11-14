                module ArchiveEngine
                module DrawFighter
                ; Документация [кадры и маски бойцов](../../Docs/FighterAssets.md#наложение-кадра)
                ; -----------------------------------------
                ; наложение текущего кадра бойца на рабочий растр сцены
                ; In:
                ;   IX - запись бойца с адресами, размерами, страницей и ориентацией
                ;   FrameWidth и FrameHeight ненулевые, таблица зеркальных битов построена
                ; Out:
                ;   текущий прямоугольник наложен, его размеры, адрес, Y и сторона сохранены для восстановления
                ;   выбрана страница масок текущего кадра
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', банковое окно
                ; Note:
                ;   прямой путь использует только основные пары HL, DE, BC и оба AF
                ;   при зеркальном выводе источник остаётся в альтернативном HL после EXX
                ; -----------------------------------------
                ; выбор страницы масок и проверка направления вывода
Entry:          LD A, (IX + @FArchiveEngineFighter.SpriteBank)
                CALL @ArchiveEngine.SelectSpritePage.Entry
                LD A, (IX + @FArchiveEngineFighter.Side)
                LD (IX + @FArchiveEngineFighter.PreviousMirror), A
                OR A
                JR Z, @ArchiveEngine.DrawFighter.Direct                         ; переход, если сторона прямая, рисовать слева направо

                ; настройка указателя пар и старшего байта таблицы обращения битов
                LD A, (IX + @FArchiveEngineFighter.FrameSource.Low)
                LD L, A
                LD A, (IX + @FArchiveEngineFighter.FrameSource.High)
                LD H, A
                LD D, HIGH(@ArchiveEngineConst.MirrorTable)
                EXX

                ; сохранение параметров прямоугольника, у зеркальной стороны адрес у правого края
                LD A, (IX + @FArchiveEngineFighter.FrameDest.Low)
                LD L, A
                LD (IX + @FArchiveEngineFighter.PreviousAddress.Low), A
                LD A, (IX + @FArchiveEngineFighter.FrameDest.High)
                LD H, A
                LD (IX + @FArchiveEngineFighter.PreviousAddress.High), A
                LD A, (IX + @FArchiveEngineFighter.DrawY)
                LD (IX + @FArchiveEngineFighter.PreviousY), A
                LD A, (IX + @FArchiveEngineFighter.FrameWidth)
                LD (IX + @FArchiveEngineFighter.PreviousWidth), A
                LD A, (IX + @FArchiveEngineFighter.FrameHeight)
                LD (IX + @FArchiveEngineFighter.PreviousHeight), A

                ; наложение зеркальной строки, источник и таблица видны после EXX
MirrorRow:      EX AF, AF'
                LD B, (IX + @FArchiveEngineFighter.FrameWidth)
MirrorByte:     LD A, (HL)
                EXX
                LD C, A
                LD E, (HL)
                INC HL
                LD A, (DE)
                AND C
                LD C, A
                LD E, (HL)
                INC HL
                LD A, (DE)
                OR C
                EXX
                LD (HL), A
                DEC HL
                DJNZ @ArchiveEngine.DrawFighter.MirrorByte

                ; возврат к правому краю следующей строки, указатель ушёл влево на ширину
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC
                LD C, (IX + @FArchiveEngineFighter.FrameWidth)
                LD B, #00
                ADD HL, BC
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.DrawFighter.MirrorRow                     ; переход, если остались строки зеркального кадра

                RET

                ; подготовка прямого вывода и сохранение прежнего адреса у левого края
Direct:         LD E, (IX + @FArchiveEngineFighter.FrameSource.Low)
                LD D, (IX + @FArchiveEngineFighter.FrameSource.High)
                LD A, (IX + @FArchiveEngineFighter.FrameDest.Low)
                LD (IX + @FArchiveEngineFighter.PreviousAddress.Low), A
                LD L, A
                LD A, (IX + @FArchiveEngineFighter.FrameDest.High)
                LD (IX + @FArchiveEngineFighter.PreviousAddress.High), A
                LD H, A
                EX DE, HL
                LD A, (IX + @FArchiveEngineFighter.DrawY)
                LD (IX + @FArchiveEngineFighter.PreviousY), A
                LD A, (IX + @FArchiveEngineFighter.FrameWidth)
                LD (IX + @FArchiveEngineFighter.PreviousWidth), A
                LD A, (IX + @FArchiveEngineFighter.FrameHeight)
                LD (IX + @FArchiveEngineFighter.PreviousHeight), A

                ; чтение пар маска и рисунок и продвижение слева направо
DirectRow:      EX AF, AF'
                LD B, (IX + @FArchiveEngineFighter.FrameWidth)
DirectByte:     LD A, (DE)
                AND (HL)
                INC HL
                OR (HL)
                INC HL
                LD (DE), A
                INC DE
                DJNZ @ArchiveEngine.DrawFighter.DirectByte

                ; продвижение назначения через остаток строки без изменения источника
                EX DE, HL
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                ADD HL, BC
                LD C, (IX + @FArchiveEngineFighter.FrameWidth)
                LD B, #00
                OR A
                SBC HL, BC
                EX DE, HL
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.DrawFighter.DirectRow                     ; переход, если остались строки прямого кадра

                RET

                endmodule
                endmodule
