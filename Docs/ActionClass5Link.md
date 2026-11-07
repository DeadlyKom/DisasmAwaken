# Класс 5, новое нулевое слово

[ConfigureClass5Link](../Source/Action/ConfigureClass5Link.asm) занимает
6525..6535. После подстановки задаёт StateCode=01 и обновляет Stream0.
Общий выбор связи исполняется только при полном новом HL=0000,
ненулевое слово завершает вызов без общего поиска.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).
