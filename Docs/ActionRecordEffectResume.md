# Возврат к обходу после большого эффекта

[CheckRecordEffectThreshold](../Source/Action/CheckRecordEffectThreshold.asm)
выбирает порог для `Unknown13`. При `LinkedIndex ≠ #1A` или сброшенном
бите 3 `LinkFlags` порог равен `#0A`. Иначе первый байт `#9C1A`,
отличный от `#FF`, даёт `#1E`. Если отличается только `#9C1B`,
порог равен `#3C`. Если оба равны `#FF`, порог равен `#14`.
При значении от порога выполняется переход к диспетчеру `#F7E6`.
При меньшем значении вызывается большой эффект.

[ResumeAfterRecordEffect](../Source/Action/ResumeAfterRecordEffect.asm)
исполняется сразу после возврата из
[PrepareLargeEffect](../Source/Action/PrepareLargeEffect.asm).
Две исходные инструкции обнуляют `FActionRecord.LinkFlags` текущей
записи и передают управление по `#F735` в
[UpdateObjects](../Source/Action/UpdateObjects.asm).
Вход `#F7C6` находится следом в памяти и выполняется по другим путям.

В [сквозной модели](../Tools/Disasm/Research/CheckActionRecordEffectThreshold.py)
проверены 260 проходов через этот хвост с настоящим выделением эффекта
для класса 16. Сверены запись, стек и четыре переключения страниц.
[Результаты](../Tools/Disasm/Reports/ActionRecordEffectThresholdVerification.json)
