                module Station
                module ResetShipPanelSelection
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [продажа выбранного груза, отложенные callback и порядок групп панелей](../../Docs/ControlPanelGroups.md)
                ; -----------------------------------------
                ; Сброс режима списка, рамок выбора и первого компонента индекса банка 4
                ; исходная запись 4, файловые смещения #20CB..#20FE
                ; In:
                ;   AF - A сохраняемый селектор корабельных панелей, рабочие индексы DrawItemState.Index28 и Index29 допустимы
                ;   тень CurrentPage и аппаратный порт согласованы, bit5 снят, CPU-стек вне сменяемого окна
                ; Out:
                ;   HL - адрес FInterfaceItem.Flags элемента Index28, DE и BC сохранены
                ;   AF - A=(прежняя CurrentPage AND F8) OR 10, F от логического OR итоговой страницы
                ;   ShipPanelState.Selector получает входной A, PendingRedraw=1, OwnedMode=0, PanelHoverState.ShipsRow=FF
                ;   бит InterfaceFlags.FrameBit у Index29 установлен, затем у Index28 сброшен, прочие биты сохранены
                ;   байт E146 именно банка 4 равен нулю, итоговый банк 0 с сохранёнными старшими управляющими разрядами
                ;   альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2
                ; Corrupt:
                ;   HL, AF
                ; Note:
                ;   при одинаковых индексах последующий RES выигрывает, итоговый бит 0 сброшен
                ;   Selector не нормализуется до 0 или 1, все входные байты записываются без проверки
                ;   PendingRedraw является операндом периодического входа 68EA, ненулевое значение выбирает обновление через 68CC
                ;   OwnedMode выбирает источник списка, ноль использует таблицу доступности системы, ненулевое значение использует текущие индексы 9849 или 984A
                ;   назначение всех категорий Selector и полного алгоритма банка 4 этим договором не объявляется установленным
                ;   вызов не рисует экран, прежний номер банка не восстанавливается
                ; -----------------------------------------
                ; сохранение полного селектора списка без нормализации
Entry:          LD (@ShipPanelState.Selector), A
                ; запрос отложенного обновления периодическим входом 68EA
                LD A, #01
                LD (@ShipPanelState.PendingRedraw), A
                ; отмена прежней полосы наведения списка кораблей
                LD A, #FF
                LD (@PanelHoverState.ShipsRow), A
                ; выбор доступного в системе списка вместо текущего владения
                XOR A
                LD (@ShipPanelState.OwnedMode), A
                ; расчёт адреса флагов управляющего элемента 29 для установки формы рамки
                LD HL, (@DrawItemState.Index29)
                LD A, @FInterfaceItem.Flags
                CALL @Station.GetItemField.Entry
                SET @InterfaceFlags.FrameBit, (HL)
                ; расчёт адреса флагов управляющего элемента 28 для сброса формы рамки
                LD HL, (@DrawItemState.Index28)
                LD A, @FInterfaceItem.Flags
                CALL @Station.GetItemField.Entry
                RES @InterfaceFlags.FrameBit, (HL)
                ; выбор банка 4 для сброса его первого компонента индекса
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                XOR A
                LD (#E146), A
                ; возврат в банк станционного кода с сохранением старших разрядов страницы
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET

                endmodule
                endmodule
