                module Action
                module ClearMissileTargets
                ; Документация [команды захватов и наведения](../../Docs/ActionTargetCommands.md)
                ; -----------------------------------------
                ; Снятие трёх захватов ракет с задержкой повторной команды и сообщением
                ; исходная запись 17, перенесённое ядро банка 5, адреса 72BE..72E1
                ; In:
                ;   HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт
                ;   CommandDelay по A85F допускает команду только при нуле, банк 0 выбран
                ;   очередь Controls банка 1 соответствует QueueTextItemBank1, paging не заблокирован
                ;   на стеке внешний возврат и восемнадцать доступных байтов ниже SP, IRQ не вмешиваются
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, память и paging не меняются
                ;   при допуске HL=EDA8, DE и BC сохраняются, CommandDelay=7, CursorA получает поток ActionSound
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен входному SP+2
                ;   каждый запрос очереди выполняет OUT 7FFD со значениями 11 и 10, итоговая страница 10
                ;   отказ заполненной очереди молчаливый, состояние команды всё равно изменяется
                ;   при допуске Target0, Target1 и Target2 получают FF, передан указатель F354, A=FF и F=54
                ; Corrupt:
                ;   HL, AF, R, CommandDelay, захваты, CursorA, очередь, paging и восемнадцать временных байтов стека
                ; Note:
                ;   сообщение F354 содержит текст о снятии наведённых целей, его фактический вывод требует потребителя очереди
                ;   1568 композиционных сценариев проверяют обе команды, остаточные слова стека и R не сверялись
                ; -----------------------------------------
                ; Проверка задержки перед снятием существующих захватов.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, захваты сохранить

                ; Обновление задержки принятой команды, повторный запрос допускается после её отсчёта.
                LD A, #07
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Выбор исходного потока AY-канала A в банке 0.
                LD HL, @ActionMissileCreateConst.ActionSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Снятие всех трёх захватов независимо от приёма сообщения очередью.
                LD A, #FF
                LD (@ActionMissileTargets.Value.Target0), A
                LD (@ActionMissileTargets.Value.Target1), A
                LD (@ActionMissileTargets.Value.Target2), A
                ; Сохранение DE вызывающего вокруг передачи указателя сообщения.
                PUSH DE
                ; Выбор сообщения о снятии наведённых целей.
                LD DE, @ControlsFlightText.TargetsForgot
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
