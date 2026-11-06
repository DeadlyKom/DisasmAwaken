                module Action
                module UpdateBodyMotion
                ; Документация [алгоритм и проверка](../../Docs/ActionWideMotionPrefix.md)
                ; -----------------------------------------
                ; Фазовое обновление рабочего вектора, запросов панели и широких целей
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #09BD..#0BB9
                ; In:
                ;   PhaseWord и FirstMode задают фазу обработки тела, активные слова смещения и рабочий вектор доступны
                ;   SeedIndex задаёт число широких записей, для всех указанных записей доступна RAM
                ;   выбран банк 0, стек доступен для генератора и поиска, IRQ не вмешиваются
                ; Out:
                ;   чётная фаза пропускает обработку тела, нечётная выбирает обработку по FirstMode
                ;   последовательное вычитание может частично изменить вектор до перехода на TransitionBodyMode
                ;   после оценки вектора изменяются запросы панели и порог либо счётчик, по достигнутому пути
                ;   MoveWideVectors смещает широкие записи и обновляет вторую пару операндов индикатора
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, фазовые операнды, векторы, панель, состояние потока и временные слова стека
                ; Note:
                ;   формулы и граничные проверки всех участков приведены в документации
                ;   сквозной вход проверен при нулевом широком списке, хвост широкого списка отдельно при длине от нуля до шести
                ; -----------------------------------------
                ; Расчёт очередной фазы из изменяемого слова.
Entry:          LD HL, #8000
                SRL H
                RR L
                LD (@ActionBodyMotionState.PhaseWord), HL
                JP NC, @Action.UpdateBodyMotion.MoveWideVectors                 ; переход, если исходная фаза чётная, обработать только широкий список

                RR H
                LD (@ActionBodyMotionState.PhaseWord), HL
                LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                DEC A
                JR Z, @Action.TransitionBodyMode.CheckRandom                    ; переход, если режим 1 ожидает случайного слова

                DEC A
                JR Z, @Action.TransitionBodyMode.LowerWords                     ; переход, если режим 2 требует предварительного уменьшения старших слов

                ; Вычитание знакового смещения из первой 24-битной компоненты.
SubtractMotion: LD HL, (@ActionTransformWorkVector.Value.Component0.LowWord)
                LD A, (@ActionTransformWorkVector.Value.Component0.High)
                LD DE, (#E5B3)
                BIT 7, D
                LD C, #00
                JR Z, @Action.UpdateBodyMotion.SubtractX                        ; переход, если смещение X неотрицательно и его знаковое расширение равно нулю

                DEC C
SubtractX:      OR A
                SBC HL, DE
                LD (@ActionTransformWorkVector.Value.Component0.LowWord), HL
                SBC A, C
                JP PE, @Action.TransitionBodyMode.Entry                         ; переход, если первая компонента переполнилась после записи младшего слова

                LD (@ActionTransformWorkVector.Value.Component0.High), A
                ; Вычитание смещения из второй компоненты.
                LD HL, (@ActionTransformWorkVector.Value.Component1.LowWord)
                LD A, (@ActionTransformWorkVector.Value.Component1.High)
                LD DE, (#E5D2)
                BIT 7, D
                LD C, #00
                JR Z, @Action.UpdateBodyMotion.SubtractY                        ; переход, если смещение Y неотрицательно и его знаковое расширение равно нулю

                DEC C
SubtractY:      OR A
                SBC HL, DE
                LD (@ActionTransformWorkVector.Value.Component1.LowWord), HL
                SBC A, C
                JP PE, @Action.TransitionBodyMode.Entry                         ; переход, если вторая компонента переполнилась после записи младшего слова

                LD (@ActionTransformWorkVector.Value.Component1.High), A
                ; Вычитание смещения из третьей компоненты.
                LD HL, (@ActionTransformWorkVector.Value.Component2.LowWord)
                LD DE, (#E5ED)
                LD A, (@ActionTransformWorkVector.Value.Component2.High)
                BIT 7, D
                LD C, #00
                JR Z, @Action.UpdateBodyMotion.SubtractDepth                    ; переход, если смещение глубины неотрицательно и его знаковое расширение равно нулю

                DEC C
SubtractDepth:  OR A
                SBC HL, DE
                LD (@ActionTransformWorkVector.Value.Component2.LowWord), HL
                SBC A, C
                JP PE, @Action.TransitionBodyMode.Entry                         ; переход, если третья компонента переполнилась после записи младшего слова

                LD (@ActionTransformWorkVector.Value.Component2.High), A
                ; Оценка свёрнутых старших байтов для выбора ветки панели.
                CALL @Action.MaxFoldedVectorHigh.Entry
                LD A, L
                AND A
                JR NZ, @Action.UpdateBodyMotion.ClearGauge                      ; переход, если максимум свёрнутых старших байтов ненулевой

                ; Расчёт трёх модулей средних байтов и их максимума.
                LD HL, (@ActionTransformWorkVector.Value.Component0.LowWord + 1)
                BIT 7, H
                LD A, L
                JR Z, @Action.UpdateBodyMotion.SaveMidX                         ; переход, если первая компонента неотрицательна

                NEG
SaveMidX:       LD E, A
                LD HL, (@ActionTransformWorkVector.Value.Component1.LowWord + 1)
                BIT 7, H
                LD A, L
                JR Z, @Action.UpdateBodyMotion.CompareMidY                      ; переход, если вторая компонента неотрицательна

                NEG
CompareMidY:    CP E
                JR C, @Action.UpdateBodyMotion.ReadMidDepth                     ; переход, если модуль среднего байта Y меньше текущего максимума

                LD E, A
ReadMidDepth:   LD HL, (@ActionTransformWorkVector.Value.Component2.LowWord + 1)
                BIT 7, H
                LD A, L
                JR Z, @Action.UpdateBodyMotion.CompareMidDepth                  ; переход, если третья компонента неотрицательна

                NEG
CompareMidDepth:CP E
                JR C, @Action.UpdateBodyMotion.ScaleGauge                       ; переход, если модуль среднего байта глубины меньше текущего максимума

                LD E, A
                ; Преобразование максимума в значение четвёртой шкалы.
ScaleGauge:     LD A, E
                NEG
                SRL A
                CP #2F
                JR C, @Action.UpdateBodyMotion.SaveGauge                        ; переход, если значение шкалы меньше #2F

                LD A, #2E
SaveGauge:      LD (#6682), A
                LD A, #01
                LD (#667D), A
                ; Проверка блокировки пополнения счётчика.
                LD A, (#9C29)
                INC A
                RET Z                                                           ; выход, если байт блокировки равен #FF

                ; Вращение фазы пополнения и проверка её младшего бита.
                LD A, #80
                RRCA
                LD (#683C), A
                JP NC, @Action.UpdateBodyMotion.MoveWideVectors                 ; переход, если прежний младший бит фазы пополнения равен нулю

                ; Выбор байта и проверка кандидата счётчика относительно лимита.
                CALL @Action.SelectPreferredByte.Entry
                INC A
                LD C, A
                LD DE, (#9BD2)
                INC E
                LD A, D
                CP E
                JR C, @Action.UpdateBodyMotion.RequestGauge                     ; переход, если кандидат счётчика превышает лимит

                LD (#9BD2), DE
                LD (HL), C
RequestGauge:   LD A, #01
                LD (#665C), A
                JP @Action.UpdateBodyMotion.MoveWideVectors

                ; Сброс значения четвёртой шкалы с запросом перерисовки.
ClearGauge:     LD A, (#6682)
                AND A
                JR Z, @Action.UpdateBodyMotion.CheckBias                        ; переход, если прежнее значение четвёртой шкалы равно нулю

                LD (#667D), A
                XOR A
                LD (#6682), A
                ; Проверка порога пересчёта Compare06A.
CheckBias:      LD A, L
                CP #1C
                JR C, @Action.UpdateBodyMotion.CheckMode                        ; переход, если максимум ниже #1C и пересчитывать порог не нужно

                SUB #1B
                ADD A, #00
                JR NC, @Action.UpdateBodyMotion.SaveBias                        ; переход, если сумма порога с поправкой помещается в байт

                LD A, #FF
SaveBias:       LD (@ActionApplyParametersState.Compare06A), A
                ; Проверка необходимости смены режима тела.
CheckMode:      LD A, L
                CP #40
                JP C, @Action.UpdateBodyMotion.MoveWideVectors                  ; переход, если максимум ниже #40

                LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                CP #02
                JP NZ, @Action.TransitionBodyMode.Entry                         ; переход, если режим отличается от 2 и максимум требует перехода

                ; Проверка длины списка широких векторов.
MoveWideVectors:LD A, #00
                OR A
                RET Z                                                           ; выход, если широкий список пуст

                PUSH AF
                ; Расчёт шага X как знаковой четверти с заменой нуля единицей.
                LD HL, (#E5B3)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.UpdateBodyMotion.StoreStepX                      ; переход, если первый шаг уже ненулевой

                INC L
StoreStepX:     LD (@ActionBodyMotionState.WideStepX), HL
                ; Расчёт шага Y по тому же правилу.
                LD HL, (#E5D2)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.UpdateBodyMotion.StoreStepY                      ; переход, если второй шаг уже ненулевой

                INC L
StoreStepY:     LD (@ActionBodyMotionState.WideStepY), HL
                ; Расчёт шага глубины по тому же правилу.
                LD HL, (#E5ED)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.UpdateBodyMotion.StoreStepDepth                  ; переход, если третий шаг уже ненулевой

                INC L
StoreStepDepth: LD (@ActionBodyMotionState.WideStepDepth), HL
                POP AF
                LD IY, @ActionWideVectors.Vector00
                ; Смещение всех трёх знаковых 32-битных компонент записи.
MoveWideRecord: EX AF, AF'
                LD L, (IY + @FActionWideVector.Component0.Byte0)
                LD H, (IY + @FActionWideVector.Component0.Byte1)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.UpdateBodyMotion.MoveWideX                        ; переход, если шаг X неотрицателен

                DEC BC
MoveWideX:      OR A
                SBC HL, DE
                LD (IY + @FActionWideVector.Component0.Byte0), L
                LD (IY + @FActionWideVector.Component0.Byte1), H
                LD L, (IY + @FActionWideVector.Component0.Byte2)
                LD H, (IY + @FActionWideVector.Component0.Byte3)
                SBC HL, BC
                LD (IY + @FActionWideVector.Component0.Byte2), L
                LD (IY + @FActionWideVector.Component0.Byte3), H
                LD L, (IY + @FActionWideVector.Component1.Byte0)
                LD H, (IY + @FActionWideVector.Component1.Byte1)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.UpdateBodyMotion.MoveWideY                        ; переход, если шаг Y неотрицателен

                DEC BC
MoveWideY:      OR A
                SBC HL, DE
                LD (IY + @FActionWideVector.Component1.Byte0), L
                LD (IY + @FActionWideVector.Component1.Byte1), H
                LD L, (IY + @FActionWideVector.Component1.Byte2)
                LD H, (IY + @FActionWideVector.Component1.Byte3)
                SBC HL, BC
                LD (IY + @FActionWideVector.Component1.Byte2), L
                LD (IY + @FActionWideVector.Component1.Byte3), H
                LD L, (IY + @FActionWideVector.Component2.Byte0)
                LD H, (IY + @FActionWideVector.Component2.Byte1)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.UpdateBodyMotion.MoveWideDepth                    ; переход, если шаг глубины неотрицателен

                DEC BC
MoveWideDepth:  OR A
                SBC HL, DE
                LD (IY + @FActionWideVector.Component2.Byte0), L
                LD (IY + @FActionWideVector.Component2.Byte1), H
                LD L, (IY + @FActionWideVector.Component2.Byte2)
                LD H, (IY + @FActionWideVector.Component2.Byte3)
                SBC HL, BC
                LD (IY + @FActionWideVector.Component2.Byte2), L
                LD (IY + @FActionWideVector.Component2.Byte3), H
                LD BC, #000C
                ADD IY, BC
                EX AF, AF'
                DEC A
                JP NZ, @Action.UpdateBodyMotion.MoveWideRecord                  ; переход, если остались записи для смещения

                ; Поиск близкого вектора после смещения списка.
                CALL @Action.FindFirstNearWideVector.Entry
                LD A, L
                AND A
                JR NZ, @Action.UpdateBodyMotion.ClearWideGauge                  ; переход, если поиск вернул ненулевой байт L

                LD A, H
                NEG
                SRL A
                CP #2F
                JR C, @Action.UpdateBodyMotion.SaveWideGauge                    ; переход, если значение индикатора меньше #2F

                LD A, #2E
SaveWideGauge:  LD (#6693), A
                LD A, #01
                LD (#668E), A
                RET

ClearWideGauge: LD A, (#6693)
                AND A
                JR Z, @Action.UpdateBodyMotion.CompareIndex                     ; переход, если прежнее значение индикатора равно нулю

                LD (#668E), A
                XOR A
                LD (#6693), A
CompareIndex:   LD A, (#9BC5)
                CP E
                RET

                endmodule
                endmodule
