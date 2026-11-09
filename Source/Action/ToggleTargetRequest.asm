                module Action
                module ToggleTargetRequest
                ; Документация [команды захватов и наведения](../../Docs/ActionTargetCommands.md)
                ; -----------------------------------------
                ; Переключение младшего бита запроса наведения с двумя сообщениями
                ; исходная запись 17, перенесённое ядро банка 5, адреса 72E2..7316
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
                ;   при допуске Request получает прежний байт XOR 1, остальные семь битов сохраняются
                ;   A равен новому Request, F соответствует XOR, ненулевой результат выбирает F1E1, нулевой F1F0
                ;   после сообщения состояния независимо ставится F214, название режима наведения на цель
                ; Corrupt:
                ;   HL, AF, R, CommandDelay, Request, CursorA, очередь, paging и восемнадцать временных байтов стека
                ; Note:
                ;   Request является проверяемым на ноль байтом, XOR 1 не нормализует произвольный исходный ненулевой байт
                ;   внутренний вход QueueEnabled не проверяет задержку и не меняет Request, QueueModeName только ставит вторую строку
                ;   переход из клавиатурного обработчика 7439 на 72F2 является отдельным внутренним входом переключения, родительский договор целиком ему не приписывается
                ; -----------------------------------------
                ; Проверка задержки перед изменением запроса наведения.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, Request сохранить

                ; Выбор исходного звукового потока принятой команды.
                LD HL, @ActionMissileCreateConst.ActionSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Обновление задержки принятой команды.
                LD A, #07
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Обновление только бита 0 Request, остальные разряды не нормализуются.
ToggleRequest:  LD A, (@ActionAimFollowState.Request)
                XOR #01
                LD (@ActionAimFollowState.Request), A
                JR NZ, @Action.ToggleTargetRequest.QueueEnabled                 ; переход, если новый Request ненулевой, поставить сообщение о включении

                ; Передача сообщения о выключении с сохранением DE вызывающего.
                PUSH DE
                LD DE, @ControlsFlightText.ModeDisabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                JR @Action.ToggleTargetRequest.QueueModeName

                ; Передача сообщения о включении с сохранением DE вызывающего.
QueueEnabled:   PUSH DE
                LD DE, @ControlsFlightText.ModeEnabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Передача названия режима отдельным запросом, отказ первой строки не проверяется.
QueueModeName:  PUSH DE
                LD DE, @ControlsFlightText.Targeting
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
