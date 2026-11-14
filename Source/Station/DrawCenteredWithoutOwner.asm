                module Station
                module DrawCenteredWithoutOwner
                ; Документация [центрируемый элемент без записи в карту владельцев](../../Docs/DrawCenteredWithoutOwner.md)
                ; -----------------------------------------
                ; Рисование центрируемого элемента без регистрации в карте владельцев
                ; исходная запись 4, станционный банк 0, адреса C2CB..C2DE
                ; In:
                ;   HL индекс элемента, остальные требования к рамке, тексту и стеку по DrawCenteredItem
                ;   банк 0 выбран, операнд CenteredItemDrawState.RegisterTarget доступен для записи, IRQ не вмешивается
                ; Out:
                ;   HL, DE, BC сохранены, AF содержит A=C3 и F последнего текстового прохода
                ;   рамка и текст записаны в bitmap, таблица индексов и карта владельцев сохранены
                ;   RegisterTarget восстановлен на RegisterItemCells.Entry, SP увеличен на два
                ; Corrupt:
                ;   AF, HL' в части L', AF', R, CenteredItemDrawState.RegisterTarget, TextWindow, bitmap, текстовые и растровые операнды, временные слова CPU-стека
                ; Note:
                ;   временная цель RegisterTarget указывает на собственный RET, реальный CALL сохраняет слово C2FB
                ;   после возврата записывается постоянная цель BEAE, прежнее произвольное слово теряется
                ;   при рисовании доступен весь текстовый договор DrawCenteredItem, регистрация и освобождение старой записи пропущены
                ;   штатный вызов C2CB не установлен
                ; -----------------------------------------
                ; Сохранение индекса элемента перед отключением регистрации.
Entry:          PUSH HL
                ; Подмена цели регистрации адресом собственного RET.
                LD HL, @Station.DrawCenteredWithoutOwner.Return
                LD (@CenteredItemDrawState.RegisterTarget), HL
                ; Восстановление индекса и рисование рамки с текстом.
                POP HL
                CALL @Station.DrawCenteredItem.Entry
                ; Сохранение возвращённого HL и восстановление постоянной цели регистрации.
                PUSH HL
                LD HL, @Station.RegisterItemCells.Entry
                LD (@CenteredItemDrawState.RegisterTarget), HL
                ; Восстановление HL и общий выход, этот RET служит также пустой целью регистрации.
                POP HL
Return:         RET

                endmodule
                endmodule
