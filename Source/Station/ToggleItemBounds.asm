                module Station
                module ToggleItemBounds
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [смена геометрии и продолжение действия](../../Docs/BoundsToggle.md)
; -----------------------------------------
; Возврат сохранённой геометрии либо установка исходного большого прямоугольника
; исходная запись 4, файловые смещения #6C30..#6C80
; In:
;   HL - новая обёртка только для отсутствующего в списке DE-индекса, DE - индекс FInterfaceItem
;   выполняются предусловия MoveItemToTail, четыре текущих и четыре сохранённых поля доступны
;   стек вмещает динамический FBoundsToggleFrame, значение геометрии интерпретируется как байтовое без валидации
; Out:
;   HL=входной DE-индекс, DE и BC сохранены, IX - физическое начало выбранной записи
;   при Width<16 и Height<8 текущие X,Y,Width,Height становятся 6,4,20,10, A=прежний Height,F=#81
;   иначе текущие поля заменяются SavedX..SavedHeight, A=SavedHeight
;   на восстановлении F=(F_compare AND #C4) OR (SavedHeight AND #28) OR 1, Compare относится к Width-16 либо Height-8
;   InterfaceState.EventEnabled=0, обработчик перенесён в конец списка до изменения геометрии
; Corrupt:
;   HL, AF, IX
; Note:
;   альтернативные регистры, IY, I и IFF сохраняются, SP восстанавливается
;   Saved-поля и остальные двенадцать байтов записи сохраняются, проверки знаковых координат и размеров нет
;   сравнение Height выполняется только при Width<16, любой другой размер выбирает восстановление
;   большой прямоугольник задан исходными байтами, нового размещения данных не вводится
;   FBoundsToggleFrame содержит WorkspaceIndex, SavedIndex, ReturnAddress, первое слово снимается до умножения индекса
;   карта владельцев и пиксели здесь не обновляются, EventEnabled=0 запрашивает последующее перестроение
; -----------------------------------------
                ; запрос перестроения интерфейса и запрет событий до него
Entry:          XOR A
                LD (@InterfaceState.EventEnabled), A
                ; создание FBoundsToggleFrame.SavedIndex и временного WorkspaceIndex из DE
                PUSH DE
                PUSH DE
                ; перенос обработчика выбранного индекса до изменения геометрии
                CALL @Station.MoveItemToTail.Entry
                ; извлечение WorkspaceIndex в HL, выбранный обработчик MoveItemToTail больше не нужен
                POP HL
                ; расчёт байтового смещения записи как 16*индекс по модулю 65536
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ; перенос смещения в DE и сохранение исходного индекса в выходном HL
                EX DE, HL
                ; расчёт IX как физического адреса FInterfaceItem с исходным смещением
                LD IX, @StationState.Items
                ADD IX, DE
                ; проверка текущей ширины на порог 16, большие значения выбирают сохранённую геометрию
                LD A, (IX + FInterfaceItem.Width)
                CP @BoundsToggleConst.WidthLimit
                JR C, @Station.ToggleItemBounds.CheckHeight                     ; переход, если Width меньше 16, проверить порог Height

                ; восстановление четырёх текущих полей из физического сохранённого прямоугольника
Restore:        LD A, (IX + FInterfaceItem.SavedX)
                LD (IX + FInterfaceItem.X), A
                LD A, (IX + FInterfaceItem.SavedY)
                LD (IX + FInterfaceItem.Y), A
                LD A, (IX + FInterfaceItem.SavedWidth)
                LD (IX + FInterfaceItem.Width), A
                LD A, (IX + FInterfaceItem.SavedHeight)
                LD (IX + FInterfaceItem.Height), A
                ; восстановление DE-индекса и установка Carry, S,Z,P/V остаются от сравнения размера
                POP DE
                SCF
                RET

                ; проверка высоты только у записей с шириной меньше 16
CheckHeight:    LD A, (IX + FInterfaceItem.Height)
                CP @BoundsToggleConst.HeightLimit
                JR NC, @Station.ToggleItemBounds.Restore                        ; переход, если Height не меньше 8, восстановить сохранённый прямоугольник

                ; установка исходного большого прямоугольника 6,4,20,10 без изменения Saved-полей
                LD (IX + FInterfaceItem.X), @BoundsToggleConst.ExpandedX
                LD (IX + FInterfaceItem.Y), @BoundsToggleConst.ExpandedY
                LD (IX + FInterfaceItem.Width), @BoundsToggleConst.ExpandedWidth
                LD (IX + FInterfaceItem.Height), @BoundsToggleConst.ExpandedHeight
                ; восстановление DE-индекса, Carry=1, остальные значимые флаги от Height-8
                POP DE
                SCF
                RET

                endmodule
                endmodule
