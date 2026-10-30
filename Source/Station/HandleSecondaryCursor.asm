                module Station
                module HandleSecondaryCursor
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [событие с входом Entry+3, отложенный callback и общая развилка активации](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Подготовка callback установки курсора B через геометрию либо активацию
; исходная запись 4, файловые смещения #1FD6..#1FDF
; In:
;   DE - индекс элемента, BC - сохраняемый контекст, AF - селектор по договору ActivateInterfaceCallback
;   действуют условия TrackItemGeometry, ToggleItemBounds и ActivateItem для реально выбранной ветви, FlagsCache подготовлен
;   Entry содержит исходный JP в Action, диспетчер может входить сразу через Action=Entry+3
; Out:
;   HL заменён адресом SelectSecondaryListCursor.Entry, затем выполняется настоящий ActivateInterfaceCallback
;   NextCallback получает этот адрес до выбора ветви, новое действие этим обработчиком немедленно не вызывается
;   при A=0 возможны интерактивная геометрия либо переключение границ, ненулевой A активирует элемент по общему договору
;   DE и BC сохранены, HL, AF и IX соответствуют выбранному пути ActivateInterfaceCallback с новым callback
;   H', DE', BC', IY, I и IFF сохраняются по договорам помощников, L' и AF' рабочие на пути рисунка
;   RET после общего помощника возвращает тому же вызывающему коду, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, AF, HL', AF', IX и графическое состояние выбранного общего пути
; Note:
;   первый JP не создаёт стекового адреса возврата, вход Action пропускает только этот трёхбайтовый префикс
;   на нулевом селекторе сохранённый NextCallback сам по себе не означает, что операция списка была исполнена
;   проверка основана на точной последовательности десяти байтов и доказанных договорах общего помощника, это не самостоятельное доказательство аппаратного ввода
; -----------------------------------------
                ; передача с внешней трёхбайтовой обёртки в доступный диспетчеру вход Action
Entry:          JP @Station.HandleSecondaryCursor.Action

                ; выбор адреса SelectSecondaryListCursor для сохранения в NextCallback, прямого вызова операции здесь нет
Action:         LD HL, @Station.SelectSecondaryListCursor.Entry
                ; общий выбор геометрии, контура либо активации с новым callback
                CALL @Station.ActivateInterfaceCallback.Entry
                RET

                endmodule
                endmodule
