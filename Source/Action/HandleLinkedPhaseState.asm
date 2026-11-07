                module Action
                module HandleLinkedPhaseState
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedPhaseState.md)
                ; -----------------------------------------
                ; Обновление связанной записи с отдельным случайным окном и шагом третьей фазы
                ; исходная запись 17, адреса F289..F355
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает FActionRecord с полями связанного и фазового состояний
                ;   ClassCode AND 7F находится в диапазоне 0..25 для достигнутого DispatchRecordClass, действуют договоры всех достигнутых детей
                ;   Input0/1/2 ComputePatchedVector уже содержат предназначенные для этого шага слова, данный обработчик не обновляет их через LoadLinkedRecordVectors
                ;   доступны выбранные записи, исходные таблицы геометрии, состояния потоков и экранные буферы
                ;   ACTION банка 0, перенесённый код банка 5 и корень банка 1 доступны, CPU-стек допускает рамки детей, IRQ исключены
                ; Out:
                ;   при LinkedIndex=FF R>=7E допускает ближайшего кандидата с переходом State0E, иначе выполняется диспетчер класса
                ;   при оставшемся FF SavedStateCode=5 завершает обработчик, другие байты задают косвенный хвост по обёрнутому удвоению состояния
                ;   для существующей связи Unknown13<23 допускает State06 при R>=64 для полных классов, отличных от 8 и 9
                ;   попытка класса 19 здесь допускается при R>=28, кроме полных классов 2, 3 и запрещённого бита запроса класса 8
                ;   после попытки класс 8 сохраняет состояние, остальные полные классы получают State0F независимо от выделения
                ;   недоступный подготовленный контекст очищает связь до FF, неотрицательный DEC Unknown14 сохраняется, единица вызывает общий класс 17
                ;   только после подготовки и счётчика вызывается SpawnClass9ForClass8, полный класс 8 затем выполняет State12 до внешнего возврата
                ;   остальные классы вызывают StepRandomizedThirdPhase, затем текущие кэшированные Components и прежние Input0/1/2 передаются общему CheckMotion по F201
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R и paging определяются достигнутыми детьми, IX, I/IM/IFF сохраняются
                ;   обычный итог PC=F0F8 с сохранённым внешним SP, State12 выполняет внешний RET, косвенный следующий обработчик не получает новой рамки
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, поля записей, состояния потоков, изменяемые операнды, буферы, экран и CPU-стек детей, условно 7FFD
                ; Note:
                ;   порядок не эквивалентен State02, случайное окно класса 19 направлено в другую сторону, класс 8 проверяется позднее и есть отдельный фазовый шаг
                ;   LoadLinkedRecordVectors здесь не вызывается, подмена прежних глобальных Input0/1/2 словами вновь выбранной записи изменила бы оригинал
                ;   при передаче в CheckMotion роли текущего и глобального векторов противоположны их подготовке в State02
                ;   44032 сценария включили все индексы связи, 52 полных класса, сохранённые состояния класса 9, настоящую геометрию, создание, State12 и 48 экранных вызовов
                ;   сверены регистры кроме R растеризатора, все банки, кратность записей и OUT, точный R подтверждён на 43984 остальных путях
                ;   дополнительно прошли 44032 профиля без маркера отказа за массивом, косвенный следующий обработчик и общий F0F8 не исполнялись
                ;   полное произведение входов, произвольные изменения кода индексом за массивом, R/T растеризатора, аппаратные IRQ, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Проверка существования связи, только исходный FF после INC становится нулём.
Entry:          LD A, (IX + @FActionRecord.LinkedIndex)
                INC A
                JR NZ, @Action.HandleLinkedPhaseState.CheckLinked               ; переход, если LinkedIndex не равен FF, проверить существующую связь

                ; Проверка R перед поиском новой связи, порог этого состояния равен 7E.
                LD A, R
                CP @ActionLinkedPhaseConst.ListRMin
CheckList:      JR C, @Action.HandleLinkedPhaseState.RefreshClass               ; переход, если прочитанный R меньше 7E, обновить класс без поиска кандидата

                CALL @Action.CheckCandidateListReady.Entry
                JR Z, @Action.HandleLinkedPhaseState.RefreshClass               ; переход, если допуск списка вернул Z, обновить класс без выбора кандидата

                ; Поиск ближайшего кандидата с сохранением исходного поведения старого результата.
                CALL @Action.FindNearestListedRecord.Entry
                ; Обновление State0E и связи найденным либо сохранённым результатом дочернего поиска.
                LD (IX + @FActionRecord.StateCode), @ActionLinkedPhaseConst.LinkedState
                LD (IX + @FActionRecord.LinkedIndex), A
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Обновление класса и повторная проверка фактически изменённой связи.
RefreshClass:   CALL @Action.DispatchRecordClass.Entry
                LD A, (IX + @FActionRecord.LinkedIndex)
                INC A
                JP NZ, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если после диспетчера LinkedIndex не равен FF, продолжить общий расчёт

                ; Проверка сохранённого состояния против собственного State05 перед косвенным хвостом.
                LD A, (IX + @FActionRecord.SavedStateCode)
                CP @ActionLinkedPhaseConst.OwnState
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если SavedStateCode равен 5, не вызывать этот же обработчик повторно

                ; Расчёт адреса следующего обработчика с исходным байтовым оборачиванием SLA.
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

                ; Проверка Unknown13 перед случайными действиями связанной записи.
CheckLinked:    LD A, (IX + @FActionRecord.Unknown13)
                CP @ActionLinkedPhaseConst.ParameterLimit
                JP NC, @Action.HandleLinkedPhaseState.PrepareLinked             ; переход, если Unknown13 не меньше 23, сразу подготовить связь

                ; Проверка одного значения R с сохранением в C для второй границы.
                LD A, R
                CP @ActionLinkedPhaseConst.EffectRMin
                LD C, A
                JR C, @Action.HandleLinkedPhaseState.CheckSpawn                 ; переход, если прочитанный R меньше 64, проверить окно класса 19

                LD A, (IX + @FActionRecord.ClassCode)
                CP @ActionLinkedPhaseConst.Class8
                JR Z, @Action.HandleLinkedPhaseState.CheckSpawn                 ; переход, если полный ClassCode равен 8, не устанавливать State06

                CP @ActionLinkedPhaseConst.Class9
                JR Z, @Action.HandleLinkedPhaseState.CheckSpawn                 ; переход, если полный ClassCode равен 9, не устанавливать State06

                ; Обновление StateCode до 6 после старшего случайного допуска.
                LD (IX + @FActionRecord.StateCode), @ActionLinkedPhaseConst.EffectState
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Проверка нижней включённой границы R>=28 для создания класса 19, направление отличается от State02.
CheckSpawn:     LD A, C
                CP @ActionLinkedPhaseConst.SpawnRMin
                JR C, @Action.HandleLinkedPhaseState.PrepareLinked              ; переход, если тот же R меньше 28, пропустить создание и подготовить связь

                ; Проверка полных классов, исключённых из попытки класса 19.
                LD A, (IX + @FActionRecord.ClassCode)
                CP @ActionLinkedPhaseConst.Class3
                JR Z, @Action.HandleLinkedPhaseState.PrepareLinked              ; переход, если ClassCode равен 3, пропустить создание класса 19

                CP @ActionLinkedPhaseConst.Class2
                JR Z, @Action.HandleLinkedPhaseState.PrepareLinked              ; переход, если ClassCode равен 2, пропустить создание класса 19

                CP @ActionLinkedPhaseConst.Class8
                JR NZ, @Action.HandleLinkedPhaseState.SpawnClass19              ; переход, если ClassCode не равен 8, вызвать общий создатель класса 19

                ; Проверка бита 2 запроса полного класса 8 перед общим создателем.
                BIT 2, (IX + @FActionRecord.ReuseByte)
                JR NZ, @Action.HandleLinkedPhaseState.PrepareLinked             ; переход, если бит 2 ReuseByte установлен, пропустить попытку класса 19

                ; Создание класса 19 по младшему двухбитовому счётчику с исходными изменениями списка.
SpawnClass19:   CALL @Action.SpawnClass19AndUpdateList.Entry
                LD A, (IX + @FActionRecord.ClassCode)
                CP @ActionLinkedPhaseConst.Class8
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если полный ClassCode равен 8, сохранить состояние после попытки

                ; Обновление State0F для остальных полных классов независимо от выделения ребёнка.
                LD (IX + @FActionRecord.StateCode), @ActionLinkedPhaseConst.PhaseState
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Подготовка указателя цели и кэша Components без загрузки выбранных глобальных векторных слов.
PrepareLinked:  CALL @Action.PrepareLinkedRecordContext.Entry
                JR NZ, @Action.HandleLinkedPhaseState.CheckCounter              ; переход, если подготовленный контекст доступен, проверить Unknown14

                ; Обновление LinkedIndex до FF при недоступной подготовленной записи.
                LD (IX + @FActionRecord.LinkedIndex), @ActionLinkedPhaseConst.NoLink
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Проверка результата DEC Unknown14 до записи и возможного общего создания класса 17.
CheckCounter:   LD A, (IX + @FActionRecord.Unknown14)
                DEC A
                JP M, @Action.HandleLinkedPhaseState.SpawnClass9                ; переход, если результат DEC отрицателен, сохранить прежний Unknown14

                ; Обновление Unknown14 неотрицательным результатом декремента.
                LD (IX + @FActionRecord.Unknown14), A
                JP Z, @Action.SpawnLinkedClass17AndContinue.Entry               ; переход, если результат DEC равен нулю, вызвать общий класс 17

                ; Создание класса 9 проверяется только после подготовки связи и допуска счётчика.
SpawnClass9:    CALL @Action.SpawnClass9ForClass8.Entry
                LD A, (IX + @FActionRecord.ClassCode)
                CP @ActionLinkedPhaseConst.Class8
                JP Z, @Action.AcquireLinkAndApplyOffsets.Entry                  ; переход, если полный ClassCode равен 8, выполнить State12 и локальный возвратный хвост

                ; Обновление третьей фазы и счётчика направления настоящим отдельным фазовым помощником.
                CALL @Action.StepRandomizedThirdPhase.Entry
                ; Подготовка противоположно ориентированных аргументов из кэша текущей записи и уже существующих глобальных Input0/1/2.
LoadMotion:     LD DE, (@ActionPatchedVectorState.Input0)
                LD BC, (@ActionPatchedVectorState.Input1)
                LD HL, (@ActionLinkedContextState.Component0)
                EXX
                LD HL, (@ActionLinkedContextState.Component1)
                LD DE, (@ActionLinkedContextState.Component2)
                LD BC, (@ActionPatchedVectorState.Input2)
                EXX
                ; Продолжение по общему CheckMotion состояния 02 без новой возвратной рамки.
                JP @Action.HandleLinkedTargetState.CheckMotion

                endmodule
                endmodule
