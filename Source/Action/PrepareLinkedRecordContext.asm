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
                ;   RecordPointer всегда получает выбранный адрес, даже если старший байт его Component0 равен 80
                ;   A равен прочитанному старшему байту выбранной Component0, F соответствует CP с 80, Z означает только недоступность этой записи
                ;   при недоступности HL равен выбранному адресу плюс один, три компонентных операнда сохраняются
                ;   иначе Component0..2 операндов получают три исходных слова Components текущей записи IX, HL равен её третьей компоненте
                ;   DE, BC, HL', DE', BC', AF', IX, IY, I/IM/IFF и paging сохраняются, IY непосредственно не загружается
                ;   SP после внешнего RET увеличен на два, R добавляет 11 либо 23 M1 до отказа для FF либо обычного индекса и ещё 16 при подготовке компонент
                ; Corrupt:
                ;   HL, AF, R, RecordPointer, условно три компонентных операнда и два временных байта CPU-стека, SP внешним RET
                ; Note:
                ;   FF в этом договоре не означает индекс 255 и не даёт E0C0, отдельный адрес A780 сохраняется без нового размещения
                ;   проверка сравнивает полный старший байт с 80, младший код маркера не читается
                ;   197120 сценариев покрывают все слова каждой компоненты и все байты связи, за исходным массивом сохранены оригинальные байты
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
