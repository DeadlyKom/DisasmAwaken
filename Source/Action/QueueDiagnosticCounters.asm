                module Action
                module QueueDiagnosticCounters
                ; Физические поля [локальный контекст](../../Docs/ActionLocalContextPhysicalData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionDiagnosticQueue.md)
                ; -----------------------------------------
                ; Постановка диагностических строк Status и Deads и трёх чисел в текстовую очередь
                ; исходная запись 17, адреса ACAB..ACD5
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, входные значения A и DE не являются параметрами
                ;   доступны числовой ActionFlightStatus.Value.Code и слово ActionArrivalState.RankScore
                ;   строки ACD6..ACE9 доступны, Controls банка 1 и его очередь соответствуют договору QueueTextItem
                ;   7FFD разблокирован, на стеке внешний возврат и доступны восемнадцать байтов ниже входного SP, IRQ не вмешиваются
                ; Out:
                ;   HL сохраняется
                ;   DE=#0200 OR LOW(исходный ActionArrivalState.RankScore), это последний переданный числовой запрос независимо от его приёма
                ;   BC сохраняется
                ;   AF содержит A=#10 и исходный F
                ;   HL', DE', BC' сохраняются
                ;   AF' содержит A'=#11 и исходный F'
                ;   IX и IY сохраняются, I, IM и IFF сохраняются
                ;   шесть запросов имеют порядок StatusText, число Value.Code, DeadsText, число HIGH(RankScore), число LOW(RankScore), NewLine
                ;   каждый запрос независимо принимается либо молча отклоняется производителем, общего статуса приёма нет
                ;   OUT 7FFD получает #11, #10 шесть раз, конечная конфигурация #10, прежняя страница не восстанавливается
                ;   SP после RET равен входному SP+2, максимальная глубина временных записей восемнадцать байтов, R меняется и отдельно не доказан
                ; Corrupt:
                ;   DE, A, A', R, очередь и её курсор, paging и восемнадцать временных байтов CPU-стека
                ; Note:
                ;   первый текст равен Status, двоеточие, пробел и LF, второй начинается CR и содержит Deads, двоеточие, пробел и LF
                ;   последний запрос передаёт отдельные CR и LF, постановка указателей не равна фактическому выводу текста
                ;   1088 сценариев проверили настоящие вызовы, все регистры кроме R/T, RAM вне стека и порядок запросов
                ;   штатная таблица клавиш вызывает этот вход для строки «Бортовой компьютер», переход и возврат проверены
                ;   остаточные значения временных слов стека, IRQ и нативный вывод этой процедурой не проверены
                ; -----------------------------------------
                ; Сохранение DE перед постановкой первого текстового указателя.
Entry:          PUSH DE
                ; Выбор исходной строки Status с завершающим LF.
                LD DE, @ActionDiagnosticMessages.StatusText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Чтение первого диагностического байта и постановка его как числа.
                LD A, (@ActionFlightStatus.Value.Code)
                CALL @Action.QueueNumberBank1.Entry
                ; Сохранение числового DE вокруг постановки второй строки.
                PUSH DE
                ; Выбор исходной строки CR, Deads и LF.
                LD DE, @ActionDiagnosticMessages.DeadsText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Постановка старшего байта ранга отдельным числом после Deads.
                LD A, (@ActionArrivalState.RankScore + 1)
                CALL @Action.QueueNumberBank1.Entry
                ; Постановка младшего байта ранга отдельным числом.
                LD A, (@ActionArrivalState.RankScore)
                CALL @Action.QueueNumberBank1.Entry
                ; Сохранение последнего числового DE вокруг постановки CR и LF.
                PUSH DE
                ; Выбор двухбайтового завершения диагностического вывода.
                LD DE, @ActionDiagnosticMessages.NewLine
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
