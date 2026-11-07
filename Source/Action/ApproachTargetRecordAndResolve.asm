                module Action
                module ApproachTargetRecordAndResolve
                ; Документация [алгоритм и проверка](../../Docs/ActionArrivalState.md)
                ; -----------------------------------------
                ; Сближение с выбранной записью, обновление связи и завершение через большой эффект
                ; исходная запись 17, адреса F57F..F669
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает текущую FActionRecord
                ;   TargetIndex задаёт обычный полный индекс цели, доступны поля целевой записи и три текущих Components
                ;   действуют договоры SelectRecordByIndex, RecordIXToIndex, ApproachWordAndAccumulate, QueueTextItemBank1 и большого эффекта
                ;   OBJECT3D банка 4, эффект банка 3, Controls банка 1 и исходные списки игровых и эффектных записей доступны
                ;   ROM выбрана по фактическому paging, код в общей RAM и ACTION доступны, до 18 дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   до проверки активности цели у неё устанавливается бит 1 LinkFlags, Unknown15 получает текущий Unknown0D, LinkedIndex индекс текущего IX
                ;   при Component0.High цели=80 ненулевой Unknown11 пытается поставить текст F248 в очередь Controls, затем большой эффект выполняется на текущем IX
                ;   при доступной цели три Components приближаются настоящим ApproachWordAndAccumulate с общим OR-накопителем в C'
                ;   первая и вторая рассчитанные Components записываются сразу, третья только при ненулевом накопителе остаточных старших байтов
                ;   на дальнем пути все три результата сохранены, фазы увеличены на 1, 2 и 3, Base0/1/2 UpdateRecordComponents обнулены, затем внешний RET
                ;   на ближнем пути третья рассчитанная компонента не сохраняется, при StateCode цели, отличном от FF, текущая запись помечается для повторного использования
                ;   затем у цели устанавливается бит 2 LinkFlags, ненулевой Unknown11 вызывает очередь текста F293
                ;   только при таком уведомлении и полном классе цели 0, 5, 6 или 7 ArrivalCount увеличивается на один по модулю 65536
                ;   ближний путь вызывает большой эффект на выбранной цели с сохранением исходного IX, потерянный путь на текущей записи
                ;   на дальнем пути HL=0, DE адрес цели, BC её третья компонента, A=C' общий накопитель, F от последнего INC OffsetPhase2, остальные альтернативные пары и AF' сохраняются
                ;   после эффекта HL, DE, BC, AF, HL', DE', BC', AF', IY и R определяются полным эффектом и игровыми детьми, IX, I/IM/IFF сохраняются
                ;   все пути выполняют внешний RET, SP=входной SP+2, дальний путь paging не меняет, очередь и эффект заканчиваются полной страницей 10
                ; Corrupt:
                ;   HL, DE, BC, AF, C', IY, R, поля связи цели, компоненты и фазы текущей записи, операнды, CPU-стек, условно остальные альтернативные пары, очередь, эффектные и игровые записи, ArrivalCount и 7FFD
                ; Note:
                ;   ближняя область задаётся нулём OR свёрнутых старших байтов остатка, это не точное совпадение трёх координат
                ;   проверка StateCode цели выполняется через обычный индекс повторно, StateCode=FF пропускает только освобождение текущей записи
                ;   бит 2 LinkFlags цели устанавливается и при StateCode=FF, очередь может молча отклонить сообщение, счётчик от успешности приёма не зависит
                ;   70256 сценариев включили все полные классы эффекта, все разности первого слова, 26 физических целей, самовыбор, уведомления и полные эффектные списки
                ;   сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие OUT, пути эффекта включают игровые дочерние записи классов ниже 16
                ;   ROM в модели синтетическая, значения 0000 и 0100 различаются, реальные игровые сообщения не отрисовывались потребителем очереди
                ;   индексы вне физических записей, полное произведение входов, аппаратные IRQ, точные T, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Поиск обычной целевой записи по TargetIndex, специальной обработки FF здесь нет.
Entry:          LD A, (IX + @FActionRecord.TargetIndex)
                CALL @Action.SelectRecordByIndex.Entry
                ; Обновление бита обратной связи, Unknown15 и LinkedIndex цели до проверки её активности.
                SET @ActionArrivalConst.LinkedBit, (IY + @FActionRecord.LinkFlags)
                LD A, (IX + @FActionRecord.Unknown0D)
                LD (IY + @FActionRecord.Unknown15), A
                CALL @Action.RecordIXToIndex.Entry
                LD (IY + @FActionRecord.LinkedIndex), A
                ; Проверка полного старшего байта первой компоненты цели, C уже содержит младший байт.
                LD C, (IY + @FActionRecord.Components.Component0.Low)
                LD A, (IY + @FActionRecord.Components.Component0.High)
                CP @ActionReuseConst.ReusableHigh
                JR NZ, @Action.ApproachTargetRecordAndResolve.Approach          ; переход, если Component0.High цели не равен 80, начать три шага сближения

                ; Проверка ненулевого Unknown11 для уведомления о потерянной цели.
                LD A, (IX + @FActionRecord.Unknown11)
                AND A
                JR Z, @Action.ApproachTargetRecordAndResolve.EffectCurrent      ; переход, если Unknown11 равен нулю, пропустить очередь потерянной цели

                ; Создание запроса текста F248 в очереди банка 1 с сохранением DE, приём не гарантирован.
                PUSH DE
                LD DE, @ActionArrivalConst.MissingText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Выбор текущего IX для большого эффекта при недоступной цели.
EffectCurrent:  LD D, IXH
                LD E, IXL
                JP @Action.ApproachTargetRecordAndResolve.EffectTarget

                ; Подготовка первой базовой компоненты и очистка только альтернативного накопителя C'.
Approach:       LD B, A
                EXX
                LD C, #00
                EXX
                ; Расчёт первой текущей компоненты и немедленная запись результата независимо от итоговой близости.
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                CALL @Action.ApproachWordAndAccumulate.Entry
                LD (IX + @FActionRecord.Components.Component0.Low), L
                LD (IX + @FActionRecord.Components.Component0.High), H
                ; Расчёт второй компоненты относительно цели и немедленная запись результата.
                LD C, (IY + @FActionRecord.Components.Component1.Low)
                LD B, (IY + @FActionRecord.Components.Component1.High)
                LD L, (IX + @FActionRecord.Components.Component1.Low)
                LD H, (IX + @FActionRecord.Components.Component1.High)
                CALL @Action.ApproachWordAndAccumulate.Entry
                LD (IX + @FActionRecord.Components.Component1.Low), L
                LD (IX + @FActionRecord.Components.Component1.High), H
                ; Расчёт третьей компоненты с общим накопителем остатка, запись пока отложена.
                LD C, (IY + @FActionRecord.Components.Component2.Low)
                LD B, (IY + @FActionRecord.Components.Component2.High)
                LD L, (IX + @FActionRecord.Components.Component2.Low)
                LD H, (IX + @FActionRecord.Components.Component2.High)
                CALL @Action.ApproachWordAndAccumulate.Entry
                ; Проверка общего C' после трёх шагов, DE сохраняет адрес выбранной записи.
                LD E, IYL
                LD D, IYH
                EXX
                LD A, C
                EXX
                AND A
                JR Z, @Action.ApproachTargetRecordAndResolve.Reached            ; переход, если общий накопитель равен нулю, обработать ближнюю область без записи третьего результата

                ; Обновление третьей компоненты только на дальнем пути.
                LD (IX + @FActionRecord.Components.Component2.Low), L
                LD (IX + @FActionRecord.Components.Component2.High), H
                ; Обновление циклических фаз шагами 1, 2 и 3, байтовое оборачивание сохраняется.
                INC (IX + @FActionRecord.OffsetPhase0)
                INC (IX + @FActionRecord.OffsetPhase1)
                INC (IX + @FActionRecord.OffsetPhase1)
                INC (IX + @FActionRecord.OffsetPhase2)
                INC (IX + @FActionRecord.OffsetPhase2)
                INC (IX + @FActionRecord.OffsetPhase2)
                ; Обновление трёх существующих базовых операндов нулевым словом перед внешним возвратом.
                LD HL, #0000
                LD (@ActionRecordUpdateState.Base0), HL
                LD (@ActionRecordUpdateState.Base1), HL
                LD (@ActionRecordUpdateState.Base2), HL
                RET

                ; Повторный поиск адреса StateCode цели по полному TargetIndex текущей записи.
Reached:        LD A, (IX + @FActionRecord.TargetIndex)
                CALL @Action.RecordIndexToAddress.Entry
                LD A, L
                OR @ActionArrivalConst.StateOffset
                LD L, A
                LD A, (HL)
                INC A
                JR Z, @Action.ApproachTargetRecordAndResolve.MarkArrival        ; переход, если StateCode цели равен FF, не освобождать текущую запись

                ; Обновление текущей записи до кода доступности 8000 с однократным FF-пропуском повторного поиска.
                CALL @Action.MarkRecordForReuse.Entry
                ; Обновление бита 2 LinkFlags цели после достижения ближней области.
MarkArrival:    SET @ActionArrivalConst.ReachedBit, (IY + @FActionRecord.LinkFlags)
                ; Проверка Unknown11 перед уведомлением и отдельным учётом выбранных полных классов.
                LD A, (IX + @FActionRecord.Unknown11)
                AND A
                JR Z, @Action.ApproachTargetRecordAndResolve.EffectTarget       ; переход, если Unknown11 равен нулю, пропустить уведомление и счётчик

                ; Создание запроса текста F293 в очереди Controls банка 1 без признака успешности в регистрах.
                PUSH DE
                LD DE, @ActionArrivalConst.ReachedText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Проверка полного класса цели для увеличения ArrivalCount независимо от принятия текста.
                LD A, (IY + @FActionRecord.ClassCode)
                CP #00
                JP Z, @Action.ApproachTargetRecordAndResolve.CountArrival       ; переход, если полный ClassCode цели равен 0, увеличить счётчик ближних целей

                CP #05
                JP Z, @Action.ApproachTargetRecordAndResolve.CountArrival       ; переход, если полный ClassCode цели равен 5, увеличить счётчик ближних целей

                CP #06
                JP Z, @Action.ApproachTargetRecordAndResolve.CountArrival       ; переход, если полный ClassCode цели равен 6, увеличить счётчик ближних целей

                CP #07
                JP NZ, @Action.ApproachTargetRecordAndResolve.EffectTarget      ; переход, если полный ClassCode цели не равен 7, пропустить увеличение счётчика

                ; Обновление слова ArrivalCount на один по модулю 65536 с сохранением рабочего HL.
CountArrival:   PUSH HL
                LD HL, (@ActionArrivalState.ArrivalCount)
                INC HL
                LD (@ActionArrivalState.ArrivalCount), HL
                POP HL
                ; Выбор IX из сохранённого DE для полного большого эффекта и восстановление исходного IX после возврата.
EffectTarget:   PUSH IX
                LD IXH, D
                LD IXL, E
                CALL @Action.PrepareLargeEffect.Entry
                POP IX
                RET

                endmodule
                endmodule
