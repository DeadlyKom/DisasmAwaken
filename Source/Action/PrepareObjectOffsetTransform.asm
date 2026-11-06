                module Action
                module PrepareObjectOffsetTransform
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetTransfer.md)
                ; -----------------------------------------
                ; Проверка маркера записи и подготовка смещений для вычислителя 6D06
                ; исходная запись 17, адреса F0F8..F137
                ; In:
                ;   IX указывает FActionRecord, банк 0 выбран, код общей RAM доступен для записи
                ; Out:
                ;   при старшем байте первой компоненты 80 выполняется RET, AF=8042, прочие регистры и RAM сохранены
                ;   иначе Offset0..2 получают байты 07, 08 плюс 128 и 09, E содержит старый счётчик 10
                ;   счётчик обновляется до кандидата INC только при кандидате ниже порога 0F, иначе записывается прежнее значение
                ;   D содержит байт 24 после условного сброса, SP сохранён, управление передано 6D06
                ; Corrupt:
                ;   DE, AF, R, три изменяемых операнда и два поля записи
                ; Note:
                ;   если класс меньше 16 и состояние не 13, байт 24 обнуляется, на остальных путях сохраняется
                ;   196608 сценариев сверяют регистры и R, исходные записи и переход до первой инструкции 6D06
                ; -----------------------------------------
                ; Проверка маркера отсутствующей записи перед обновлением операндов.
Entry:          LD A, (IX + @FActionRecord.Components.Component0.High)
                CP #80
                RET Z                                                           ; выход, если старший байт первой компоненты равен 80

                ; Подготовка трёх байтов смещений вычислителя, второй сдвинут на 128 по модулю байта.
                LD A, (IX + @FActionRecord.Unknown07)
                LD (@ActionObjectOffsetTransferState.Offset0), A
                LD A, (IX + @FActionRecord.Unknown08)
                ADD A, #80
                LD (@ActionObjectOffsetTransferState.Offset1), A
                LD A, (IX + @FActionRecord.Unknown09)
                LD (@ActionObjectOffsetTransferState.Offset2), A
                ; Расчёт кандидата следующего счётчика с сохранением старого значения в E.
                LD A, (IX + @FActionRecord.Unknown10)
                LD E, A
                INC A
                CP (IX + @FActionRecord.TargetIndex)
                JR C, @Action.PrepareObjectOffsetTransform.StoreCounter         ; переход, если байтовый кандидат меньше порога 0F, записать его

                DEC A
StoreCounter:   LD (IX + @FActionRecord.Unknown10), A
                ; Проверка класса и состояния перед сбросом фазового счётчика.
                LD A, (IX + @FActionRecord.ClassCode)
                CP #10
                JR NC, @Action.PrepareObjectOffsetTransform.LoadPhase           ; переход, если класс не меньше 16, сохранить фазовый счётчик

                LD A, (IX + @FActionRecord.Unknown0A)
                CP #13
                JR Z, @Action.PrepareObjectOffsetTransform.LoadPhase            ; переход, если состояние равно 13, сохранить фазовый счётчик

                LD (IX + @FActionRecord.Unknown24), #00
                ; Подготовка D для вычислителя и хвостовая передача с прежним CPU-стеком.
LoadPhase:      LD D, (IX + @FActionRecord.Unknown24)
                JP @Action.ApplyObjectOffsetVector.Entry

                endmodule
                endmodule
