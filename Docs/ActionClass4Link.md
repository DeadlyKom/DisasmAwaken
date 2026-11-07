# Класс 4, связь с классами 5 и 14

[ConfigureClass4Link](../Source/Action/ConfigureClass4Link.asm) занимает
65AD..65C5. После подстановки задаёт StateCode=02 и LinkedIndex=FF,
при R не меньше 70 ищет класс 5 либо 14. Прямой вызов генератора
в этом обработчике отсутствует.
[Полные правила, регистры и проверка](ActionAdditionalClassHandlers.md).
