                module Action
                module ApplyParameterSet
                ; Физические поля [очередь и параметры](../../Docs/ActionQueueParameterPhysicalData.md)
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
                ;   поля 04 и 09 задают PairedLineStep фазового допуска и LinkedRLimit обратной связи, их потребители установлены
                ;   все пятнадцать целей являются доказанными непосредственными операндами исходных инструкций ACTION
                ;   имена полей описывают установленные роли операндов, полный игровой смысл Unknown11 и EffectReserve этим маршрутизатором не устанавливается
                ; -----------------------------------------
                ; выбор пятнадцатибайтового набора, подготовленного BuildParameterTables
Entry:          LD HL, @ControlsParameterTablesState.Parameters
                ; обновление базового порога Link1ABaseLimit для связи 1A при сброшенном бите 3
                LD A, (HL)
                LD (@ActionApplyParametersState.Link1ABaseLimit), A
                INC HL
                ; чтение поля 01 сохранено, следующий LD A, (HL) заменяет его без использования
                LD A, (HL)
                INC HL
                ; обновление порога OtherLinkLimit для индекса связи, отличного от 1A
                LD A, (HL)
                LD (@ActionApplyParametersState.OtherLinkLimit), A
                INC HL
                ; применение поля 03 к аддитивному операнду общего кода
                LD A, (HL)
                LD (@ActionApplyParametersState.RegenPhaseStep), A
                INC HL
                ; обновление PairedLineStep фазового допуска двух линий прицела
                LD A, (HL)
                LD (@ActionApplyParametersState.PairedLineStep), A
                INC HL
                ; применение поля 05 ко второму аддитивному операнду общего кода
                LD A, (HL)
                LD (@ActionApplyParametersState.ThirdGaugeStep), A
                INC HL
                ; применение одного поля 06 к порогу SpawnLowLimit и аддитивному операнду SpawnBiasBase
                LD A, (HL)
                LD (@ActionApplyParametersState.SpawnLowLimit), A
                LD (@ActionApplyParametersState.SpawnBiasBase), A
                INC HL
                ; обновление операнда Class0RLimit, порога аппаратного R для класса 0
                LD A, (HL)
                LD (@ActionApplyParametersState.Class0RLimit), A
                INC HL
                ; обновление операнда RandomLowLimit, порога младшего байта Stream10 в банке 0
                LD A, (HL)
                LD (@ActionApplyParametersState.RandomLowLimit), A
                INC HL
                ; обновление порога R обратной связи CheckAndToggleLinkedOverlay в банке 0
                LD A, (HL)
                LD (@ActionApplyParametersState.LinkedRLimit), A
                INC HL
                ; обновление операнда Class3RLimit, порога аппаратного R для класса 3
                LD A, (HL)
                LD (@ActionApplyParametersState.Class3RLimit), A
                INC HL
                ; применение поля 0B к порогу SavedLowLimit
                LD A, (HL)
                LD (@ActionApplyParametersState.SavedLowLimit), A
                INC HL
                ; применение поля 0C к маске SpawnValueMask
                LD A, (HL)
                LD (@ActionApplyParametersState.SpawnValueMask), A
                INC HL
                ; применение поля 0D к операнду SpawnValueCap
                LD A, (HL)
                LD (@ActionApplyParametersState.SpawnValueCap), A
                INC HL
                ; применение поля 0E к маске SpawnField11, это же значение остаётся в A
                LD A, (HL)
                LD (@ActionApplyParametersState.SpawnField11), A
                RET

                endmodule
                endmodule
