                module Action
                module ToggleFreeFlightMode
                ; Документация [команда свободного полёта](../../Docs/ActionFreeFlightCommand.md)
                ; -----------------------------------------
                ; Условная смена опкода координатного обновления с сообщением о свободном полёте
                ; исходная запись 17, перенесённое ядро банка 5, адреса 754C..7593
                ; In:
                ;   HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт
                ;   CommandDelay допускает обработку только при нуле, FreeFlight.Value=FF означает отсутствие оборудования
                ;   LimitWord является изменяемым словом ограничителя IncreaseGaugeWord по 7693, это не само SignedWord
                ;   банк 0 выбран, очередь Controls банка 1 удовлетворяет QueueTextItemBank1, paging разблокирован
                ;   CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, записи и OUT отсутствуют
                ;   при нулевой задержке CommandDelay получает 20 до остальных проверок
                ;   при FreeFlight.Value=FF HL, DE и BC сохраняются, A=0, F=50, остальные состояния и paging не меняются
                ;   при LimitWord не 0088 HL=(LimitWord-0088) AND FFFF, DE сохранён, BC=0088, A=(FreeFlight.Value+1) AND FF, F соответствует SBC с нулевым входным Carry
                ;   при полном допуске CursorA получает EDA8, HL=EDA8, DE сохранён, BC=0088
                ;   MotionOpcode=3A заменяется на C9, любой другой исходный опкод заменяется на 3A, A содержит записанный опкод
                ;   итоговый F соответствует CP исходного MotionOpcode,3A, он сохраняется обоими вызовами очереди
                ;   для исходного 3A переданы F1E1 и F200, иначе F1F0 и F200, приём двух записей независим
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен входному SP+2
                ;   при полном допуске OUT 7FFD получает 11,10,11,10, итоговая страница 10, прежняя конфигурация не восстанавливается
                ; Corrupt:
                ;   HL, BC, AF, R, CommandDelay, CursorA, MotionOpcode, очередь, paging и восемнадцать временных байтов стека на соответствующих путях
                ; Note:
                ;   RET по 6E72 пропускает часть UpdateMotionFromControls после двух уже выполненных предшествующих вызовов, а не отключает всё обновление кадра
                ;   проверены все 65536 ограничителей и все 256 исходных опкодов, произвольный опкод читается как данные и этой моделью не исполняется
                ;   66576 сценариев исполняют настоящие очередь и банковую обёртку, R, такты и остаточные слова временного стека не сверяются
                ; -----------------------------------------
                ; Проверка задержки перед изменением режима свободного полёта.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, опкод координатного обновления сохранить

                ; Обновление задержки до проверок оборудования и ограничителя.
                LD A, @ActionFreeFlightConst.Delay
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Проверка полного кода FreeFlight.Value, только FF означает отсутствие оборудования.
                LD A, (@ActionShipEquipment.FreeFlight.Value)
                INC A
                RET Z                                                           ; выход, если FreeFlight.Value равен FF, прочее состояние сохранить при уже установленной задержке

                ; Проверка текущего изменяемого LimitWord, разрешено только исходное значение сброса 0088.
                LD HL, (@ActionControlDecayState.LimitWord)
                LD BC, @ActionControlDecayConst.ResetWord
                OR A
                SBC HL, BC
                RET NZ                                                          ; выход, если LimitWord отличается от 0088, сохранить опкод и звуковой поток

                ; Выбор исходного звукового потока принятой команды.
                LD HL, @ActionMissileCreateConst.ActionSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Проверка фактического опкода начала координатной цепочки.
                LD A, (@ActionGaugeWordKeysState.MotionOpcode)
                CP @ActionGaugeKeyConst.MotionOpcode
                JR Z, @Action.ToggleFreeFlightMode.QueueEnabled                 ; переход, если MotionOpcode равен 3A, поставить сообщение о включении свободного полёта

                ; Передача сообщения о выключении свободного полёта с сохранением DE.
                PUSH DE
                LD DE, @ControlsFlightText.ModeDisabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Восстановление исходного LD A,(nn), его двухбайтовый операнд сохраняется.
                LD A, @ActionGaugeKeyConst.MotionOpcode
                JR @Action.ToggleFreeFlightMode.StoreOpcode

                ; Передача сообщения о включении свободного полёта с сохранением DE.
QueueEnabled:   PUSH DE
                LD DE, @ControlsFlightText.ModeEnabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Выбор RET вместо первого чтения координатной цепочки, последующие байты не меняются.
                LD A, @ActionFreeFlightConst.ReturnOpcode
                ; Обновление одного существующего опкода UpdateMotionFromControls.
StoreOpcode:    LD (@ActionGaugeWordKeysState.MotionOpcode), A
                ; Передача названия режима отдельным запросом, отказ первой записи не проверяется.
                PUSH DE
                LD DE, @ControlsFlightText.FreeFlight
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
