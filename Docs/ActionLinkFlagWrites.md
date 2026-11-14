# Проверенные писатели LinkFlags

[CheckActionLinkFlagWrites.py](../Tools/Disasm/Research/CheckActionLinkFlagWrites.py) сопоставляет именованные обращения к FActionRecord.LinkFlags с зарегистрированными инструкциями и исходными байтами TRD. Дополнительно включены два писателя через HL, для которых отдельно проверен расчёт адреса поля. Фактическое определение структуры даёт LinkFlags=12, четыре именованных номера битов сверены с Includes/Const. [Отчёт](../Tools/Disasm/Reports/ActionLinkFlagWritesVerification.json).

## Исходные инструкции

| Адрес | Владелец инструкции | Преобразование поля |
|---|---|---|
| #611A | [CreateLinkedMissileRecord](../Source/Action/CreateLinkedMissileRecord.asm) | обнуление, A после XOR |
| #613B | [CreateLinkedMissileRecord](../Source/Action/CreateLinkedMissileRecord.asm) | SET 1 |
| #61EE | [CreateBoostDebrisRecord](../Source/Action/CreateBoostDebrisRecord.asm) | обнуление, A после XOR |
| #6365 | [ApplyPendingRecordLink](../Source/Action/ApplyPendingRecordLink.asm) | SET 0 |
| #647E | [CreateCargoAndUpdateList](../Source/Action/CreateCargoAndUpdateList.asm) | обнуление, литерал 00 |
| #7277 | [ActivateAntimissileSystem](../Source/Action/ActivateAntimissileSystem.asm) | SET 0 |
| #727B | [ActivateAntimissileSystem](../Source/Action/ActivateAntimissileSystem.asm) | SET 3 |
| #7903 | [SpawnAlternate](../Source/Action/SpawnAlternate.asm) | обнуление, A после XOR |
| #7A6B | [SpawnAlternate](../Source/Action/SpawnAlternate.asm) | обнуление, литерал 00 |
| #7DE8 | [FinishSpawnRecord](../Source/Action/FinishSpawnRecord.asm) | обнуление, литерал 00 |
| #E826 | [CheckAndToggleLinkedOverlay](../Source/Action/CheckAndToggleLinkedOverlay.asm) | SET 0 |
| #E8F6 | [SpawnLinkedClass9Records](../Source/Action/SpawnLinkedClass9Records.asm) | обнуление, литерал 00 |
| #F46A | [SpawnPeriodicClass3Record](../Source/Action/SpawnPeriodicClass3Record.asm) | обнуление, литерал 00 |
| #F585 | [ApproachTargetRecordAndResolve](../Source/Action/ApproachTargetRecordAndResolve.asm) | SET 1 |
| #F62C | [ApproachTargetRecordAndResolve](../Source/Action/ApproachTargetRecordAndResolve.asm) | SET 2 |
| #F7BF | [ResumeAfterRecordEffect](../Source/Action/ResumeAfterRecordEffect.asm) | обнуление, литерал 00 |
| #F843 | [DispatchObjectState](../Source/Action/DispatchObjectState.asm) | обнуление, литерал 00 |

Всего подтверждены десять обнулений и семь SET, последний набор использует только биты 0, 1, 2 и 3. Для трёх записей из A установлено происхождение значения от XOR A. Между XOR и записью проходят только присваивания памяти, сохраняющие A. Это локальное доказательство последовательного фрагмента, вход посередине и вмешательство другого исполнителя им не разрешаются. Шесть отрицательных проб отвергают замену XOR на OR и перезапись A значением FF перед целевой записью.

В CreateLinkedMissileRecord перед SET 1,(HL) исполняются RecordIndexToAddress, сложение младшего байта с 0C и его запись в L. Для проверенных выровненных слотов переноса нет. В ApplyPendingRecordLink перед SET 0,(HL) исходный указатель PendingRecord увеличивается на FActionRecord.LinkFlags. Пригодность всех входных указателей и индексов этим сопоставлением не доказывается.

## Проверка преобразования байта

Каждая из 17 исходных инструкций исполнена для всех 256 прежних значений поля в слотах 0, 12 и 24, всего 13056 случаев. SET даёт 5376 проверок, обнуление 7680. Сверены единственная запись с точным адресом и значением, следующий PC и сохранение регистров кроме R/T/PC. Наблюдатель записи подтверждён отдельной настоящей CPU-инструкцией. Прерывания и аппаратная последовательность шинных циклов не моделируются.

SET сохраняет старшую тетраду прежнего байта, нулевая запись сбрасывает её вместе с младшей. Поэтому при исходной нулевой старшей тетраде и выполнении только перечисленных преобразований она остаётся нулевой. Это условный инвариант данного набора писателей, а не установленный инвариант всей игры. При ненулевой входной старшей тетраде SET её не удаляет.

Проверка исполняет изолированные инструкции в плоском представлении оригинального ACTION без переключения банков и родительских вызовов. Для записей из A начальное A=0 согласовано с отдельным локальным доказательством XOR. Числовые слоты являются условиями модели. Остальные косвенные обращения, блочные переносы, CPU-стек, генерируемый код и ROM-обработчики могут иметь другие области записи, они здесь не исключены. Назначение старших битов 7..4 и их происхождение в нативном процессе остаются открытыми.

Именованные читатели отдельно сохранены в отчёте, UpdateObjects читает весь байт, CheckRecordEffectThreshold проверяет бит 3. Прежнее доказательство влияния старших битов на нулевую проверку сохраняется. [Роли и читатели](ActionObjectRecords.md#разряды-linkflags), [структура](../Includes/Structs/Include.inc).
