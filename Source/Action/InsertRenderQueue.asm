                module Action
                module InsertRenderQueue
                ; Физические поля [очередь и параметры](../../Docs/ActionQueueParameterPhysicalData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionRenderQueueInsert.md)
                ; -----------------------------------------
                ; Вставка снимка объекта в связанную очередь по исходному знаковому сравнению глубины
                ; исходная запись 17, код ACTION банка 0, адреса E40F..E4A5, смещения #840F..#84A5
                ; In:
                ;   HL сохраняется только при пустом и исчерпанном списке, DE, BC и AF аргументов не задают
                ;   HL', DE', BC', AF' сохраняются, IX и IY служат указателями на узлы
                ;   Output0, Output1, Output2 задают три слова снимка, Input1 читается в DE и не участвует в сортировке
                ;   Head содержит младший байт первого узла либо 01, FreeOffset задаёт 00, 0E, ..., EE либо FC при исчерпании
                ;   узлы находятся в странице 8F, конечная цепочка Next не содержит циклов, глубина узла читается по смещению 0C
                ;   HeaderWord0 по 9B8D сохраняет частично неизвестный заголовок, PhasePair по 9B12 содержит Phase0/Phase1, Phase2 по 9B14 третью фазу
                ;   ACTION доступен в банке 0, IRQ не вмешиваются, SP используется для записи данных и не является возвращаемым стеком этого фрагмента
                ; Out:
                ;   BC=Output2, DE=Input1 по всем путям, проверяется только бит Sign результата word(depth_узла - Output2 - Carry)
                ;   Carry перед каждым сравнением равен результату CP смещения узла с 01, для смещения 00 он равен 1
                ;   первый отрицательный результат задаёт вставку перед этим узлом, отсутствие такого результата задаёт вставку в конец
                ;   при FreeOffset=FC записей RAM нет, A=FC, F=6A, SP сохранён, продолжение по E4A6
                ;   при отказе пустого списка HL, IX и IY сохранены, иначе HL содержит последнее сравнение, IX указывает предшественника либо исходную голову
                ;   при обходе после головы IYH=8F, IYL содержит последний проверенный следующий узел либо исходный IYL, пока следующего узла не было
                ;   при успехе новый узел получает Next, Head либо Next предшественника указывает на него, FreeOffset увеличен на 14
                ;   поля HeaderWord0, PhasePair, Phase2 и три слова Output0..2 записаны по смещениям 03..0D, байты 01 и 02 сохранены
                ;   после успеха HL=HeaderWord0, DE=Input1, BC=Output2, A=Phase2, F соответствует ADD старого FreeOffset,0E
                ;   после успеха SP=адрес нового узла + 3, продолжение по E0E2, входной SP не восстанавливается
                ;   HL', DE', BC', AF', I, IM и IFF сохраняются, вызовов процедур и портовых операций нет
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IY, SP при успехе, R, Head либо связь предшественника, FreeOffset и данные нового узла
                ; Note:
                ;   это исходная очередь отрисовки, имя описывает наблюдаемые поля снимка и последующий потребитель, весь игровой цикл ещё не доказан
                ;   SBC не заменяется знаковым сравнением без оборачивания, Overflow отдельно не проверяется, равные глубины у смещения 00 дают отрицательный результат
                ;   PUSH AF пишет временный F по смещению 06, следующий PUSH HL заменяет этот байт старшим байтом PhasePair
                ;   SP после записи указывает внутрь узла, последующее E0E2 само меняет стек, обычного RET здесь нет
                ;   страница 8F в этой фазе является рабочей областью, исходные дисковые байты 8F00 не объявляются начальными узлами
                ;   неизвестные байты 01 и 02 сохраняются и явно остаются неизвестными, память для новых узлов не выделяется
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка ключа очереди
                ; Чтение глубины Output2, Input1 возвращается в DE и здесь не участвует в сравнении.
Entry:          LD BC, (@ActionPatchedVectorState.Output2)
                LD DE, (@ActionPatchedVectorState.Input1)
                ; Проверка пустой цепочки по Head=01.
                LD A, (@ActionRenderQueueInsertState.Head)
                CP @ActionRenderQueueConst.EndLink
                JR Z, @Action.InsertRenderQueue.InsertHead                      ; переход, если Head равен 01, вставить узел перед пустой цепочкой

                ; Создание указателя IX на голову очереди в странице 8F, Carry от CP сохраняется.
                LD IXH, @ActionRenderQueueConst.Page
                LD IXL, A
                ; Чтение глубины головы и расчёт разности с Output2 и сохранённым займом.
                LD L, (IX+FActionRenderNode.Components.Component2.Low)
                LD H, (IX+FActionRenderNode.Components.Component2.High)
                SBC HL, BC
                JP M, @Action.InsertRenderQueue.InsertHead                      ; переход, если бит Sign разности головы установлен, вставить перед головой

                ; Подготовка страницы IY для последующих узлов.
                LD IYH, @ActionRenderQueueConst.Page
                ; -----------------------------------------
                ; Поиск места вставки
                ; Чтение Next предшественника и проверка конца цепочки, CP также задаёт Carry следующего SBC.
FindNext:       LD A, (IX+FActionRenderNode.Next)
                CP @ActionRenderQueueConst.EndLink
                JR Z, @Action.InsertRenderQueue.InsertTail                      ; переход, если Next равен 01, вставить после последнего узла

                ; Создание указателя IY на следующий узел без изменения Carry.
                LD IYL, A
                ; Чтение глубины следующего узла и расчёт исходной разности с займом, смещение 00 даёт дополнительную единицу.
                LD L, (IY+FActionRenderNode.Components.Component2.Low)
                LD H, (IY+FActionRenderNode.Components.Component2.High)
                SBC HL, BC
                JP M, @Action.InsertRenderQueue.InsertMiddle                    ; переход, если бит Sign разности следующего узла установлен, вставить между IX и IY

                ; Обновление предшественника для следующей проверки.
                LD A, IYL
                LD IXL, A
                JP @Action.InsertRenderQueue.FindNext

                ; -----------------------------------------
                ; Вставка перед головой
                ; Проверка свободного смещения на FC, отказ не меняет цепочку и стек.
InsertHead:     LD A, (@ActionRenderQueueInsertState.FreeOffset)
                CP @ActionRenderQueueConst.FullOffset
                JP Z, @Action.ReadRenderQueue.Entry                             ; переход, если FreeOffset равен FC, очередь исчерпана

                ; Создание нового узла с прежней головой в Next и обновление Head.
                LD L, A
                LD H, @ActionRenderQueueConst.Page
                LD A, (@ActionRenderQueueInsertState.Head)
                LD (HL), A
                LD A, L
                LD (@ActionRenderQueueInsertState.Head), A
                JP @Action.InsertRenderQueue.WritePayload

                ; -----------------------------------------
                ; Вставка в конец
                ; Проверка свободного смещения перед изменением Next последнего узла.
InsertTail:     LD A, (@ActionRenderQueueInsertState.FreeOffset)
                CP @ActionRenderQueueConst.FullOffset
                JR Z, @Action.ReadRenderQueue.Entry                             ; переход, если FreeOffset равен FC, очередь исчерпана

                ; Обновление Next предшественника и установка конечного маркера нового узла.
                LD (IX+FActionRenderNode.Next), A
                LD L, A
                LD H, @ActionRenderQueueConst.Page
                LD (HL), @ActionRenderQueueConst.EndLink
                JP @Action.InsertRenderQueue.WritePayload

                ; -----------------------------------------
                ; Вставка между узлами
                ; Проверка свободного смещения до изменения двух связей.
InsertMiddle:   LD A, (@ActionRenderQueueInsertState.FreeOffset)
                CP @ActionRenderQueueConst.FullOffset
                JR Z, @Action.ReadRenderQueue.Entry                             ; переход, если FreeOffset равен FC, очередь исчерпана

                ; Сохранение прежнего Next в новом узле и замена Next предшественника.
                LD L, A
                LD H, @ActionRenderQueueConst.Page
                LD A, (IX+FActionRenderNode.Next)
                LD (IX+FActionRenderNode.Next), L
                LD (HL), A
                LD A, L
                ; -----------------------------------------
                ; Запись снимка через SP
                ; Расчёт следующего свободного смещения с шагом 14, SP ставится за конец нового узла.
WritePayload:   ADD A, FActionRenderNode
                LD (@ActionRenderQueueInsertState.FreeOffset), A
                LD L, A
                LD SP, HL
                ; Запись трёх слов снимка в обратном порядке, Output2 затем Output1 и Output0.
                PUSH BC
                LD HL, (@ActionPatchedVectorState.Output1)
                PUSH HL
                LD HL, (@ActionPatchedVectorState.Output0)
                PUSH HL
                ; Запись Phase2 через PUSH AF, временный F ниже него затем перекрывается.
                LD A, (@ActionRenderQueueInsertState.Phase2)
                PUSH AF
                ; Смещение SP на байт для упаковки трёх исходных полей без добавления выравнивания.
                INC SP
                ; Запись PhasePair, его старший байт заменяет временный F.
                LD HL, (@ActionRenderQueueInsertState.PhasePair)
                PUSH HL
                ; Запись HeaderWord0, байты узла 01 и 02 остаются нетронутыми.
                LD HL, (@ActionRenderQueueInsertState.HeaderWord0)
                PUSH HL
                JP @Action.RenderSceneFrame.AdvanceRecord

                ; -----------------------------------------
                endmodule
                endmodule
