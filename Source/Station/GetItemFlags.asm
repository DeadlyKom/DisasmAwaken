                module Station
                module GetItemFlags
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [указатель поля Flags](../../Docs/Interface.md)
; -----------------------------------------
; Получение адреса поля Flags элемента через последовательный вход GetItemField
; исходная запись 4, файловые смещения #3EEB..#3EEC
; In:
;   HL - шестнадцатибитный индекс, существование записи не проверяется
; Out:
;   HL - (StationState.Items+16*исходный HL+FInterfaceItem.Flags) по модулю 65536
;   DE и BC сохранены, AF=#F1A0
; Corrupt:
;   HL, AF
; Note:
;   поле не читается, возвращается только его адрес
;   после LD A,FInterfaceItem.Flags исполнение идёт в следующем файле GetItemField без CALL
;   альтернативные и индексные регистры, I и IFF сохраняются, стек сбалансирован
;   адрес #9EEB относится к станционному коду, указатель за пределами таблицы не отклоняется
; -----------------------------------------
                ; выбор физического смещения Flags перед последовательным входом GetItemField
Entry:          LD A, FInterfaceItem.Flags

                ; JP @Station.GetItemField.Entry, продолжение в GetItemField.asm

                endmodule
                endmodule
