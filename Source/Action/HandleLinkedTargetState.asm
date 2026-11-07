                module Action
                module HandleLinkedTargetState
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedTargetState.md)
                ; -----------------------------------------
                ; Обновление связи, выбор дочерних действий и геометрическое сопровождение записи в состоянии 02
                ; исходная запись 17, адреса F138..F221
                ; In:
                ;   HL, DE, BC и AF числовых аргументов основного входа не задают, IX указывает FActionRecord с доступными полями связи, класса и контекстов
                ;   ClassCode AND 7F находится в диапазоне 0..25 для достигнутого DispatchRecordClass, действуют договоры всех достигнутых детей
                ;   обычные выбранные записи, состояния потоков, таблицы геометрии и экранные буферы доступны в своих физических банках
                ;   ACTION банка 0, перенесённый код банка 5 и корень банка 1 доступны, CPU-стек допускает рамки детей, IRQ исключены
                ; Out:
                ;   при LinkedIndex=FF аппаратный R допускает поиск ближайшего кандидата, принятая цель задаёт State0E и LinkedIndex
                ;   если поиск не выполнен, вызывается DispatchRecordClass, новая непустая связь завершает обработчик
                ;   при оставшемся FF SavedStateCode=2 завершает обработчик, другие значения вызывают косвенный хвост по EF50+((2*SavedStateCode) AND FF)
                ;   при исходной связи сначала выполняется SpawnClass9ForClass8, полный класс 8 затем передаёт управление State12 до внешнего возврата
                ;   остальные связанные записи в зависимости от Unknown13 и R переходят в State06 либо пытаются создать класс 19 с последующим State0F
                ;   общая подготовка недоступной цели очищает LinkedIndex до FF, отказ векторного контекста приводит к диспетчеру класса
                ;   Unknown14 уменьшается только при неотрицательном результате DEC, исходная единица ведёт к общему создателю класса 17
                ;   после подготовки шести аргументов проверка движения выбирает State11 либо шаг кодов, затем проверяются максимум модулей, случайное окно создания и экранный сегмент
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R и итоговый paging определяются реально достигнутыми детьми, IX, I/IM/IFF сохраняются
                ;   обычный итог PC=F0F8 при сохранённом внешнем SP, State12 заканчивается внешним RET, косвенный хвост сохраняет SP и выбирает следующий PC без нового CALL
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, поля текущей и дочерних записей, состояния потоков, изменяемый код, буферы, экран и CPU-стек детей, условно 7FFD
                ; Note:
                ;   проверки полных классов 8 и 9 не маскируют старший бит, маскирование выполняется только самим DispatchRecordClass
                ;   Unknown14=00 и 81..FF не сохраняют результат DEC, 80 уменьшается до 7F, единица записывает ноль перед созданием
                ;   SLA SavedStateCode намеренно оборачивает индекс по модулю 256, верхняя граница таблицы состояний не проверяется
                ;   44656 сценариев исполнили реальные поиски, диспетчеры, создание, контексты, геометрию и доступные экранные пути, включая дополнительный вход F142
                ;   дополнительно прошли 44656 профилей без маркера отказа за массивом, учтена запись индекса текущей записи поверх JR NZ по C94B
                ;   сверены регистры кроме R растеризатора, восемь банков, кратность записей и OUT, косвенный следующий обработчик и общий F0F8 не исполнялись
                ;   полное произведение входов, R/T растеризатора, аппаратные IRQ, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Проверка исходной связи через обёрнутое увеличение, только FF становится нулём.
Entry:          LD A, (IX + @FActionRecord.LinkedIndex)
                INC A
                JR NZ, @Action.HandleLinkedTargetState.CheckLinked              ; переход, если исходный LinkedIndex не равен FF, обработать существующую связь

                ; Проверка аппаратного R перед поиском новой связи для несвязанной записи.
                LD A, R
                CP #78
                ; -----------------------------------------
                ; Дополнительный вход CheckListGate
                ; In, Carry задаёт готовый допуск списка, IX указывает запись, действует остальной договор State02.
                ; Out, поиск либо диспетчер класса и общие продолжения сохраняют исходные правила, R повторно не читается.
                ; Corrupt, регистры, поля и дочерние эффекты из договора основного входа.
                ; -----------------------------------------
CheckListGate:  JR C, @Action.HandleLinkedTargetState.RefreshClass              ; переход, если Carry установлен, пропустить поиск кандидата и обновить класс

                CALL @Action.CheckCandidateListReady.Entry
                JR Z, @Action.HandleLinkedTargetState.RefreshClass              ; переход, если допуск списка вернул Z, обновить класс без выбора кандидата

                ; Поиск ближайшего доступного кандидата, старый результат при пустом полезном списке сохраняется по договору поиска.
                CALL @Action.FindNearestListedRecord.Entry
                ; Обновление State0E и связи принятым результатом поиска.
                LD (IX + @FActionRecord.StateCode), #0E
                LD (IX + @FActionRecord.LinkedIndex), A
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Обновление класса и повторная проверка связи после фактического обработчика класса.
RefreshClass:   CALL @Action.DispatchRecordClass.Entry
                LD A, (IX + @FActionRecord.LinkedIndex)
                INC A
                JP NZ, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если после диспетчера LinkedIndex не равен FF, продолжить общий расчёт

                ; Проверка сохранённого состояния перед косвенным продолжением без новой возвратной рамки.
                LD A, (IX + @FActionRecord.SavedStateCode)
                CP #02
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если SavedStateCode равен 2, не вызывать этот же обработчик повторно

                ; Расчёт адреса слова состояния, удвоение SavedStateCode выполняется в одном байте без ограничения таблицей.
SelectSaved:    SLA A
                LD L, A
                LD H, #00
                LD DE, @ActionObjectStateHandlers.State00
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                JP (HL)

                ; Создание класса 9 для полного класса 8 перед выбором дальнейшего пути связи.
CheckLinked:    CALL @Action.SpawnClass9ForClass8.Entry
                LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JP Z, @Action.AcquireLinkAndApplyOffsets.Entry                  ; переход, если полный ClassCode равен 8, выполнить State12 с общим локальным хвостом

                ; Проверка Unknown13 перед двумя случайными ветвями смены состояния либо создания класса 19.
                LD A, (IX + @FActionRecord.Unknown13)
                CP #23
                JR NC, @Action.HandleLinkedTargetState.PrepareLinked            ; переход, если Unknown13 не меньше 23, пропустить случайные действия и подготовить связь

                ; Проверка R с сохранением того же прочитанного байта в C для второй границы.
                LD A, R
                CP #64
                LD C, A
                JR C, @Action.HandleLinkedTargetState.CheckSpawn                ; переход, если прочитанный R меньше 64, проверить вторую случайную границу

                LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JR Z, @Action.HandleLinkedTargetState.CheckSpawn                ; переход, если полный ClassCode равен 8, не устанавливать State06

                CP #09
                JR Z, @Action.HandleLinkedTargetState.CheckSpawn                ; переход, если полный ClassCode равен 9, не устанавливать State06

                ; Обновление StateCode до 6 при принятом старшем случайном допуске.
                LD (IX + @FActionRecord.StateCode), #06
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Проверка ранее прочитанного R относительно нижнего окна создания класса 19.
CheckSpawn:     LD A, C
                CP #32
                JR NC, @Action.HandleLinkedTargetState.PrepareLinked            ; переход, если тот же R не меньше 32, пропустить создание и подготовить связь

                ; Проверка полных исключённых классов 3, 2 и отдельного бита запроса класса 8.
                LD A, (IX + @FActionRecord.ClassCode)
                CP #03
                JR Z, @Action.HandleLinkedTargetState.PrepareLinked             ; переход, если ClassCode равен 3, пропустить создание класса 19

                CP #02
                JR Z, @Action.HandleLinkedTargetState.PrepareLinked             ; переход, если ClassCode равен 2, пропустить создание класса 19

                CP #08
                JR NZ, @Action.HandleLinkedTargetState.SpawnClass19             ; переход, если ClassCode не равен 8, выполнить общий создатель класса 19

                BIT 2, (IX + @FActionRecord.ReuseByte)
                JR NZ, @Action.HandleLinkedTargetState.PrepareLinked            ; переход, если бит 2 ReuseByte установлен, не повторять запрос создания

                ; Попытка создания класса 19 по младшему двухбитовому счётчику с исходными побочными эффектами списка.
SpawnClass19:   CALL @Action.SpawnClass19AndUpdateList.Entry
                LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если после попытки ClassCode равен 8, сохранить текущее состояние

                ; Обновление State0F после попытки класса 19 независимо от успешности выделения.
                LD (IX + @FActionRecord.StateCode), #0F
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Подготовка физического указателя цели и кэшированных компонент текущей записи.
PrepareLinked:  CALL @Action.PrepareLinkedRecordContext.Entry
                JR NZ, @Action.HandleLinkedTargetState.LoadLinked               ; переход, если подготовленный контекст доступен, загрузить выбранные векторы

                ; Обновление LinkedIndex до FF при недоступной цели.
                LD (IX + @FActionRecord.LinkedIndex), #FF
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Чтение двух наборов выбранного контекста либо исходного особого контекста 1A.
LoadLinked:     CALL @Action.LoadLinkedRecordVectors.Entry
                JP C, @Action.HandleLinkedTargetState.DispatchClass             ; переход, если чтение векторного контекста вернуло Carry, выполнить диспетчер класса

                ; Проверка результата декремента Unknown14 до возможной записи и общего создания.
                LD A, (IX + @FActionRecord.Unknown14)
                DEC A
                JP M, @Action.HandleLinkedTargetState.LoadMotion                ; переход, если результат DEC отрицателен, не записывать уменьшенный Unknown14

                ; Обновление Unknown14 только неотрицательным результатом DEC.
                LD (IX + @FActionRecord.Unknown14), A
                JP Z, @Action.SpawnLinkedClass17AndContinue.Entry               ; переход, если результат DEC равен нулю, выполнить общий создатель класса 17

                ; -----------------------------------------
                ; Дополнительный вход LoadMotion
                ; In, шесть векторных слов и кэш Components уже подготовлены LoadLinkedRecordVectors и PrepareLinkedRecordContext.
                ; Out, загруженные аргументы переходят к CheckMotion, остальные пути и эффекты совпадают с основным договором.
                ; Corrupt, основные и альтернативные пары из геометрии и реально достигнутых детей.
                ; -----------------------------------------
                ; Подготовка шести аргументов из кэша текущей записи и трёх входных слов выбранной.
LoadMotion:     LD DE, #0000
                LD BC, #0000
                LD HL, (@ActionPatchedVectorState.Input0)
                EXX
                LD HL, (@ActionPatchedVectorState.Input1)
                LD DE, (@ActionPatchedVectorState.Input2)
                LD BC, #0000
                EXX
                ; -----------------------------------------
                ; Дополнительный вход CheckMotion
                ; In, HL/DE/BC и альтернативные пары уже заданы для CheckLinkedDistanceAndStepCodes, IX указывает текущую запись.
                ; Out, максимальный модуль не меньше 6 завершает общий шаг, остальные пути проверяют поток 0 и связанные действия.
                ; Corrupt, регистры, фазы, состояния, буферы и дочерние эффекты основного договора.
                ; -----------------------------------------
                ; Расчёт шага кодов либо временного состояния по фактическому расстоянию выбранной записи.
CheckMotion:    CALL @Action.CheckLinkedDistanceAndStepCodes.Entry
                LD A, H
                CP L
                JR NC, @Action.HandleLinkedTargetState.CheckDelta               ; переход, если H не меньше L, использовать H как максимальный модуль

                LD A, L
                ; Проверка максимума двух возвращённых байтов относительно допуска 6.
CheckDelta:     CP #06
                JP NC, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если максимальный модуль не меньше 6, продолжить общий расчёт без случайных действий

                ; Обновление потока 0 перед выбором общего окна создания либо экранного сегмента.
                CALL @Action.NextRandomWord0.Entry
                LD A, L
                ; Проверка полного порога Unknown11 по младшему байту нового случайного слова.
                CP (IX + @FActionRecord.Unknown11)
                JR NC, @Action.CheckClass17SpawnWindow.Entry                    ; переход, если L не меньше Unknown11, проверить общее окно создания класса 17

                ; Проверка и XOR-вывод связанного сегмента, Carry выбирает необходимость повторного обновления класса.
                CALL @Action.CheckAndToggleLinkedOverlay.Entry
                JR NC, @Action.HandleLinkedTargetState.Finish                   ; переход, если экранный помощник вернул Carry=0, не обновлять класс повторно

                ; -----------------------------------------
                ; Дополнительный вход DispatchClass
                ; In, IX указывает запись допустимого для DispatchRecordClass полного класса с маской 7F.
                ; Out, фактический обработчик класса выполнен, затем PC=F0F8 и внешний SP сохранён.
                ; Corrupt, регистры и поля только из достигнутого обработчика класса, собственные инструкции добавляют CALL и JP.
                ; -----------------------------------------
DispatchClass:  CALL @Action.DispatchRecordClass.Entry
Finish:         JP @Action.PrepareObjectOffsetTransform.Entry

                ; -----------------------------------------
                endmodule
                endmodule
