                module Action
                module SpawnAlternate
                ; Изменяемые поля записи [общие параметры обоих создателей](../../Docs/ActionSpawnRecordFinish.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionSpawnSchedule.md)
                ; -----------------------------------------
                ; Создание записей по шаблону либо по альтернативной ветке планировщика
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #1A96..#1D02
                ; In:
                ;   Entry читает признаки #9B82/#9B83, координаты и зерно из общего состояния
                ;   CheckDistance принимает слово потока 0 в HL, SetCountdown принимает счётчик в A и младший байт сохранённого слова в E
                ;   доступны список FActionRecord, оригинальные шаблоны, банки 0, 1, 3 и 4, порт 7FFD разблокирован
                ; Out:
                ;   Entry создаёт записи класса #12 по строкам шаблона либо проверяет сохранённое слово
                ;   CheckDistance выбирает Entry, возврат или альтернативное создание, SetCountdown сохраняет счётчик и выбирает параметры альтернативной записи
                ;   BuildRandom при успехе передаёт IX на FinishSpawnRecord.ReadHeader, при отсутствии записи возвращается
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, рабочие записи, операнды кода, состояния потоков, 7FFD
                ; Note:
                ;   при входе в шаблонный цикл EXX выполняется на каждой успешной аллокации, поиск перед обменом заменяет DE на #0040
                ;   при переполнении помечается запись, первые две суммы успевают записаться, дальнейшие строки не обрабатываются
                ;   модели сравнивают четыре раздельных участка, полный выход регистров после диспетчера, IRQ и нативный игровой запуск не проверены
                ; -----------------------------------------
                ; Проверка #9B83 перед выбором шаблона.
Entry:          LD A, (#9B83)
                AND A
                JP NZ, @Action.SpawnAlternate.CheckSavedWord                    ; переход, если #9B83 ненулевой, шаблон не читать

                LD BC, (#9B7E)
                LD DE, (#9B7B)
                LD HL, (#9B78)
                LD A, #01
                LD (#9B83), A
                LD (#9B82), A
                EXX
                LD A, #10
                LD (#792E), A
                LD HL, (#9BC1)
                LD DE, (#9BC3)
                LD A, (#9BC5)
                EX AF, AF'
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                CALL @Controls.BuildSeededIndices.Entry
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                DEC L
                LD H, #00
                ADD HL, HL
                LD DE, @ActionSpawnTemplates.Seed00
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD IXL, A
                LD A, (HL)
                LD IXH, A
                ; Поиск записи для очередной восьмибайтовой строки шаблона.
NextTemplate:   CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск дошёл до маркера конца

                EXX
                PUSH HL
                PUSH DE
                PUSH BC
                PUSH BC
                LD C, (IX + @FSpawnTemplateRow.Delta0)
                LD B, (IX + @FSpawnTemplateRow.Delta0 + 1)
                XOR A
                INC A
                ADC HL, BC
                JP PO, @Action.SpawnAlternate.StoreFirst                        ; переход, если первая знаковая сумма не переполнилась

                XOR A
StoreFirst:     LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                EX DE, HL
                LD C, (IX + @FSpawnTemplateRow.Delta1)
                LD B, (IX + @FSpawnTemplateRow.Delta1 + 1)
                OR A
                ADC HL, BC
                JP PO, @Action.SpawnAlternate.StoreSecond                       ; переход, если вторая знаковая сумма не переполнилась

                XOR A
StoreSecond:    LD (IY + @FActionRecord.Components.Component1.Low), L
                LD (IY + @FActionRecord.Components.Component1.High), H
                POP HL
                LD C, (IX + @FSpawnTemplateRow.Delta2)
                LD B, (IX + @FSpawnTemplateRow.Delta2 + 1)
                OR A
                ADC HL, BC
                JP PO, @Action.SpawnAlternate.CheckOverflow                     ; переход, если третья знаковая сумма не переполнилась

                XOR A
CheckOverflow:  OR A
                JR Z, @Action.SpawnAlternate.ReleaseRecord                      ; переход, если хотя бы одна знаковая сумма переполнилась

                LD (IY + @FActionRecord.Components.Component2.Low), L
                LD (IY + @FActionRecord.Components.Component2.High), H
                LD A, (IX + @FSpawnTemplateRow.ModelOffset)
                LD (IY + @FActionRecord.ModelOffset), A
                LD A, (IX + @FSpawnTemplateRow.OffsetPhase1)
                LD (IY + @FActionRecord.OffsetPhase1), A
                XOR A
                LD (IY + @FActionRecord.OffsetPhase0), A
                LD (IY + @FActionRecord.OffsetPhase2), A
                LD (IY + @FActionRecord.StateCode), #09
                LD (IY + @FActionRecord.LinkedIndex), A
                LD (IY + @FActionRecord.LinkFlags), A
                LD (IY + @FActionRecord.Unknown0D), A
                LD (IY + @FActionRecord.TargetIndex), A
                LD (IY + @FActionRecord.Unknown10), A
                LD (IY + @FActionRecord.Unknown11), A
                LD (IY + @FActionRecord.Unknown10), A
                LD (IY + @FActionRecord.ClassCode), #12
                LD (IY + @FActionRecord.Unknown13), #FF
                LD (IY + @FActionRecord.Unknown14), #FF
                LD (IY + @FActionRecord.LinkOverride), #FF
                LD (IY + @FActionRecord.SavedStateCode), A
                LD (IY + @FActionRecord.PhaseMoveTimer), A
                LD (IY + @FActionRecord.ReuseByte), #10
                LD (#792E), A
                LD (IY + @FActionRecord.Unknown24), A
                LD BC, FSpawnTemplateRow
                ADD IX, BC
                LD A, (IX + @FSpawnTemplateEnd.EndCode)
                CP #80
RestorePairs:   POP BC
                POP DE
                POP HL
                RET Z                                                           ; выход, если обнаружен конец шаблона либо запись помечена после переполнения

                JP @Action.SpawnAlternate.NextTemplate

                ; Пометка записи после переполнения одной из знаковых сумм.
ReleaseRecord:  CALL @Action.MarkIYRecordForReuse.Entry
                JR @Action.SpawnAlternate.RestorePairs

                ; Сохранение слова потока 0 и проверка трёх знаковых расстояний.
CheckDistance:  LD (#799C), HL
                LD HL, (#9B79)
                LD A, H
                OR A
                JP P, @Action.SpawnAlternate.FirstAbs                           ; переход, если первое слово неотрицательно

                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
FirstAbs:       LD B, L
                LD C, A
                LD HL, (#9B7C)
                LD A, H
                OR A
                JP P, @Action.SpawnAlternate.SecondAbs                          ; переход, если второе слово неотрицательно

                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
SecondAbs:      LD E, L
                OR C
                LD C, A
                LD HL, (#9B7F)
                LD A, H
                OR A
                JP P, @Action.SpawnAlternate.CheckMagnitudes                    ; переход, если третье слово неотрицательно

                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
CheckMagnitudes:OR C
                JR NZ, @Action.SpawnAlternate.CheckStream                       ; переход, если старший байт хотя бы одного модуля ненулевой

                LD A, L
                CP #70
                JR NC, @Action.SpawnAlternate.CheckStream                       ; переход, если третий модуль не меньше #70

                LD A, E
                CP #70
                JR NC, @Action.SpawnAlternate.CheckStream                       ; переход, если второй модуль не меньше #70

                LD A, B
                CP #70
                JR NC, @Action.SpawnAlternate.CheckStream                       ; переход, если первый модуль не меньше #70

                JP @Action.SpawnAlternate.Entry

                ; Проверка совпадения байтов следующего слова потока 1.
CheckStream:    CALL @Action.NextRandomWord1.Entry
                LD A, H
                XOR L
                RET NZ                                                          ; выход, если байты слова потока 1 различаются

                ; Проверка старшего байта 23 и изменяемого нижнего предела SavedLowLimit.
CheckSavedWord: LD DE, #0000
                LD A, D
                CP #23
                RET NZ                                                          ; выход, если старший байт сохранённого слова отличается от #23

                LD A, E
                CP #F2
                RET C                                                           ; выход, если младший байт сохранённого слова меньше текущего SavedLowLimit

                LD A, #FF
                ; Обновление счётчика и при отрицательном входе двух операндов модели и класса.
SetCountdown:   LD (#7B61), A
                AND A
                JP P, @Action.SpawnAlternate.BuildRandom                        ; переход, если входной счётчик неотрицателен, параметры оставить прежними

                LD A, E
                AND #03
                ADD A, #05
                LD (#7B61), A
                LD A, R
                RRA
                LD A, #20
                JR C, @Action.SpawnAlternate.StoreModelBias                     ; переход, если считанный младший бит R установлен, сохранить прибавку #20

                LD A, #00
StoreModelBias: LD (#79DE), A
                LD A, #06
                JR C, @Action.SpawnAlternate.StoreClass                         ; переход, если считанный младший бит R установлен, сохранить класс 6

                LD A, #00
StoreClass:     LD (#7A6A), A
                ; Поиск свободной записи для альтернативного объекта.
BuildRandom:    CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск свободной записи дошёл до маркера конца

                PUSH IY
                POP IX
                CALL @Action.NextRandomWord7.Entry
                LD A, L
                XOR H
                AND #1C
                OR #40
                ADD A, #00
                LD (IX + @FActionRecord.ModelOffset), A
                LD L, A
                LD (IX + @FActionRecord.TargetIndex), #64
                LD A, L
                CALL @Action.ReadObjectHeaderWord.Entry
                LD A, H
                PUSH AF
                CALL @Action.NextRandomWord4.Entry
                SRA H
                RR L
                LD (IX + @FActionRecord.Components.Component2.Low), L
                LD (IX + @FActionRecord.Components.Component2.High), H
                PUSH HL
                CALL @Action.NextRandomWord4.Entry
                SRA H
                RR L
                LD (IX + @FActionRecord.Components.Component1.Low), L
                LD (IX + @FActionRecord.Components.Component1.High), H
                PUSH HL
                CALL @Action.NextRandomWord4.Entry
                SRA H
                RR L
                LD (IX + @FActionRecord.Components.Component0.Low), L
                LD (IX + @FActionRecord.Components.Component0.High), H
                POP DE
                POP BC
                POP AF
                EX AF, AF'
                LD A, #1A
                EXX
                LD HL, @Voxel.CreateSmallEffect.Entry
                CALL @Action.DispatchBank3Callback.Entry
                LD A, #01
                LD (#6D39), A
                LD A, (#6D3D)
                CP #1A
                JR NC, @Action.SpawnAlternate.SetOffsets                        ; переход, если остаток кадров обхода не меньше 26

                LD A, #1A
                LD (#6D3D), A
                ; Расчёт начальных смещений по потокам 9 и 10.
SetOffsets:     LD (IX + @FActionRecord.OffsetPhase0), #00
                CALL @Action.NextRandomWord9.Entry
                LD A, L
                AND #03
                BIT 7, L
                JR Z, @Action.SpawnAlternate.StoreOffset                        ; переход, если бит 7 младшего байта потока 9 сброшен, смещение не отрицать

                NEG
StoreOffset:    ADD A, H
                LD (IX + @FActionRecord.OffsetPhase1), A
                CALL @Action.NextRandomWord10.Entry
                LD A, L
                AND #1F
                LD (IX + @FActionRecord.OffsetPhase2), A
                CALL @Action.NextRandomWord12.Entry
                LD A, L
                AND #55
                LD L, A
                LD A, H
                AND #2A
                AND L
                LD L, A
                LD A, (@ActionApplyParametersState.SpawnField11)
                OR L
                LD (IX + @FActionRecord.Unknown11), A
                CALL @Action.NextRandomWord2.Entry
                LD (IX + @FActionRecord.ClassCode), #00
                LD (IX + @FActionRecord.LinkFlags), #00
                LD (IX + @FActionRecord.Unknown14), #00
                LD (IX + @FActionRecord.LinkOverride), #FF
                LD (IX + @FActionRecord.LinkedIndex), #FF
                LD HL, (#EBDB)
                LD (IX + @FActionRecord.Unknown0D), L
                LD (IX + @FActionRecord.Unknown0E), H
                CALL @Action.NextRandomWord13.Entry
                LD A, (@ActionApplyParametersState.SpawnValueMask)
                OR L
                LD L, A
                LD A, (@ActionApplyParametersState.SpawnValueCap)
                LD H, A
                LD A, L
                CP H
                JR C, @Action.SpawnAlternate.StoreLimit                         ; переход, если кандидат для поля #13 меньше верхнего предела

                LD A, H
                DEC A
StoreLimit:     LD (IX + @FActionRecord.Unknown13), A
                LD (IX + @FActionRecord.Unknown10), #20
                XOR A
                LD (IX + @FActionRecord.Unknown24), A
                LD (IX + @FActionRecord.PhaseMoveTimer), A
                LD (IX + @FActionRecord.Unknown20), #FF
                LD (IX + @FActionRecord.Unknown21), #FF
                LD (#EBDD), A
                CALL @Action.NextRandomWord3.Entry
                LD A, (IX + @FActionRecord.StateCode)
                LD (IX + @FActionRecord.SavedStateCode), A
                LD A, R
                AND #0F
                INC A
                AND #0F
                LD B, A
                LD (IX + @FActionRecord.ReuseByte), B
                JP @Action.FinishSpawnRecord.ReadHeader

                endmodule
                endmodule
