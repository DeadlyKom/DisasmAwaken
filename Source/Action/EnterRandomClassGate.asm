                module Action
                module EnterRandomClassGate
                ; Документация [хвостовой вход в случайный допуск класса](../../Docs/ActionRandomClassGateEntry.md)
                ; -----------------------------------------
                ; Хвостовой вход в проверку случайного допуска класса
                ; исходная запись 17, ACTION банка 0, адреса F68E..F690
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX текущая FActionRecord
                ;   выбран ACTION банка 0, подготовлен Stream0, действует входной договор DispatchClassOnHighRandomWord
                ; Out:
                ;   JP передаёт управление DispatchClassOnHighRandomWord с исходным SP и регистрами, R учитывает один дополнительный M1
                ;   при полном исполнении выходы, записи и возврат определяются договором DispatchClassOnHighRandomWord
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', R, Stream0 и стек по DispatchClassOnHighRandomWord
                ;   остальные регистры и поля по допущенному обработчику класса
                ; Note:
                ;   три байта следуют после RET обработчика StepIdleObjectOffset, штатный вызывающий путь F68E неизвестен
                ;   65536 исполнений до внешнего RET сверены с моделью случайного допуска, включая R и восемь банков RAM
                ; -----------------------------------------
                ; Передача исходного возврата проверке случайного допуска класса.
Entry:          JP @Action.DispatchClassOnHighRandomWord.Entry

                endmodule
                endmodule
