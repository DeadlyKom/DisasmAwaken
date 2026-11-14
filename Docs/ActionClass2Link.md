# Класс 2, связь с классами 6 и 7

[ConfigureClass2Link](../Source/Action/ConfigureClass2Link.asm) занимает
6549..6565. После подстановки задаёт StateCode=02 и LinkedIndex=FF,
при R не меньше 70 повторяет подстановку и ищет класс 6 либо 7.
Дополнительный SelectSixSeven по 655A также используется классом 6,
он не выполняет начальную проверку R и не задаёт StateCode самостоятельно.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).

[Точные выходы без генераторов и дополнительные сценарии](ActionAdditionalClassHandlers.md#выходы-классов-2-4-и-7-без-генераторов).
