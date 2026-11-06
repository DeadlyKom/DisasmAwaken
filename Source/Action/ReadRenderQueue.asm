                module Action
                module ReadRenderQueue
                ; Документация [алгоритм и проверка](../../Docs/ActionRenderQueueControl.md)
                ; -----------------------------------------
                ; Восстановление стека чтения очереди и загрузка снимка узла с обновлением AY
                ; исходная запись 17, код ACTION банка 0, адреса E4A6..E4DA, смещения #84A6..#84DA
                ; In:
                ;   основной Entry не принимает числовые аргументы в HL, DE, BC и AF
                ;   SavedEntrySP по E4A7 задаёт восстанавливаемый стек, Head содержит смещение головы страницы 8F либо 01
                ;   дополнительный LoadNode по E4B1 принимает HL как указатель FActionRenderNode, на CPU-стеке доступен возврат всего обхода
                ;   для LoadNode курсоры AY и смеситель удовлетворяют договору UpdateAyEffects, R влияет на шум, IRQ не вмешиваются
                ;   два неизвестных байта узла 01 и 02 не интерпретируются, ACTION доступен в банке 0
                ; Out:
                ;   Entry восстанавливает SP=SavedEntrySP, A=Head, H=8F, L и DE, BC, F сохраняются, переход в SelectRenderQueueNode по E4FF
                ;   если селектор видит Head=01, он возвращается по восстановленному стеку, иначе передаёт HL в LoadNode
                ;   LoadNode сохраняет входной HL словом на стеке и записывает адрес этого слова в SavedNodeSP по E4D6
                ;   по полям узла восстанавливаются HeaderWord0, PhasePair, Phase2, Output0, Output1 и Output2
                ;   после чтения полей восстанавливается SP=SavedNodeSP, затем исполняется настоящий UpdateAyEffects
                ;   LoadNode заканчивается перед E4DB, SP равен входному SP минус 2, сохранённый указатель узла остаётся на вершине
                ;   после LoadNode DE=Output1, BC=BFFD, A=max(4, ChannelCLevel >> 1), F соответствует CP половины уровня с 4
                ;   после LoadNode H равен старшему байту продвинутого курсора B либо нулю при отключённом B, L равен 00 либо 20 по порогу R
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются по обоим входам, paging не меняется
                ;   Entry сам RAM не пишет, LoadNode использует четыре дополнительных байта CPU-стека и выполняет обмен AY по договору UpdateAyEffects
                ; Corrupt:
                ;   HL, DE, BC, AF, SP, R по выбранному входу, SavedNodeSP, восстановленные переменные снимка, курсоры AY, четыре байта стека и регистры AY по LoadNode
                ; Note:
                ;   Entry и LoadNode имеют разные границы модели, запись SavedEntrySP выполняется ранее в прологе UnknownE020
                ;   при загрузке Phase2 POP AF также читает F из старшего байта PhasePair, последующий AY-потребитель заменяет этот F
                ;   полное исполнение RenderQueuedObject и всех вызовов вывода не входит в договор загрузки
                ;   частота AY-тиков при обходе и слышимое звучание не подтверждены, R учитывается в точке чтения LD A,R
                ; -----------------------------------------
                ; -----------------------------------------
                ; Начало чтения очереди
                ; Восстановление сохранённого до обхода SP, он нужен для завершающего RET всей очереди.
Entry:          LD SP, #0000
                ; Чтение головы и подготовка страницы узлов без изменения входного F.
                LD A, (@ActionRenderQueueInsertState.Head)
                LD H, @ActionRenderQueueConst.Page
                JP @Action.SelectRenderQueueNode.Entry

                ; -----------------------------------------
                ; Загрузка выбранного узла
                ; Сохранение указателя узла на обычном CPU-стеке и адреса его слова перед чтением данных через SP.
LoadNode:       PUSH HL
                LD (@ActionRenderQueueControlState.SavedNodeSP), SP
                ; Расчёт адреса HeaderWord0, два неизвестных байта узла пропускаются.
                INC L
                INC L
                INC L
                LD SP, HL
                ; Восстановление двух исходных слов заголовка снимка в физическом порядке полей.
                POP HL
                LD (@ActionRenderQueueInsertState.HeaderWord0), HL
                POP HL
                LD (@ActionRenderQueueInsertState.PhasePair), HL
                ; Расчёт положения SP для чтения Phase2 через A, F читается из уже использованного старшего байта PhasePair.
                DEC SP
                POP AF
                LD (@ActionRenderQueueInsertState.Phase2), A
                ; Восстановление трёх слов Output0, Output1 и Output2 из полей Components.
                POP HL
                LD (@ActionPatchedVectorState.Output0), HL
                POP DE
                LD (@ActionPatchedVectorState.Output1), DE
                POP BC
                LD (@ActionPatchedVectorState.Output2), BC
                ; Восстановление обычного стека, сохранённый указатель узла остаётся на его вершине.
                LD SP, #0000
                ; Обновление настоящего AY-потребителя перед отдельной цепочкой вывода RenderQueuedObject.
                CALL @Action.UpdateAyEffects.Entry
                ; JP @Action.RenderQueuedObject.Entry, продолжение в RenderQueuedObject.asm

                ; -----------------------------------------
                endmodule
                endmodule
