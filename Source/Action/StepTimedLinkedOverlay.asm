                module Action
                module StepTimedLinkedOverlay
                ; Документация [алгоритм и проверка](../../Docs/ActionTimedLinkedState.md)
                ; -----------------------------------------
                ; Уменьшение таймера, восстановление состояния и обновление связанного сегмента либо создание класса 17
                ; исходная запись 17, адреса F3C8..F3EF
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, входной Carry учитывается DEC таймера
                ;   IX указывает FActionRecord с PhaseMoveTimer, Unknown19, Unknown11, LinkedIndex и входами общих помощников
                ;   действуют договоры PrepareLinkedRecordContext, NextRandomWord0, CheckAndToggleLinkedOverlay и CheckClass17SpawnWindow
                ;   ACTION банка 0, перенесённый код банка 5, таблицы и экранные буферы доступны, CPU-стек допускает рамки детей, IRQ исключены
                ; Out:
                ;   PhaseMoveTimer уменьшается на один по модулю 256, исходный ноль становится FF и не вызывает истечение
                ;   только при исходном таймере 1 StateCode получает Unknown19, затем управление сразу идёт к F0F8
                ;   при ненулевом новом таймере подготавливается связанный контекст, его Z пропускает оба следующих общих пути
                ;   при доступном контексте обновляется поток 0, его L сравнивается с полным Unknown11
                ;   при L>=Unknown11 выполняется общий CheckClass17SpawnWindow с исходными H и A=L
                ;   при L<Unknown11 вызывается полный CheckAndToggleLinkedOverlay, его Carry здесь игнорируется
                ;   HL, DE, BC, AF, HL', DE', BC', AF' и IY определяются достигнутым путём, IX, I/IM/IFF и paging сохраняются
                ;   внешний SP сохраняется, PC=F0F8, общий расчёт смещений сюда не включён
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, PhaseMoveTimer, условно StateCode и эффекты реально достигнутых детей
                ; Note:
                ;   Unknown19 читается как полный код состояния только на пути истечения, допустимость значения здесь не проверяется
                ;   Unknown11 является порогом младшего случайного байта в этом состоянии, общего назначения поля для всех классов не утверждается
                ;   65536 сценариев проверили все пары таймера и порога, истечение, оборачивание нуля, отказ контекста, реальное создание и экранный вывод
                ;   сверены регистры кроме R растеризатора, восемь банков и кратность записей, на путях без растеризатора R проверен точно
                ;   общий F0F8, полное произведение входов, R/T растеризатора, аппаратные IRQ, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Обновление таймера по модулю 256, истечение наступает только при исходной единице.
Entry:          LD A, (IX + @FActionRecord.PhaseMoveTimer)
                DEC A
                LD (IX + @FActionRecord.PhaseMoveTimer), A
                JR NZ, @Action.StepTimedLinkedOverlay.CheckLinked               ; переход, если уменьшенный таймер ненулевой, проверить связанную запись

                ; Восстановление полного StateCode из Unknown19 без добавления проверки диапазона.
                LD A, (IX + @FActionRecord.Unknown19)
                LD (IX + @FActionRecord.StateCode), A
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Подготовка указателя выбранной записи и трёх кэшированных компонент текущего IX.
CheckLinked:    CALL @Action.PrepareLinkedRecordContext.Entry
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если подготовленный контекст недоступен, продолжить общий расчёт смещений

                ; Обновление потока 0 только при доступной связанной записи.
                CALL @Action.NextRandomWord0.Entry
                ; Проверка младшего случайного байта относительно полного Unknown11 для выбора общего пути.
                LD A, L
                CP (IX + @FActionRecord.Unknown11)
                JP NC, @Action.CheckClass17SpawnWindow.Entry                    ; переход, если L не меньше Unknown11, проверить общее окно создания класса 17

                ; Обновление связанного сегмента, Carry экранного помощника в этом состоянии не изменяет продолжение.
                CALL @Action.CheckAndToggleLinkedOverlay.Entry
                JP @Action.PrepareObjectOffsetTransform.Entry

                endmodule
                endmodule
