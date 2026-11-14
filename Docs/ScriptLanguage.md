# Торговый язык LANG.C

Вход интерпретатора — `#C000`, начало текста — `#CA8F`.
Активные байты вынесены в [MarketScript.asm](../Source/Text/Data/MarketScript.asm),
проверенные ветви товаров описаны в [OriginalTradeScript](OriginalTradeScript.md).
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
| #C992 | `j` | [Text.PushUsedTonnage](../Source/Text/PushUsedTonnage.asm) |
| #C995 | `J` | [Text.PushTonnageCapacity](../Source/Text/PushTonnageCapacity.asm) |
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
| #CA01 | `s` | [Text.IsShipTypeMissingFromRow](../Source/Text/IsShipTypeMissingFromRow.asm) |
| #CA04 | `k` | [Text.ReadShipEquipmentLimit](../Source/Text/ReadShipEquipmentLimit.asm) |
| #CA07 | `c` | [Text.ReadSecondaryEquipmentPrice](../Source/Text/ReadSecondaryEquipmentPrice.asm) |
| #CA0A | `v` | [Text.ReadSecondaryEquipmentWeight](../Source/Text/ReadSecondaryEquipmentWeight.asm) |
| #CA0D | `s` | [Text.IsSkimmerTypeMissingFromRow](../Source/Text/IsSkimmerTypeMissingFromRow.asm) |
| #CA10 | `k` | [Text.ReadSkimmerEquipmentLimit](../Source/Text/ReadSkimmerEquipmentLimit.asm) |
| #CA13 | `c` | [Text.GetCargoSecondByte](../Source/Text/GetCargoSecondByte.asm) |
| #CA16 | `c` | [Text.GetMarketPrice](../Source/Text/GetMarketPrice.asm) |
| #CA19 | `s` | [Text.IsMarketSaleLegal](../Source/Text/IsMarketSaleLegal.asm) |
| #CA1C | `m` | [Text.GetIndexedLoad](../Source/Text/GetIndexedLoad.asm) |
| #CA1F | `c` | [Text.ReadStrideFiveWord](../Source/Text/ReadStrideFiveWord.asm) |
| #CA22 | `t` | [Text.ReadStrideFiveByte](../Source/Text/ReadStrideFiveByte.asm) |
| #CA25 | `s` | [Text.ReadShipSaleField](../Source/Text/ReadShipSaleField.asm) |
| #CA28 | `s` | [Text.GetKeyMajor](../Source/Text/GetKeyMajor.asm) |
| #CA2B | `c` | [Text.GetKeyMinor](../Source/Text/GetKeyMinor.asm) |
| #CA2E | `u` | [Text.GetKeySize](../Source/Text/GetKeySize.asm) |
| #CA31 | `p` | [Text.GetKeyFingerprint](../Source/Text/GetKeyFingerprint.asm) |
| #CA34 | `g` | [Text.GetKeyRegion](../Source/Text/GetKeyRegion.asm) |
| #CA37 | `c` | [Text.ReadSkimmerPriceField](../Source/Text/ReadSkimmerPriceField.asm) |
| #CA3A | `v` | [Text.ReadSkimmerLoadAddend](../Source/Text/ReadSkimmerLoadAddend.asm) |
| #CA3D | `c` | [Text.PushWordFieldWriter](../Source/Text/PushWordFieldWriter.asm) |
| #CA40 | `u` | [Text.PushByteUWriter](../Source/Text/PushByteUWriter.asm) |
| #CA43 | `g` | [Text.PushCargo7BitWriter](../Source/Text/PushCargo7BitWriter.asm) |
| #CA46 | `G` | [Text.PushMarket7BitWriter](../Source/Text/PushMarket7BitWriter.asm) |
| #CA49 | `o` | [Text.PushEquipmentQuantityWriter](../Source/Text/PushEquipmentQuantityWriter.asm) |
| #CA4C | `i` | [Text.PushSecondQuantityWriter](../Source/Text/PushSecondQuantityWriter.asm) |
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

## Границы поиска токена и временный стек числа

[FindToken](../Source/Text/FindToken.asm) не пишет RAM. На совпадении он возвращается обычным RET, сохраняет C и изменяет R. При отсутствии символа выполняется переход в SkipLine.Entry, который загружает ScriptRuntimeState.SavedSP. Это нелокальный выход, вложенные адреса возврата отбрасываются. Последующие команды не входят в локальный договор поиска.

[DispatchToken](../Source/Text/DispatchToken.asm) оставляет в RAM два байта временного адреса возврата CALL FindToken. На успешном пути POP, выполняемый RET, восстанавливает SP, но не очищает эти байты. Косвенный JP передаёт обработчику стек вызывающего кода. При ошибке адрес возврата поиска остаётся в RAM, а SP заменяется в SkipLine. Эффекты выбранного обработчика описываются отдельно.

[ReadDecimal5](../Source/Text/ReadDecimal5.asm) при одной цифре не записывает RAM. При двух и более цифрах вычисление разрядов повторно использует два байта ниже входного SP для PUSH HL и POP BC. После возврата эти байты сохраняют последнее записанное промежуточное слово, SP увеличен на два относительно входа. R изменяется, альтернативные регистры, IY, I и IFF сохраняются при исполнении без прерываний. Это вывод из последовательности инструкций, новый нативный запуск или сборка для этих уточнений не выполнялись.

### Полная область цифровых записей ReadDecimal5

[CheckDecimal.py](../Tools/Disasm/Research/CheckDecimal.py) и [DecimalVerification.json](../Tools/Disasm/Reports/DecimalVerification.json) проверяют все 111110 строк из цифр длиной от одной до пяти, включая все ведущие нули. Ещё 1002 случая проверяют разделители, шестую цифру и отдельные граничные записи. Перед исполнением логический LANG сопоставляется с секторной областью и хешем полного оригинального TRD.

При одной цифре DE и C сохраняются, B становится нулём, A содержит эту цифру. При двух и более цифрах DE содержит младшие разряды без первой цифры. B всегда равен нулю, C содержит удвоенную первую цифру при длине два либо первую цифру при длине три, четыре и пять. A равен 1 при длине два–четыре и первой цифре при длине пять. Это рабочие остатки вычисления, результатом остаётся HL.

Наблюдатель записей CPU подтверждает отсутствие записей вне двух временных байтов стека и сохранение слова возврата. Для двух цифр в этой паре остаётся удвоенная цифра десятков, для трёх–пяти остаётся первая цифра. Порядок шинных циклов PUSH модель не доказывает. Проверены сохранение I, IFF, IM, альтернативных регистров, IY и старшего бита R. Значения I, IFF, IM и R меняются между сценариями, полное декартово произведение входных регистров и произвольное перекрытие текста со стеком не проверяются. Прерывания и нативный запуск не выполнялись.

### Разделение CPU-стека и стека выражений

[EmitOperator](../Source/Text/EmitOperator.asm) после успешного поиска записывает два байта адреса оператора по исходному HL'. CALL поиска и PUSH переноса слова между наборами регистров последовательно используют одну пару ниже входного SP. Неуспешный поиск переходит в SkipLine, не записывая адрес оператора в выражение.

[CallExpression](../Source/Text/CallExpression.asm) до обработчика только читает шестибайтовую FExpressionCall. В двух байтах ниже входного SP он оставляет возврат в PushExpressionWord, ещё два байта повторно использует для Left, Handler и Right. Перед косвенным JP SP меньше входного на два, HL' у начала использованной записи. [PushExpressionWord](../Source/Text/PushExpressionWord.asm) после RET обработчика записывает результат DE вместо Left и продвигает HL' на два, три исходных слова заменяются одним. При таком обработчике итоговый SP на два больше исходного, первоначальное слово возврата сохранено.

Расширенная [модель вызова](../Tools/Disasm/Research/CheckExpressionCalls.py) проверяет 65537 границ обработчика, включая все правые слова при связанном левом слове, и прежние 726 полных вызовов шести реальных операторов. [Отчёт](../Tools/Disasm/Reports/ExpressionCallVerification.json) подтверждает собственные записи CPU и неизменность выражения до обработчика, физическое происхождение байтов и положительный контроль наблюдателя. Все комбинации левого операнда, адреса обработчика и правого операнда, произвольные адреса стеков, прерывания и шинный порядок PUSH не проверяются. Сборка и нативное исполнение не выполнялись.

## Собственные эффекты простых бинарных операторов

Все десять перечисленных операторов не записывают RAM и CPU-стек, возвращаются через исходное слово RET и увеличивают SP на два. I, IFF, альтернативные и индексные регистры сохраняются без прерываний. R изменяется, его старший бит сохраняется.

| Оператор | Смысл флагов | M1 до RET включительно |
|---|---|---|
| [CompareEqual](../Source/Text/CompareEqual.asm) | F от полного вычитания слов | 6 при равенстве, иначе 8 |
| [CompareLess](../Source/Text/CompareLess.asm) | F от полного вычитания слов | 6 при левом меньше, иначе 8 |
| [CompareGreater](../Source/Text/CompareGreater.asm) | F от полного вычитания слов | 6 при равенстве, 7 при левом меньше, иначе 9 |
| [CompareNotLess](../Source/Text/CompareNotLess.asm) | F от полного вычитания слов | 6 при левом меньше, иначе 8 |
| [CompareNotGreater](../Source/Text/CompareNotGreater.asm) | F от полного вычитания слов | 6 при левом меньше, 7 при равенстве, иначе 9 |
| [AddSaturated](../Source/Text/AddSaturated.asm) | S, Z, PV входные, остальные от суммы до ограничения | 5 без переполнения, иначе 6 |
| [SubtractSaturated](../Source/Text/SubtractSaturated.asm) | F от разности до ограничения | 7 без займа, иначе 8 |
| [AndWords](../Source/Text/AndWords.asm) | F от младшего байта результата AND | 7 |
| [OrWords](../Source/Text/OrWords.asm) | F от младшего байта результата OR | 7 |
| [CopyRightOperand](../Source/Text/CopyRightOperand.asm) | AF сохраняется | 3 |

В сравнениях изменение DE через INC/DEC не пересчитывает флаги, F продолжает описывать полную разность слов. AND/OR при ненулевом старшем байте и нулевом младшем могут вернуть Z=1. Ограничение переполненной суммы до FFFF и отрицательной разности до нуля также не пересчитывает F после выбора граничного значения.

[CheckSimpleOperators.py](../Tools/Disasm/Research/CheckSimpleOperators.py) сверяет исходные инструкции с отдельными формулами результата, флагов и M1. В [отчёте](../Tools/Disasm/Reports/SimpleOperatorsVerification.json) 2621440 случаев, по 262144 на оператор. Для каждого левого слова проверены четыре правых профиля, равное, следующее и предыдущее с оборачиванием, а также инверсия всех битов. Подтверждены все регистры кроме T, отсутствие собственных записей и сохранность возврата. Полное произведение операндов, AF и R, произвольные адреса стека и умножение этой моделью не проверяются. Физические секторные байты и хеш оригинального TRD сверены, наблюдатель записей подтверждён CPU. Сборка, прерывания и нативный запуск не выполнялись.

### Три байтовых сумматора индекса

[GetEquipIndex](../Source/Text/GetEquipIndex.asm), [GetCargoIndex](../Source/Text/GetCargoIndex.asm) и [SumSecondaryIndex](../Source/Text/SumSecondaryIndex.asm) имеют одинаковые двенадцать исходных байтов команд за исключением двух адресов чтения. Каждый возвращает BC с B=0 и C суммой двух байтов по модулю 256, A содержит ту же сумму, F от полного байтового сложения. FF является обычным слагаемым, перенос не добавляется к B. В RAM и CPU-стек записи нет, RET увеличивает SP на два. R увеличивается на семь M1, старший бит сохраняется.

Расширенная [CheckWeightFields.py](../Tools/Disasm/Research/CheckWeightFields.py) проверяет все 65536 пары каждого сумматора, 196608 случаев, а также прежние 3584 прямых чтения кодированных количеств. [Отчёт](../Tools/Disasm/Reports/WeightFieldsVerification.json) содержит точный R, отсутствие записей и сохранение возврата именно для трёх сумматоров. Физические байты STATIONF и LANG сверены с оригинальным TRD. Полное произведение компонент, AF и R и произвольные адреса стека не проверяются, прерывания не исполняются.
