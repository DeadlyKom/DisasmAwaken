                module Action
                module CreateLinkedMissileRecord
                ; Документация [алгоритм и проверка](../../Docs/ActionClass17Spawn.md)
                ; -----------------------------------------
                ; Создание связанной ракеты игрока или персонажа из альтернативных компонент
                ; исходная запись 17, перенесённый код банка 5, адреса 60E8..6144
                ; In:
                ;   HL и DE числовых аргументов не задают, B задаёт копируемый индекс в Phase0OrLink, C обычный индекс целевой записи
                ;   A задаёт начальный EffectReserve, HL', DE', BC' задают три копируемых Components, A' начальный Unknown11
                ;   доступны исходный список FActionRecord до маркера 8080 и запись по A100+64*C, ограничение индекса не добавляется
                ;   перенесённый общий код банка 5, ACTION банка 0 и изменяемый InitialParam доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   HL при успехе равен 0040, при отсутствии слота сохраняется
                ;   DE при успехе равен A100+64*C+0B, при отсутствии слота равен 0040
                ;   BC сохраняется
                ;   AF при успехе содержит A=индекс ребёнка и F=45 OR (A AND 28), при отсутствии слота A=80/F=42
                ;   HL', DE', BC' сохраняются
                ;   AF' равен 0044 только при успехе, при отказе исходный AF' сохраняется
                ;   IX сохраняется, IY указывает выделенную запись либо маркер при отказе
                ;   I, IM, IFF и paging сохраняются, SP после внешнего RET равен входному SP+2
                ;   R добавляет стоимость FindReusableRecord и ещё 88 M1 при успехе либо 5 при отказе
                ;   InitialParam получает входной A даже при отсутствии слота, поиск может очистить и пропустить ReuseByte=FF
                ;   при успехе Components ребёнка получают входные альтернативные HL, DE и BC, ModelOffset=90, OffsetPhase0/1/2=0, StateCode=8
                ;   при инициализации ребёнка LinkedIndex=0 и LinkFlags=0, Phase0OrLink=B, Phase2OrTarget=C
                ;   Unknown11 получает входной A', ClassCode=11, EffectReserve получает входной A, TargetCodeStep=2, прочие поля сохраняются после действий поиска
                ;   затем у цели устанавливается бит 1 LinkFlags и её LinkedIndex получает индекс ребёнка, при совпадении цели с ребёнком его конечные LinkFlags=02 и LinkedIndex равен собственному индексу
                ; Corrupt:
                ;   HL, DE, AF, AF', IY, R, InitialParam, выделенная запись, обратная связь цели, шесть временных байтов CPU-стека, SP внешним RET
                ; Note:
                ;   Unknown11 ребёнка класса 17 соответствует авторскому LZS, ноль означает ракету персонажа, неноль ракету игрока, роли поля у других классов не переопределяются
                ;   авторский T_ROKET=#11 и модель ROKET по смещению #90 подтверждены исходными байтами, общий вход обслуживает ракеты игрока и персонажей
                ;   в 275 сценариях цель совпала с ребёнком, отдельно сверены окончательные поля после обратной связи и полное число M1 всех 66560 исполнений
                ;   выделенные записи выровнены на 64 байта, преобразование IY даёт нулевой L и устанавливает Z/PV, успешный SCF сохраняет их, признаком успеха служит Carry
                ;   C=FF здесь обычный индекс и не выбирает специальную запись A780, диапазон и побочные записи исходной адресной формулы сохранены
                ;   OffsetScaleLow, MissileRepeatDelay, ReuseByte после очистки поиска и остальные неинициализируемые поля не зануляются дополнительно
                ;   66560 сценариев проверили все 65536 пар B/C, все начальные параметры, занятые слоты, однократный FF-пропуск и отсутствие свободного слота
                ;   сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие поисковые и индексные дети
                ;   полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Сохранение начального EffectReserve в исходном операнде до поиска свободной записи.
Entry:          LD (@ActionClass17SpawnState.InitialParam), A
                ; Поиск свободного слота с сохранением обеих входных частей BC.
                PUSH BC
                CALL @Action.FindReusableRecord.Entry
                POP BC
                RET Z                                                           ; выход, если поиск достиг маркера без свободного слота, начальный параметр уже сохранён

                ; Копирование трёх Components из альтернативного набора в реальную выделенную запись.
InitializeSlot: EXX
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                LD (IY + @FActionRecord.Components.Component1.Low), E
                LD (IY + @FActionRecord.Components.Component1.High), D
                LD (IY + @FActionRecord.Components.Component2.Low), C
                LD (IY + @FActionRecord.Components.Component2.High), B
                EXX
                ; Обновление исходных нулевых фаз, полей связи, модели и состояния дочерней записи.
                XOR A
                LD (IY + @FActionRecord.ModelOffset), #90
                LD (IY + @FActionRecord.OffsetPhase0), A
                LD (IY + @FActionRecord.OffsetPhase1), A
                LD (IY + @FActionRecord.OffsetPhase2), A
                LD (IY + @FActionRecord.StateCode), #08
                LD (IY + @FActionRecord.LinkedIndex), A
                LD (IY + @FActionRecord.LinkFlags), A
                ; Сохранение индекса стрелявшего B в Phase0OrLink и индекса цели C в Phase2OrTarget ракеты.
                LD (IY + @FActionRecord.Phase0OrLink), B
                LD (IY + @FActionRecord.Phase2OrTarget), C
                ; Преобразование альтернативного A в начальный Unknown11, альтернативный AF получает 0044 от XOR.
                EX AF, AF'
                LD (IY + @FActionRecord.Unknown11), A
                ; Обновление полного класса 17, изменяемого начального параметра и шага кодов движения.
                LD (IY + @FActionRecord.ClassCode), #11
                LD (IY + @FActionRecord.EffectReserve), #00
                LD (IY + @FActionRecord.TargetCodeStep), #02
                ; Расчёт адреса обычной целевой записи по входному C без особой обработки FF.
                LD A, C
                CALL @Action.RecordIndexToAddress.Entry
                ; Расчёт адреса LinkFlags цели и установка флага ракетной атаки до обновления её LinkedIndex.
                LD A, L
                ADD A, #0C
                LD L, A
                SET @ActionArrivalConst.RocketAttackBit, (HL)
                ; Преобразование созданного адреса IY в обычный индекс и запись обратной ссылки у цели.
                DEC L
                EX DE, HL
                CALL @Action.RecordIYToIndex.Entry
                LD (DE), A
                ; Установка Carry как результата успешного создания, остальные флаги преобразования индекса сохраняются.
                SCF
                RET

                endmodule
                endmodule
