                module Action
                module SpawnLinkedClass9Records
                ; Документация [алгоритм и проверка](../../Docs/ActionChildSpawn.md)
                ; -----------------------------------------
                ; Условное создание одной либо двух записей класса 9 с индексом родителя и копией его связи
                ; исходная запись 17, адреса E86B..E91D
                ; In:
                ;   HL, DE и BC задают сохраняемый контекст ранних ветвей, A задаёт начальный StateCode дочерних записей
                ;   IX указывает активного родителя FActionRecord, ReuseByte доступен для изменения, от A100 достижим маркер поиска свободной записи
                ;   действуют договоры NextRandomWord11, FindReusableRecord и RecordAddressToIndex, записи детей доступны для изменения
                ;   ACTION банка 0 выбран, четыре дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   при установленном бите 2 ReuseByte возвращается исходный A и F от индексного BIT с входным Carry, RAM сохраняется
                ;   иначе InitialState получает входной A до вызова потока 11, при новом L>=0A выполняется RET, бит 2 родителя остаётся сброшенным
                ;   при L<0A бит 2 устанавливается до поиска места, прочитанный R выбирает запрос одной либо двух дочерних записей
                ;   каждая найденная запись получает Components родителя плюс одно общее положительное BC-смещение, индекс родителя в Unknown20 и требуемый класс 8 в Unknown21
                ;   дочерние ClassCode=9, StateCode=InitialState, SavedStateCode=0D, LinkedIndex копирует текущую связь родителя, остальные поля описаны в документации
                ;   после полного создания B=0, C и DE сохраняются от входа, HL равен новому слову потока 11, A равен связи родителя, F=42
                ;   при отказе FindReusableRecord возвращает AF=8042 и обменённые через EXX основные и альтернативные пары, оставшийся счётчик находится в альтернативном B
                ;   при отказе бит 2 родителя не очищается, уже созданные записи сохраняются, автоматического отката нет
                ;   AF', IX, I/IM/IFF и paging сохраняются, IY равен последней найденной записи либо маркеру, SP после внешнего RET увеличен на два
                ;   R добавляет 3 M1 при исходно установленном бите 2 и 74 при случайном отказе, точная стоимость остальных путей приведена в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IY, R, InitialState, поток 11, бит 2 родителя, выбранные записи и до четырёх байтов CPU-стека, SP внешним RET
                ; Note:
                ;   число запрошенных записей зависит от реально прочитанного R, его бит 7 выбирает модель 88 либо 8C, исходные чтения не заменены случайными числами
                ;   поиск не резервирует запись отдельным флагом, компоненты ребёнка с итоговым старшим байтом 80 могут снова участвовать в следующем поиске
                ;   неуравновешенный EXX на раннем RET Z является исходным поведением, вызывающий код обязан учитывать его
                ;   73472 сценария сравнивают реальные дети, точные регистры, флаги, R, восемь банков, значения и кратность всех записей
                ;   полное произведение списков и входов, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись
                ; -----------------------------------------
                ; Проверка уже инициированного запроса детей по биту 2 родителя, остальные биты ReuseByte не трактуются этим условием.
Entry:          BIT @ActionSelectedRecordProximityConst.ClearedReuseBit, (IX + @FActionRecord.ReuseByte)
                RET NZ                                                          ; выход, если бит 2 родителя установлен, не менять состояние потока и записей

                ; Сохранение входного A в общий операнд начального состояния детей до случайного допуска.
                LD (@ActionChildSpawnState.InitialState), A
                ; Получение нового слова физического потока 11, младший байт определяет допуск.
                CALL @Action.NextRandomWord11.Entry
                LD A, L
                CP @ActionChildSpawnConst.LowLimit
                RET NC                                                          ; выход, если новый L не меньше 0A, не устанавливать бит запроса родителя

                ; Обновление бита запроса до поиска места, отказ выделения этот бит не откатывает.
                SET @ActionSelectedRecordProximityConst.ClearedReuseBit, (IX + @FActionRecord.ReuseByte)
                ; Расчёт числа запросов, младший бит реально прочитанного R плюс один даёт 1 либо 2.
                LD A, R
                AND #01
                INC A
                LD B, A
                ; Поиск следующей доступной записи с сохранением счётчика в альтернативном B через EXX.
NextChild:      EXX
                CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск достиг маркера, оставить пары обменёнными через EXX и сохранить уже созданных детей

                ; Расчёт байтового индекса родителя и сохранение его как цели ребёнка с требуемым полным классом 8.
                PUSH IX
                POP HL
                CALL @Action.RecordAddressToIndex.Entry
                LD (IY + @FActionRecord.Unknown20), A
                LD (IY + @FActionRecord.Unknown21), @ActionChildSpawnConst.RequiredClass
                ; Расчёт одного общего смещения, старший байт 1 либо 2 и младший байт 0..127 читаются из разных R.
                LD A, R
                AND #01
                INC A
                LD B, A
                LD A, R
                AND #7F
                LD C, A
                ; Создание трёх компонент ребёнка, к каждой компоненте родителя прибавляется один и тот же BC по модулю 65536.
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                ADD HL, BC
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                LD L, (IX + @FActionRecord.Components.Component1.Low)
                LD H, (IX + @FActionRecord.Components.Component1.High)
                ADD HL, BC
                LD (IY + @FActionRecord.Components.Component1.Low), L
                LD (IY + @FActionRecord.Components.Component1.High), H
                LD L, (IX + @FActionRecord.Components.Component2.Low)
                LD H, (IX + @FActionRecord.Components.Component2.High)
                ADD HL, BC
                LD (IY + @FActionRecord.Components.Component2.Low), L
                LD (IY + @FActionRecord.Components.Component2.High), H
                ; Выбор байтового смещения модели по биту 7 прочитанного R, старый Carry на выбор не влияет.
                LD C, @ActionChildSpawnConst.ModelWithBit7
                LD A, R
                RLA
                JR C, @Action.SpawnLinkedClass9Records.StoreModel               ; переход, если бит 7 прочитанного R установлен, сохранить ModelOffset=88

                LD C, @ActionChildSpawnConst.ModelNoBit7
                ; Обновление выбранной модели и исходных управляющих полей ребёнка.
StoreModel:     LD (IY + @FActionRecord.ModelOffset), C
                LD (IY + @FActionRecord.TargetIndex), @ActionChildSpawnConst.TargetLife
                LD (IY + @FActionRecord.OffsetPhase0), #00
                ; Расчёт OffsetPhase1 из четырёх младших битов следующего прочитанного R.
                LD A, R
                AND @ActionChildSpawnConst.Phase1Mask
                LD (IY + @FActionRecord.OffsetPhase1), A
                ; Расчёт OffsetPhase2 из трёх младших битов отдельного чтения R.
                LD A, R
                AND @ActionChildSpawnConst.Phase2Mask
                LD (IY + @FActionRecord.OffsetPhase2), A
                ; Заполнение времени, начального состояния, сохранённого состояния и полного класса ребёнка.
                LD (IY + @FActionRecord.Unknown11), @ActionChildSpawnConst.TimerByte11
                LD (IY + @FActionRecord.StateCode), #02
                LD (IY + @FActionRecord.SavedStateCode), @ActionChildSpawnConst.SavedState
                LD (IY + @FActionRecord.LinkFlags), #00
                LD (IY + @FActionRecord.ClassCode), @ActionChildSpawnConst.ChildClass
                LD (IY + @FActionRecord.Unknown14), #00
                ; Копирование связи родителя, этот байт отличается от индекса родителя в Unknown20.
                LD A, (IX + @FActionRecord.LinkedIndex)
                LD (IY + @FActionRecord.LinkedIndex), A
                ; Завершение исходных полей ребёнка, подстановка FF, управляющий код 50, байт 10 равен 1 и шаг цели 2.
                LD (IY + @FActionRecord.Unknown15), #FF
                LD (IY + @FActionRecord.Unknown13), @ActionChildSpawnConst.ControlByte13
                LD (IY + @FActionRecord.Unknown10), @ActionChildSpawnConst.InitialByte10
                LD (IY + @FActionRecord.TargetCodeStep), @ActionChildSpawnConst.TargetStep
                ; Восстановление основного счётчика запросов и его уменьшение только после полностью записанного ребёнка.
                EXX
                DEC B
                JP NZ, @Action.SpawnLinkedClass9Records.NextChild               ; переход, если остаётся второй запрос, снова обменять пары и искать доступную запись

                RET

                endmodule
                endmodule
