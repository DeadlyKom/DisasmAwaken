                module Station
                module HandleMapPanelEvent
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [порядок решений, два вида раннего Carry, сравнение строки и десять удалений](../../Docs/MapPanelEvent.md)
; -----------------------------------------
; Обработка события панели карты с выбором точки, прокруткой либо закрытием набора связанных панелей
; исходная запись 4, файловые смещения #0EB9..#0F19
; In:
;   HL - запасная обёртка основной карты, DE - её индекс, BC - контекст, AF - полный селектор действия
;   IX - FInterfaceItem геометрии карты для возможной PanMapView, указатель, FlagsCache и список удовлетворяют RepaintAndTrack.KeepSelector
;   запасная обёртка и индекс согласованы, все callback закрытия и рисователи соблюдают собственные договоры
;   для выбранной ветви выполняются условия SelectMapPointAndRefresh, PanMapView либо CloseMenuOnRow и десяти DropItemDraw
;   поля индексов связанных панелей доступны, PeriodicCall является исходным изменяемым операндом MainLoop
;   договоры HALT, paging, SP и IFF реально вызываемого пути обеспечиваются окружением
; Out:
;   RepaintState.ExitInstruction получает A7, после RepaintAndTrack Carry немедленно завершает событие
;   у входного селектора с битом 7 ранний возврат сохраняет A, F=(A AND A8) OR 1, HL, DE, BC и IX сохранены, A'=A7, F' прежний альтернативный F
;   выполненное действие TrackItemGeometry также завершает событие через Carry, остальные ветви тогда не исполняются
;   при Carry=0 и возвращённом A=1 выполнен хвостовой переход в SelectMapPointAndRefresh, результаты соответствуют её договору
;   иначе отрицательный InterfaceState.EventCode вызывает хвостовую PanMapView, до сравнения строки закрытия
;   при неотрицательном EventCode разные символьные строки PointerY и OriginYLow также передают управление PanMapView
;   при совпавшей строке удаляется основная карта и последовательно десять связанных элементов, PeriodicCall заменяется EmptyCallback
;   после закрытия HL=EmptyCallback.Entry, DE содержит последний индекс VariantPanelState.ItemIndex, BC сохранён от CloseMenuOnRow, C номер символьной строки
;   AF на закрывающей ветви соответствует последнему DropItemDraw, EventEnabled сброшен удалением согласованной основной записи
;   регистры и побочные эффекты выбранной хвостовой ветви соответствуют её договору, IY и альтернативные регистры также зависят от callback и рисунка RepaintAndTrack
;   SP обычного возврата равен входному SP+2 при соблюдении всех договоров, реальная память и исходные инструкции не перемещены
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по достигнутым callback и ветвям, список, экраны, геометрия, выбор и PeriodicCall
; Note:
;   порядок решений существенен, селектор 1 обрабатывается до знака EventCode и до проверки строки
;   повторная перерисовка и перенос карты могут уже произойти внутри RepaintAndTrack, даже если затем будет выбрана прокрутка либо закрытие
;   при закрытии сравниваются только символьные строки, X указателя и старший байт начала TextWindow не учитываются
;   имена пока не разобранных связанных обработчиков не заменены предположениями, для них используются доказанные номера записей
;   диспетчерная модель проверяет реальные перенос и удаления, полные выбор и прокрутка имеют отдельные интеграционные модели, нативные IRQ не проверены
; -----------------------------------------
                ; перенос карты в хвост, возможный рисунок и геометрическое действие с сохранением полного селектора
Entry:          CALL @Station.RepaintAndTrack.KeepSelector
                RET C                                                           ; выход, если селектор запрещён битом 7 либо интерактивная геометрия уже обработала событие

                ; проверка селектора 1 до знака кода события и до строки закрытия
                DEC A
                JP Z, @Station.SelectMapPointAndRefresh.Entry                   ; переход, если RepaintAndTrack вернул селектор 1, выбрать ближайшую точку и обновить панели

                ; проверка знака кода события после исключения ветви выбора точки
                LD A, (@InterfaceState.EventCode)
                AND A
                JP M, @Station.PanMapView.Entry                                 ; переход, если бит 7 EventCode установлен, начать прокрутку карты

                ; проверка совпадения символьных строк указателя и текстового начала, при совпадении удалить основную карту
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.PanMapView.Entry                                ; переход, если символьные строки не совпали, прокручивать вместо закрытия

                ; удаление связанного обработчика записи 21 по его сохранённому индексу
                LD DE, (@DrawItemState.Index21)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 12 по его сохранённому индексу
                LD DE, (@DrawItemState.Index12)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 13 по его сохранённому индексу
                LD DE, (@DrawItemState.Index13)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 14 по его сохранённому индексу
                LD DE, (@DrawItemState.Index14)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 15 по его сохранённому индексу
                LD DE, (@DrawItemState.Index15)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 17 по его сохранённому индексу
                LD DE, (@DrawItemState.Index17)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 16 по его сохранённому индексу
                LD DE, (@DrawItemState.Index16)
                CALL @Station.DropItemDraw.Entry
                ; удаление связанного обработчика записи 18 по его сохранённому индексу
                LD DE, (@DrawItemState.Index18)
                CALL @Station.DropItemDraw.Entry
                ; удаление панели сведений о системах
                LD DE, (@SystemInfoState.ItemIndex)
                CALL @Station.DropItemDraw.Entry
                ; удаление панели планет, последний DropItemDraw определяет конечный AF
                LD DE, (@VariantPanelState.ItemIndex)
                CALL @Station.DropItemDraw.Entry
                ; отключение периодического обновления панели планет заменой операнда callback на EmptyCallback
                LD HL, @Station.EmptyCallback.Entry
                LD (@MenuCommandState.PeriodicCall), HL
                RET

                endmodule
                endmodule
