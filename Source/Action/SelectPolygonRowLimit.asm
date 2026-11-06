                module Action
                module SelectPolygonRowLimit
                ; Документация [алгоритм и проверка](../../Docs/ActionPolygonRowSelection.md)
                ; -----------------------------------------
                ; Выбор ближайшего предела строк с приоритетом левого ребра и настройкой следующего перехода
                ; исходная запись 17, адреса D4C1..D4F4
                ; In:
                ;   HL содержит H текущей страницы масок, входной L не используется
                ;   DE содержит D текущей строки, входной E не используется, BC содержит сохраняемый пиксельный адрес
                ;   AF входных аргументов не задаёт, MaximumRow, LeftEndRow и RightEndRow содержат строки от 0 до 95
                ;   HL', DE', BC', AF', IX и IY содержат сохраняемый контекст строкового ядра
                ;   ACTION доступен на запись в банке 0, SP принадлежит вызывающему ядру и данным блоком не используется
                ; Out:
                ;   HL содержит прежний H и L=MaximumRow, DE содержит прежний D и E=LeftEndRow, BC сохранён
                ;   RowLimit равен min(MaximumRow,LeftEndRow,RightEndRow)
                ;   если RightEndRow меньше min(LeftEndRow,MaximumRow), RowBranch=3B для подготовки правого ребра
                ;   иначе при LeftEndRow меньше MaximumRow выбран RowBranch=45 для подготовки левого ребра
                ;   во всех остальных случаях RowBranch=36 для восстановления CPU-стека и окончания заливки
                ;   A равен выбранному RowBranch, F относится к CP RightEndRow,min(LeftEndRow,MaximumRow)
                ;   HL', DE', BC', AF', IX, IY, SP, I, IM, IFF и paging сохранены, R меняется
                ;   управление передано JP D22D на общую инструкцию INC D перед рисованием строки, адрес возврата в стек не добавляется
                ;   ровно по одному байту записано в RowLimit и RowBranch, другие области RAM и порты не изменяются
                ; Corrupt:
                ;   HL, только L, DE, только E, AF, R, два операнда RowLimit и RowBranch
                ; Note:
                ;   равные пределы рёбер выбирают левую цепочку, если её предел ещё меньше общего максимума
                ;   два сравнения необходимы для сохранения исходного приоритета, равенство общему максимуму завершает заполнение
                ;   D22D увеличивает D перед рисованием, после строки D содержит номер следующей строки для проверки предела
                ;   884736 сценариев исчерпывают три входные строки 0..95, сверены регистры кроме R и исчерпывающий журнал записей
                ;   целое строковое ядро, R/T, IRQ, сборка и нативное исполнение этим договором не доказываются
                ; -----------------------------------------
                ; -----------------------------------------
                ; Общий предел и пределы двух рёбер
                ; Чтение изменяемого общего максимума и текущего предела левой цепочки.
Entry:          LD L, #00
                LD E, #00
                ; Проверка достижения общего максимума левой цепочкой, флаги сохраняются при чтении правого предела.
                LD A, E
                CP L
                LD A, (@ActionPolygonPreparationState.RightEndRow)
                JR C, @Action.SelectPolygonRowLimit.CompareEdges                ; переход, если левый предел меньше общего максимума, сравнить два ребра

                ; Проверка правого предела относительно общего максимума при уже достигшей максимума левой цепочке.
                CP L
                JR C, @Action.SelectPolygonRowLimit.FinishAtRight               ; переход, если правый предел меньше общего максимума, подготовить следующее правое ребро

                ; -----------------------------------------
                ; Завершение по общему максимуму
                ; Обновление RowLimit общим максимумом и перехода к восстановлению CPU-стека.
FinishAtMax:    LD A, L
                LD (@ActionPolygonPreparationState.RowLimit), A
                LD A, @ActionPolygonRowSelectionConst.StopOffset
                LD (@ActionPolygonPreparationState.RowBranch), A
                ; Продолжение строки по D22D, текущее значение D уже подготовлено вызывающей цепочкой.
                JP @Action.PolygonFillRows.DrawRow

                ; -----------------------------------------
                ; Выбор ближайшего ребра
                ; Проверка правого предела относительно левого с приоритетом левого при равенстве.
CompareEdges:   CP E
                JR C, @Action.SelectPolygonRowLimit.FinishAtRight               ; переход, если правый предел строго меньше левого, подготовить следующее правое ребро

                ; Обновление RowLimit левым пределом и перехода к подготовке левого ребра.
FinishAtLeft:   LD A, E
                LD (@ActionPolygonPreparationState.RowLimit), A
                LD A, @ActionPolygonRowSelectionConst.LeftOffset
                LD (@ActionPolygonPreparationState.RowBranch), A
                ; Продолжение строки по D22D после выбора левой цепочки.
                JP @Action.PolygonFillRows.DrawRow

                ; -----------------------------------------
                ; Правое ребро достигает предела раньше
                ; Обновление RowLimit правым пределом и перехода к подготовке правого ребра.
FinishAtRight:  LD (@ActionPolygonPreparationState.RowLimit), A
                LD A, @ActionPolygonRowSelectionConst.RightOffset
                LD (@ActionPolygonPreparationState.RowBranch), A
                ; Продолжение строки по D22D после выбора правой цепочки.
                JP @Action.PolygonFillRows.DrawRow

                ; -----------------------------------------
                endmodule
                endmodule
