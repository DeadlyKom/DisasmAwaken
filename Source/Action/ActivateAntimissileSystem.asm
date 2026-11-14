                module Action
                module ActivateAntimissileSystem
                ; Документация [поиск ракеты противоракетной командой и общий вход вывода](../../Docs/ActionAntimissileCommand.md)
                ; -----------------------------------------
                ; Поиск первой ракеты класса 11 с целью 1A, установка признаков противоракетной обработки и вывод сегмента
                ; исходная запись 17, перенесённое ядро банка 5, адреса 722E..72BD
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, ненулевая CommandDelay запрещает команду
                ;   список начинается по A100, шаг 40, свободная запись имеет High=80, конечный маркер имеет Low=High=80
                ;   до маркера доступны ClassCode, Phase2OrTarget, LinkFlags и ViewPosition
                ;   банк 0 выбран, Controls банка 1 содержит очередь, действуют договоры QueueTextItemBank1 и CheckAndToggleLinkedOverlay.CheckDepthSigns
                ;   проекционные таблицы и экран подготовлены, изменяемые операнды доступны для записи, paging разблокирован
                ;   обычный стек допускает тридцать два дополнительных байта и не пересекает рабочие области детей, IRQ и повторный вход исключены
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, RAM и paging сохраняются
                ;   иначе задержка получает 5, сообщение F32D передаётся до поиска, CursorA получает EDC1 независимо от наличия ракеты
                ;   выбирается первая активная запись ClassCode=11 и Phase2OrTarget=1A, StateCode не проверяется
                ;   при достижении маркера HL указывает его Low, DE=0040, A=80, F=42, BC содержит пару Phase2OrTarget:ClassCode последней просмотренной активной записи либо исходную BC
                ;   у выбранной записи LinkFlags получает старое значение OR 09 до проверок её векторного контекста
                ;   при ViewPosition.X.High=80 HL указывает выбранную запись, DE=0040, BC=1A11, A=80, F=41, альтернативные регистры сохраняются
                ;   иначе три слова выбранной записи переходят в альтернативные BC, HL и DE, главные BC=0003, HL=00B0, DE=FFFF
                ;   Output0 и Input0..Input2 получают 0003, Output1 получает 00B0, Output2 получает FFFF, исходные операнды не восстанавливаются
                ;   после CALL внутреннего CheckDepthSigns действуют его проверки знаков, signed overflow и полный договор проекции, клиппинга и XOR-сегмента
                ;   IX восстанавливается на всех возвращающихся путях, SP после внешнего RET равен исходному SP+2, I, IM и IFF сохраняются
                ;   при нулевой задержке OUT 7FFD получает 11,10, итоговый paging равен 10, отказ очереди не отменяет поиск и изменения записи
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY по договору сегмента, R, задержка, CursorA, LinkFlags, шесть изменяемых слов, очередь, экран и буферы детей, paging и CPU-стек по пути
                ; Note:
                ;   оборудование PS1 и PS2 здесь не проверяется, бит 3 LinkFlags впоследствии выбирает их порог в CheckRecordEffectThreshold
                ;   ветвь ViewPosition.X.High=80 сохраняет уже установленные биты 0 и 3, отрицательная глубина и отказ проекции также их не отменяют
                ;   внутренний вход E835 пропускает поиск связанной записи и случайное создание обратной связи полной процедуры E804
                ;   197716 сценариев исполняют исходный обработчик, настоящую очередь, внутренний вход, проекцию и растеризатор
                ;   сверены регистры кроме R и тактов, все банки RAM и кратность записей вне тридцати двух временных байтов обычного стека
                ;   полное совместное произведение входов, IRQ, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Проверка задержки перед повторной противоракетной командой.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, сохранить состояние

                ; Обновление задержки и постановка сообщения до поиска подходящей ракеты.
                LD A, #05
                LD (@ActionMissileLaunchState.CommandDelay), A
                PUSH DE
                LD DE, @ControlsFlightText.AntimissileOn
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Выбор звукового потока независимо от результата поиска.
                LD HL, @ActionAyStreams.AntimissRow00
                LD (@ActionAyEffectState.CursorA), HL
                ; Подготовка адреса перед первой записью, NextRecord добавит размер FActionRecord.
                LD HL, @ActionObjectRecords.Record00.Components.Component0.High - @FActionRecord
                LD DE, @FActionRecord
                JP @Action.ActivateAntimissileSystem.NextRecord

                ; Проверка младшего байта свободной записи, пара 8080 завершает список.
CheckEndMarker: DEC L
                LD A, (HL)
                CP #80
                RET Z                                                           ; выход, если Low свободной записи равен 80, ракета не найдена

                INC L
                ; Поиск следующей записи, активность определяется только High первой компоненты.
NextRecord:     ADD HL, DE
                LD A, (HL)
                CP #80
                JR Z, @Action.ActivateAntimissileSystem.CheckEndMarker          ; переход, если High равен 80, проверить конечный маркер

                ; Чтение ClassCode и Phase2OrTarget исходными операциями над младшим байтом адреса.
                LD A, L
                ADD A, #11
                LD L, A
                LD C, (HL)
                DEC L
                DEC L
                DEC L
                LD B, (HL)
                SUB #11
                LD L, A
                ; Проверка класса ракеты, код состояния записи здесь не ограничивается.
                LD A, C
                CP #11
                JR NZ, @Action.ActivateAntimissileSystem.NextRecord             ; переход, если ClassCode не равен 11, продолжить поиск

                ; Проверка цели ракеты, только код 1A выбирается противоракетной командой.
                LD A, B
                CP #1A
                JR NZ, @Action.ActivateAntimissileSystem.NextRecord             ; переход, если Phase2OrTarget не равен 1A, продолжить поиск

                ; Сохранение вызывающего IX и выбор найденной физической FActionRecord.
                PUSH IX
                DEC L
                PUSH HL
                POP IX
                ; Обновление признаков обратной связи и противоракетного выбора порога до всех векторных отказов.
                SET @ActionLinkFlagsConst.BackLinkBit, (IX + @FActionRecord.LinkFlags)
                SET @ActionLinkFlagsConst.AntimissileBit, (IX + @FActionRecord.LinkFlags)
                ; Проверка маркера векторного контекста выбранной записи.
                LD A, (IX + @FActionRecord.ViewPosition.X.High)
                CP #80
                SCF
                JR Z, @Action.ActivateAntimissileSystem.RestoreIndex            ; переход, если ViewPosition.X.High равен 80, восстановить IX без отмены LinkFlags

                ; Подготовка трёх слов выбранной записи и сохранение их в альтернативном наборе.
                LD B, A
                LD C, (IX + @FActionRecord.ViewPosition.X.Low)
                LD L, (IX + @FActionRecord.ViewPosition.Y.Low)
                LD H, (IX + @FActionRecord.ViewPosition.Y.High)
                LD E, (IX + @FActionRecord.ViewPosition.Depth.Low)
                LD D, (IX + @FActionRecord.ViewPosition.Depth.High)
                EXX
                ; Обновление исходных изменяемых операндов, фиксированный второй контекст имеет BC=3, HL=176 и DE=-1.
                LD BC, #0003
                LD (@ActionPatchedVectorState.Output0), BC
                LD (@ActionPatchedVectorState.Input0), BC
                LD (@ActionPatchedVectorState.Input1), BC
                LD (@ActionPatchedVectorState.Input2), BC
                LD HL, #00B0
                LD (@ActionPatchedVectorState.Output1), HL
                LD DE, #FFFF
                LD (@ActionPatchedVectorState.Output2), DE
                ; Вызов внутреннего входа проверки двух контекстов, поиск связи и случайная обратная ссылка E804 пропускаются.
                CALL @Action.CheckAndToggleLinkedOverlay.CheckDepthSigns
                ; Восстановление IX на обоих путях после установки LinkFlags.
RestoreIndex:   POP IX
                RET

                endmodule
                endmodule
