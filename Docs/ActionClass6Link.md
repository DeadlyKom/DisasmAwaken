# Класс 6, два противоположных выбора

[ConfigureClass6Link](../Source/Action/ConfigureClass6Link.asm) занимает
657F..6593. После подстановки задаёт StateCode=01 и обновляет Stream0.
Ненулевой `(R & H) | L` ведёт в общий SelectLink, нулевой в повторную
подстановку и фильтр классов 6/7. Исходная инверсия условия сохраняется.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).
