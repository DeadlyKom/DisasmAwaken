                module Action
                module CreateCargoAndUpdateList
                ; Документация [алгоритм и проверка](../../Docs/ActionClass19Spawn.md)
                ; -----------------------------------------
                ; Создание груза по двухбитовому счётчику и обновление списка кодом из сохранённого HL
                ; исходная запись 17, адреса 6417..64DE
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает текущую активную FActionRecord
                ;   ReuseByte AND 03 задаёт число оставшихся попыток 0..3, прочие шесть битов этого байта сохраняются при декременте
                ;   действуют договоры FindReusableRecord, RecordAddressToIndex и RecordIndexToAddress, список A01C достигает FE либо заменяемой ячейки
                ;   родительские Components, OffsetPhase0..2 и OffsetScaleLow читаются, свободная запись и список доступны для изменения
                ;   перенесённый код банка 5 и ACTION банка 0 доступны, два дополнительных байта CPU-стека доступны, IRQ не вмешиваются
                ; Out:
                ;   при нулевом двухбитовом счётчике AF=0054, C=входной ReuseByte, HL, DE и B сохраняются, RAM и альтернативные регистры сохраняются
                ;   иначе младшие два бита ReuseByte уменьшаются до поиска места, отказ поиска этот декремент не отменяет
                ;   из прочитанного R строятся вид x, управляющий код 1..8 и сохранённая пара HL, подробная формула приведена в документации
                ;   при отсутствии места AF=8042, DE=0040, HL содержит R-образованный набор, IY указывает маркер, AF' содержит управляющий код и флаги его INC
                ;   при успехе ребёнок получает Components родителя плюс 200, ModelOffset=98, StateCode=04, ClassCode=13 и точные управляющие поля по документации
                ;   Phase0OrLink, LocalPhase1 и Phase2OrTarget ребёнка получают OffsetPhase0..2 родителя
                ;   OffsetScaleLow=min(max(родительский OffsetScaleLow−30,0),69)
                ;   Unknown11 ребёнка получает управляющий код 1..8, ReuseByte ребёнка=10 при x<5 и 0 иначе, PickupKind=x
                ;   RecordAddressToIndex получает сохранённую пару HL из R, а не адрес ребёнка IY, полученный код E не обязан соответствовать созданной записи
                ;   FE списка завершает вызов без добавления, FF заменяется E, обычная ячейка заменяется E только при High=80 указанной ею записи
                ;   после созданного ребёнка HL указывает достигнутую ячейку списка, DE=00:E, B=x, C равен прежнему ReuseByte родителя
                ;   AF зависит от последней проверки списка, AF' содержит ограниченный OffsetScaleLow и F от CP результата до ограничения с 70
                ;   IX, I/IM/IFF и paging сохраняются, IY найденная запись либо маркер, SP после внешнего RET увеличен на два
                ;   R добавляет 5 M1 при нулевом счётчике, остальные ветви точно учтены независимой моделью, временная рамка равна двум байтам
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, младшие два бита ReuseByte родителя, ReuseByte просмотренных свободных строк, создаваемая запись, условная ячейка списка и два временных байта CPU-стека, SP внешним RET
                ; Note:
                ;   авторский T_CARGO=#13 и текущая модель CRG1 подтверждены оригинальными байтами, подготовленный вход общий для команд EjectCargo и EjectMine, последующая жизнь объекта здесь не проверяется
                ;   в исходном коде HL перед RecordAddressToIndex не заменяется IY, эта особенность сохранена без исправления алгоритма
                ;   полученный код всегда чётный и может равняться FE, такой байт реально записывается и способен стать ранним маркером следующего просмотра
                ;   фазы 07..09 ребёнка здесь не инициализируются, они не отождествляются с клонированными байтами 0D..0F
                ;   92160 сценариев покрыли все пары ReuseByte и R, все OffsetScaleLow и первые байты списка, реальные дети исполнены до полного RET
                ;   сверены точные регистры, флаги, R, восемь банков и кратность записей, смысл PickupKind и управляющего кода 1..8 не выдумывается
                ;   полное произведение входов, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Проверка младшего двухбитового счётчика ReuseByte, это многобитовое числовое поле, а не два независимых флага.
Entry:          LD A, (IX + @FActionRecord.ReuseByte)
                LD C, A
                AND @ActionClass19SpawnConst.CountMask
                RET Z                                                           ; выход, если младшие два бита ReuseByte равны нулю, не искать свободную запись

                ; Обновление счётчика на единицу с сохранением старших шести битов, попытка расходуется до поиска места.
                DEC A
                LD B, A
                LD A, C
                AND @ActionClass19SpawnConst.KeepUpper
                OR B
                LD (IX + @FActionRecord.ReuseByte), A
                ; Чтение R для вида и управляющего кода, исходный полный R сохраняется в H.
                LD A, R
                LD H, A
                AND @ActionClass19SpawnConst.KindMask
                CP @ActionClass19SpawnConst.KindLimit
                JR C, @Action.CreateCargoAndUpdateList.StoreKind                ; переход, если младшие пять битов R меньше 27, сохранить код вида без вычитания

                ; Расчёт нормализованного кода, исходные 27..31 становятся 22..26.
                SUB @ActionClass19SpawnConst.KindSubtract
                ; Подготовка L из кода вида и проверка отдельной метки для первых пяти кодов.
StoreKind:      LD L, A
                CP @ActionClass19SpawnConst.KindSubtract
                JR NC, @Action.CreateCargoAndUpdateList.BuildControl            ; переход, если нормализованный код не меньше 5, оставить бит 7 L сброшенным

                ; Установка временной метки в бите 7 L, позднее она превращается в бит 4 ReuseByte ребёнка.
                SET @ActionClass19SpawnConst.TemporaryBit, L
                ; Расчёт управляющего кода из битов 4..6 исходного R с прибавлением единицы, диапазон 1..8.
BuildControl:   LD A, H
                AND @ActionClass19SpawnConst.ControlMask
                RRCA
                RRCA
                RRCA
                RRCA
                INC A
                ; -----------------------------------------
                ; Подготовленный вход без расхода счётчика и генерации от R
                ; In:
                ;   HL содержит подготовленный код списка, L задаёт пометку в бите 7 и значение PickupKind в битах 6..0
                ;   DE входного аргумента не задаёт, C сохраняется, B заменяется L, AF содержит A для Unknown11 и сохраняемые в AF' флаги
                ;   IX указывает активного родителя, действуют договоры поиска места и конечного списка, два дополнительных байта стека доступны, IRQ не вмешиваются
                ; Out:
                ;   при отсутствии места AF=8042, HL сохранён, DE=0040, B=входной L, C сохранён, AF'=входной AF, IY указывает маркер
                ;   при успехе поля ребёнка следуют основному телу, Unknown11 получает входной A, PickupKind=входной L AND 7F
                ;   ReuseByte ребёнка=10 при входном бите 7 L, иначе 0, код списка рассчитывается из входного HL, не из адреса ребёнка IY
                ;   после успеха HL указывает достигнутую ячейку списка, DE=00:E, B=входной L AND 7F, C сохранён, AF определяется последней проверкой списка
                ;   IX, I, IM, IFF и paging сохраняются, SP после RET равен входному SP+2, IY указывает ребёнка либо маркер
                ; Corrupt:
                ;   HL, DE, BC только B, AF, HL', DE', BC', AF', IY, R, запись ребёнка, список, пометки поиска и два временных байта CPU-стека по пути
                ; Note:
                ;   родительский счётчик не уменьшается, случайный код не рассчитывается, весь входной A сохраняется без ограничения 1..8
                ;   [Договор внутреннего входа и 82496 сценариев](../../Docs/ActionPreparedClass19Spawn.md)
                ; -----------------------------------------
SpawnPrepared:  LD B, L
                ; Сохранение управляющего кода и его флагов в AF' перед поиском свободной записи.
                EX AF, AF'
                CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск достиг маркера, не откатывать уже уменьшенный счётчик родителя

                ; Создание трёх компонент ребёнка прибавлением 200 по модулю 65536, исходный R-образованный HL сохраняется через EXX.
                EXX
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD DE, @ActionClass19SpawnConst.ComponentDelta
                ADD HL, DE
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                LD L, (IX + @FActionRecord.Components.Component1.Low)
                LD H, (IX + @FActionRecord.Components.Component1.High)
                ADD HL, DE
                LD (IY + @FActionRecord.Components.Component1.Low), L
                LD (IY + @FActionRecord.Components.Component1.High), H
                LD L, (IX + @FActionRecord.Components.Component2.Low)
                LD H, (IX + @FActionRecord.Components.Component2.High)
                ADD HL, DE
                LD (IY + @FActionRecord.Components.Component2.Low), L
                LD (IY + @FActionRecord.Components.Component2.High), H
                ; Заполнение модели 98, состояния 4, отсутствующей связи FF и нулевых LinkFlags.
                LD (IY + @FActionRecord.ModelOffset), @ActionClass19SpawnConst.ModelOffset
                LD (IY + @FActionRecord.StateCode), @ActionClass19SpawnConst.InitialState
                LD (IY + @FActionRecord.LinkedIndex), #FF
                LD (IY + @FActionRecord.LinkFlags), #00
                ; Копирование трёх фаз родителя в локальные поля ребёнка для ApplyRecordLocalOffsets.
                LD A, (IX + @FActionRecord.OffsetPhase0)
                LD (IY + @FActionRecord.Phase0OrLink), A
                LD A, (IX + @FActionRecord.OffsetPhase1)
                LD (IY + @FActionRecord.LocalPhase1), A
                LD A, (IX + @FActionRecord.OffsetPhase2)
                LD (IY + @FActionRecord.Phase2OrTarget), A
                ; Расчёт управляющего байта ребёнка, сначала вычитается 30 с отдельным ограничением снизу.
                ; При выбросе груза или мины IX=#A780, масштаб читается из старшего байта скорости по #A790.
                LD A, (IX + @FActionRecord.OffsetScaleLow)
                SUB @ActionClass19SpawnConst.RateSubtract
                JR NC, @Action.CreateCargoAndUpdateList.ClampHigh               ; переход, если исходный OffsetScaleLow не меньше 30, сохранить результат вычитания

                ; Ограничение отрицательной разности нулём вместо байтового оборачивания.
                XOR A
                ; Проверка исключающего верхнего порога 70 перед ограничением до 69.
ClampHigh:      CP @ActionClass19SpawnConst.RateLimit
                JR C, @Action.CreateCargoAndUpdateList.StoreScale               ; переход, если уменьшенное значение меньше 70, сохранить его без верхнего ограничения

                ; Ограничение управляющего байта значением 69, флаги CP сохраняются для итогового AF'.
                LD A, @ActionClass19SpawnConst.RateMaximum
                ; Сохранение ограниченного OffsetScaleLow и восстановление управляющего кода 1..8 из AF'.
StoreScale:     LD (IY + @FActionRecord.OffsetScaleLow), A
                EX AF, AF'
                LD (IY + @FActionRecord.Unknown11), A
                ; Завершение класса 19 и управляющего байта 13 значением 20, затем возврат к сохранённым основным парам через EXX.
                LD (IY + @FActionRecord.ClassCode), @ActionClass19SpawnConst.ChildClass
                LD (IY + @FActionRecord.EffectReserve), @ActionClass19SpawnConst.ControlByte13
                EXX
                ; Проверка временной метки в бите 7 B, она относится к коду вида, не к биту 7 ReuseByte.
                BIT @ActionClass19SpawnConst.TemporaryBit, B
                LD A, @ActionClass19SpawnConst.ChildEffectMask
                JR NZ, @Action.CreateCargoAndUpdateList.StoreTag                ; переход, если временная метка B установлена, записать ребёнку ReuseByte=10

                ; Обнуление ReuseByte ребёнка для остальных нормализованных кодов.
                XOR A
                ; Сохранение маски эффекта и нормализованного кода в PickupKind с удалением временного бита 7.
StoreTag:       LD (IY + @FActionRecord.ReuseByte), A
                RES @ActionClass19SpawnConst.TemporaryBit, B
                LD (IY + @FActionRecord.PickupKind), B
                ; Расчёт кода списка из сохранённого R-образованного HL, подстановка адреса IY в оригинале отсутствует.
                CALL @Action.RecordAddressToIndex.Entry
                LD E, A
                ; Подготовка просмотра фиксированного списка с A01C, код для записи сохранён в E.
                LD HL, @ActionCandidateListData.Slot00.Code - 1
                ; Поиск ячейки FF либо недоступной записи до маркера FE, нулевой индекс является обычным элементом.
NextItem:       INC HL
                LD A, (HL)
                CP @ActionCandidateListConst.ListEnd
                JR C, @Action.CreateCargoAndUpdateList.CheckOld                 ; переход, если прочитан обычный код меньше FE, проверить доступность указанной записи

                RET Z                                                           ; выход, если прочитан FE, не добавлять новый код за маркером

                ; Замена FF производным кодом E, в том числе разрешённым значением FE.
                LD (HL), E
                RET

                ; Проверка старшего байта Component0 существующей цели, курсор списка сохраняется через EXX.
CheckOld:       EXX
                CALL @Action.RecordIndexToAddress.Entry
                INC L
                LD A, (HL)
                CP @ActionReuseConst.ReusableHigh
                EXX
                JP NZ, @Action.CreateCargoAndUpdateList.NextItem                ; переход, если указанная запись имеет High не равный 80, сохранить ячейку и искать следующую

                ; Замена недоступной цели производным кодом E без повторного преобразования адреса ребёнка.
                LD (HL), E
                RET

                endmodule
                endmodule
