                module Station
                module HandleHelpContentsAction
                ; Документация [полный селектор, закрытие двух ключей, прокрутка и отсутствие проверки FF подсветки](../../Docs/HelpPanelActions.md)
                ; -----------------------------------------
                ; Закрытие пары, прокрутка CR-заголовков либо выбор раздела с перерисовкой обеих панелей
                ; исходная запись 4, файловые смещения #0C8C..#0CF6
                ; In:
                ;   HL, DE, BC, AF и IX удовлетворяют RepaintAndFlag, CloseMenuOnRow, XorRowIfSelected и ScrollWindowRows
                ;   для выбора раздела ContentsTop и IndexRow задают существующую LF-запись после байтового сложения, обе панели доступны
                ;   для перерисовки выполняются договоры DrawHelpText и DrawHelpContents, IRQ сохраняет рабочий контекст
                ;   для прокрутки геометрия безопасна, исходный банк станции 0 выбран и аппаратное переключение не заблокировано
                ; Out:
                ;   при Carry RepaintAndFlag немедленно возвращается его контекст, при A=1 и Carry=0 выполняется SelectSection
                ;   в прочих случаях совпадение символьных строк удаляет текущий ключ, затем первый ключ TextIndex
                ;   при несовпадении отключается перенос, прежняя XOR-полоса снимается, IndexRow=FF
                ;   прокрутка получает RenderCall=DrawHelpContents.RenderTitles, EndLimit=7, A=8, HL=ContentsTop, итоговый HL записан в ContentsTop
                ;   SelectSection при младшем ContentsTop=FF возвращает AF=0050 без сброса TopLine, смены записи и рисования
                ;   иначе TopLine=0, выбранный байт равен ContentsTop.L+IndexRow по модулю 256 и записан через Help.SelectText
                ;   после выбора BeginScreenUpdate, DrawHelpText, DrawHelpContents и EndScreenUpdate дают итоговые HL, DE, BC последнего рисователя и A=10 с сохранённым его F
                ;   IndexRow после перерисовки равен FF, VisibleTitles обновлён, ContentsTop сохранён, банк и страница равны 10, SP после возврата входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX и BC' по фактическим помощникам, список, экраны, курсор, указатель, TopLine, ContentsTop, IndexRow, VisibleTitles, кэш и операнды
                ; Note:
                ;   FF проверяется только в младшем ContentsTop, старший байт не участвует в выборе, IndexRow=FF отдельно не отвергается
                ;   все 65280 суммы проверены до SelectText, недопустимые полученные номера не передавались индексатору
                ;   номер 7 является последним индексом восьми заголовков, это параметр предела ScrollWindowRows, не число строк окна
                ;   открытие скрытого экрана и две перерисовки выполняются только после принятого выбора, временный код рисователей также учитывается их договорами
                ; -----------------------------------------
                ; перерисовка и обработка геометрии перед действием списка разделов
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если RepaintAndFlag вернул Carry, выбор и прокрутка подавлены

                ; проверка селектора 1 для перехода к выбору раздела
                DEC A
                JP Z, @Station.HandleHelpContentsAction.SelectSection           ; переход, если возвращённый селектор равен 1, выбрать раздел

                ; условное удаление текущего списка по совпадению символьных строк Y
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.HandleHelpContentsAction.ScrollTitles           ; переход, если строки различаются, снять подсветку и прокрутить список

                ; чтение ключа связанной текстовой панели перед вторым удалением
                LD DE, (@HelpPanelState.TextIndex)
                JP @Station.DropItemDraw.Entry

                ; отключение переноса перед повторной печатью CR-заголовков
ScrollTitles:   CALL @Station.DisableTextWrap.Entry
                ; чтение текущих высоты наведения и пиксельного отступа из операнда UpdateIndexListHover
                LD DE, (@HelpPanelState.HoverRows)
                LD A, (@PanelHoverState.IndexRow)
                ; снятие прежней XOR-полосы, FF не рисует полосу
                CALL @Station.XorRowIfSelected.Entry
                ; сброс номера подсветки после снятия старого изображения
                LD A, #FF
                LD (@PanelHoverState.IndexRow), A
                ; обновление callback на внутренний вход печати заголовков без новой рамки
                LD HL, @Station.DrawHelpContents.RenderTitles
                LD (#A265), HL
                ; подготовка предела 7 для восьми исходных CR-заголовков
                LD HL, #0007
                LD (#A235), HL
                ; подготовка верхнего отступа 8 и полного индекса ContentsTop
                LD A, #08
                LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                ; сохранение полного итогового индекса списка разделов
                LD (@HelpPanelState.ContentsTop), HL
                RET

                ; проверка маркера FF только в младшем байте ContentsTop
SelectSection:  LD A, (@HelpPanelState.ContentsTop)
                INC A
                RET Z                                                           ; выход, если младший ContentsTop равен FF, не выбирать запись

                DEC A
                LD C, A
                ; сброс полной прокрутки текстовой панели перед сменой записи
                LD HL, #0000
                LD (@HelpPanelState.TopLine), HL
                ; расчёт байтового номера LF-записи, IndexRow=FF отдельно не проверяется
                LD A, (@PanelHoverState.IndexRow)
                ADD A, C
                ; сохранение номера в альтернативном AF на время выбора банка HELP
                EX AF, AF'
                LD A, #17
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                ; обновление операнда выбранной LF-записи в банке 7
                CALL @Help.SelectText.Entry
                ; возврат банка станции перед скрытым обновлением обеих панелей
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; создание экранного снимка и отключение обновления указателя
                CALL @Station.BeginScreenUpdate.Entry
                ; перерисовка LF-текста от сброшенной верхней строки
                CALL @Station.DrawHelpText.Entry
                ; перерисовка списка, сброс XOR-состояния и обновление видимого числа строк
                CALL @Station.DrawHelpContents.Entry
                ; возобновление указателя и показ обновлённого базового экрана
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
