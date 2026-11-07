# Класс 8, исходное состояние 12

[ConfigureClass8Link](../Source/Action/ConfigureClass8Link.asm) занимает
6536..6548. После подстановки задаёт StateCode=12 и обновляет Stream0.
Только нулевой `(R & H) | L` ведёт в общий SelectLink, который при
принятой связи может изменить состояние на 02.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).
