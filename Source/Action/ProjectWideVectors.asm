                module Action
                module ProjectWideVectors
                ; Физические поля [локальный контекст](../../Docs/ActionLocalContextPhysicalData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionWideProjectionInput.md)
                ; -----------------------------------------
                ; Обход широких векторов с выбором масштаба, отрисовкой близких записей и публикацией выбранной
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0D53..#0E3B
                ; In:
                ;   SeedIndex задаёт число доступных FActionWideVector, читаются два контекста и байт выбора по #9BCA
                ;   страница 0 выбрана, доступны коэффициенты преобразования и код рисователя страницы 1
                ;   стек содержит внешний возврат и доступен для кадров дочерних вызовов, IRQ не вмешиваются
                ; Out:
                ;   при нулевом счётчике публикуются три маркера #80 без обхода
                ;   иначе обход всех записей и публикация старших байтов трёх результатов на выбранной итерации
                ;   IY и внешний SP восстанавливаются, при отрисовке выбирается страница 1 с возвратом на страницу 0
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, R, рабочие компоненты, выходы преобразования, состояние рисователя, 7FFD при отрисовке и временный CPU-стек
                ; Note:
                ;   близкая запись определяется верхними словами от −60 до 59, дальняя сдвигается на четыре бита
                ;   дочерние процедуры могут оставить частично обновлённые выходы при переполнении
                ;   сквозная модель проверяет физические списки от нуля до шести записей и обе ветки, точный набор побочных записей и R отдельно не сверялись
                ; -----------------------------------------
                ; Установка исходного маркера во всех трёх публикуемых байтах.
Entry:          LD A, #80
                LD (@ActionWideProjectionLoopState.Published0), A
                LD (@ActionWideProjectionLoopState.Published1), A
                LD (@ActionWideProjectionLoopState.Published2), A
                ; Проверка числа записей перед запуском обхода.
                LD A, (@ControlsParameterTablesState.SeedIndex)
                OR A
                RET Z                                                           ; выход, если список широких векторов пуст

                LD B, A
                ; Сравнение двух пар контекста перед выбором номера публикации.
                CALL @Action.CompareContextWordPairs.Entry
                LD A, (@ActionWideProjectionLoopState.SelectedIndex)
                JR Z, @Action.ProjectWideVectors.SetCountdown                   ; переход, если обе пары контекста совпали

                LD A, #FE
                ; Расчёт обратного счётчика до выбранной записи.
SetCountdown:   INC A
                LD C, A
                PUSH IY
                LD IY, @ActionWideVectors.Vector00
                LD DE, FActionWideVector
                ; Проверка диапазона верхних слов текущего вектора.
CheckVector:    CALL @Action.CheckThreeUpperWordsNear.Entry
                JR NC, @Action.ProjectWideVectors.ScaleFarVector                ; переход, если хотя бы одно верхнее слово вне диапазона от −60 до 59

                PUSH DE
                ; Сохранение рамки обхода перед преобразованием и отрисовкой близкой записи.
                PUSH IY
                PUSH BC
                CALL @Action.CopyAndTransformComponents.Entry
                CALL @Action.DrawBankedProjectedBody.Entry
                ; Восстановление рамки обхода после обеих веток.
RestoreFrame:   POP BC
                POP IY
                POP DE
                DEC C
                JR NZ, @Action.ProjectWideVectors.AdvanceVector                 ; переход, если счётчик до публикуемой записи ещё не равен нулю

                ; Публикация старших байтов трёх результатов преобразования.
                LD A, (@ActionPatchedVectorState.Output0 + 1)
                LD (@ActionWideProjectionLoopState.Published0), A
                LD A, (@ActionPatchedVectorState.Output1 + 1)
                LD (@ActionWideProjectionLoopState.Published1), A
                LD A, (@ActionPatchedVectorState.Output2 + 1)
                LD (@ActionWideProjectionLoopState.Published2), A
                ; Переход к следующей физической записи.
AdvanceVector:  ADD IY, DE
                DJNZ @Action.ProjectWideVectors.CheckVector

                POP IY
                RET

                ; Сохранение рамки обхода и подготовка уменьшенных компонент.
ScaleFarVector: PUSH DE
                PUSH IY
                PUSH BC
                LD B, (IY + @FActionWideVector.Component0.Byte3)
                LD H, (IY + @FActionWideVector.Component0.Byte2)
                LD L, (IY + @FActionWideVector.Component0.Byte1)
                LD A, (IY + @FActionWideVector.Component0.Byte0)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (@ActionComponentWork.Component0.Low), A
                LD (@ActionComponentWork.Component0.Middle), HL
                LD B, (IY + @FActionWideVector.Component1.Byte3)
                LD H, (IY + @FActionWideVector.Component1.Byte2)
                LD L, (IY + @FActionWideVector.Component1.Byte1)
                LD A, (IY + @FActionWideVector.Component1.Byte0)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (@ActionComponentWork.Component1.Low), A
                LD (@ActionComponentWork.Component1.Middle), HL
                LD B, (IY + @FActionWideVector.Component2.Byte3)
                LD H, (IY + @FActionWideVector.Component2.Byte2)
                LD L, (IY + @FActionWideVector.Component2.Byte1)
                LD A, (IY + @FActionWideVector.Component2.Byte0)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (@ActionComponentWork.Component2.Low), A
                LD (@ActionComponentWork.Component2.Middle), HL
                CALL @Action.TransformWorkComponents.Entry
                JP @Action.ProjectWideVectors.RestoreFrame

                endmodule
                endmodule
