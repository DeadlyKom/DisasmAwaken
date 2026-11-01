                module Station
                module ShipModelChoice
                ; Документация [единица после RepaintAndFlag, строка FF, сброс описания, пять ключей и физический хвост удаления](../../Docs/ShipModelActions.md)
                ; -----------------------------------------
                ; Пустая ветвь действия и отдельное применение выбранной строки с отложенной перерисовкой
                ; исходная запись 4, файловые смещения #0A55..#0A7B
                ; In:
                ;   Entry не принимает параметров и сразу возвращается, ApplyChoice является отдельным входом по 67AA
                ;   HL, DE, BC исходный контекст экранного обновления ApplyChoice, AF в нём не является параметром
                ;   PanelHoverState.ShipsRow содержит полный байт строки, код и слова описания доступны для записи
                ;   выполняются договоры BeginScreenUpdate, EndScreenUpdate, указателя и переключения банка без аппаратной блокировки
                ; Out:
                ;   Entry сохраняет все регистры, флаги и память, SP после RET равен входному+2
                ;   ApplyChoice возвращает HL=0, DE и BC сохранены, AF=010C
                ;   HL', DE', BC', IX и IY ApplyChoice сохранены, AF' зависит от ResumePointer, I и IFF сохраняются
                ;   при ShipsRow!=FF в банк 4 записан байт RowOperand, при FF прежний байт сохранён
                ;   всё слово ModelDescriptionState.TopRow обнулено даже при FF, PendingRedraw=1
                ;   CurrentPage=10, выбран банк станции 0 и базовый экран, UpdateBlocked=0, SP после RET входному+2
                ; Corrupt:
                ;   HL, AF, AF' по указателю, RowOperand банка 4 при непустой строке, TopRow, PendingRedraw, состояние экранного обновления
                ; Note:
                ;   номер строки не ограничивается числом моделей, FF только запрещает конкретную запись, допустимость других значений обеспечивает вызывающий код
                ;   BeginScreenUpdate и EndScreenUpdate выполняются даже при FF, периодический callback здесь не меняется
                ;   модель не рисуется немедленно, ненулевой PendingRedraw обслуживается последующим AnimateShipPreview
                ;   проверены все строки и два прежних байта модели, обе страницы, полное слово сброса и точная последовательность OUT
                ; -----------------------------------------
                ; пустая ветвь действия, применение выбранной строки начинается отдельно в ApplyChoice
Entry:          RET

                ; сохранение базового экрана в банке 7 и начало скрытого обновления состояния выбора
ApplyChoice:    CALL @Station.BeginScreenUpdate.Entry
                ; выбор банка 4 перед изменением операнда номера модели
                LD A, @ShipPreviewConst.PreviewPage
                CALL @Station.SelectRamBank.Entry
                ; чтение выбранной строки и проверка числового маркера отсутствия FF
                LD A, (@PanelHoverState.ShipsRow)
                CP @TradePanelConst.NoRow
                JR Z, @Station.ShipModelChoice.ReturnBank0                      ; переход, если строка равна FF, сохранить прежний номер модели

                ; запись строки в существующий операнд LD A по E146 именно банка 4
                LD (@D3DPreviewState.RowOperand), A
                ; возврат окна RAM в банк станции 0 при сохранённом скрытом экране
ReturnBank0:    LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; обнуление всего 16-битного начала описания независимо от наличия выбранной строки
                LD HL, #0000
                LD (@ModelDescriptionState.TopRow), HL
                ; возобновление указателя и возврат видимого базового экрана
                CALL @Station.EndScreenUpdate.Entry
                ; установка отложенного запроса, новый кадр здесь не рисуется
                LD A, #01
                LD (@ShipPanelState.PendingRedraw), A
                RET

                endmodule
                endmodule
