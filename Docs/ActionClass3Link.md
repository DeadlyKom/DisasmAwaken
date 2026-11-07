# Класс 3, фильтр и специальный код

[ConfigureClass3Link](../Source/Action/ConfigureClass3Link.asm) занимает
65DE..660D. После подстановки задаёт StateCode=02 и LinkedIndex=FF.
При R не меньше Class3RLimit ищет класс 5 либо 14, иначе проверяет Gate и новое
слово Stream8 перед записью отдельного кода 1A.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).

Текущие операнды порогов могут изменяться ApplyParameterSet. Значения 70, A0 и 06 относятся к исходным байтам, а не ко всем игровым настройкам. [Писатели, точные переменные условия и проверка](ActionParameterThresholds.md).
