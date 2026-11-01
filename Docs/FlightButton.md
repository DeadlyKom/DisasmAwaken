# Кнопка «Перелет» и её пустой callback

Исходная запись FInterfaceItem элемента 21 содержит TextIndex=40, обработчик `#7B46` и рисователь `#7B51`. Общий DrawCenteredItem пропускает TextIndex+1 ограничителей LF от `#E4AA`. Выбранные физические байты дают строку `Перелет` с CR, исходное написание сохраняется.

[InstallFlightButtonCallback](../Source/Station/InstallFlightButtonCallback.asm) делает JP во внутренний BindCallback `#7B49`, загружает в HL адрес `#7B50`, вызывает ActivateInterfaceCallback и возвращается. Поэтому ссылка на `#7B50` является доказанным использованием адреса кода, хотя она записана LD HL, а не непосредственным CALL или JP. Договор установщика совпадает с [остальными отложенными адаптерами](DeferredActionAdapters.md), с фиксированной целью EmptyFlightCallback.

[EmptyFlightCallback](../Source/Station/EmptyFlightCallback.asm) состоит из одного исходного байта C9, RET. Он сохраняет основные, альтернативные и индексные регистры, I, IFF, IM, память и порты. SP увеличивается на два, PC снимается с CPU-стека, R увеличивается при выборке инструкции. Алгоритма перелёта в этом callback нет. Это не утверждение об отсутствии других механизмов перелёта во всём проекте.

[DrawFlightButton](../Source/Station/DrawFlightButton.asm) читает изменяемое слово индекса, которое исходный загрузчик заполняет значением 21, и хвостовым JP передаёт его DrawCenteredItem. Временный C9 первого байта отключает весь рисователь по обычному договору [DrawAdapters](DrawAdapters.md).

При настоящем вызове через CloseActiveItem пустой callback получает AF=0044. После его RET вызывающая процедура сбрасывает сохранённый адрес callback в EmptyCallback, восстанавливает HL и DE и устанавливает Carry. Эти действия относятся к CloseActiveItem, а не к самому RET по 7B50.

[CheckFlightButton.py](../Tools/Disasm/Research/CheckFlightButton.py) проверяет исходные TextIndex и текстовые байты, все 65536 AF пустого callback, два полных пути установки и косвенного вызова через CloseActiveItem и четыре сравнения рисователя с настоящим DrawCenteredItem. [Отчёт](../Tools/Disasm/Reports/FlightButtonVerification.json).

Установщик дополнительно включён в [CheckDeferredActionAdapters.py](../Tools/Disasm/Research/CheckDeferredActionAdapters.py), который проверяет все селекторы и ветви активации. Независимый bitmap, игровой перелёт, сборка и нативный запуск этими проверками не подтверждены.
