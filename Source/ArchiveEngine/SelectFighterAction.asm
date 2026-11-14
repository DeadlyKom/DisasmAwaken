                module ArchiveEngine
                module SelectFighterAction
                ; Документация [клавиши и выбор действия](../../Docs/FighterAssets.md#клавиши-и-выбор-действия)
                ; -----------------------------------------
                ; потребление накопленного ввода и выбор первого подходящего правила текущего действия
                ; In:
                ;   IX - запись бойца, Request в диапазоне 0..35, таблица Rules доступна
                ; Out:
                ;   оба накопителя обнулены, совпавшее правило заменяет Request
                ;   неизменившийся набор дополнительных клавиш передаётся правилам как нулевой
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; -----------------------------------------
                ; чтение таблицы и накопителей, проверка повторного набора дополнительных клавиш
Entry:          LD E, (IX + @FArchiveEngineFighter.Rules.Low)
                LD D, (IX + @FArchiveEngineFighter.Rules.High)
                LD C, (IX + @FArchiveEngineFighter.PrimaryBits)
                LD B, (IX + @FArchiveEngineFighter.ExtraBits)
                LD A, (IX + @FArchiveEngineFighter.PreviousExtra)
                CP B
                JR NZ, @ArchiveEngine.SelectFighterAction.Remember              ; переход, если набор дополнительных клавиш изменился, сохранить его

                XOR A
                LD (IX + @FArchiveEngineFighter.ExtraBits), A
                LD B, A
                JR @ArchiveEngine.SelectFighterAction.Clear

Remember:       LD (IX + @FArchiveEngineFighter.PreviousExtra), B

                ; очистка обоих накопителей после передачи значений в регистры
Clear:          XOR A
                LD (IX + @FArchiveEngineFighter.PrimaryBits), A
                LD (IX + @FArchiveEngineFighter.ExtraBits), A

                ; чтение указателя блока по текущему запросу и проверка числа правил
                LD A, (IX + @FArchiveEngineFighter.Request)
                LD L, A
                LD H, #00
                ADD HL, HL
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                LD H, D
                LD L, E
                LD A, (HL)
                OR A
                RET Z                                                           ; выход, если у действия нет правил

                INC HL

                ; проверка совпадения маски и ожидаемого значения основной группы
CheckRule:      EX AF, AF'
                LD A, C
                AND (HL)
                INC HL
                XOR (HL)
                JR NZ, @ArchiveEngine.SelectFighterAction.NextRule              ; переход, если основная группа не совпала, пропустить правило

                ; проверка дополнительной группы для прошедшего первое сравнение правила
                INC HL
                LD A, B
                AND (HL)
                INC HL
                XOR (HL)
                JR Z, @ArchiveEngine.SelectFighterAction.Match                  ; переход, если обе группы совпали, применить правило

                ; возврат к одинаковой позиции внутри записи перед переходом к следующей
                DEC HL
                DEC HL
NextRule:       INC HL
                INC HL
                INC HL
                INC HL
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.SelectFighterAction.CheckRule             ; переход, если остались непроверенные правила

                RET

                ; замена запроса номером действия из совпавшей записи
Match:          INC HL
                LD A, (HL)
                LD (IX + @FArchiveEngineFighter.Request), A
                RET

                endmodule
                endmodule
