# Торговый язык LANG.C

Вход интерпретатора — `#C000`, начало текста — `#CA8F`.
Символы и таблицы проверены по самому файлу. [Исходный сценарий](MarketScript.txt)
сохранён в UTF-8 для чтения, сборка использует исходные байты CP866.

Сценарий содержит покупку и продажу товаров, кораблей и оборудования,
плату за стоянку и начальные проверки. Поле `c` используется как кредиты,
`X` выбирает событие. Полное предметное назначение остальных полей ещё
требует сверки со структурами и писателями состояния.

Сравнение возвращает слово 0 или 1 в DE. Слова выражений помещаются
через HL альтернативного набора. Операнды и методы работы со стеком
разбираются в исходниках Text, арифметические ограничения — в [Arithmetic](Arithmetic.md).

Числовой литерал читает [ReadDecimal5](../Source/Text/ReadDecimal5.asm).
Вызывающий код уже должен подтвердить первую цифру, IX указывает на неё.
Считыватель принимает от одной до пяти цифр и оставляет IX на первом
непрочитанном символе. После пятой цифры шестой символ не проверяется.
Ведущие нули допустимы, результат возвращается в HL по модулю 65536,
поэтому 99999 превращается в 34463. Насыщения и сообщения о переполнении нет.

Число вычисляется с конца: сначала единицы, затем вклады десятков, сотен,
тысяч и десятков тысяч. Множители 10, 100, 1000 и 10000 получаются
сложениями и сдвигами HL. Временные слова на CPU-стеке восстанавливаются.
Альтернативные регистры и IY сохраняются.
[Проверка оригинальных байтов](../Tools/Disasm/Research/CheckDecimal.py)
охватила все 100000 чисел диапазона 0..99999 и 1002 дополнительных случая
с ведущими нулями, шестой цифрой и всеми недесятичными разделителями
после первых четырёх позиций. Результат —
[DecimalVerification.json](../Tools/Disasm/Reports/DecimalVerification.json).

Ниже все 102 трёхбайтовые записи семейства таблиц `#C935..#CA66`.
Одинаковый символ в разных подтаблицах имеет разное назначение.

Физически они собраны из 102 экземпляров FScriptToken в
[TokenBindings.asm](../Source/Text/Data/TokenBindings.asm). Поле Symbol
занимает байт, Handler занимает слово младшим байтом вперёд.
Имена экземпляров обозначают символы, они не заменяют ещё не завершённый
смысловой разбор свойств. Группа Suffixes содержит несколько подтаблиц,
которые выбираются вызывающим кодом с собственным ограничением B.

[FindToken](../Source/Text/FindToken.asm) сначала прибавляет размер записи
к HL, поэтому входной HL указывает за три байта до первой записи.
При совпадении он возвращает адрес поля Symbol и устанавливает Z.
Счётчик B уменьшается только после несовпадения. Входной B=0 даёт 256
проверок. Если символа нет, выполняется переход в SkipLine с последующим
сбросом CPU-стека, обычного возврата с кодом ошибки не предусмотрено.

[EmitOperator](../Source/Text/EmitOperator.asm) читает символ через IX,
ищет его среди 11 бинарных операторов и пишет адрес обработчика
в буфер через альтернативный HL. Указатель буфера увеличивается на два.
[Проверка](../Tools/Disasm/Reports/TokenDispatchVerification.json)
охватила 102 записи таблиц, 256 случаев нулевого счётчика, отсутствие
символа и запись всех 11 операторов. Полное исполнение сценария этим не доказано.

## Вызов бинарного выражения

[CallExpression](../Source/Text/CallExpression.asm) читает физическую
запись FExpressionCall из трёх слов перед альтернативным HL.
Первое слово передаётся как левый операнд DE, второе как адрес обработчика
HL, третье как правый операнд BC. Указатель стека выражений уменьшается на шесть.

На CPU-стек помещается адрес [PushExpressionWord](../Source/Text/PushExpressionWord.asm),
затем выполняется JP (HL). Обработчик должен вернуть результат в DE
через RET и сохранить альтернативный HL. Общий возврат пишет результат
вместо первого слова записи и продвигает указатель на два. Три слова
заменяются одним, итоговая вершина меньше входной на четыре байта.
CPU-стек при таком обработчике восстанавливается.

[Проверка](../Tools/Disasm/Reports/ExpressionCallVerification.json)
подтвердила состояние перед хвостовым вызовом и 726 полных вызовов
шести исходных обработчиков. Она не доказывает контракт произвольного
адреса, записанного вместо обработчика.

## Реестр привязок

| Адрес записи | Символ | Обработчик |
| --- | --- | --- |
| #C935 | `?` | [Text.TestExpression](../Source/Text/TestExpression.asm) |
| #C938 | `:` | [Text.ApplyCondition](../Source/Text/ApplyCondition.asm) |
| #C93B | `{` | [Text.BeginBlock](../Source/Text/BeginBlock.asm) |
| #C93E | `}` | [Text.EndBlock](../Source/Text/EndBlock.asm) |
| #C941 | `@` | [Text.ApplyInverseCondition](../Source/Text/ApplyInverseCondition.asm) |
| #C944 | `+` | [Text.ApplyAddFieldOperation](../Source/Text/ApplyAddFieldOperation.asm) |
| #C947 | `-` | [Text.ApplyRemoveFieldOperation](../Source/Text/ApplyRemoveFieldOperation.asm) |
| #C94A | `=` | [Text.AssignValue](../Source/Text/AssignValue.asm) |
| #C94D | `,` | [Text.Command2C](../Source/Text/Command2C.asm) |
| #C950 | `T` | [Text.RecomputeTonnage](../Source/Text/RecomputeTonnage.asm) |
| #C953 | `M` | [Text.QueueTextAndStopAtLine](../Source/Text/QueueTextAndStopAtLine.asm) |
| #C956 | `m` | [Text.QueueTextCommand](../Source/Text/QueueTextCommand.asm) |
| #C959 | `^` | [Text.FinishScript](../Source/Text/FinishScript.asm) |
| #C95C | `#` | [Text.Command23](../Source/Text/Command23.asm) |
| #C95F | `W` | [Text.Command57](../Source/Text/Command57.asm) |
| #C962 | `=` | [Text.CompareEqual](../Source/Text/CompareEqual.asm) |
| #C965 | `*` | [Text.MultiplyWithChecks](../Source/Text/MultiplyWithChecks.asm) |
| #C968 | `+` | [Text.AddSaturated](../Source/Text/AddSaturated.asm) |
| #C96B | `-` | [Text.SubtractSaturated](../Source/Text/SubtractSaturated.asm) |
| #C96E | `<` | [Text.CompareLess](../Source/Text/CompareLess.asm) |
| #C971 | `>` | [Text.CompareGreater](../Source/Text/CompareGreater.asm) |
| #C974 | `[` | [Text.CompareNotGreater](../Source/Text/CompareNotGreater.asm) |
| #C977 | `]` | [Text.CompareNotLess](../Source/Text/CompareNotLess.asm) |
| #C97A | `&` | [Text.AndWords](../Source/Text/AndWords.asm) |
| #C97D | `!` | [Text.OrWords](../Source/Text/OrWords.asm) |
| #C980 | `:` | [Text.CopyRightOperand](../Source/Text/CopyRightOperand.asm) |
| #C983 | `c` | [Text.ReadCredits](../Source/Text/ReadCredits.asm) |
| #C986 | `o` | [Text.ReadFieldLowero](../Source/Text/ReadFieldLowero.asm) |
| #C989 | `i` | [Text.ReadFieldLoweri](../Source/Text/ReadFieldLoweri.asm) |
| #C98C | `k` | [Text.ReadFieldLowerk](../Source/Text/ReadFieldLowerk.asm) |
| #C98F | `r` | [Text.ReadFieldLowerr](../Source/Text/ReadFieldLowerr.asm) |
| #C992 | `j` | [Text.ReadFieldLowerj](../Source/Text/ReadFieldLowerj.asm) |
| #C995 | `J` | [Text.ReadFieldUpperJ](../Source/Text/ReadFieldUpperJ.asm) |
| #C998 | `y` | [Text.PushTrue](../Source/Text/PushTrue.asm) |
| #C99B | `n` | [Text.PushFalse](../Source/Text/PushFalse.asm) |
| #C99E | `X` | [Text.ReadEventCode](../Source/Text/ReadEventCode.asm) |
| #C9A1 | `u` | [Text.ReadFieldLoweru](../Source/Text/ReadFieldLoweru.asm) |
| #C9A4 | `G` | [Text.ReadFieldUpperG](../Source/Text/ReadFieldUpperG.asm) |
| #C9A7 | `O` | [Text.ReadFieldUpperO](../Source/Text/ReadFieldUpperO.asm) |
| #C9AA | `I` | [Text.ReadFieldUpperI](../Source/Text/ReadFieldUpperI.asm) |
| #C9AD | `K` | [Text.ReadFieldUpperK](../Source/Text/ReadFieldUpperK.asm) |
| #C9B0 | `R` | [Text.ReadFieldUpperR](../Source/Text/ReadFieldUpperR.asm) |
| #C9B3 | `g` | [Text.ReadFieldLowerg](../Source/Text/ReadFieldLowerg.asm) |
| #C9B6 | `e` | [Text.ReadFieldLowere](../Source/Text/ReadFieldLowere.asm) |
| #C9B9 | `m` | [Text.ReadFieldLowerm](../Source/Text/ReadFieldLowerm.asm) |
| #C9BC | `p` | [Text.ReadFieldLowerp](../Source/Text/ReadFieldLowerp.asm) |
| #C9BF | `t` | [Text.ReadFieldLowert](../Source/Text/ReadFieldLowert.asm) |
| #C9C2 | `(` | [Text.ReadFieldCode28](../Source/Text/ReadFieldCode28.asm) |
| #C9C5 | `1` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9C8 | `2` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9CB | `3` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9CE | `4` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9D1 | `5` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9D4 | `6` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9D7 | `7` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9DA | `8` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9DD | `9` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9E0 | `0` | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) |
| #C9E3 | `L` | [Text.ReadFieldUpperL](../Source/Text/ReadFieldUpperL.asm) |
| #C9E6 | `l` | [Text.ReadFieldLowerl](../Source/Text/ReadFieldLowerl.asm) |
| #C9E9 | `Y` | [Text.ReadFieldUpperY](../Source/Text/ReadFieldUpperY.asm) |
| #C9EC | `y` | [Text.ReadFieldLowery](../Source/Text/ReadFieldLowery.asm) |
| #C9EF | `s` | [Text.CheckThresholdSet30](../Source/Text/CheckThresholdSet30.asm) |
| #C9F2 | `n` | [Text.HasActiveNeighbor](../Source/Text/HasActiveNeighbor.asm) |
| #C9F5 | `s` | [Text.CheckThresholdSet14](../Source/Text/CheckThresholdSet14.asm) |
| #C9F8 | `n` | [Text.HasSecondActiveNeighbor](../Source/Text/HasSecondActiveNeighbor.asm) |
| #C9FB | `c` | [Text.ReadStridedWord](../Source/Text/ReadStridedWord.asm) |
| #C9FE | `v` | [Text.ReadStridedByte](../Source/Text/ReadStridedByte.asm) |
| #CA01 | `s` | [Text.IsByteMissingFromFour](../Source/Text/IsByteMissingFromFour.asm) |
| #CA04 | `k` | [Text.GetHighBitCode](../Source/Text/GetHighBitCode.asm) |
| #CA07 | `c` | [Text.Property070](../Source/Text/Property070.asm) |
| #CA0A | `v` | [Text.Property071](../Source/Text/Property071.asm) |
| #CA0D | `s` | [Text.Property072](../Source/Text/Property072.asm) |
| #CA10 | `k` | [Text.Property073](../Source/Text/Property073.asm) |
| #CA13 | `c` | [Text.GetCargoSecondByte](../Source/Text/GetCargoSecondByte.asm) |
| #CA16 | `c` | [Text.GetMarketPrice](../Source/Text/GetMarketPrice.asm) |
| #CA19 | `s` | [Text.IsMarketMarkClear](../Source/Text/IsMarketMarkClear.asm) |
| #CA1C | `m` | [Text.GetIndexedLoad](../Source/Text/GetIndexedLoad.asm) |
| #CA1F | `c` | [Text.ReadStrideFiveWord](../Source/Text/ReadStrideFiveWord.asm) |
| #CA22 | `t` | [Text.ReadStrideFiveByte](../Source/Text/ReadStrideFiveByte.asm) |
| #CA25 | `s` | [Text.Property080](../Source/Text/Property080.asm) |
| #CA28 | `s` | [Text.GetKeyMajor](../Source/Text/GetKeyMajor.asm) |
| #CA2B | `c` | [Text.GetKeyMinor](../Source/Text/GetKeyMinor.asm) |
| #CA2E | `u` | [Text.GetKeySize](../Source/Text/GetKeySize.asm) |
| #CA31 | `p` | [Text.GetKeyFingerprint](../Source/Text/GetKeyFingerprint.asm) |
| #CA34 | `g` | [Text.GetKeyRegion](../Source/Text/GetKeyRegion.asm) |
| #CA37 | `c` | [Text.Property086](../Source/Text/Property086.asm) |
| #CA3A | `v` | [Text.Property087](../Source/Text/Property087.asm) |
| #CA3D | `c` | [Text.PushWordFieldWriter](../Source/Text/PushWordFieldWriter.asm) |
| #CA40 | `u` | [Text.PushByteUWriter](../Source/Text/PushByteUWriter.asm) |
| #CA43 | `g` | [Text.PushCargo7BitWriter](../Source/Text/PushCargo7BitWriter.asm) |
| #CA46 | `G` | [Text.PushMarket7BitWriter](../Source/Text/PushMarket7BitWriter.asm) |
| #CA49 | `o` | [Text.PushEquipmentWeightWriter](../Source/Text/PushEquipmentWeightWriter.asm) |
| #CA4C | `i` | [Text.PushSecondWeightWriter](../Source/Text/PushSecondWeightWriter.asm) |
| #CA4F | `J` | [Text.PushByteJWriter](../Source/Text/PushByteJWriter.asm) |
| #CA52 | `t` | [Text.ActivateResourceRecord](../Source/Text/ActivateResourceRecord.asm) |
| #CA55 | `p` | [Text.WriteIndexedPMode](../Source/Text/WriteIndexedPMode.asm) |
| #CA58 | `v` | [Text.WriteIndexedVMode](../Source/Text/WriteIndexedVMode.asm) |
| #CA5B | `m` | [Text.WriteIndexedMMode](../Source/Text/WriteIndexedMMode.asm) |
| #CA5E | `e` | [Text.WriteIndexedEMode](../Source/Text/WriteIndexedEMode.asm) |
| #CA61 | `K` | [Text.SetPrimarySelection](../Source/Text/SetPrimarySelection.asm) |
| #CA64 | `R` | [Text.SetSecondarySelection](../Source/Text/SetSecondarySelection.asm) |

## Связанные исходники

| Вход | Процедура |
| --- | --- |
| #C7DA | [Text.DispatchToken](../Source/Text/DispatchToken.asm) |
| #C900 | [Text.GetEquipIndex](../Source/Text/GetEquipIndex.asm) |
| #C918 | [Text.GetCargoIndex](../Source/Text/GetCargoIndex.asm) |
