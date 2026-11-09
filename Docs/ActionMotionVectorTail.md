# Масштабирование движения для следующего кадра

[Фрагмент 6E6C](../Source/Action/UpdateMotionFromControls.asm) сначала вызывает
[StepNearZeroWord](../Source/Action/StepNearZeroWord.asm) и
[диспетчер клавиш 6F1D](../Source/Action/ScanActionKeys.asm). После их
возврата по `#6E72` берётся знаковое слово `SignedWord` по `#A78F`.
Три байтовых коэффициента `C20`, `C21` и `C22` относятся к третьей
строке той же матрицы, которую читает
[ComputePatchedVector](../Source/Action/ComputePatchedVector.asm).

Каждый вызов [MultiplySignedScaled](../Source/Action/MultiplySignedScaled.asm)
передаёт слово в `DE`, коэффициент в `A`, а продолжение в `IX`.
Результат в `HL` сохраняется по `#E5B3`, `#E5D2` или `#E5ED`
соответственно. Сохраняются исходные свойства умножителя, в том числе
нулевой модуль байтового коэффициента `#80`. Все три пары исходных NOP
остаются между чтением коэффициента и чтением слова.

В [кадровом цикле](../Source/Action/UpdateFrame.asm) этот фрагмент
вызывается после [обходчика эффектов](ActionVisualEffectWalk.md).
Обходчик использует значения тех же трёх слов до их пересчёта.

[Модель хвоста](../Tools/Disasm/Research/CheckActionMotionVectorTail.py)
прошла 65536 сценариев с каждым значением знакового слова.
Сверены три результата, регистры, R и возврат стека. Проверка
начинается после обоих первых вызовов.
[Результаты](../Tools/Disasm/Reports/ActionMotionVectorTailVerification.json)

[Сквозная модель без нажатий](../Tools/Disasm/Research/CheckActionMotionWithoutKeys.py)
выполнила 5376 сценариев с настоящим сканированием 27 условий,
затуханием и тремя умножениями. Сверены знаковое слово, три результата
и внешний стек. Все чтения клавиатуры возвращали `#FF`. Эта модель
охватывает полный проход без выбора обработчика.
[Результаты](../Tools/Disasm/Reports/ActionMotionWithoutKeysVerification.json)

## Самомодификация начала хвоста

[ToggleFreeFlightMode](../Source/Action/ToggleFreeFlightMode.asm) заменяет исходный опкод 3A по 6E72 на C9 либо восстанавливает 3A. При C9 оба предшествующих вызова уже выполнены, но три последующих умножения и записи Component0..2 пропускаются. IX и прочие регистры остаются результатом предшествующих процедур, их сохранение на полном входе этим не утверждается. Произвольные иные опкоды договором не охвачены. [Алгоритм команды](ActionFreeFlightCommand.md).

[Отдельная модель возвратного хвоста](../Tools/Disasm/Research/CheckActionFreeFlightReturnTail.py) начинает с 6E72 после доказанной записи C9. В [1024 сценариях](../Tools/Disasm/Reports/ActionFreeFlightReturnTailVerification.json) проверены все F и четыре граничных R, точное сохранение регистров, один M1, SP+2 и неизменность всей RAM. Предшествующие StepNearZeroWord и ScanActionKeys в этой проверке не исполняются. Эта проверка не заменяет полного исполнения UpdateMotionFromControls или нативной игры.

## Пары направления вида

[ToggleViewDirection](../Source/Action/ToggleViewDirection.asm) создаёт по 6E75, 6E88 и 6E9B три согласованные пары 0000 либо ED44. Две NOP сохраняют загруженный C2i, NEG даёт эффективный коэффициент (-C2i) AND FF. Исходный коэффициент 80 остаётся 80, особенность MultiplySignedScaled с нулевым модулем не исправляется. Две NOP и NEG занимают по два байта и два M1.

[65536 сценариев заднего хвоста](../Tools/Disasm/Reports/ActionMotionRearTailVerification.json) действительно исполняют все три NEG и проверяют результаты, регистры, флаги, R и внешний возврат. Предшествующие вызовы и все побочные записи RAM этой моделью отдельно не проверяются. [Модель](../Tools/Disasm/Research/CheckActionMotionVectorTail.py) запускает этот вариант аргументом --rear. [Создание пар и его отдельная проверка](ActionViewDirectionCommand.md).
