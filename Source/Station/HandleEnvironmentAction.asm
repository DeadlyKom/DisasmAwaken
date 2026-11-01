                module Station
                module HandleEnvironmentAction
                ; Документация [применение FSettingWord при закрытии, байтовый выбор, клавиатура и реальные кадры стека](../../Docs/SettingsPanelActions.md)
                ; -----------------------------------------
                ; Закрытие с применением настроек среды, прокрутка, Y/N и ограниченный ввод клавиш или цветов
                ; исходная запись 4, файловые смещения #0D98..#0E39
                ; In:
                ;   HL запасной рисователь, DE ключ панели, BC, AF и IX выполняют договоры RepaintAndFlag и CloseMenuOnRow
                ;   для закрытия SettingsText.Interface и массив FSettingWord от InterfaceChoices.MouseOption доступны, подпись ограничена нулём
                ;   для прокрутки окно безопасно для очистки, ввод, callback, указатель и IRQ удовлетворяют ScrollWindowRows
                ;   для выбора младший TopRow и сохранённая строка дают допустимый индекс, родительские поля и стек доступны
                ;   для редактирования существуют реальные пробуждения десяти HALT ReadMatrixKey и последующее допустимое нажатие, окно и рисователи подготовлены
                ; Out:
                ;   при Carry RepaintAndFlag возвращается его контекст, выбор, применение и прокрутка подавлены
                ;   при Carry=0 и возвращённом A!=1 CloseMenuOnRow удаляет текущий ключ при совпадении символьных Y, затем ParseSettingsLabel применяет всю подпись
                ;   закрытие возвращает HL контекста перед ParseSettingsLabel, DE за обработанными FSettingWord, BC у нуля подписи, AF=0054
                ;   при несовпадении Y снимается старая XOR-полоса, сохранённая строка=FF, EndLimit=12, RenderCall внутреннего RenderRows соответствующего рисователя
                ;   ScrollWindowRows получает A=8 и полное слово TopRow, его итоговый HL записан обратно, остальные выходы согласно его договору
                ;   выбор единицей при младшем TopRow=FF возвращает основной AF=0050 без редактирования и рисования
                ;   иначе индекс равен TopRow.L плюс сохранённая строка по модулю 256, переключатель меняет Y на N, всякое иное старое значение на Y
                ;   клавишное поле сначала получает подчёркивание, затем допустимый результат ReadMatrixKey, промежуточные отказы повторяют ввод
                ;   после принятого значения BeginScreenUpdate, TryDrawEnvironmentPanel и EndScreenUpdate дают A=10, F и HL, DE, BC результата последнего условного рисования
                ;   на обычном завершении редактирования страница 10 и UpdateBlocked=0, альтернативные и индексные регистры по выполненным помощникам, SP после RET входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', BC' по прокрутке, IX по фактическим помощникам, подпись либо FSettingWord по ветви, список, экраны, указатель, TopRow, подсветка и операнды
                ; Note:
                ;   подпись меняется при выборе, FSettingWord записываются только при закрытии, исполнения всех будущих потребителей этим нет
                ;   полный TopRow используется прокруткой, выбор читает только младший байт и не отвергает FF сохранённой строки
                ;   индекс 12 является исходным последним редактируемым индексом, фактическая проверка шага остаётся двухступенчатой в ScrollWindowRows
                ;   после записи подчёркивания старое значение не восстанавливается, Cancel не предусмотрен, Caps Shift повторяет ввод
                ;   FSettingsEditFrame описывает два сохранённых слова перед рисованием, после POP BC остаётся FSettingsWaitFrame
                ;   модель реально сканирует матрицу, но HALT клавиатурной задержки освобождает явно без IRQ и без доказательства времени, IRQ рамки и прокрутки исполняются отдельно
                ;   индексы 0..3 переключают Y/N, 4..9 принимают любую клавишу кроме Caps Shift, 10..11 принимают коды 30..37, от 12 проверяются 30..31
                ;   оба предварительных и заключительных обращения к панели условные, отсутствие точного адреса либо C9 может пропустить рисование и сброс подсветки
                ; -----------------------------------------
                ; перерисовка и обработка геометрии до действия установок среды
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено

                ; проверка единицы в возвращённом селекторе действия
                DEC A
                JP Z, @Station.HandleEnvironmentAction.SelectValue              ; переход, если возвращённый селектор равен 1, выбрать значение

                ; условное удаление текущей панели при совпадении символьных строк Y
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.HandleEnvironmentAction.ScrollRows              ; переход, если строки различаются, выполнить прокрутку

                ; обновление физических FSettingWord из всей отредактированной подписи после удаления панели
                LD BC, @SettingsText.Interface
                LD DE, @InterfaceChoices.MouseOption
                JP @Station.ParseSettingsLabel.Entry

                ; подготовка колонки среды и снятие прежней XOR-полосы
ScrollRows:     CALL @Station.SetupEnvironmentText.Entry
                LD DE, (@EnvironmentPanelState.HoverRows)
                LD A, (@PanelHoverState.EnvironmentRow)
                CALL @Station.XorRowIfSelected.Entry
                ; сброс сохранённой строки после снятия старой полосы
                LD A, #FF
                LD (@PanelHoverState.EnvironmentRow), A
                ; обновление callback прокрутки, рамка и настройка повторно не вызываются
                LD HL, @Station.DrawEnvironmentPanel.RenderRows
                LD (#A265), HL
                ; подготовка последнего индекса двенадцать и верхнего отступа 8
                LD HL, @SettingsEditConst.EnvLastRow
                LD (#A235), HL
                LD A, #08
                ; чтение полного сохранённого индекса TopRow для прокрутки
                LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                ; сохранение полного результата прокрутки
                LD (@EnvironmentPanelState.TopRow), HL
                RET

                ; проверка FF только младшего байта TopRow
SelectValue:    LD A, (@EnvironmentPanelState.TopRow)
                INC A
                RET Z                                                           ; выход, если младший TopRow равен FF, ничего не редактировать

                ; расчёт байтового индекса значения, FF сохранённой строки отдельно не отбрасывается
                DEC A
                LD C, A
                LD A, (@PanelHoverState.EnvironmentRow)
                ADD A, C
                LD C, A
                LD B, #00
                LD HL, @SettingsText.Interface
                ADD HL, BC
                ; проверка первых четырёх переключателей Y/N
                LD A, C
                CP @SettingsEditConst.ToggleCount
                JR NC, @Station.HandleEnvironmentAction.BeginKeyEdit            ; переход, если индекс не меньше 4, начать клавиатурное редактирование

                ; проверка прежнего Y, только он меняется на N, остальные символы заменяются Y
                LD A, (HL)
                CP @SettingsLabelConst.YesChar
                LD A, @SettingsLabelConst.NoChar
                JR Z, @Station.HandleEnvironmentAction.StoreToggle              ; переход, если прежнее значение равно Y, записать подготовленный N

                LD A, @SettingsLabelConst.YesChar
                ; обновление одного символа переключателя без немедленного изменения FSettingWord
StoreToggle:    LD (HL), A
                JR @Station.HandleEnvironmentAction.Redraw

                ; обновление редактируемого символа подчёркиванием до начала ожидания клавиши
BeginKeyEdit:   LD A, (HL)
                LD (HL), @SettingsEditConst.PendingGlyph
                ; создание экранного снимка перед показом промежуточного подчёркивания
                CALL @Station.BeginScreenUpdate.Entry
                ; создание FSettingsWaitFrame с ValuePointer поверх внешнего ReturnAddress
                PUSH HL
                ; создание FSettingsEditFrame с SavedIndex поверх ValuePointer и ReturnAddress
                PUSH BC
                ; условное рисование промежуточного состояния только при точном адресе панели
                CALL @Station.TryDrawEnvironmentPanel.Entry
                CALL @Station.EndScreenUpdate.Entry
                ; восстановление SavedIndex, на стеке остаётся FSettingsWaitFrame
                POP BC
                ; ожидание кода настоящей матрицы после десяти пробуждений HALT
ReadKey:        CALL @Station.ReadMatrixKey.Entry
                ; проверка Caps Shift, эта клавиша не завершает редактирование
                CP @SettingsEditConst.CapsShift
                JR Z, @Station.HandleEnvironmentAction.ReadKey                  ; переход, если прочитан Caps Shift, снова ждать клавишу

                ; сохранение кода клавиши и проверка класса выбранного поля
                LD E, A
                LD A, C
                CP @SettingsEditConst.ColorStart
                JR C, @Station.HandleEnvironmentAction.StoreKey                 ; переход, если индекс меньше 10, принять любую клавишу кроме Caps Shift

                ; проверка однобитового Bright по индексу не меньше 12
                CP @SettingsEditConst.BrightIndex
                LD A, E
                JR NC, @Station.HandleEnvironmentAction.CheckBright             ; переход, если индекс не меньше 12, проверить цифру 0 либо 1

                ; проверка нижней границы цифр Ink и Paper
                CP @SettingsLabelConst.DigitZero
                JR C, @Station.HandleEnvironmentAction.ReadKey                  ; переход, если код меньше цифры 0, повторить ввод

                ; проверка верхней исключающей границы цифры 8 для Ink и Paper
                CP @SettingsEditConst.InkLimit
                JR NC, @Station.HandleEnvironmentAction.ReadKey                 ; переход, если код не меньше цифры 8, повторить ввод

                JR @Station.HandleEnvironmentAction.StoreKey

                ; проверка нижней границы цифр Bright
CheckBright:    CP @SettingsLabelConst.DigitZero
                JR C, @Station.HandleEnvironmentAction.ReadKey                  ; переход, если код меньше цифры 0, повторить ввод

                ; проверка верхней исключающей границы цифры 2 для Bright
                CP @SettingsEditConst.BitLimit
                JR NC, @Station.HandleEnvironmentAction.ReadKey                 ; переход, если код не меньше цифры 2, повторить ввод

                ; восстановление ValuePointer из FSettingsWaitFrame, далее на стеке обычный возврат
StoreKey:       POP HL
                ; обновление ровно одного символа принятой клавишей либо цифрой
                LD (HL), E
                ; создание снимка и условная перерисовка принятого значения
Redraw:         CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.TryDrawEnvironmentPanel.Entry
                ; возобновление указателя и показ базового экрана
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
