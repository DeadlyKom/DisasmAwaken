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
                ;   читается Component0.High, для активной записи доступны остальные фазовые поля, класс, состояние и порог
                ;   OffsetScaleLow и OffsetScaleHigh активной записи доступны для записи, ACTION банка 0 и общая RAM доступны
                ;   действует договор ApplyObjectOffsetVector, шесть байтов под SP и внешний возврат не перекрывают его код, таблицы, операнды и результаты
                ;   IRQ и повторный вход исключены
                ;   числовые постусловия исходного вычислителя требуют сохранности его инструкций, таблиц и внешнего возврата после записей детей, игра эту сохранность не проверяет
                ; Out:
                ;   при LinkedIndex=FF R>=7E допускает ближайшего кандидата с переходом State0E, иначе выполняется диспетчер класса
                ;   при оставшемся FF SavedStateCode=5 завершает обработчик, другие байты задают косвенный хвост по обёрнутому удвоению состояния
                ;   для существующей связи EffectReserve<23 допускает State06 при R>=64 для полных классов, отличных от 8 и 9
                ;   попытка класса 19 здесь допускается при R>=28, кроме полных классов 2, 3 и запрещённого бита запроса класса 8
                ;   после попытки класс 8 сохраняет состояние, остальные полные классы получают State0F независимо от выделения
                ;   недоступный подготовленный контекст очищает связь до FF, неотрицательный DEC MissileRepeatDelay сохраняется, единица вызывает общий класс 17
                ;   только после подготовки и счётчика вызывается SpawnClass9ForClass8, полный класс 8 затем выполняет State12 до внешнего возврата
                ;   остальные классы вызывают StepRandomizedThirdPhase, затем текущие кэшированные Components и прежние Input0/1/2 передаются общему CheckMotion по F201
                ;   обычный путь F0F8 исполняется до внешнего RET при соблюдении условий исходного вычислителя, State12 имеет собственный внешний RET
                ;   косвенный хвост сохраняет SP и передаёт управление выбранному следующему обработчику без нового CALL, постусловия возврата зависят также от него
                ;   следующие эффекты общего вычислителя относятся только к обычной активной ветви, при маркере AF=8042 и остальные результаты детей сохраняются
                ;   на активной ветви нижеследующие результаты вычислителя относятся к V из прежнего OffsetScaleLow и выбранного старшего байта
                ;   HL=(-Q) AND FFFF при бите 7 S=1, иначе HL=Q, DE=Q при бите 7 S=1, иначе DE=abs(V)
                ;   BC - B=W[Offset0], C=0
                ;   AF - A=S, F от 16-разрядного 0-Q при бите 7 S=1, иначе флаги логического XOR с результатом S
                ;   HL', DE', BC' сохраняют результаты достигнутых детей
                ;   AF' - A'=U, F'=(U AND 28) OR (40 при U=0) OR (10 при 2*((P SHR 16) AND 0F)+(U AND 1)>0F), остальные биты F' нулевые
                ;   IX восстановлен, IYH сохраняет результат достигнутых детей, IYL=W[(Offset1+64) AND FF]
                ;   Coefficient0..2 содержат результат построителя, Base0..2 содержат три произведения с одним входным V
                ;   SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются
                ;   Offset0..2 получают OffsetPhase0, wrap8(OffsetPhase1+80) и OffsetPhase2
                ;   OffsetScaleLow получает wrap8(старое+1), если этот кандидат ниже Phase2OrTarget, иначе сохраняется прежний байт
                ;   OffsetScaleHigh обнулён при ClassCode<10 и StateCode не равном 13, иначе сохранён
                ;   на активной ветви R учитывает 30+Hold+4*Small+2*Small*Different M1 подготовки плюс полный вычислитель, старший бит R сохраняется
                ;   на возвращающихся ветвях SP=входной SP+2, IX и I/IM/IFF сохраняются, paging и прочие эффекты определяются реально достигнутыми детьми
                ;   R включает префикс, дочерние вызовы и общий хвост ровно один раз, на путях с отсечением точный счёт R отдельно не доказан
                ;   при наложении обратной связи на математический код действуют изменённые инструкции, полный возврат не гарантируется, случаи 61, 63, 193 и 194 документированы отдельно
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, поля записей, состояния потоков, изменяемые операнды, буферы, экран и CPU-стек детей, условно 7FFD
                ;   три фазовых операнда, Coefficient0..2, Base0..2 и условно масштабы активного общего хвоста, при произвольной связи возможны записи в исполняемый код
                ; Note:
                ;   порядок не эквивалентен State02, случайное окно класса 19 направлено в другую сторону, класс 8 проверяется позднее и есть отдельный фазовый шаг
                ;   LoadLinkedRecordVectors здесь не вызывается, подмена прежних глобальных Input0/1/2 словами вновь выбранной записи изменила бы оригинал
                ;   при передаче в CheckMotion роли текущего и глобального векторов противоположны их подготовке в State02
                ;   44032 сценария включили все индексы связи, 52 полных класса, сохранённые состояния класса 9, настоящую геометрию, создание, State12 и 48 экранных вызовов
                ;   сверены регистры кроме R растеризатора, все банки, кратность записей и OUT, точный R подтверждён на 43984 остальных путях
                ;   полное произведение входов, произвольные изменения кода индексом за массивом, R произвольных потоков и T растеризатора, аппаратные IRQ, сборка и нативная игра не проверялись
                ;   новая серия 44032 случаев при явном условии исходного математического кода проверяет 39948 обычных путей до RET и 292 прямых возвратов
                ;   104 профилей с изменёнными математическими инструкциями сверены только до F0F8, 3688 косвенных передач сверены до выбранного PC, внешним возвратом эти границы не считаются
                ;   в серии без искусственного маркера точный R проверен во всех 44032 сценариях, включая 47 внутренних и 15 отсечённых линий фиксированного пакета, остальные регистры кроме T, восемь банков, кратность присваиваний и порты совпали
                ;   отдельная новая серия без искусственного маркера отказа экранного пути за массивом прошла, достигнуты 62 экранных вызова, наблюдаемая временная глубина 28 байтов, точный R фиксированного пакета подтверждён, произвольные потоки не покрыты
                ;   полное произведение полей, продолжение изменённого кода и косвенных обработчиков, R произвольных потоков и T растеризатора, IRQ, сборка и нативная игра остаются границами проверки
                ;   эффективное слово V перед 6D06 содержит прежний OffsetScaleLow в E и итоговый OffsetScaleHigh в D, это не входное DE всей процедуры
                ;   Hold=1 при сохранении прежнего младшего масштаба, иначе 0, Small=1 при ClassCode<10, Different=1 при StateCode не равном 13, иначе соответствующий признак нулевой
                ;   10, 13 и 80 в условиях полей обозначают шестнадцатеричные коды, числа M1 десятичные
                ;   c2 обозначает третий байтовый коэффициент, m=abs(s8(c2)) AND 7F, P=m*abs(V), Q=floor(P/128), U=P SHR 15, S=c2 XOR HIGH слова V
                ;   нулевой фактор для коэффициента 80 сохранён, знак определяется исходным байтом коэффициента и старшим байтом V
                ;   каждое Base равно -floor((abs(s8(c_i)) AND 7F)*abs(V)/128) при бите 7 c_i XOR HIGH V, иначе положительному частному, всё по модулю 65536
                ;   шесть временных байтов после возврата содержат исходный IX по SP-2, слово V по SP-4 и внутренний возврат 6D0C по SP-6, POP не очищает RAM
                ;   для фактора m>0 умножение даёт 35+floor(log2(m))+2*popcount(m) M1, при m=0 даёт 32 M1
                ;   к каждому умножению добавляются семь M1 при V<0, две при бите 7 коэффициента и четыре при бите 7 его XOR HIGH V
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

                ; Проверка EffectReserve перед случайными действиями связанной записи.
CheckLinked:    LD A, (IX + @FActionRecord.EffectReserve)
                CP @ActionLinkedPhaseConst.ParameterLimit
                JP NC, @Action.HandleLinkedPhaseState.PrepareLinked             ; переход, если EffectReserve не меньше 23, сразу подготовить связь

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
SpawnClass19:   CALL @Action.CreateCargoAndUpdateList.Entry
                LD A, (IX + @FActionRecord.ClassCode)
                CP @ActionLinkedPhaseConst.Class8
                JP Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если полный ClassCode равен 8, сохранить состояние после попытки

                ; Обновление State0F для остальных полных классов независимо от выделения ребёнка.
                LD (IX + @FActionRecord.StateCode), @ActionLinkedPhaseConst.PhaseState
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Подготовка указателя цели и кэша Components без загрузки выбранных глобальных векторных слов.
PrepareLinked:  CALL @Action.PrepareLinkedRecordContext.Entry
                JR NZ, @Action.HandleLinkedPhaseState.CheckCounter              ; переход, если подготовленный контекст доступен, проверить MissileRepeatDelay

                ; Обновление LinkedIndex до FF при недоступной подготовленной записи.
                LD (IX + @FActionRecord.LinkedIndex), @ActionLinkedPhaseConst.NoLink
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Проверка результата DEC MissileRepeatDelay до записи и возможного общего создания класса 17.
CheckCounter:   LD A, (IX + @FActionRecord.MissileRepeatDelay)
                DEC A
                JP M, @Action.HandleLinkedPhaseState.SpawnClass9                ; переход, если результат DEC отрицателен, сохранить прежний MissileRepeatDelay

                ; Обновление MissileRepeatDelay неотрицательным результатом декремента.
                LD (IX + @FActionRecord.MissileRepeatDelay), A
                JP Z, @Action.CreateMissileAndContinueOffsets.Entry             ; переход, если результат DEC равен нулю, вызвать общий класс 17

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
