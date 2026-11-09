                module Action
                module ToggleViewDirection
                ; Документация [переключение переднего и заднего вида](../../Docs/ActionViewDirectionCommand.md)
                ; -----------------------------------------
                ; Разворот базиса, обновление точек и согласованная смена трёх опкодных пар направления вида
                ; исходная запись 17, перенесённое ядро банка 5, адреса 762A..767F
                ; In:
                ;   HL, DE, BC и AF входных числовых аргументов не задают, BC сохраняемый контекст
                ;   CommandDelay допускает обработку только при нуле, выбран банк 0, paging разблокирован
                ;   действуют договоры NegateOuterBasisRows, InitializeBankedBufferPoints и QueueTextItemBank1, Controls банка 1 загружен
                ;   первый байт NegateFirst выбирает направление, произвольные прежние байты остальных пар перезаписываются
                ;   CPU-стек допускает восемнадцать дополнительных байтов, IRQ и повторный вход исключены
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, запись памяти и OUT отсутствуют
                ;   при допуске CursorA получает EE1B, CommandDelay получает 20, шесть слов базиса меняют знак по договору NegateOuterBasisRows
                ;   35 точек банка 1 подготовлены заново, Seed обновлён 70 раз, BC сохраняется, DE содержит исходный C02 базиса
                ;   при нулевом исходном первом байте три пары получают ED44, HL=44ED, переданы F1E1 и F239, выбран задний вид
                ;   при любом ненулевом первом байте три пары получают 0000, HL=0000, переданы F1E1 и F228, выбран передний вид
                ;   A содержит исходный первый байт, F соответствует AND этого байта, IX и IY сохраняются
                ;   HL', DE', BC', AF' получают результаты InitializeBankedBufferPoints, I, IM и IFF сохраняются
                ;   OUT 7FFD получает 11,10 три раза, итоговая полная конфигурация 10, каждая из двух строк очереди независимо принимается либо отклоняется
                ;   SP после внешнего RET равен исходному SP+2, максимальная дополнительная глубина восемнадцать байтов
                ; Corrupt:
                ;   HL, DE, AF, HL', DE', BC', AF', R, CommandDelay, CursorA, шесть слов базиса, точки и Seed банка 1, шесть байтов изменяемого кода, очередь, paging и восемнадцать временных байтов стека
                ; Note:
                ;   ED44 исполняется как NEG, 0000 как две NOP, длина и число M1 каждой пары равны двум, здесь пары только создаются
                ;   каждое переключение сначала меняет знак базиса и перестраивает точки, даже при произвольном прежнем ненулевом первом байте
                ;   2568 композиционных сценариев проверяют настоящие три дочерних тела, RAM и регистры кроме R и тактов
                ;   исполнение созданных NEG отдельно проверено на 65536 знаковых словах, нативный вид и полный игровой кадр не проверялись
                ; -----------------------------------------
                ; Проверка задержки перед переключением переднего и заднего вида.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, базис, точки и опкоды сохранить

                ; Выбор исходного звукового потока принятой команды.
                LD HL, @ActionViewDirectionConst.Sound
                LD (@ActionAyEffectState.CursorA), HL
                ; Обновление задержки до разворота базиса и повторной подготовки точек.
                LD A, @ActionViewDirectionConst.Delay
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Изменение знака двух внешних строк физического базиса, средняя строка сохраняется.
                CALL @Action.NegateOuterBasisRows.Entry
                ; Повторная подготовка 35 банковых точек с 70 настоящими шагами генератора.
                CALL @Action.InitializeBankedBufferPoints.Entry
                ; Проверка первого опкода режима, остальные две пары как входное условие не читаются.
                LD A, (@Action.UpdateMotionFromControls.NegateFirst)
                AND A
                JR Z, @Action.ToggleViewDirection.SelectRear                    ; переход, если первый опкод равен нулю, записать NEG во все три пары и выбрать задний вид

                ; Создание трёх пар NOP для переднего вида, все шесть прежних байтов перезаписываются.
                LD HL, @ActionViewDirectionConst.ForwardPair
                LD (@Action.UpdateMotionFromControls.NegateFirst), HL
                LD (@Action.UpdateMotionFromControls.NegateSecond), HL
                LD (@Action.UpdateMotionFromControls.NegateThird), HL
                ; Передача сообщения о включении выбранного режима, флаги проверки первого опкода сохраняются.
                PUSH DE
                LD DE, @ControlsFlightText.ModeEnabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Передача названия переднего вида отдельным запросом очереди.
                PUSH DE
                LD DE, @ControlsFlightText.ForwardView
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                ; Создание трёх инструкций NEG из исходного слова 44ED, в памяти оно хранится ED,44.
SelectRear:     LD HL, @ActionViewDirectionConst.RearPair
                LD (@Action.UpdateMotionFromControls.NegateFirst), HL
                LD (@Action.UpdateMotionFromControls.NegateSecond), HL
                LD (@Action.UpdateMotionFromControls.NegateThird), HL
                ; Передача сообщения о включении выбранного режима, флаги проверки первого опкода сохраняются.
                PUSH DE
                LD DE, @ControlsFlightText.ModeEnabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Передача названия заднего вида отдельным запросом очереди.
                PUSH DE
                LD DE, @ControlsFlightText.RearView
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
