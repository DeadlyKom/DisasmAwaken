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
