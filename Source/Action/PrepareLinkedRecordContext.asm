                module Action
                module PrepareLinkedRecordContext
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedContext.md)
                ; -----------------------------------------
                ; Подготовка адреса связанной записи и трёх компонент текущей записи в операндах последующего расчёта
                ; исходная запись 17, адреса E761..E793
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает читаемые LinkedIndex и Components записи
                ;   обычный индекс 00..FE адресует A100+64*индекс, особый FF выбирает A780
                ;   ACTION банка 0 доступен, четыре изменяемых слова доступны для записи, два дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   HL при недоступности равен выбранному адресу плюс один, иначе равен третьему слову Components текущей записи IX
                ;   DE и BC сохраняются
                ;   AF содержит A=прочитанный старший байт выбранной Component0 и F от CP с 80, Z означает только недоступность этой записи
                ;   HL', DE', BC', AF' сохраняются
                ;   IX и IY сохраняются, выбранный адрес записывается в операнд будущего LD IY,nn без изменения живого IY
                ;   RecordPointer всегда получает выбранный адрес, даже при Component0.High=80
                ;   при доступной цели Component0..2 операндов получают три исходных слова Components текущей записи IX, иначе все три операнда сохраняются
                ;   I, IM, IFF и paging сохраняются, SP после внешнего RET равен входному SP+2
                ;   R добавляет 11 либо 23 M1 до отказа для FF либо обычного индекса и ещё 16 при подготовке компонент, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, AF, R, RecordPointer, условно три компонентных операнда и два временных байта CPU-стека, SP внешним RET
                ; Note:
                ;   FF в этом договоре не означает индекс 255 и не даёт E0C0, отдельный адрес A780 сохраняется без нового размещения
                ;   проверка сравнивает полный старший байт с 80, младший код маркера не читается
                ;   197632 сценария покрывают все слова каждой компоненты, все байты связи и все старшие байты A780 для FF и обычного 1A
                ;   RecordPointer читает LoadLinkedRecordVectors, Component0..2 читают LoadMotion состояния 02 и LoadMotion состояния 05 с различной ориентацией аргументов
                ;   точные регистры, флаги, R, восемь банков и все записи проверены, последующие потребители операндов этим тестом не исполняются
                ;   все совместные входы, IRQ, сборка и нативный запуск не проверялись
                ; -----------------------------------------
                ; Проверка специального кода связи FF до обычного преобразования индекса.
Entry:          LD A, (IX + @FActionRecord.LinkedIndex)
                INC A
                JR NZ, @Action.PrepareLinkedRecordContext.UseIndex              ; переход, если LinkedIndex отличается от FF, восстановить индекс и вычислить его адрес

                ; Выбор исходного специального адреса A780 вместо обычного адреса индекса 255.
                LD HL, @ActionLinkedContextConst.SpecialRecord
                JR @Action.PrepareLinkedRecordContext.StorePointer

                ; Восстановление обычного индекса после проверки INC и расчёт адреса без ограничения исходным массивом.
UseIndex:       DEC A
                CALL @Action.RecordIndexToAddress.Entry
                ; Обновление операнда будущего LD IY,nn выбранным адресом, живой IY здесь сохраняется.
StorePointer:   LD (@ActionLinkedContextState.RecordPointer), HL
                ; Проверка старшего байта первой компоненты выбранной записи после сохранения указателя.
                INC L
                LD A, (HL)
                CP @ActionReuseConst.ReusableHigh
                RET Z                                                           ; выход, если старший байт выбранной Component0 равен 80, сохранить прежние компонентные операнды

                ; Подготовка исходной компоненты 0 текущей записи в операнд последующего LD DE,nn.
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD (@ActionLinkedContextState.Component0), HL
                ; Подготовка исходной компоненты 1 текущей записи в операнд последующего LD BC,nn.
                LD L, (IX + @FActionRecord.Components.Component1.Low)
                LD H, (IX + @FActionRecord.Components.Component1.High)
                LD (@ActionLinkedContextState.Component1), HL
                ; Подготовка исходной компоненты 2 текущей записи в операнд LD BC,nn после будущего EXX.
                LD L, (IX + @FActionRecord.Components.Component2.Low)
                LD H, (IX + @FActionRecord.Components.Component2.High)
                LD (@ActionLinkedContextState.Component2), HL
                RET

                endmodule
                endmodule
