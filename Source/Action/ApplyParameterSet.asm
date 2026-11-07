                module Action
                module ApplyParameterSet
                ; Изменяемые пороги [писатели и влияние](../../Docs/ActionParameterThresholds.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionApplyParameters.md)
                ; -----------------------------------------
                ; Применение пятнадцати полей набора к исходным адресам ACTION, поле 1 читается без записи, поле 6 используется дважды
                ; исходная запись 17, общий код фиксированного банка 2, верхнее окно банка 0, смещения #4C5D..#4CAA
                ; In:
                ;   HL, DE, BC и AF входных аргументов не задают, последовательные поля 00..0E читаются из Parameters по 9BA4
                ;   перед входом выбран верхний банк 0, общий код ACTION перенесён в 6000, все перечисленные целевые адреса доступны для записи
                ;   на CPU-стеке внешний возврат, дополнительная рамка не требуется, IRQ не вмешиваются
                ; Out:
                ;   HL=9BB2, DE и BC сохраняются, A=поле 0E, F сохраняется буквально
                ;   выполнены 15 записей по таблице маршрутов, поле 01 только прочитано, поле 06 записано в две разные цели
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, R получает 46 M1
                ; Corrupt:
                ;   HL, AF в части A, пятнадцать целевых байтов, R
                ; Note:
                ;   исходный набор читается в фиксированном порядке, указатель HL продвигается только четырнадцать раз
                ;   две цели Unknown04 и Unknown09 пока не отнесены к доказанным инструкциям или полям данных
                ;   тринадцать остальных целей являются доказанными непосредственными операндами исходных инструкций ACTION
                ;   игровые имена полей и поведение всех изменяемых процедур ещё не установлены, гарантируется точная маршрутизация байтов
                ; -----------------------------------------
                ; выбор пятнадцатибайтового набора, подготовленного BuildParameterTables
Entry:          LD HL, @ControlsParameterTablesState.Parameters
                ; применение поля 00 к операнду CImmediate00 в верхнем банке 0
                LD A, (HL)
                LD (@ActionApplyParametersState.CImmediate00), A
                INC HL
                ; чтение поля 01 сохранено, следующий LD A, (HL) заменяет его без использования
                LD A, (HL)
                INC HL
                ; применение поля 02 к соседнему операнду CImmediate02
                LD A, (HL)
                LD (@ActionApplyParametersState.CImmediate02), A
                INC HL
                ; применение поля 03 к аддитивному операнду общего кода
                LD A, (HL)
                LD (@ActionApplyParametersState.AddImmediate03), A
                INC HL
                ; обновление Unknown04, игровой потребитель этого байта ещё не установлен
                LD A, (HL)
                LD (@ActionApplyParametersState.Unknown04), A
                INC HL
                ; применение поля 05 ко второму аддитивному операнду общего кода
                LD A, (HL)
                LD (@ActionApplyParametersState.AddImmediate05), A
                INC HL
                ; применение одного поля 06 к порогу Compare06A и аддитивному операнду AddImmediate06B
                LD A, (HL)
                LD (@ActionApplyParametersState.Compare06A), A
                LD (@ActionApplyParametersState.AddImmediate06B), A
                INC HL
                ; обновление операнда Class0RLimit, порога аппаратного R для класса 0
                LD A, (HL)
                LD (@ActionApplyParametersState.Class0RLimit), A
                INC HL
                ; обновление операнда RandomLowLimit, порога младшего байта Stream10 в банке 0
                LD A, (HL)
                LD (@ActionApplyParametersState.RandomLowLimit), A
                INC HL
                ; обновление Unknown09 в выбранном верхнем банке 0
                LD A, (HL)
                LD (@ActionApplyParametersState.Unknown09), A
                INC HL
                ; обновление операнда Class3RLimit, порога аппаратного R для класса 3
                LD A, (HL)
                LD (@ActionApplyParametersState.Class3RLimit), A
                INC HL
                ; применение поля 0B к порогу Compare0B
                LD A, (HL)
                LD (@ActionApplyParametersState.Compare0B), A
                INC HL
                ; применение поля 0C к маске OrImmediate0C
                LD A, (HL)
                LD (@ActionApplyParametersState.OrImmediate0C), A
                INC HL
                ; применение поля 0D к операнду HImmediate0D
                LD A, (HL)
                LD (@ActionApplyParametersState.HImmediate0D), A
                INC HL
                ; применение поля 0E к маске OrImmediate0E, это же значение остаётся в A
                LD A, (HL)
                LD (@ActionApplyParametersState.OrImmediate0E), A
                RET

                endmodule
                endmodule
