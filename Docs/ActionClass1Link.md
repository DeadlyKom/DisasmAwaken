# Класс 1, связь и смена класса

[ConfigureClass1Link](../Source/Action/ConfigureClass1Link.asm) занимает
6594..65AC. После незавершившей подстановки задаёт StateCode=01,
обновляет Stream0 и при нулевом предикате `(R & H) | L` вызывает общий
выбор связи. Только после его NZ записывает ClassCode=00.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).

[Последний поток и точные выходы регистров](ActionAdditionalClassHandlers.md#последний-поток-и-выходы-классов-1-3-5-6-и-8).
