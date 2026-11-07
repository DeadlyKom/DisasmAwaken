# Создание связанной записи с общим продолжением

[SpawnLinkedClass17AndContinue](../Source/Action/SpawnLinkedClass17AndContinue.asm) занимает F24F..F254 ACTION банка 0. Настоящий CALL вызывает [SpawnClass17FromCurrentLink](../Source/Action/SpawnClass17FromCurrentLink.asm), затем без проверки результата выполняется JP F0F8. Внешний SP сохраняется, собственные инструкции добавляют два M1. Требуются восемь дополнительных байтов стека с учётом дочерней рамки.

В [проверке State02](../Tools/Disasm/Research/CheckActionLinkedTargetState.py) эта обёртка реально исполнена 5700 раз в наборе из 44656 сценариев. Сверены точные регистры, R, все восемь банков и кратность записей. Это не подмена вызова короткой моделью. [Результат](../Tools/Disasm/Reports/ActionLinkedTargetStateVerification.json).

Общий F0F8, полное произведение входов, аппаратные IRQ, точные T, сборка и нативная игра не проверялись.
