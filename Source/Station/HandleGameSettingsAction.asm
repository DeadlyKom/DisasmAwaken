                module Station
                module HandleGameSettingsAction
                ; Документация [применение FSettingWord при закрытии, байтовый выбор, клавиатура и реальные кадры стека](../../Docs/SettingsPanelActions.md)
                ; -----------------------------------------
                ; Закрытие с применением игровых настроек, прокрутка и редактирование переключателя или клавиши
                ; исходная запись 4, файловые смещения #1848..#18CB
                ; In:
                ;   HL запасной рисователь, DE ключ панели, BC, AF и IX выполняют договоры RepaintAndFlag и CloseMenuOnRow
                ;   для закрытия SettingsText.Controls и массив FSettingWord от ControlOptions.Unknown00 доступны, подпись ограничена нулём
                ;   для прокрутки окно безопасно для очистки, ввод, callback, указатель и IRQ удовлетворяют ScrollWindowRows
                ;   для выбора младший TopRow и сохранённая строка дают допустимый индекс, родительские поля и стек доступны
                ;   для редактирования существуют реальные пробуждения десяти HALT ReadMatrixKey и последующее допустимое нажатие, окно и рисователи подготовлены
                ; Out:
                ;   при Carry RepaintAndFlag возвращается его контекст, выбор, применение и прокрутка подавлены
                ;   при Carry=0 и возвращённом A!=1 CloseMenuOnRow удаляет текущий ключ при совпадении символьных Y, затем ParseSettingsLabel применяет всю подпись
                ;   закрытие возвращает HL контекста перед ParseSettingsLabel, DE за обработанными FSettingWord, BC у нуля подписи, AF=0054
                ;   при несовпадении Y снимается старая XOR-полоса, сохранённая строка=FF, EndLimit=26, RenderCall внутреннего RenderRows соответствующего рисователя
                ;   ScrollWindowRows получает A=8 и полное слово TopRow, его итоговый HL записан обратно, остальные выходы согласно его договору
                ;   выбор единицей при младшем TopRow=FF возвращает основной AF=0050 без редактирования и рисования
                ;   иначе индекс равен TopRow.L плюс сохранённая строка по модулю 256, переключатель меняет Y на N, всякое иное старое значение на Y
                ;   клавишное поле сначала получает подчёркивание, затем допустимый результат ReadMatrixKey, промежуточные отказы повторяют ввод
                ;   после принятого значения BeginScreenUpdate, TryDrawGameSettings и EndScreenUpdate дают A=10, F и HL, DE, BC результата последнего условного рисования
                ;   на обычном завершении редактирования страница 10 и UpdateBlocked=0, альтернативные и индексные регистры по выполненным помощникам, SP после RET входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', BC' по прокрутке, IX по фактическим помощникам, подпись либо FSettingWord по ветви, список, экраны, указатель, TopRow, подсветка и операнды
                ; Note:
                ;   подпись меняется при выборе, FSettingWord записываются только при закрытии, исполнения всех будущих потребителей этим нет
                ;   полный TopRow используется прокруткой, выбор читает только младший байт и не отвергает FF сохранённой строки
                ;   индекс 26 является исходным последним редактируемым индексом, фактическая проверка шага остаётся двухступенчатой в ScrollWindowRows
                ;   после записи подчёркивания старое значение не восстанавливается, Cancel не предусмотрен, Caps Shift повторяет ввод
                ;   FSettingsEditFrame описывает два сохранённых слова перед рисованием, после POP BC остаётся FSettingsWaitFrame
                ;   модель реально сканирует матрицу, но HALT клавиатурной задержки освобождает явно без IRQ и без доказательства времени, IRQ рамки и прокрутки исполняются отдельно
                ;   только индекс 0 переключает Y/N, остальные редактируемые индексы 1..26 принимают любую клавишу кроме Caps Shift
                ;   перед ожиданием клавиши вызывается прямой DrawGameSettings, заключительный вызов условный, алиас ключа не заменяет точного адреса для последнего
                ;   шаблон содержит 43 позиции, из них 16 последних CR-подписей пустые, предел исходной прокрутки остаётся 26, записи сохранены без сокращения
                ; -----------------------------------------
                ; перерисовка и обработка геометрии перед действием установок игры
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено

                ; проверка единицы возвращённого селектора для выбора значения
                DEC A
                JP Z, @Station.HandleGameSettingsAction.SelectValue             ; переход, если возвращённый селектор равен 1, выбрать значение

                ; условное удаление текущей панели при совпадении символьных Y
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.HandleGameSettingsAction.ScrollRows             ; переход, если строки различаются, выполнить прокрутку

                ; обновление физических FSettingWord всей игровой подписью после удаления панели
                LD BC, @SettingsText.Controls
                LD DE, @ControlOptions.Unknown00
                JP @Station.ParseSettingsLabel.Entry

                ; подготовка игровой колонки и снятие прежней XOR-полосы
ScrollRows:     CALL @Station.SetupGameSettingsText.Entry
                LD DE, (@GameSettingsPanelState.HoverRows)
                LD A, (@PanelHoverState.GameSettingsRow)
                CALL @Station.XorRowIfSelected.Entry
                ; сброс номера подсветки после снятия старой полосы
                LD A, #FF
                LD (@PanelHoverState.GameSettingsRow), A
                ; обновление callback на внутренний RenderRows без новой рамки
                LD HL, @Station.DrawGameSettings.RenderRows
                LD (#A265), HL
                ; подготовка последнего индекса 26 для исходной прокрутки
                LD HL, @SettingsEditConst.GameLastRow
                LD (#A235), HL
                ; подготовка отступа 8 и полного TopRow
                LD A, #08
                LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                ; сохранение полного итогового индекса прокрутки
                LD (@GameSettingsPanelState.TopRow), HL
                RET

                ; проверка FF только младшего байта TopRow
SelectValue:    LD A, (@GameSettingsPanelState.TopRow)
                INC A
                RET Z                                                           ; выход, если младший TopRow равен FF, ничего не редактировать

                ; расчёт байтовой суммы TopRow и сохранённой строки, FF строки отдельно не проверяется
                DEC A
                LD C, A
                LD A, (@PanelHoverState.GameSettingsRow)
                ADD A, C
                LD C, A
                LD B, #00
                LD HL, @SettingsText.Controls
                ADD HL, BC
                LD A, C
                ; проверка единственного переключателя с индексом ноль
                AND A
                JR NZ, @Station.HandleGameSettingsAction.BeginKeyEdit           ; переход, если индекс ненулевой, начать ввод клавиши

                ; проверка прежнего Y, он меняется на N, остальные символы заменяются Y
                LD A, (HL)
                CP @SettingsLabelConst.YesChar
                LD A, @SettingsLabelConst.NoChar
                JR Z, @Station.HandleGameSettingsAction.StoreToggle             ; переход, если прежнее значение равно Y, записать подготовленный N

                LD A, @SettingsLabelConst.YesChar
                ; обновление одного символа переключателя без записи физических настроек
StoreToggle:    LD (HL), A
                JR @Station.HandleGameSettingsAction.Redraw

                ; обновление символа подчёркиванием перед ожиданием клавиши
BeginKeyEdit:   LD A, (HL)
                LD (HL), @SettingsEditConst.PendingGlyph
                ; создание снимка экрана перед промежуточным состоянием
                CALL @Station.BeginScreenUpdate.Entry
                ; создание FSettingsWaitFrame с ValuePointer поверх внешнего возврата
                PUSH HL
                ; создание FSettingsEditFrame с SavedIndex поверх кадра ожидания
                PUSH BC
                ; прямое рисование промежуточного состояния игры независимо от точного указателя списка
                CALL @Station.DrawGameSettings.Entry
                CALL @Station.EndScreenUpdate.Entry
                ; восстановление SavedIndex, на стеке остаётся ValuePointer и внешний возврат
                POP BC
                ; ожидание кода клавиатурной матрицы после десяти пробуждений HALT
ReadKey:        CALL @Station.ReadMatrixKey.Entry
                ; проверка Caps Shift перед записью принятой клавиши
                CP @SettingsEditConst.CapsShift
                JR Z, @Station.HandleGameSettingsAction.ReadKey                 ; переход, если прочитан Caps Shift, повторить ожидание

                ; снятие ValuePointer кадра ожидания после принятого кода
                POP HL
                ; обновление ровно одного символа принятой клавишей
                LD (HL), A
                ; создание снимка и условная перерисовка окончательного значения
Redraw:         CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.TryDrawGameSettings.Entry
                ; возобновление указателя и показ базового экрана
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
