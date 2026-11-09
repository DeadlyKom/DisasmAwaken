                module Action
                module RequestHyperJump
                ; Документация [запрос гиперперехода и расход до сравнения контекстов](../../Docs/ActionHyperJump.md)
                ; Документация [физический байт стоимости](../../Docs/ActionNewsOrdersAndJumpCost.md)
                ; -----------------------------------------
                ; Проверка гиперследа, списание выбранного запаса и перенос пятибайтового контекста перед перезагрузкой ACTION
                ; исходная запись 17, перенесённое ядро банка 5, адреса 70F6..7175
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, CommandDelay должен быть нулём, HyperTrail.Value=FF запрещает действие
                ;   доступны Preferred, Fallback, ActionHyperJumpCost.Value.Cost и два соседних пятибайтовых контекста по 9BC1 и 9BC6
                ;   Selector по 7104 является операндом CP n, исходное значение 00, проверенная серия относится к этому исходному значению
                ;   при принятом переходе действуют условия PrepareHyperJumpRelay, банк 0 выбран, IRQ и повторный вход исключены
                ;   на отказе внешний адрес возврата доступен на CPU-стеке, дополнительная память не выделяется
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку и F соответствует AND A
                ;   при HyperTrail.Value=FF HL, DE и BC сохраняются, A=0, F соответствует INC FF после AND нулевой задержки
                ;   при исходном Selector=00 ненулевой Preferred выбирает двойную стоимость, нулевой Preferred выбирает одинарную стоимость из Fallback
                ;   стоимость расширяется до слова до удвоения, Preferred не покрывает двойную стоимость больше FF
                ;   при недостаточном запасе A=0, HL содержит обёрнутую разность, DE содержит стоимость, BC сохраняется, F соответствует SBC с очищенным Carry
                ;   при достаточном запасе младший байт разности записывается в выбранное поле до сравнения контекстов
                ;   при совпавших пяти байтах возврат сохраняет уже выполненное списание, HL=0, DE содержит второе совпавшее слово, B содержит последний байт текущего контекста, C сохраняется, AF=0042
                ;   при различии пяти байтов второй контекст полностью копируется в первый и последовательное исполнение продолжается в PrepareHyperJumpRelay по 7176
                ;   на границе 7176 HL содержит второе слово нового контекста, A его пятый байт, DE и F остаются от последнего выполненного сравнения, B меняется лишь при достигнутом сравнении пятого байта
                ;   альтернативные и индексные регистры, I, IM, IFF и paging до 7176 сохраняются, на раннем RET SP увеличивается на 2, на принятой границе SP не меняется
                ; Corrupt:
                ;   HL, DE, BC в части B на последнем сравнении, AF, R, выбранный байт запаса и пять байтов текущего контекста, далее эффекты PrepareHyperJumpRelay
                ; Note:
                ;   сравнение пятибайтовых контекстов происходит после расхода, совпадение не отменяет списание
                ;   при переносе станционного контекста по смещению CD Cost получает последний результат MapState.LastDistance
                ;   изменённый Selector может выбирать маршрут по сравнению с другим байтом, его исходное значение не объявляется вечной константой
                ;   132864 сценария проверяют все пары запас/стоимость обоих маршрутов, задержки, оборудование и каждый байт контекста
                ;   сверены регистры кроме R и тактов, все банки RAM и кратность записей, принятые пути остановлены непосредственно перед сообщением по 7176
                ;   настоящий подготовитель с выводом сообщения, 256 потребителями и полными задержками проверен отдельно, TR-DOS и нативная игра не исполнялись
                ; -----------------------------------------
                ; Проверка задержки перед запросом гиперперехода.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, сохранить состояние

                ; Проверка полного кода HyperTrail.Value, только FF запрещает действие.
                LD A, (@ActionShipEquipment.HyperTrail.Value)
                INC A
                RET Z                                                           ; выход, если HyperTrail.Value равен FF, запас сохранить

                ; Выбор маршрута расхода через существующий операнд Selector, исходный байт сравнения равен 00.
                LD A, (@ActionPreferredByteState.Value.Preferred)
                CP #00
                JP Z, @Action.RequestHyperJump.TryFallback                      ; переход, если Preferred равен Selector, попробовать одинарную стоимость из Fallback

                ; Расчёт двойной стоимости в слове DE, удвоение не оборачивается по байту.
                LD A, (@ActionHyperJumpCost.Value.Cost)
                LD E, A
                LD D, #00
                LD A, (@ActionPreferredByteState.Value.Preferred)
                LD L, A
                LD H, #00
                OR A
                RL E
                RL D
                ; Проверка доступного Preferred 16-битным вычитанием с предварительно очищенным Carry.
                XOR A
                SBC HL, DE
                JP NC, @Action.RequestHyperJump.SpendPreferred                  ; переход, если Preferred покрывает двойную стоимость, записать остаток

                RET

                ; Списание Preferred до любого сравнения контекстов, последующий ранний выход расход не отменяет.
SpendPreferred: LD A, L
                LD (@ActionPreferredByteState.Value.Preferred), A
                JP @Action.RequestHyperJump.CompareContexts

                ; Расчёт одинарной стоимости и проверка Fallback 16-битным вычитанием.
TryFallback:    LD A, (@ActionHyperJumpCost.Value.Cost)
                LD E, A
                LD D, #00
                LD A, (@ActionPreferredByteState.Value.Fallback)
                LD L, A
                LD H, #00
                XOR A
                SBC HL, DE
                JP NC, @Action.RequestHyperJump.SpendFallback                   ; переход, если Fallback покрывает стоимость, записать остаток

                RET

                ; Списание Fallback до сравнения пятибайтовых контекстов.
SpendFallback:  LD A, L
                LD (@ActionPreferredByteState.Value.Fallback), A
                ; Проверка первого слова соседних пятибайтовых контекстов после уже выполненного расхода.
CompareContexts:LD HL, (@ActionOtherContext.Value.OtherFirst)
                LD DE, (@ActionParameterSeeds.Value.SeedFirst)
                XOR A
                SBC HL, DE
                JP NZ, @Action.RequestHyperJump.CopyContext                     ; переход, если первые слова различаются, скопировать новый контекст

                ; Проверка второго слова контекстов, Carry от равного предыдущего вычитания сброшен.
                LD HL, (@ActionOtherContext.Value.OtherSecond)
                LD DE, (@ActionParameterSeeds.Value.SeedSecond)
                XOR A
                SBC HL, DE
                JP NZ, @Action.RequestHyperJump.CopyContext                     ; переход, если вторые слова различаются, скопировать новый контекст

                ; Проверка пятого байта при двух совпавших словах.
                LD A, (@ActionParameterSeeds.Value.StepControl)
                LD B, A
                LD A, (@ActionContextIndex.Value.SelectedIndex)
                SBC A, B
                JP NZ, @Action.RequestHyperJump.CopyContext                     ; переход, если пятые байты различаются, скопировать новый контекст

                RET

                ; Копирование всех пяти байтов второго контекста в первый перед подготовителем перезагрузки.
CopyContext:    LD HL, (@ActionOtherContext.Value.OtherFirst)
                LD (@ActionParameterSeeds.Value.SeedFirst), HL
                LD HL, (@ActionOtherContext.Value.OtherSecond)
                LD (@ActionParameterSeeds.Value.SeedSecond), HL
                LD A, (@ActionContextIndex.Value.SelectedIndex)
                LD (@ActionParameterSeeds.Value.StepControl), A
                ; JP @Action.PrepareHyperJumpRelay.Entry, продолжение в PrepareHyperJumpRelay.asm

                endmodule
                endmodule
