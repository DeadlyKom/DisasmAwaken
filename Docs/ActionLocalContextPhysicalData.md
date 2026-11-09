# Локальные поля контекста ACTION

Оформлены десять существующих байтов фиксированного банка 2. Между ними сохранены неизвестные промежутки, адреса и исходные значения не изменены. Структуры отражают доказанные обращения, их наличие не устанавливает полный игровой смысл всех полей.

| Адрес | Физическая запись | Поля и исходные значения |
|---|---|---|
| 9BC6..9BC9 | [OtherContext](../Source/Action/Data/OtherContext.asm) | FContextWordPair, OtherFirst=4B38, OtherSecond=4AF4 |
| 9BCA | [ContextIndex](../Source/Action/Data/ContextIndex.asm) | FContextPublishIndex.SelectedIndex=02 |
| 9BCD | [IndexedGate](../Source/Action/Data/IndexedGate.asm) | FIndexedGateValue.Value=00 |
| 9BCE..9BCF | [ArrivalCounter](../Source/Action/Data/ArrivalCounter.asm) | FArrivalCounter.Value=0000 |
| 9BD2..9BD3 | [ByteLimitCounter](../Source/Action/Data/ByteLimitCounter.asm) | FByteLimitCounter, Current=00, Limit=28 |

## Сравнение и публикация

[CompareContextWordPairs](../Source/Action/CompareContextWordPairs.asm) сравнивает OtherFirst с SeedFirst, при неравенстве сразу возвращает первую разность. Только при равенстве сравниваются OtherSecond и SeedSecond, с новым очищенным Carry. [ProjectWideVectors](../Source/Action/ProjectWideVectors.asm) при совпадении обеих пар использует SelectedIndex и затем увеличивает его на один для обратного счётчика. При несовпадении выбирает FE и также увеличивает на один. Эти локальные роли не доказывают названия планет, координат или допустимую игровую ёмкость.

## Байт поправок и порогов

[ApplyIndexedDelta](../Source/Action/ApplyIndexedDelta.asm) использует Value одновременно как signed8 для сложения и как unsigned8 при проверке прежнего значения. При допустимом индексе получается clamp(signed8(old)+delta, 0, 127), затем бит 5 принудительно устанавливается, если прежний unsigned8(old) меньше 32. Эта установка относится к старому значению, а не к знаку нового результата. При ненулевом режиме по 9B83 неотрицательная исходная поправка предварительно увеличивается на десять. [Подробный алгоритм](ActionTypeDelta.md) сохраняет особенности исходных переполнений.

Схема байта 7..0 не задаёт независимые игровые флаги. Биты 7..0 совместно образуют числовой аргумент, только для бита 5 установлена дополнительная принудительная запись с маской 20. При исходном нуле дальнейший результат зависит от поправки и правила установки этого бита. Неизвестные игровые значения разрядов не назначаются. Alias UnknownGate сохранён, хотя физическое поле теперь оформлено структурой.

## Два разных счётчика

[ApproachTargetRecordAndResolve](../Source/Action/ApproachTargetRecordAndResolve.asm) увеличивает ArrivalCount как слово по модулю 65536 на своей ближней ветви для классов 0, 5, 6 и 7 при ненулевом Unknown11. [QueueDiagnosticCounters](../Source/Action/QueueDiagnosticCounters.asm) выводит его два байта после текста Deads отдельными числовыми запросами, сначала старший, затем младший. Диагностическая надпись сама по себе не доказывает, что слово считает убийства или смерти игрока.

У FByteLimitCounter другой адрес и другой алгоритм. [UpdateBodyMotion](../Source/Action/UpdateBodyMotion.asm) при разрешённом пополнении читает Current в E и Limit в D, увеличивает E по модулю 256, сравнивает беззнаковые D и E. Если кандидат не выше Limit, сохраняет пару и увеличивает байт, выбранный SelectPreferredByte. Иначе не сохраняет ни счётчик, ни выбранный байт. На обоих исходах ставится запрос второй шкалы. При Current=FF кандидат равен нулю, искусственного насыщения здесь нет.

[ConsumeMissileStock](../Source/Action/ConsumeMissileStock.asm) уменьшает только Current по модулю 256, Limit сохраняется. Этот отдельный декремент не даёт оснований назвать всю пару общим запасом ракет. Игровые единицы и связь пополнения со списанием остаются неизвестными. [Разбор пополнения](ActionWideMotionPrefix.md) и [списания](ActionMissileConsume.md) описывают отдельные условия входа.

[Описание физических полей](../Tools/Disasm/Research/ActionLocalContextPhysicalData.py) и [отчёт](../Tools/Disasm/Reports/ActionLocalContextPhysicalDataClassification.json) проверяют инициализаторы и размещение. Модели каждого потребителя перечислены в REQUIRED_REPORTS, границы их доказательств не расширяются классификацией данных. Сборка и нативный запуск не выполнялись.
