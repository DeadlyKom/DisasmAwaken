# Хвостовой вход в случайный допуск класса

[EnterRandomClassGate](../Source/Action/EnterRandomClassGate.asm) занимает
три исходных байта C3 9E F6 по F68E в ACTION банка 0. Инструкция JP
передаёт управление [DispatchClassOnHighRandomWord](ActionRandomClassGate.md)
с прежним адресом возврата на стеке. Дополнительной рамки нет, R учитывает
один дополнительный M1. Дальнейшие эффекты определяются проверкой слова
потока 0 и выбранным обработчиком класса.

Предыдущая инструкция по F68D завершает
[StepIdleObjectOffset](ActionIdleState.md) через RET. Штатный источник
перехода к F68E остаётся неизвестным.

[Сценарий](../Tools/Disasm/Research/CheckActionRandomClassGate.py) в режиме
`--via-entry` перебирает все 65 536 начальных слов потока, исполняет все
26 целей диспетчера и сравнивает регистры, флаги, R, SP, восемь банков
RAM и кратность записей. Проверен полный возврат после исходного JP.
[Отчёт](../Tools/Disasm/Reports/ActionRandomClassGateEntryVerification.json).
