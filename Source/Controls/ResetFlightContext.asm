                module Controls
                module ResetFlightContext
                ; Документация [сброс полётного контекста и активация параметров](../../Docs/ControlsResetFlightContext.md)
                ; -----------------------------------------
                ; Сброс рабочих векторов, списков объектов и эффектов и перенос ключа перед активацией параметров
                ; исходная запись 23, исходное окно CONTROL банка 1, адреса DD87..DE09
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, доступен HyperDiablo.Value, две таблицы широких векторов и OtherContext
                ;   список объектов с шагом FActionRecord имеет маркер 8080, список эффектов с шагом FVisualEffect имеет отрицательный State
                ;   верхнее окно показывает банк 1, общее ядро ACTION доступно на запись, на CPU-стеке действительный внешний адрес возврата
                ;   для последовательного продолжения действуют договоры BuildAndActivateParameters и незаблокированный paging, IRQ не вмешиваются
                ; Out:
                ;   старшие слова первых двух компонент ActionTransformWorkVector обнулены, третье получает 0200 при HyperDiablo.Value=FF и 1100 иначе
                ;   в ActionWideVectors скопирован один из двух исходных шаблонов, FF выбирает DF91, прочие значения DFD9
                ;   до маркера объектов каждая запись получает Component0=8000 и ReuseByte=FF, до отрицательного маркера эффектов обнуляются State
                ;   OtherContext и SelectedIndex скопированы в ParameterSeeds, по ScheduleSpawn.OpcodeGate записан XOR четырёх байтов ключа AND 7 либо C9 при нуле
                ;   на границе DE0A HL=OtherSecond, DE=OtherFirst, BC=значение опкода, A равен этому же байту, F от AND 07, даже при подстановке C9
                ;   HL', DE', BC', AF' сохранены до DE0A, IX указывает маркер эффектов, IY указывает маркер объектов, SP и банк 1 на этой границе сохранены
                ;   полный выход через BuildAndActivateParameters выбирает банк 0 и снимает первоначальный внешний адрес возврата
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, указанные векторы, записи до маркеров, ParameterSeeds, опкод и состояние дочерней активации
                ; Note:
                ;   исходный контроль окончания списка объектов проверяет полный маркер 8080, текущая запись с любым иным заголовком сбрасывается
                ;   запись в планировщик меняет байт инструкции, его прежний непосредственный операнд не перезаписывается
                ;   2048 сценариев проверили все байты оборудования, восемь результатов свёртки, выбор шаблона и обе границы списков
                ;   регистры префикса сверены кроме R и тактов, все банки и последовательность записей сверены до полного возврата через настоящий дочерний код
                ;   остаточный загрузчик содержит прямой CALL DD87, его перенос в настоящей игре, исполнение подставленного опкода и нативный запуск не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка полётных векторов
                ; Проверка кода оборудования, только FF выбирает исходный набор без гиперсистемы.
Entry:          LD A, (@ActionShipEquipment.HyperDiablo.Value)
                INC A
                LD BC, @ControlsResetFlightConst.NoDiabloWord
                JR Z, @Controls.ResetFlightContext.StoreVector                  ; переход, если HyperDiablo.Value равен FF, сохранить старшее слово 0200

                LD B, @ControlsResetFlightConst.DiabloHigh
                ; Обновление старших слов трёх компонент, младшие байты остаются прежними.
StoreVector:    LD HL, #0000
                LD (@ActionTransformWorkVector.Value.Component2.LowWord + 1), BC
                LD (@ActionTransformWorkVector.Value.Component0.LowWord + 1), HL
                LD (@ActionTransformWorkVector.Value.Component1.LowWord + 1), HL
                ; Выбор одного из двух исходных шаблонов широких векторов по сохранённому Z.
                LD HL, @ControlsVectorsNoDiablo.Vector00
                JR Z, @Controls.ResetFlightContext.CopyVectors                  ; переход, если HyperDiablo.Value равен FF, копировать шаблон DF91

                LD HL, @ControlsVectorsWithDiablo.Vector00
                ; Копирование шести широких векторов в рабочий список.
CopyVectors:    LD DE, @ActionWideVectors.Vector00
                LD BC, @ControlsResetFlightConst.VectorBytes
                LDIR
                ; -----------------------------------------
                ; Освобождение записей объектов
                ; Подготовка позиции перед первой физической записью и размера шага.
                LD IY, @ActionObjectRecords.Record00 - @FActionRecord
                LD DE, @FActionRecord
NextObject:     ADD IY, DE
                ; Проверка обоих байтов маркера 8080 перед сбросом текущей записи.
                LD A, (IY + @FActionRecord.Components.Component0.Low)
                CP @ActionReuseConst.ReusableHigh
                JR NZ, @Controls.ResetFlightContext.ClearObject                 ; переход, если младший байт компоненты отличается от 80, освободить запись

                CP (IY + @FActionRecord.Components.Component0.High)
                JR Z, @Controls.ResetFlightContext.BeginEffects                 ; переход, если оба байта равны 80, закончить обход объектов

                ; Установка заголовка доступной записи и признака однократного пропуска.
ClearObject:    LD (IY + @FActionRecord.Components.Component0.Low), #00
                LD (IY + @FActionRecord.Components.Component0.High), #80
                LD (IY + @FActionRecord.ReuseByte), @ActionReuseConst.SkipOnce
                JR @Controls.ResetFlightContext.NextObject

                ; -----------------------------------------
                ; Освобождение записей эффектов
                ; Выбор позиции до первого эффекта.
BeginEffects:   LD IX, @ActionBankedCallbackState.ContextBase
                LD DE, @FVisualEffect
NextEffect:     ADD IX, DE
                ; Проверка знака полного байта State до очистки текущего эффекта.
                LD A, (IX + @FVisualEffect.State)
                AND A
                JP M, @Controls.ResetFlightContext.CopyContext                  ; переход, если State отрицателен, закончить обход эффектов

                ; Освобождение записи эффекта без изменения остальных полей.
                LD (IX + @FVisualEffect.State), #00
                JR @Controls.ResetFlightContext.NextEffect

                ; -----------------------------------------
                ; Перенос ключа и запись опкода
                ; Копирование двух слов ключа и связанного байта в активный контекст.
CopyContext:    LD HL, (@ActionOtherContext.Value.OtherFirst)
                LD (@ActionParameterSeeds.Value.SeedFirst), HL
                EX DE, HL
                LD HL, (@ActionOtherContext.Value.OtherSecond)
                LD (@ActionParameterSeeds.Value.SeedSecond), HL
                LD A, (@ActionContextIndex.Value.SelectedIndex)
                LD (@ActionParameterSeeds.Value.StepControl), A
                ; Расчёт трёхбитной свёртки четырёх байтов двух слов.
                LD A, L
                XOR H
                XOR E
                XOR D
                AND @ControlsResetFlightConst.FoldMask
                LD C, A
                JR NZ, @Controls.ResetFlightContext.StoreOpcode                 ; переход, если свёртка ненулевая, сохранить её как байт опкода

                LD C, @ControlsResetFlightConst.ZeroFoldOpcode
StoreOpcode:    LD A, C
                ; Обновление опкода планировщика в общей RAM, байт непосредственного операнда остаётся прежним.
                LD (@Action.ScheduleSpawn.OpcodeGate), A
                ; -----------------------------------------
                ; JP @Controls.BuildAndActivateParameters.Entry, продолжение в BuildAndActivateParameters.asm

                ; -----------------------------------------
                endmodule
                endmodule
