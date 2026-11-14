                module ArchiveEngine
                module PollFighterKeys
                ; Документация [клавиши и выбор действия](../../Docs/FighterAssets.md#клавиши-и-выбор-действия)
                ; -----------------------------------------
                ; преобразование девяти клавиш в биты двух накопителей бойца
                ; In:
                ;   IX - запись бойца, Side выбирает раскладку основной группы
                ; Out:
                ;   PrimaryBits и ExtraBits содержат прежние биты и новые нажатия
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; -----------------------------------------
                ; проверка стороны и выбор первой строки раскладки
Entry:          LD HL, @FArchiveEngineFighter.Primary0
                LD A, (IX + @FArchiveEngineFighter.Side)
                OR A
                JR Z, @ArchiveEngine.PollFighterKeys.Primary                    ; переход, если сторона прямая, оставить исходный порядок клавиш

                LD HL, @FArchiveEngineFighter.Mirror0
Primary:        LD D, IXH
                LD E, IXL
                ADD HL, DE
                LD A, @ArchiveEngineConst.PrimaryKeyCount
                LD E, #01

                ; чтение порта основной клавиши и проверка её активного нуля
PrimaryKey:     EX AF, AF'
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                IN A, (C)
                AND (HL)
                INC HL
                JR NZ, @ArchiveEngine.PollFighterKeys.NextPrimary               ; переход, если основная клавиша отпущена, пропустить запись бита

                LD A, E
                OR (IX + @FArchiveEngineFighter.PrimaryBits)
                LD (IX + @FArchiveEngineFighter.PrimaryBits), A
NextPrimary:    SLA E
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.PollFighterKeys.PrimaryKey                ; переход, если остались основные клавиши

                ; дополнительная группа использует одну раскладку для обеих сторон
                LD HL, @FArchiveEngineFighter.Extra0
                LD D, IXH
                LD E, IXL
                ADD HL, DE
                LD A, @ArchiveEngineConst.ExtraKeyCount
                LD E, #01

                ; чтение дополнительной клавиши и проверка её активного нуля
ExtraKey:       EX AF, AF'
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                IN A, (C)
                AND (HL)
                INC HL
                JR NZ, @ArchiveEngine.PollFighterKeys.NextExtra                 ; переход, если дополнительная клавиша отпущена, пропустить запись бита

                LD A, E
                OR (IX + @FArchiveEngineFighter.ExtraBits)
                LD (IX + @FArchiveEngineFighter.ExtraBits), A
NextExtra:      SLA E
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.PollFighterKeys.ExtraKey                  ; переход, если остались дополнительные клавиши

                RET

                endmodule
                endmodule
