# Action

Операционные факты ниже получены из исходных инструкций.
Список непосредственных чтений и записей не включает косвенные обращения
через HL, DE, BC, IX/IY и эффекты вызываемых подпрограмм.



## CreateMissileForTarget

[Action.CreateMissileForTarget](../../Source/Action/CreateMissileForTarget.asm)

Проверка существования записи цели, поиск свободного слота, инициализация ракеты и создание обратной связи у цели.

[Три пути, поля, флаги и модели](../ActionMissileCreation.md).

## RefreshFlightPanel

[Action.RefreshFlightPanel](../../Source/Action/RefreshFlightPanel.asm)

Принудительное обновление шести шкал и четырёх пар счётчика панели полёта.

Вход `#6145`, запись 17, смещения `#0382..#03AE`.

- Прямые вызовы: `#6649`, `#AB1B`.
- Непосредственные чтения: `#9BBD`, `#9BBF`.
- Непосредственные записи: `#664A`, `#665C`, `#666B`, `#667D`, `#668E`, `#669F`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRefreshPanel.md).

## ReleaseClass14Records

[Action.ReleaseClass14Records](../../Source/Action/ReleaseClass14Records.asm)

Пометка всех активных записей класса 14 через повторный поиск от начала массива.

Вход `#6172`, запись 17, смещения `#03AF..#03B9`.

- Прямые вызовы: `#E98D`, `#F03D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionClass14Reuse.md).

## CreateRandomClass20Record

[Action.CreateRandomClass20Record](../../Source/Action/CreateRandomClass20Record.asm)

Создание записи класса 20 из двух случайных компонент и транспонированного преобразования.

[Алгоритм, точные регистры и модель](../ActionClass20Spawn.md).

## StepRandomizedThirdPhase

[Action.StepRandomizedThirdPhase](../../Source/Action/StepRandomizedThirdPhase.asm)

Случайное обновление счётчика направления и знаковый шаг третьей фазы записи.

[Алгоритм, точные регистры и модель](../ActionRandomPhaseStep.md).

## CheckLinkedDistanceAndStepCodes

[Action.CheckLinkedDistanceAndStepCodes](../../Source/Action/CheckLinkedDistanceAndStepCodes.asm)

Проверка расстояния связанной записи перед шагом кодов либо переходом во временное состояние.

[Алгоритм, точные регистры и модель](../ActionLinkedMotionGate.md).

## StepRecordTargetCodes

[Action.StepRecordTargetCodes](../../Source/Action/StepRecordTargetCodes.asm)

Подвод двух байтов записи к рассчитанным кодам с различными правилами ограничения шага.

Вход `#6265`, запись 17, смещения `#04A2..#04F1`.

- Прямые вызовы: `#AD5A`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordCodeStep.md).

## EnterTimedPhaseFromMotion

[Action.EnterTimedPhaseFromMotion](../../Source/Action/EnterTimedPhaseFromMotion.asm)

Восстановление рамки движения и установка временного состояния 11 со случайным таймером.

[Алгоритм, точные регистры и модель](../ActionEnterTimedState.md).

## CountClass3LinksUpToTwo

[Action.CountClass3LinksUpToTwo](../../Source/Action/CountClass3LinksUpToTwo.asm)

Подсчёт до двух активных записей класса 3 с кодом 02 и совпадающей ссылкой.

Вход `#62CF`, запись 17, смещения `#050C..#054D`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionClass3LinkCount.md).

## ApproachWordAndAccumulate

[Action.ApproachWordAndAccumulate](../../Source/Action/ApproachWordAndAccumulate.asm)

Приближение HL к BC по обёрнутой разности с накоплением старшего байта остатка в C'.

[Алгоритм, точные регистры и модель](../ActionApproachWord.md).

## ApplyPendingRecordLink

[Action.ApplyPendingRecordLink](../../Source/Action/ApplyPendingRecordLink.asm)

Установка бита 0 LinkFlags, замена LinkedIndex на 1A и условная поправка по ClassCode записи.

Вход `#635B`, запись 17, смещения `#0598..#05F2`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9B83`, `#9BCD`.
- Непосредственные записи: `#635C`, `#9BCD`, `#ECA9`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRecordLinkEvent.md).

## ApplyIndexedDelta

[Action.ApplyIndexedDelta](../../Source/Action/ApplyIndexedDelta.asm)

Применение знаковой табличной поправки к байту 9BCD с ограничением и установкой бита 5 по прежнему значению.

[Договор и независимая модель](../ActionTypeDelta.md).

## RequestPairedAimLines

[Action.RequestPairedAimLines](../../Source/Action/RequestPairedAimLines.asm)

Фазовый допуск двух XOR-линий к прицелу с расходом третьей шкалы и включением захвата цели.

[Алгоритм, точные регистры и модель](../ActionPairedAimLines.md).

## SpawnClass19AndUpdateList

[Action.SpawnClass19AndUpdateList](../../Source/Action/SpawnClass19AndUpdateList.asm)

Создание записи класса 19 по двухбитовому счётчику и обновление списка кодом из сохранённого HL.

[Алгоритм, точные регистры и модель](../ActionClass19Spawn.md).

## DispatchRecordClass

[Action.DispatchRecordClass](../../Source/Action/DispatchRecordClass.asm)

Косвенный переход по оборачиваемому байтовому индексу класса записи.

Вход `#64DF`, запись 17, смещения `#071C..#072C`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: `JP (HL)`.

[Алгоритм, контракты и проверка](../ActionClassDispatch.md).

## ReturnIgnoredRecordClass

[Action.ReturnIgnoredRecordClass](../../Source/Action/ReturnIgnoredRecordClass.asm)

Немедленный общий возврат исходных классов 10..25 без изменения записи.

[Алгоритм, точные регистры и модель](../ActionIgnoredClasses.md).

## ConfigureClass5Link

[Action.ConfigureClass5Link](../../Source/Action/ConfigureClass5Link.asm)

Подстановка и общий выбор связи только при новом нулевом слове потока 0.

[Алгоритм, точные регистры и модель](../ActionClass5Link.md).

## ConfigureClass8Link

[Action.ConfigureClass8Link](../../Source/Action/ConfigureClass8Link.asm)

Подстановка, состояние 12 и общий выбор связи при нулевом аппаратном предикате.

[Алгоритм, точные регистры и модель](../ActionClass8Link.md).

## ConfigureClass2Link

[Action.ConfigureClass2Link](../../Source/Action/ConfigureClass2Link.asm)

Подстановка и выбор связи среди классов 6 и 7 после аппаратного порога.

[Алгоритм, точные регистры и модель](../ActionClass2Link.md).

## ConfigureClass7Link

[Action.ConfigureClass7Link](../../Source/Action/ConfigureClass7Link.asm)

Подстановка и выбор связи с исключением классов 6 и 7 после аппаратного порога.

[Алгоритм, точные регистры и модель](../ActionClass7Link.md).

## ConfigureClass6Link

[Action.ConfigureClass6Link](../../Source/Action/ConfigureClass6Link.asm)

Подстановка с противоположными путями общего выбора и фильтра классов 6 и 7.

[Алгоритм, точные регистры и модель](../ActionClass6Link.md).

## ConfigureClass1Link

[Action.ConfigureClass1Link](../../Source/Action/ConfigureClass1Link.asm)

Подстановка и условный общий выбор связи со сменой класса на 0 после успеха.

[Алгоритм, точные регистры и модель](../ActionClass1Link.md).

## ConfigureClass4Link

[Action.ConfigureClass4Link](../../Source/Action/ConfigureClass4Link.asm)

Подстановка и выбор связи среди классов 5 и 14 после аппаратного порога.

[Алгоритм, точные регистры и модель](../ActionClass4Link.md).

## ConfigureClass9Link

[Action.ConfigureClass9Link](../../Source/Action/ConfigureClass9Link.asm)

Запись кода 0D с сохранением LinkedIndex либо кода 01 со сбросом LinkedIndex в FF.

[Алгоритм, точные регистры и модель](../ActionClass9Link.md).

## ConfigureClass3Link

[Action.ConfigureClass3Link](../../Source/Action/ConfigureClass3Link.asm)

Подстановка, фильтр классов 5 и 14 либо специальный код 26 по потоку 8.

[Алгоритм, точные регистры и модель](../ActionClass3Link.md).

## ConfigureClass0Link

[Action.ConfigureClass0Link](../../Source/Action/ConfigureClass0Link.asm)

Применение подстановки либо выбор новой связи после порога R с общим входом SelectLink.

[Алгоритм, точные регистры и модель](../ActionClass0Link.md).

## CopyRecordLinkOverride

[Action.CopyRecordLinkOverride](../../Source/Action/CopyRecordLinkOverride.asm)

Копирование разрешённого байта подстановки в LinkedIndex и запись кода 02.

[Алгоритм, точные регистры и модель](../ActionLinkOverride.md).

## DrawBankedGauge

[Action.DrawBankedGauge](../../Source/Action/DrawBankedGauge.asm)

Выбор банка 1, вывод шестистрочной шкалы и обязательный выбор банка 0.

Вход `#6639`, запись 17, смещения `#0876..#0885`.

- Прямые вызовы: `#AB1B`, `#E8FD`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionGaugeWrapper.md).

## UpdatePanelGauges

[Action.UpdatePanelGauges](../../Source/Action/UpdatePanelGauges.asm)

Условное обновление шести шкал, сброс пяти запросов и насыщение шестого значения.

Вход `#6649`, запись 17, смещения `#0886..#090E`.

- Прямые вызовы: `#6639`, `#74FB`.
- Непосредственные чтения: `#A78F`, `#A794`, `#A8BC`.
- Непосредственные записи: `#664A`, `#666B`, `#667D`, `#668E`, `#669F`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionPanelGauges.md).

## SubtractScaledWorkVector

[Action.SubtractScaledWorkVector](../../Source/Action/SubtractScaledWorkVector.asm)

Вычитание трёх знаковых масштабированных слов из рабочего 24-битного вектора до первого переполнения.

Вход `#66D2`, запись 17, смещения `#090F..#0963`.

[Алгоритм, контракты и проверка](../ActionSubtractWorkVector.md).

## TransitionBodyMode

[Action.TransitionBodyMode](../../Source/Action/TransitionBodyMode.asm)

Переключение режима тела и изменение старших слов рабочего вектора.

Вход `#6727`, запись 17, смещения `#0964..#09BC`.

[Алгоритм, контракты и проверка](../ActionBodyModeTransition.md).

## UpdateBodyMotion

[Action.UpdateBodyMotion](../../Source/Action/UpdateBodyMotion.asm)

Фазовое обновление рабочего вектора, запросов панели и широких целей.

Вход `#6780`, запись 17, смещения `#09BD..#0BB9`.

- Прямые вызовы: `#699C`, `#69BE`, `#74FB`.
- Непосредственные чтения: `#6682`, `#6693`, `#9B6F`, `#9B70`, `#9B71`, `#9B72`, `#9B73`, `#9B74`, `#9B75`, `#9B76`, `#9B77`, `#9B81`, `#9BC5`, `#9BD2`, `#9C29`, `#E5B3`, `#E5D2`, `#E5ED`.
- Непосредственные записи: `#665C`, `#667D`, `#6682`, `#668E`, `#6693`, `#6781`, `#683C`, `#68D5`, `#68FD`, `#6925`, `#7B6B`, `#9B6F`, `#9B71`, `#9B72`, `#9B74`, `#9B75`, `#9B77`, `#9BD2`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionWideMotionPrefix.md).

## BuildBankedParameterSet

[Action.BuildBankedParameterSet](../../Source/Action/BuildBankedParameterSet.asm)

Выбор банка Controls и хвостовая подготовка с активацией набора параметров.

[Алгоритм, точные регистры и модель](../ActionBankedParameterBuild.md).

## CompareContextWordPairs

[Action.CompareContextWordPairs](../../Source/Action/CompareContextWordPairs.asm)

Сравнение двух пар слов контекста с ранним выходом по первой разности.

Вход `#6986`, запись 17, смещения `#0BC3..#0BD8`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9BC1`, `#9BC3`, `#9BC6`, `#9BC8`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionContextWordPairs.md).

## MaxFoldedVectorHigh

[Action.MaxFoldedVectorHigh](../../Source/Action/MaxFoldedVectorHigh.asm)

Максимум трёх старших байтов с дополнением отрицательных кодов через CPL.

Вход `#699C`, запись 17, смещения `#0BD9..#0BFA`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9B71`, `#9B74`, `#9B77`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionVectorHighMaximum.md).

## FindFirstNearWideVector

[Action.FindFirstNearWideVector](../../Source/Action/FindFirstNearWideVector.asm)

Поиск первого близкого широкого вектора и выбор его наибольшего старшего байта.

Вход `#69BE`, запись 17, смещения `#0BFB..#0C65`.

- Прямые вызовы: `#6A29`.
- Непосредственные чтения: `#688B`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionNearVectorSearch.md).

## CheckThreeUpperWordsNear

[Action.CheckThreeUpperWordsNear](../../Source/Action/CheckThreeUpperWordsNear.asm)

Проверка трёх знаковых верхних слов на диапазон от минус 60 до 59.

Вход `#6A29`, запись 17, смещения `#0C66..#0CAA`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionFoldedNearWords.md).

## PrepareBodyTransform

[Action.PrepareBodyTransform](../../Source/Action/PrepareBodyTransform.asm)

Подготовка компонент тела и передача арифметическому преобразованию AF43.

Вход `#6A6E`, запись 17, смещения `#0CAB..#0CE9`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9B1F`, `#9B22`, `#9B25`.
- Непосредственные записи: `#6AAE`, `#9B1E`, `#9B21`, `#9B24`, `#AF48`, `#AF56`, `#AF69`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPrepareBodyTransform.md).

## RestoreBodyStack

[Action.RestoreBodyStack](../../Source/Action/RestoreBodyStack.asm)

Восстановление настоящего SP после арифметического накопителя.

[Алгоритм, точные регистры и модель](../ActionRestoreBodyStack.md).

## PublishTransformedBody

[Action.PublishTransformedBody](../../Source/Action/PublishTransformedBody.asm)

Публикация знаковых компонент, подготовка проекции и рисование преобразованного тела.

Вход `#6AB0`, запись 17, смещения `#0CED..#0D52`.

- Прямые вызовы: `#AB1B`, `#CEFA`.
- Непосредственные чтения: `#9B81`, `#D7A2`, `#D7C4`, `#D9B6`.
- Непосредственные записи: `#9B1F`, `#9B22`, `#9B25`, `#9B8A`, `#9B8B`, `#9B8C`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPrepareBodyTransform.md).

## ProjectWideVectors

[Action.ProjectWideVectors](../../Source/Action/ProjectWideVectors.asm)

Обход широких векторов с выбором масштаба, отрисовкой близких записей и публикацией выбранной.

Вход `#6B16`, запись 17, смещения `#0D53..#0E3B`.

- Прямые вызовы: `#6986`, `#6A29`, `#6BFF`, `#6C19`, `#6C7E`.
- Непосредственные чтения: `#688B`, `#9BCA`, `#D7A3`, `#D7C5`, `#D9B7`.
- Непосредственные записи: `#9B1E`, `#9B1F`, `#9B21`, `#9B22`, `#9B24`, `#9B25`, `#9B87`, `#9B88`, `#9B89`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionWideProjectionInput.md).

## CopyAndTransformComponents

[Action.CopyAndTransformComponents](../../Source/Action/CopyAndTransformComponents.asm)

Копирование трёх трёхбайтовых компонент с шагом четыре и последующее преобразование рабочего вектора.

Вход `#6BFF`, запись 17, смещения `#0E3C..#0E55`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionComponentTransform.md).

## TransformWorkComponents

[Action.TransformWorkComponents](../../Source/Action/TransformWorkComponents.asm)

Преобразование старших слов трёх рабочих компонент с очисткой Low и знаковым кодированием результата.

Вход `#6C19`, запись 17, смещения `#0E56..#0E7C`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9B1F`, `#9B22`, `#9B25`.
- Непосредственные записи: `#6C41`, `#9B1E`, `#9B21`, `#9B24`, `#AF48`, `#AF56`, `#AF69`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionComponentTransform.md).

## RestoreComponentStack

[Action.RestoreComponentStack](../../Source/Action/RestoreComponentStack.asm)

Восстановление CPU SP после вычисления рабочих компонент перед знаковым кодированием.

[Алгоритм, точные регистры и модель](../ActionComponentStack.md).

## EncodeSignedComponents

[Action.EncodeSignedComponents](../../Source/Action/EncodeSignedComponents.asm)

Кодирование трёх выходных слов в знак и модуль с обратным знаком компоненты 1.

Вход `#6C43`, запись 17, смещения `#0E80..#0EBA`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#D7A2`, `#D7C4`, `#D9B6`.
- Непосредственные записи: `#9B1F`, `#9B22`, `#9B25`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionComponentEncoding.md).

## DrawBankedProjectedBody

[Action.DrawBankedProjectedBody](../../Source/Action/DrawBankedProjectedBody.asm)

Проекция и рисование тела в банке CONTROL с шахматным рисунком.

Вход `#6C7E`, запись 17, смещения `#0EBB..#0ECB`.

- Прямые вызовы: `#AB1B`, `#CEFA`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ProjectedBodyEntry.md).

## UpdateThirdGlyphVector

[Action.UpdateThirdGlyphVector](../../Source/Action/UpdateThirdGlyphVector.asm)

Подготовка трёх входных слов, расчёт вектора с арифметическим SP и обновление третьего экранного знака.

Вход `#6C8F`, запись 17, смещения `#0ECC..#0EED`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9B79`, `#9B7C`, `#9B7F`, `#9B82`.
- Непосредственные записи: `#6CB2`, `#AF48`, `#AF56`, `#AF69`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionThirdGlyphVector.md).

## RestoreThirdGlyphStack

[Action.RestoreThirdGlyphStack](../../Source/Action/RestoreThirdGlyphStack.asm)

Восстановление CPU SP после векторного вычислителя перед публикацией третьего знака.

[Алгоритм, точные регистры и модель](../ActionThirdGlyphStack.md).

## PublishThirdGlyphVector

[Action.PublishThirdGlyphVector](../../Source/Action/PublishThirdGlyphVector.asm)

Перенос четвертей двух выходных слов и знакового байта третьего слова во вход третьего экранного знака.

Вход `#6CB4`, запись 17, смещения `#0EF1..#0F12`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#D7A3`, `#D7C4`, `#D9B6`.
- Непосредственные записи: `#9B84`, `#9B85`, `#9B86`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionThirdGlyphPublish.md).

## InitializeBankedBufferPoints

[Action.InitializeBankedBufferPoints](../../Source/Action/InitializeBankedBufferPoints.asm)

Подготовка 35 координат точек в Controls банка 1 с возвратом полной конфигурации 10.

Вход `#6CD6`, запись 17, смещения `#0F13..#0F20`.

- Прямые вызовы: `#AB1B`, `#CAB3`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionBankedBufferInit.md).

## TransferToStationLoader

[Action.TransferToStationLoader](../../Source/Action/TransferToStationLoader.asm)

Выбор конфигурации 11 и хвостовая передача управления DCE3 загрузчика следующего режима.

[Алгоритм, точные регистры и модель](../ActionStationTransfer.md).

## DispatchBank3Callback

[Action.DispatchBank3Callback](../../Source/Action/DispatchBank3Callback.asm)

Передача управления HL с конфигурацией банка 3, обменом AF и возвратным хвостом Runtime.

Вход `#6CEF`, запись 17, смещения `#0F2C..#0F3C`.

- Прямые вызовы: `#AB1B`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: `JP (HL)`.

[Алгоритм, контракты и проверка](../ActionBankedCallback.md).

## RestoreRuntimePage

[Action.RestoreRuntimePage](../../Source/Action/RestoreRuntimePage.asm)

Выдача конфигурации 10 в 7FFD и возврат внешнему вызывающему после банкового обработчика.

[Алгоритм, точные регистры и модель](../ActionBankedCallbackReturn.md).

## ApplyObjectOffsetVector

[Action.ApplyObjectOffsetVector](../../Source/Action/ApplyObjectOffsetVector.asm)

Расчёт трёх базовых слов записи по коэффициентам смещения.

[Алгоритм, точные регистры и модель](../ActionObjectOffsetVector.md).

## UpdateVisualEffects

[Action.UpdateVisualEffects](../../Source/Action/UpdateVisualEffects.asm)

Обход эффектов, продвижение ресурсов и растеризация допущенных записей.

Вход `#6D38`, запись 17, смещения `#0F75..#100D`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#E5B3`, `#E5D2`, `#E5ED`.
- Непосредственные записи: `#6D39`, `#6D3D`, `#6DD2`, `#AF48`, `#AF56`, `#AF69`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionVisualEffectWalk.md).

## ResumeVisualEffect

[Action.ResumeVisualEffect](../../Source/Action/ResumeVisualEffect.asm)

Восстановление стека и банковый вызов рисователя эффекта при положительной глубине.

[Алгоритм, точные регистры и модель](../ActionVisualEffectResume.md).

[Алгоритм, контракты и проверка](../ActionVisualEffectWalk.md).

## ClassifyCoordinateRegion

[Action.ClassifyCoordinateRegion](../../Source/Action/ClassifyCoordinateRegion.asm)

Классификация пары H,L по трём непересекающимся прямоугольникам с кодом 3 вне них.

Вход `#6E2B`, запись 17, смещения `#1068..#10A8`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRegionType.md).

## UpdateMotionFromControls

[Action.UpdateMotionFromControls](../../Source/Action/UpdateMotionFromControls.asm)

Обработка управления и расчёт трёх смещений из знакового слова.

Вход `#6E6C`, запись 17, смещения `#10A9..#10E8`.

- Прямые вызовы: `#6EAC`, `#6F1D`.
- Непосредственные чтения: `#A78F`, `#CBD8`, `#CBEE`, `#CC09`.
- Непосредственные записи: `#E5B3`, `#E5D2`, `#E5ED`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionMotionVectorTail.md).

## StepNearZeroWord

[Action.StepNearZeroWord](../../Source/Action/StepNearZeroWord.asm)

Изменение слова около нуля, запрос шестой шкалы и выключение обработки при модуле от двух.

Вход `#6EAC`, запись 17, смещения `#10E9..#111A`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#A78F`.
- Непосредственные записи: `#669F`, `#6EAD`, `#A78F`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionNearZeroWord.md).

## ReverseScaledVector

[Action.ReverseScaledVector](../../Source/Action/ReverseScaledVector.asm)

Инвертирование трёх масштабированных компонент и обновление общего знакового слова с разрешением его обработки.

[Алгоритм, точные регистры и модель](../ActionVectorReverse.md).

## ScanActionKeys

[Action.ScanActionKeys](../../Source/Action/ScanActionKeys.asm)

Обход 27 клавиатурных условий и программные вызовы обработчиков.

Вход `#6F1D`, запись 17, смещения `#115A..#118A`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#A85F`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: `IN A,(C)`.
- Косвенное завершение: `JP (HL)`.

[Алгоритм, контракты и проверка](../ActionMotionVectorTail.md).

## RestoreKeyScanFrame

[Action.RestoreKeyScanFrame](../../Source/Action/RestoreKeyScanFrame.asm)

Восстановление IX, BC, DE и HL после обработчика клавиши и продолжение сканирования.

Вход `#6F4E`, запись 17, смещения `#118B..#1191`.

[Рамка и отдельная проверка хвоста](../ActionKeyDispatchPrefix.md).

## LatchControlsAndDecay

[Action.LatchControlsAndDecay](../../Source/Action/LatchControlsAndDecay.asm)

Фиксация запросов управления и фазовое приближение трёх знаковых величин к нулю.

Вход `#6F55`, запись 17, смещения `#1192..#1253`.

- Прямые вызовы: `#6172`.
- Непосредственные чтения: `#9B95`, `#9B96`, `#9B97`.
- Непосредственные записи: `#669F`, `#6F56`, `#6F59`, `#6F7B`, `#6F8D`, `#6FB0`, `#6FC2`, `#6FE5`, `#6FF6`, `#7693`, `#76CD`, `#76F0`, `#7713`, `#7736`, `#7759`, `#777C`, `#9B95`, `#9B96`, `#9B97`, `#A78F`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionControlDecay.md).

## IgnoreKey

[Action.IgnoreKey](../../Source/Action/IgnoreKey.asm)

Пустой обработчик клавиши, возврат к восстановлению рамки без изменения регистров.

Вход `#704B`, запись 17, смещение `#1288`.

[Вызов, возврат и перекрытие последнего указателя](../ActionKeyDispatchPrefix.md).

## RequestMissile0

[Action.RequestMissile0](../../Source/Action/RequestMissile0.asm)

Условный запрос запуска по Target0 с продолжением в общий хвост.

[Пути, состояние и границы проверки](../ActionMissileRequests.md).

## CompleteMissileLaunch

[Action.CompleteMissileLaunch](../../Source/Action/CompleteMissileLaunch.asm)

Создание ракеты, поправка состояния по классу цели и последующее списание запаса.

[Пути, состояние и границы проверки](../ActionMissileRequests.md).

## RequestMissile1

[Action.RequestMissile1](../../Source/Action/RequestMissile1.asm)

Условный запрос запуска по Target1 с переходом в общий хвост.

[Пути, состояние и границы проверки](../ActionMissileRequests.md).

## RequestMissile2

[Action.RequestMissile2](../../Source/Action/RequestMissile2.asm)

Условный запрос запуска по Target2 с переходом в общий хвост.

[Пути, состояние и границы проверки](../ActionMissileRequests.md).

## ReportMissingMissileTarget

[Action.ReportMissingMissileTarget](../../Source/Action/ReportMissingMissileTarget.asm)

Передача в очередь сообщения об отсутствии захваченной цели с сохранением регистров.

Вход `#709B`, запись 17.

[Контракт и композиционная проверка](../ActionMissileLaunch.md).

## CheckMissileLaunch

[Action.CheckMissileLaunch](../../Source/Action/CheckMissileLaunch.asm)

Проверка кода захваченной цели и остатка ракет, очистка трёх захватов при пустом запасе.

Вход `#70A4`, запись 17.

[Контракт и композиционная проверка](../ActionMissileLaunch.md).

## ConsumeMissileStock

[Action.ConsumeMissileStock](../../Source/Action/ConsumeMissileStock.asm)

Уменьшение выбранного запаса и отдельного байта 9BD2, передача сообщения о пуске и нового остатка очереди.

Вход `#70C6`, запись 17.

[Контракт и композиционная проверка](../ActionMissileConsume.md).

## SelectMissileStock

[Action.SelectMissileStock](../../Source/Action/SelectMissileStock.asm)

Выбор ненулевого приоритетного остатка ракет либо запасного счётчика с возвратом адреса.

Вход `#70ED`, запись 17, смещения `#132A..#1332`.

[Назначение, контракт и проверка](../ActionMissileStock.md).

## RequestHyperJump

[Action.RequestHyperJump](../../Source/Action/RequestHyperJump.asm)

Проверка гиперследа, списание выбранного запаса и перенос пятибайтового контекста перед перезагрузкой ACTION.

[Договоры и границы проверки](../ActionHyperJump.md).

## PrepareHyperJumpRelay

[Action.PrepareHyperJumpRelay](../../Source/Action/PrepareHyperJumpRelay.asm)

Сообщение гиперперехода, вывод очереди, исходная задержка и перенос загрузчика ACTION в 4200.

[Договоры и границы проверки](../ActionHyperJumpPreparation.md).

## ActivateAntimissileSystem

[Action.ActivateAntimissileSystem](../../Source/Action/ActivateAntimissileSystem.asm)

Поиск первой ракеты класса 11 с целью 1A, установка признаков противоракетной обработки и вывод сегмента.

[Договоры и границы проверки](../ActionAntimissileCommand.md).

## ClearMissileTargets

[Action.ClearMissileTargets](../../Source/Action/ClearMissileTargets.asm)

Снятие трёх захватов ракет с задержкой повторной команды и сообщением.

[Договоры и границы проверки](../ActionTargetCommands.md).

## ToggleTargetRequest

[Action.ToggleTargetRequest](../../Source/Action/ToggleTargetRequest.asm)

Переключение младшего бита запроса наведения с двумя сообщениями.

[Договоры и границы проверки](../ActionTargetCommands.md).

## RequestAimOrCollectTarget

[Action.RequestAimOrCollectTarget](../../Source/Action/RequestAimOrCollectTarget.asm)

Запрос прицельных линий либо притягивание и сбор захваченного объекта по режиму силового луча.

[Договоры и границы проверки](../ActionTractorCollect.md).

## ToggleTractorMode

[Action.ToggleTractorMode](../../Source/Action/ToggleTractorMode.asm)

Переключение режима силового луча и запроса наведения со снятием захватов.

[Договоры и границы проверки](../ActionTractorModeCommand.md).

## CycleTargetOverlayMode

[Action.CycleTargetOverlayMode](../../Source/Action/CycleTargetOverlayMode.asm)

Смена режима отображения целей при наличии системы наведения.

[Договоры и границы проверки](../ActionOverlayModeCommand.md).

## RequestBoost

[Action.RequestBoost](../../Source/Action/RequestBoost.asm)

Запрос ускорения с проверкой классов и квантованных старших байтов координат.

[Договоры и границы проверки](../ActionBoostCommand.md).

## SelectPreferredByte

[Action.SelectPreferredByte](../../Source/Action/SelectPreferredByte.asm)

Выбор ненулевого предпочтительного байта либо запасного значения с возвратом адреса выбранного поля.

Вход `#74FB`, запись 17, смещения `#1738..#1740`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionPreferredByte.md).

## AdvanceBoost

[Action.AdvanceBoost](../../Source/Action/AdvanceBoost.asm)

Общий хвост ускорения с фазовым расходом выбранного байта, созданием класса 20 и шестнадцатью шагами шкалы.

[Договоры и границы проверки](../ActionBoostAdvance.md).

## ToggleFreeFlightMode

[Action.ToggleFreeFlightMode](../../Source/Action/ToggleFreeFlightMode.asm)

Условная смена опкода координатного обновления с сообщением о свободном полёте.

[Договоры и границы проверки](../ActionFreeFlightCommand.md).

## EjectCargo

[Action.EjectCargo](../../Source/Action/EjectCargo.asm)

Выброс первого ненулевого байта из начала пар груза с сообщением независимо от размещения.

[Договоры и границы проверки](../ActionEjectCommands.md).

## EjectMine

[Action.EjectMine](../../Source/Action/EjectMine.asm)

Списание одной мины и попытка создания помеченной записи класса 19.

[Договоры и границы проверки](../ActionEjectCommands.md).

## RequestStationReturn

[Action.RequestStationReturn](../../Source/Action/RequestStationReturn.asm)

Однократная команда возврата к станции с переходом в банковый подготовитель загрузки.

[Договоры и границы проверки](../ActionStationReturnCommand.md).

## ToggleViewDirection

[Action.ToggleViewDirection](../../Source/Action/ToggleViewDirection.asm)

Разворот базиса, обновление точек и согласованная смена трёх опкодных пар направления вида.

[Договоры и границы проверки](../ActionViewDirectionCommand.md).

## IncreaseGaugeWord

[Action.IncreaseGaugeWord](../../Source/Action/IncreaseGaugeWord.asm)

Увеличение слова шестой шкалы с исходными клавиатурными ограничениями.

[Алгоритм, точные регистры и модель](../ActionKeyGaugeIncrease.md).

## DecreaseGaugeWord

[Action.DecreaseGaugeWord](../../Source/Action/DecreaseGaugeWord.asm)

Уменьшение слова шестой шкалы с исходными клавиатурными ограничениями.

[Алгоритм, точные регистры и модель](../ActionKeyGaugeDecrease.md).

## RequestTurnNegative

[Action.RequestTurnNegative](../../Source/Action/RequestTurnNegative.asm)

Запрос уменьшения управления Turn с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyTurnNegative.md).

## RequestTurnPositive

[Action.RequestTurnPositive](../../Source/Action/RequestTurnPositive.asm)

Запрос увеличения управления Turn с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyTurnPositive.md).

## RequestXNegative

[Action.RequestXNegative](../../Source/Action/RequestXNegative.asm)

Запрос уменьшения управления X с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyXNegative.md).

## RequestXPositive

[Action.RequestXPositive](../../Source/Action/RequestXPositive.asm)

Запрос увеличения управления X с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyXPositive.md).

## RequestYNegative

[Action.RequestYNegative](../../Source/Action/RequestYNegative.asm)

Запрос уменьшения управления Y с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyYNegative.md).

## RequestYPositive

[Action.RequestYPositive](../../Source/Action/RequestYPositive.asm)

Запрос увеличения управления Y с накопителем повтора и исходной знаковой границей.

[Алгоритм, точные регистры и модель](../ActionKeyYPositive.md).

## SpawnAlternate

[Action.SpawnAlternate](../../Source/Action/SpawnAlternate.asm)

Создание записей по шаблону либо по альтернативной ветке планировщика.

Вход `#7859`, запись 17, смещения `#1A96..#1D02`.

- Прямые вызовы: `#6CEF`, `#AACC`, `#AB1B`, `#DE9A`, `#E9A1`, `#EB79`, `#EB80`, `#EB87`, `#EB9C`, `#EBAA`, `#EBB1`, `#EBB8`, `#EBC6`, `#EBCD`, `#F03D`.
- Непосредственные чтения: `#6D3D`, `#7DE4`, `#7E07`, `#7E09`, `#9B78`, `#9B79`, `#9B7B`, `#9B7C`, `#9B7E`, `#9B7F`, `#9B83`, `#9BC1`, `#9BC3`, `#9BC5`, `#EBDB`.
- Непосредственные записи: `#6D39`, `#6D3D`, `#792E`, `#799C`, `#79DE`, `#7A6A`, `#7B61`, `#9B82`, `#9B83`, `#EBDD`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionSpawnSchedule.md).

## ScheduleSpawn

[Action.ScheduleSpawn](../../Source/Action/ScheduleSpawn.asm)

Планирование создания объекта, выбор класса, модели и начальных координат.

Вход `#7B58`, запись 17, смещения `#1D95..#2010`.

[Алгоритм, контракты и проверка](../ActionSpawnSchedule.md).

## FinishSpawnRecord

[Action.FinishSpawnRecord](../../Source/Action/FinishSpawnRecord.asm)

Заполнение параметров новой записи и передача диспетчеру класса.

Вход `#7DD4`, запись 17, смещения `#2011..#20D9`.

[Алгоритм, контракты и проверка](../ActionSpawnRecordFinish.md).

## SelectWideTargetAndStep

[Action.SelectWideTargetAndStep](../../Source/Action/SelectWideTargetAndStep.asm)

Выбор первой близкой широкой цели либо первой записи и обновление кодов текущего объекта.

Вход `#7E9D`, запись 17, смещения `#20DA..#20F3`.

- Прямые вызовы: `#6A29`.
- Непосредственные чтения: `#688B`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionSelectWideTarget.md).

## StepRecordTowardWideVector

[Action.StepRecordTowardWideVector](../../Source/Action/StepRecordTowardWideVector.asm)

Обновление двух кодов записи по трём широким компонентам выбранной цели.

Вход `#7EB7`, запись 17, смещения `#20F4..#214A`.

- Прямые вызовы: `#7F0E`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#7F0F`, `#7F12`, `#7F23`, `#7F26`, `#7F37`, `#7F3A`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionWideTargetStep.md).

## ClampPatchedVectorWords

[Action.ClampPatchedVectorWords](../../Source/Action/ClampPatchedVectorWords.asm)

Сведение трёх изменяемых 32-битных значений к словам с исходным насыщением и знаком по биту 23.

Вход `#7F0E`, запись 17, смещения `#214B..#21B2`.

- Прямые вызовы: `#7F76`.
- Непосредственные чтения: `#7F0F`, `#7F23`, `#7F37`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionClampVectorWords.md).

## AbsSigned32

[Action.AbsSigned32](../../Source/Action/AbsSigned32.asm)

Модуль знакового 32-битного DE:HL с сохранением исходного переполнения минимального значения.

Вход `#7F76`, запись 17, смещения `#21B3..#21CB`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionAbsSigned32.md).

## StartFlight

[Action.StartFlight](../../Source/Action/StartFlight.asm)

Вывод панели из страницы 6 и инициализация полётного режима.

Вход `#A82D`, запись 17, смещения `#482D..#4858`.

- Прямые вызовы: `#6040`, `#6145`, `#6CD6`, `#AB1B`, `#DE0A`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## MainLoop

[Action.MainLoop](../../Source/Action/MainLoop.asm)

Повторение процедуры полётного кадра.

Вход `#A859`, запись 17, смещения `#4859..#485D`.

- Прямые вызовы: `#A85E`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## UpdateFrame

[Action.UpdateFrame](../../Source/Action/UpdateFrame.asm)

Обработка таймеров, управления, визуальных модулей и игровых объектов.

Вход `#A85E`, запись 17, смещения `#485E..#4ACB`.

- Прямые вызовы: `#635B`, `#6649`, `#66D2`, `#6780`, `#6C8F`, `#6D38`, `#6E6C`, `#7B58`, `#AB1B`, `#C870`, `#CAE3`, `#CB00`, `#D10A`, `#E020`, `#E021`, `#E291`, `#E97A`, `#ECA2`, `#ECA8`, `#F094`, `#F10D`, `#F729`.
- Непосредственные чтения: `#6682`, `#6693`, `#9C1C`, `#9C1D`, `#9C1E`, `#A78C`, `#A794`, `#D408`, `#D6CC`, `#D873`, `#E507`.
- Непосредственные записи: `#5A1A`, `#5A1C`, `#664A`, `#666B`, `#A781`, `#A78C`, `#A794`, `#A85F`, `#A8B3`, `#A8BC`, `#A92D`, `#A966`, `#C09F`, `#C13A`, `#C1DC`, `#C243`, `#C247`, `#C2B8`, `#C301`, `#C370`, `#C3D5`, `#C44E`, `#C545`, `#C5CA`, `#C5E7`, `#C649`, `#C672`, `#C6AE`, `#C6B2`, `#C733`, `#C765`, `#C787`, `#C820`, `#C92F`, `#C9A2`, `#C9C4`, `#CA24`, `#CA2F`, `#CA96`, `#CB29`, `#CB39`, `#CB9F`, `#CBA4`, `#CC77`, `#CCE5`, `#CD79`, `#CDC3`, `#CE0E`, `#CE1C`, `#CE28`, `#CE6C`, `#CE9D`, `#CF47`, `#CF9C`, `#CFEF`, `#D083`, `#D0C6`, `#D0CB`, `#D0D0`, `#D0D5`, `#D0F2`, `#D0F6`, `#D138`, `#D1BA`, `#D222`, `#D2DE`, `#D2FD`, `#D34D`, `#D355`, `#D359`, `#D3CF`, `#D3F9`, `#D3FE`, `#D408`, `#D53B`, `#D5C9`, `#D5D1`, `#D67D`, `#D6CC`, `#D77A`, `#D7C1`, `#D82D`, `#D873`, `#D877`, `#D87B`, `#D87F`, `#D883`, `#D887`, `#D88B`, `#D88F`, `#DA61`, `#DA9E`, `#E310`, `#E507`, `#ECA9`, `#ECF6`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## ReadObjectHeaderWord

[Action.ReadObjectHeaderWord](../../Source/Action/ReadObjectHeaderWord.asm)

Чтение слова по указателю страницы 9E из банка OBJECT3D с последующим выбором банка 0.

Вход `#AACC`, запись 17, смещения `#4ACC..#4AE1`.

- Прямые вызовы: `#AB1B`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionObjectHeader.md).

## CopyObjectData

[Action.CopyObjectData](../../Source/Action/CopyObjectData.asm)

Копирование двухчастного потока OBJECT3D в исходный рабочий буфер с возвратом банка 0.

[Алгоритм, точные регистры и модель](../ActionObjectCopy.md).

## SelectMemoryPage

[Action.SelectMemoryPage](../../Source/Action/SelectMemoryPage.asm)

Запись A в #7FFD с сохранением BC.

Вход `#AB1B`, запись 17, смещения `#4B1B..#4B22`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: `OUT (C),A`.
- Косвенное завершение: нет в этом фрагменте.

## UnpackResource

[Action.UnpackResource](../../Source/Action/UnpackResource.asm)

Распаковка HR-потока в полётном коде с переносом входа, LZ-ссылками, тройками и восстановлением шестибайтового конца.

Вход `#AB23`, запись 17, смещения `#4B23..#4C37`.

- Прямые вызовы: `#AC38`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionUnpack.md).

## ReadWordFromIX

[Action.ReadWordFromIX](../../Source/Action/ReadWordFromIX.asm)

Чтение слова младшим байтом вперёд через IX, продвижение IX на два и копирование C в B.

Вход `#AC38`, запись 22, смещения `#4C38..#4C43`.

[Алгоритм, контракты и независимая модель](../ActionParameterActivation.md).

## ActivateParameterSet

[Action.ActivateParameterSet](../../Source/Action/ActivateParameterSet.asm)

Выбор банка 0, применение набора параметров и обнуление двух слов и двух байтов состояния.

Вход `#AC44`, запись 22, смещения `#4C44..#4C5C`.

[Алгоритм, контракты и независимая модель](../ActionParameterActivation.md).

## ApplyParameterSet

[Action.ApplyParameterSet](../../Source/Action/ApplyParameterSet.asm)

Применение пятнадцати полей набора к исходным адресам ACTION, поле 1 читается без записи, поле 6 используется дважды.

Вход `#AC5D`, запись 17, смещения `#4C5D..#4CAA`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#63B9`, `#65E5`, `#6615`, `#6874`, `#79A4`, `#7B6B`, `#7DE4`, `#7E07`, `#7E09`, `#A8B5`, `#A968`, `#E6E7`, `#E823`, `#F798`, `#F79C`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionApplyParameters.md).

## QueueDiagnosticCounters

[Action.QueueDiagnosticCounters](../../Source/Action/QueueDiagnosticCounters.asm)

Постановка диагностических строк Status и Deads и трёх чисел в текстовую очередь.

[Алгоритм, точные регистры и модель](../ActionDiagnosticQueue.md).

## TransformVectorTransposed

[Action.TransformVectorTransposed](../../Source/Action/TransformVectorTransposed.asm)

Вычисление трёх выходных слов с временно транспонированной матрицей, сохранением IX/IY и восстановлением CPU-стека.

[Контракт и композиционная модель](../ActionVectorWrapper.md).

## SwapCodePatchWords

[Action.SwapCodePatchWords](../../Source/Action/SwapCodePatchWords.asm)

Обмен трёх пар полных слов изменяемого кода, включая байты операндов и следующие префиксы.

[Контракт и независимая модель](../ActionPatchSwap.md).

## SqrtWordBank1

[Action.SqrtWordBank1](../../Source/Action/SqrtWordBank1.asm)

Вызов табличного корня с выбором Controls банка 1 и сохранением BC.

Вход `#AD48`, запись 17, смещения `#4D48..#4D59`.

- Прямые вызовы: `#AB1B`, `#B0E9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionCachedRoot.md).

## EncodeHalfCoordinateDeltas

[Action.EncodeHalfCoordinateDeltas](../../Source/Action/EncodeHalfCoordinateDeltas.asm)

Два кода по трём разностям половинных координат и корню усечённых квадратов.

Вход `#AD5A`, запись 17, смещения `#4D5A..#4DB6`.

- Прямые вызовы: `#AD48`, `#AE24`, `#C6F4`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionHalfDeltaCodes.md).

## RotateBankedBasis

[Action.RotateBankedBasis](../../Source/Action/RotateBankedBasis.asm)

Поворот базисных векторов через VOXAL в странице 3.

Вход `#ADB7`, запись 17, смещения `#4DB7..#4DC4`.

- Прямые вызовы: `#AB1B`, `#E500`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRenderFrameSetup.md).

## ProjectOverlayCoordinates

[Action.ProjectOverlayCoordinates](../../Source/Action/ProjectOverlayCoordinates.asm)

Проекция двух координат относительно общей глубины с центром 128, 48.

[Алгоритм, точные регистры и модель](../ActionOverlayProjection.md).

## EncodeComponentDeltas

[Action.EncodeComponentDeltas](../../Source/Action/EncodeComponentDeltas.asm)

Кодирование отношения двух разностей слов с последовательным продолжением в EncodeSignedRatio.

[Алгоритм, точные регистры и модель](../ActionDeltaRatio.md).

## EncodeSignedRatio

[Action.EncodeSignedRatio](../../Source/Action/EncodeSignedRatio.asm)

Табличное кодирование знакового отношения с четырьмя смещениями и исходными ограничениями.

Вход `#AE24`, запись 17, смещения `#4E24..#4E72`.

- Прямые вызовы: `#AE73`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionSignedRatioCode.md).

## DivideScaledLogarithmic

[Action.DivideScaledLogarithmic](../../Source/Action/DivideScaledLogarithmic.asm)

Unknown, оставшийся фрагмент AE73..AF42 ещё не разобран.

Вход `#AE73`, запись 17, смещения `#4E73..#4F42`.

Сохраняет неизвестный договор и записи AF14, AF2F. Вычислитель AF43 выделен отдельно, его выходы и чтения не относятся к этому оставшемуся фрагменту.

[Алгоритм, контракты и независимая модель](../ActionLogRatio.md).

## ComputePatchedVector

[Action.ComputePatchedVector](../../Source/Action/ComputePatchedVector.asm)

Расчёт трёх компонентов по девяти коэффициентам с исходным переносом отрицательных произведений и досрочным выходом по переполнению.

[Контракт, перенос, SP и модель](../ActionPatchedVector.md).

## NegateOuterBasisRows

[Action.NegateOuterBasisRows](../../Source/Action/NegateOuterBasisRows.asm)

Изменение знака слов строк 2 и 0 базиса с сохранением средней строки.

[Договоры и границы проверки](../ActionReverseViewBasis.md).

## BuildObjectOffsetCoefficients

[Action.BuildObjectOffsetCoefficients](../../Source/Action/BuildObjectOffsetCoefficients.asm)

Подготовка коэффициентов смещения по трём фазовым парам.

[Алгоритм, точные регистры и модель](../ActionObjectOffsetCoefficients.md).

## SqrtWordCached

[Action.SqrtWordCached](../../Source/Action/SqrtWordCached.asm)

Целый корень в области 0000..E8FF и исходное особое поведение E900..FFFF по трём страницам таблиц.

Вход `#B0E9`, запись 17, смещения `#50E9..#516E`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionCachedRoot.md).

## ClipPolygon

[Action.ClipPolygon](../../Source/Action/ClipPolygon.asm)

Обход замкнутого списка вершин с табличным отсечением и ранним завершением контура.

Вход `#C000`, запись 17, смещения `#6000..#6070`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF0F`, `#CF1B`, `#CF1D`, `#CF1F`.
- Непосредственные записи: `#9BA3`, `#CF03`, `#CF07`, `#CF0B`, `#CF0D`, `#CF0F`, `#CF1B`, `#CF1D`, `#CF1F`.
- Ввод и вывод: нет.
- Косвенное завершение: `JP (HL)`.

[Алгоритм, контракты и композиционная проверка](../ActionPolygon.md).

## ContinueClipPolygon

[Action.ContinueClipPolygon](../../Source/Action/ContinueClipPolygon.asm)

Восстановление счётчика после ребра и продолжение либо возврат полного полигона.

Вход `#C071`, запись 17, смещения `#6071..#6079`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9BA3`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionPolygon.md).

## ReturnClipCase

[Action.ReturnClipCase](../../Source/Action/ReturnClipCase.asm)

Завершение текущего табличного случая обычным RET.

Вход `#C07A`, запись 17, смещения `#607A..#607A`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipInsideToBottomRight

[Action.ClipInsideToBottomRight](../../Source/Action/ClipInsideToBottomRight.asm)

Отсечение ребра, первая точка внутри окна, вторая снизу справа.

Вход `#C07B`, запись 17, смещения `#607B..#6089`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C5E7`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToBottomRight

[Action.ClipRightToBottomRight](../../Source/Action/ClipRightToBottomRight.asm)

Отсечение ребра, первая точка справа, вторая снизу справа.

Вход `#C08A`, запись 17, смещения `#608A..#6094`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipInsideToBottomLeft

[Action.ClipInsideToBottomLeft](../../Source/Action/ClipInsideToBottomLeft.asm)

Отсечение ребра, первая точка внутри окна, вторая снизу слева.

Вход `#C095`, запись 17, смещения `#6095..#60A3`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C540`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToBottomLeft

[Action.ClipBottomToBottomLeft](../../Source/Action/ClipBottomToBottomLeft.asm)

Отсечение ребра, первая точка снизу, вторая снизу слева.

Вход `#C0A4`, запись 17, смещения `#60A4..#60AE`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipInsideToTopRight

[Action.ClipInsideToTopRight](../../Source/Action/ClipInsideToTopRight.asm)

Отсечение ребра, первая точка внутри окна, вторая сверху справа.

Вход `#C0AF`, запись 17, смещения `#60AF..#60BD`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C4F6`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToTopRight

[Action.ClipTopToTopRight](../../Source/Action/ClipTopToTopRight.asm)

Отсечение ребра, первая точка сверху, вторая сверху справа.

Вход `#C0BE`, запись 17, смещения `#60BE..#60C8`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipInsideToTopLeft

[Action.ClipInsideToTopLeft](../../Source/Action/ClipInsideToTopLeft.asm)

Отсечение ребра, первая точка внутри окна, вторая сверху слева.

Вход `#C0C9`, запись 17, смещения `#60C9..#60D7`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C58B`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToTopLeft

[Action.ClipLeftToTopLeft](../../Source/Action/ClipLeftToTopLeft.asm)

Отсечение ребра, первая точка слева, вторая сверху слева.

Вход `#C0D8`, запись 17, смещения `#60D8..#60E2`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToInside

[Action.ClipRightToInside](../../Source/Action/ClipRightToInside.asm)

Отсечение ребра, первая точка справа, вторая внутри окна.

Вход `#C0E3`, запись 17, смещения `#60E3..#60E8`.

- Прямые вызовы: `#C5E4`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToLeft

[Action.ClipRightToLeft](../../Source/Action/ClipRightToLeft.asm)

Отсечение ребра, первая точка справа, вторая слева.

Вход `#C0E9`, запись 17, смещения `#60E9..#60EE`.

- Прямые вызовы: `#C5E4`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToBottom

[Action.ClipRightToBottom](../../Source/Action/ClipRightToBottom.asm)

Отсечение ребра, первая точка справа, вторая снизу.

Вход `#C0EF`, запись 17, смещения `#60EF..#6100`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C5E7`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToBottomLeft

[Action.ClipRightToBottomLeft](../../Source/Action/ClipRightToBottomLeft.asm)

Отсечение ребра, первая точка справа, вторая снизу слева.

Вход `#C101`, запись 17, смещения `#6101..#6118`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C5E7`, `#C662`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToTop

[Action.ClipRightToTop](../../Source/Action/ClipRightToTop.asm)

Отсечение ребра, первая точка справа, вторая сверху.

Вход `#C119`, запись 17, смещения `#6119..#612A`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C5E7`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToTopRight

[Action.ClipRightToTopRight](../../Source/Action/ClipRightToTopRight.asm)

Отсечение ребра, первая точка справа, вторая сверху справа.

Вход `#C12B`, запись 17, смещения `#612B..#6131`.

- Прямые вызовы: `#C6BD`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipRightToTopLeft

[Action.ClipRightToTopLeft](../../Source/Action/ClipRightToTopLeft.asm)

Отсечение ребра, первая точка справа, вторая сверху слева.

Вход `#C132`, запись 17, смещения `#6132..#6143`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C5E7`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToInside

[Action.ClipLeftToInside](../../Source/Action/ClipLeftToInside.asm)

Отсечение ребра, первая точка слева, вторая внутри окна.

Вход `#C144`, запись 17, смещения `#6144..#6149`.

- Прямые вызовы: `#C588`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToRight

[Action.ClipLeftToRight](../../Source/Action/ClipLeftToRight.asm)

Отсечение ребра, первая точка слева, вторая справа.

Вход `#C14A`, запись 17, смещения `#614A..#614F`.

- Прямые вызовы: `#C588`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToBottom

[Action.ClipLeftToBottom](../../Source/Action/ClipLeftToBottom.asm)

Отсечение ребра, первая точка слева, вторая снизу.

Вход `#C150`, запись 17, смещения `#6150..#6161`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C58B`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToBottomRight

[Action.ClipLeftToBottomRight](../../Source/Action/ClipLeftToBottomRight.asm)

Отсечение ребра, первая точка слева, вторая снизу справа.

Вход `#C162`, запись 17, смещения `#6162..#6173`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C58B`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToBottomLeft

[Action.ClipLeftToBottomLeft](../../Source/Action/ClipLeftToBottomLeft.asm)

Отсечение ребра, первая точка слева, вторая снизу слева.

Вход `#C174`, запись 17, смещения `#6174..#617A`.

- Прямые вызовы: `#C6BD`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToTop

[Action.ClipLeftToTop](../../Source/Action/ClipLeftToTop.asm)

Отсечение ребра, первая точка слева, вторая сверху.

Вход `#C17B`, запись 17, смещения `#617B..#618C`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C58B`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipLeftToTopRight

[Action.ClipLeftToTopRight](../../Source/Action/ClipLeftToTopRight.asm)

Отсечение ребра, первая точка слева, вторая сверху справа.

Вход `#C18D`, запись 17, смещения `#618D..#61A4`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C58B`, `#C641`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToInside

[Action.ClipBottomToInside](../../Source/Action/ClipBottomToInside.asm)

Отсечение ребра, первая точка снизу, вторая внутри окна.

Вход `#C1A5`, запись 17, смещения `#61A5..#61AA`.

- Прямые вызовы: `#C53D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToRight

[Action.ClipBottomToRight](../../Source/Action/ClipBottomToRight.asm)

Отсечение ребра, первая точка снизу, вторая справа.

Вход `#C1AB`, запись 17, смещения `#61AB..#61BC`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C540`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToLeft

[Action.ClipBottomToLeft](../../Source/Action/ClipBottomToLeft.asm)

Отсечение ребра, первая точка снизу, вторая слева.

Вход `#C1BD`, запись 17, смещения `#61BD..#61CE`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C540`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToBottomRight

[Action.ClipBottomToBottomRight](../../Source/Action/ClipBottomToBottomRight.asm)

Отсечение ребра, первая точка снизу, вторая снизу справа.

Вход `#C1CF`, запись 17, смещения `#61CF..#61D5`.

- Прямые вызовы: `#C6C8`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToTop

[Action.ClipBottomToTop](../../Source/Action/ClipBottomToTop.asm)

Отсечение ребра, первая точка снизу, вторая сверху.

Вход `#C1D6`, запись 17, смещения `#61D6..#61DB`.

- Прямые вызовы: `#C53D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToTopRight

[Action.ClipBottomToTopRight](../../Source/Action/ClipBottomToTopRight.asm)

Отсечение ребра, первая точка снизу, вторая сверху справа.

Вход `#C1DC`, запись 17, смещения `#61DC..#61F0`.

- Прямые вызовы: `#C477`, `#C496`, `#C4D4`, `#C540`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomToTopLeft

[Action.ClipBottomToTopLeft](../../Source/Action/ClipBottomToTopLeft.asm)

Отсечение ребра, первая точка снизу, вторая сверху слева.

Вход `#C1F1`, запись 17, смещения `#61F1..#620B`.

- Прямые вызовы: `#C477`, `#C496`, `#C4B5`, `#C540`, `#C657`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToInside

[Action.ClipBottomRightToInside](../../Source/Action/ClipBottomRightToInside.asm)

Отсечение ребра, первая точка снизу справа, вторая внутри окна.

Вход `#C20C`, запись 17, смещения `#620C..#6227`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C540`, `#C662`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToRight

[Action.ClipBottomRightToRight](../../Source/Action/ClipBottomRightToRight.asm)

Отсечение ребра, первая точка снизу справа, вторая справа.

Вход `#C228`, запись 17, смещения `#6228..#622E`.

- Прямые вызовы: `#C6BD`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToLeft

[Action.ClipBottomRightToLeft](../../Source/Action/ClipBottomRightToLeft.asm)

Отсечение ребра, первая точка снизу справа, вторая слева.

Вход `#C22F`, запись 17, смещения `#622F..#624D`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C5E7`, `#C662`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToBottom

[Action.ClipBottomRightToBottom](../../Source/Action/ClipBottomRightToBottom.asm)

Отсечение ребра, первая точка снизу справа, вторая снизу.

Вход `#C24E`, запись 17, смещения `#624E..#6258`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToBottomLeft

[Action.ClipBottomRightToBottomLeft](../../Source/Action/ClipBottomRightToBottomLeft.asm)

Отсечение ребра, первая точка снизу справа, вторая снизу слева.

Вход `#C259`, запись 17, смещения `#6259..#625E`.

- Прямые вызовы: `#C24E`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToTop

[Action.ClipBottomRightToTop](../../Source/Action/ClipBottomRightToTop.asm)

Отсечение ребра, первая точка снизу справа, вторая сверху.

Вход `#C25F`, запись 17, смещения `#625F..#6273`.

- Прямые вызовы: `#C24E`, `#C496`, `#C4D4`, `#C540`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomRightToTopLeft

[Action.ClipBottomRightToTopLeft](../../Source/Action/ClipBottomRightToTopLeft.asm)

Отсечение ребра, первая точка снизу справа, вторая сверху слева.

Вход `#C274`, запись 17, смещения `#6274..#628C`.

- Прямые вызовы: `#C496`, `#C4D4`, `#C662`, `#C6A9`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToInside

[Action.ClipBottomLeftToInside](../../Source/Action/ClipBottomLeftToInside.asm)

Отсечение ребра, первая точка снизу слева, вторая внутри окна.

Вход `#C28D`, запись 17, смещения `#628D..#62A8`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C58B`, `#C657`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToRight

[Action.ClipBottomLeftToRight](../../Source/Action/ClipBottomLeftToRight.asm)

Отсечение ребра, первая точка снизу слева, вторая справа.

Вход `#C2A9`, запись 17, смещения `#62A9..#62BD`.

- Прямые вызовы: `#C2BE`, `#C496`, `#C4B5`, `#C58B`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToLeft

[Action.ClipBottomLeftToLeft](../../Source/Action/ClipBottomLeftToLeft.asm)

Отсечение ребра, первая точка снизу слева, вторая слева.

Вход `#C2BE`, запись 17, смещения `#62BE..#62C8`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToBottom

[Action.ClipBottomLeftToBottom](../../Source/Action/ClipBottomLeftToBottom.asm)

Отсечение ребра, первая точка снизу слева, вторая снизу.

Вход `#C2C9`, запись 17, смещения `#62C9..#62CF`.

- Прямые вызовы: `#C6C8`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToTop

[Action.ClipBottomLeftToTop](../../Source/Action/ClipBottomLeftToTop.asm)

Отсечение ребра, первая точка снизу слева, вторая сверху.

Вход `#C2D0`, запись 17, смещения `#62D0..#62EE`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C540`, `#C657`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToTopRight

[Action.ClipBottomLeftToTopRight](../../Source/Action/ClipBottomLeftToTopRight.asm)

Отсечение ребра, первая точка снизу слева, вторая сверху справа.

Вход `#C2EF`, запись 17, смещения `#62EF..#6307`.

- Прямые вызовы: `#C496`, `#C4B5`, `#C657`, `#C695`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipBottomLeftToTopLeft

[Action.ClipBottomLeftToTopLeft](../../Source/Action/ClipBottomLeftToTopLeft.asm)

Отсечение ребра, первая точка снизу слева, вторая сверху слева.

Вход `#C308`, запись 17, смещения `#6308..#630D`.

- Прямые вызовы: `#C2BE`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToInside

[Action.ClipTopToInside](../../Source/Action/ClipTopToInside.asm)

Отсечение ребра, первая точка сверху, вторая внутри окна.

Вход `#C30E`, запись 17, смещения `#630E..#6313`.

- Прямые вызовы: `#C4F3`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToRight

[Action.ClipTopToRight](../../Source/Action/ClipTopToRight.asm)

Отсечение ребра, первая точка сверху, вторая справа.

Вход `#C314`, запись 17, смещения `#6314..#6325`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C4F6`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToLeft

[Action.ClipTopToLeft](../../Source/Action/ClipTopToLeft.asm)

Отсечение ребра, первая точка сверху, вторая слева.

Вход `#C326`, запись 17, смещения `#6326..#6337`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C4F6`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToBottom

[Action.ClipTopToBottom](../../Source/Action/ClipTopToBottom.asm)

Отсечение ребра, первая точка сверху, вторая снизу.

Вход `#C338`, запись 17, смещения `#6338..#633D`.

- Прямые вызовы: `#C4F3`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToBottomRight

[Action.ClipTopToBottomRight](../../Source/Action/ClipTopToBottomRight.asm)

Отсечение ребра, первая точка сверху, вторая снизу справа.

Вход `#C33E`, запись 17, смещения `#633E..#6358`.

- Прямые вызовы: `#C477`, `#C496`, `#C4D4`, `#C4F6`, `#C64C`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToBottomLeft

[Action.ClipTopToBottomLeft](../../Source/Action/ClipTopToBottomLeft.asm)

Отсечение ребра, первая точка сверху, вторая снизу слева.

Вход `#C359`, запись 17, смещения `#6359..#636D`.

- Прямые вызовы: `#C477`, `#C496`, `#C4B5`, `#C4F6`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopToTopLeft

[Action.ClipTopToTopLeft](../../Source/Action/ClipTopToTopLeft.asm)

Отсечение ребра, первая точка сверху, вторая сверху слева.

Вход `#C36E`, запись 17, смещения `#636E..#6374`.

- Прямые вызовы: `#C6C8`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToInside

[Action.ClipTopRightToInside](../../Source/Action/ClipTopRightToInside.asm)

Отсечение ребра, первая точка сверху справа, вторая внутри окна.

Вход `#C375`, запись 17, смещения `#6375..#6390`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C5E7`, `#C64C`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToRight

[Action.ClipTopRightToRight](../../Source/Action/ClipTopRightToRight.asm)

Отсечение ребра, первая точка сверху справа, вторая справа.

Вход `#C391`, запись 17, смещения `#6391..#639B`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToLeft

[Action.ClipTopRightToLeft](../../Source/Action/ClipTopRightToLeft.asm)

Отсечение ребра, первая точка сверху справа, вторая слева.

Вход `#C39C`, запись 17, смещения `#639C..#63B0`.

- Прямые вызовы: `#C391`, `#C477`, `#C4D4`, `#C5E7`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToBottom

[Action.ClipTopRightToBottom](../../Source/Action/ClipTopRightToBottom.asm)

Отсечение ребра, первая точка сверху справа, вторая снизу.

Вход `#C3B1`, запись 17, смещения `#63B1..#63CF`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C4F6`, `#C64C`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToBottomRight

[Action.ClipTopRightToBottomRight](../../Source/Action/ClipTopRightToBottomRight.asm)

Отсечение ребра, первая точка сверху справа, вторая снизу справа.

Вход `#C3D0`, запись 17, смещения `#63D0..#63D5`.

- Прямые вызовы: `#C391`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToBottomLeft

[Action.ClipTopRightToBottomLeft](../../Source/Action/ClipTopRightToBottomLeft.asm)

Отсечение ребра, первая точка сверху справа, вторая снизу слева.

Вход `#C3D6`, запись 17, смещения `#63D6..#63EE`.

- Прямые вызовы: `#C477`, `#C4D4`, `#C64C`, `#C681`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopRightToTop

[Action.ClipTopRightToTop](../../Source/Action/ClipTopRightToTop.asm)

Отсечение ребра, первая точка сверху справа, вторая сверху.

Вход `#C3EF`, запись 17, смещения `#63EF..#63F5`.

- Прямые вызовы: `#C6C8`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToInside

[Action.ClipTopLeftToInside](../../Source/Action/ClipTopLeftToInside.asm)

Отсечение ребра, первая точка сверху слева, вторая внутри окна.

Вход `#C3F6`, запись 17, смещения `#63F6..#6411`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C4F6`, `#C641`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToRight

[Action.ClipTopLeftToRight](../../Source/Action/ClipTopLeftToRight.asm)

Отсечение ребра, первая точка сверху слева, вторая справа.

Вход `#C412`, запись 17, смещения `#6412..#6430`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C58B`, `#C641`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToLeft

[Action.ClipTopLeftToLeft](../../Source/Action/ClipTopLeftToLeft.asm)

Отсечение ребра, первая точка сверху слева, вторая слева.

Вход `#C431`, запись 17, смещения `#6431..#6437`.

- Прямые вызовы: `#C6BD`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToBottom

[Action.ClipTopLeftToBottom](../../Source/Action/ClipTopLeftToBottom.asm)

Отсечение ребра, первая точка сверху слева, вторая снизу.

Вход `#C438`, запись 17, смещения `#6438..#644C`.

- Прямые вызовы: `#C466`, `#C477`, `#C4B5`, `#C4F6`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToBottomRight

[Action.ClipTopLeftToBottomRight](../../Source/Action/ClipTopLeftToBottomRight.asm)

Отсечение ребра, первая точка сверху слева, вторая снизу справа.

Вход `#C44D`, запись 17, смещения `#644D..#6465`.

- Прямые вызовы: `#C477`, `#C4B5`, `#C641`, `#C66D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToTop

[Action.ClipTopLeftToTop](../../Source/Action/ClipTopLeftToTop.asm)

Отсечение ребра, первая точка сверху слева, вторая сверху.

Вход `#C466`, запись 17, смещения `#6466..#6470`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ClipTopLeftToTopRight

[Action.ClipTopLeftToTopRight](../../Source/Action/ClipTopLeftToTopRight.asm)

Отсечение ребра, первая точка сверху слева, вторая сверху справа.

Вход `#C471`, запись 17, смещения `#6471..#6476`.

- Прямые вызовы: `#C466`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## ComputeTopClipProduct

[Action.ComputeTopClipProduct](../../Source/Action/ComputeTopClipProduct.asm)

Подготовка числителя пересечения (First.First-0)*(First.Second-Second.Second) исходным знаковым умножителем.

Вход `#C477`, запись 17, смещения `#6477..#6495`.

- Прямые вызовы: `#C6F4`.
- Непосредственные чтения: `#CF0B`, `#CF0D`, `#CF1B`.
- Непосредственные записи: `#CF37`, `#CF39`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipProducts.md).

## ComputeBottomClipProduct

[Action.ComputeBottomClipProduct](../../Source/Action/ComputeBottomClipProduct.asm)

Подготовка числителя пересечения (First.First-95)*(First.Second-Second.Second) исходным знаковым умножителем.

Вход `#C496`, запись 17, смещения `#6496..#64B4`.

- Прямые вызовы: `#C6F4`.
- Непосредственные чтения: `#CF0B`, `#CF0D`, `#CF1B`.
- Непосредственные записи: `#CF33`, `#CF35`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipProducts.md).

## ComputeLeftClipProduct

[Action.ComputeLeftClipProduct](../../Source/Action/ComputeLeftClipProduct.asm)

Подготовка числителя пересечения (First.First-Second.First)*(First.Second-0) исходным знаковым умножителем.

Вход `#C4B5`, запись 17, смещения `#64B5..#64D3`.

- Прямые вызовы: `#C6F4`.
- Непосредственные чтения: `#CF0B`, `#CF0D`, `#CF1D`.
- Непосредственные записи: `#CF2F`, `#CF31`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipProducts.md).

## ComputeRightClipProduct

[Action.ComputeRightClipProduct](../../Source/Action/ComputeRightClipProduct.asm)

Подготовка числителя пересечения (First.First-Second.First)*(First.Second-255) исходным знаковым умножителем.

Вход `#C4D4`, запись 17, смещения `#64D4..#64F2`.

- Прямые вызовы: `#C6F4`.
- Непосредственные чтения: `#CF0B`, `#CF0D`, `#CF1D`.
- Непосредственные записи: `#CF2B`, `#CF2D`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipProducts.md).

## ClipInsideToTop

[Action.ClipInsideToTop](../../Source/Action/ClipInsideToTop.asm)

Отсечение ребра, первая точка внутри окна, вторая сверху.

Вход `#C4F3`, запись 17, смещения `#64F3..#64F5`.

- Прямые вызовы: `#C477`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## AppendTopClipIntersection

[Action.AppendTopClipIntersection](../../Source/Action/AppendTopClipIntersection.asm)

Добавление пересечения границы с исходным делением и побайтовой проверкой координаты.

Вход `#C4F6`, запись 17, смещения `#64F6..#653C`.

- Прямые вызовы: `#C88C`.
- Непосредственные чтения: `#9BA3`, `#CF0B`, `#CF0D`, `#CF1D`, `#CF37`, `#CF38`, `#CF39`.
- Непосредственные записи: `#9BA3`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipIntersections.md).

## ClipInsideToBottom

[Action.ClipInsideToBottom](../../Source/Action/ClipInsideToBottom.asm)

Отсечение ребра, первая точка внутри окна, вторая снизу.

Вход `#C53D`, запись 17, смещения `#653D..#653F`.

- Прямые вызовы: `#C496`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## AppendBottomClipIntersection

[Action.AppendBottomClipIntersection](../../Source/Action/AppendBottomClipIntersection.asm)

Добавление пересечения границы с исходным делением и побайтовой проверкой координаты.

Вход `#C540`, запись 17, смещения `#6540..#6587`.

- Прямые вызовы: `#C88C`.
- Непосредственные чтения: `#9BA3`, `#CF0B`, `#CF0D`, `#CF1D`, `#CF33`, `#CF34`, `#CF35`.
- Непосредственные записи: `#9BA3`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipIntersections.md).

## ClipInsideToLeft

[Action.ClipInsideToLeft](../../Source/Action/ClipInsideToLeft.asm)

Отсечение ребра, первая точка внутри окна, вторая слева.

Вход `#C588`, запись 17, смещения `#6588..#658A`.

- Прямые вызовы: `#C4B5`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## AppendLeftClipIntersection

[Action.AppendLeftClipIntersection](../../Source/Action/AppendLeftClipIntersection.asm)

Добавление пересечения границы с исходным делением и побайтовой проверкой координаты.

Вход `#C58B`, запись 17, смещения `#658B..#65E3`.

- Прямые вызовы: `#C88C`.
- Непосредственные чтения: `#9BA3`, `#CF0B`, `#CF0D`, `#CF1B`, `#CF2F`, `#CF30`, `#CF31`.
- Непосредственные записи: `#9BA3`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipIntersections.md).

## ClipInsideToRight

[Action.ClipInsideToRight](../../Source/Action/ClipInsideToRight.asm)

Отсечение ребра, первая точка внутри окна, вторая справа.

Вход `#C5E4`, запись 17, смещения `#65E4..#65E6`.

- Прямые вызовы: `#C4D4`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## AppendRightClipIntersection

[Action.AppendRightClipIntersection](../../Source/Action/AppendRightClipIntersection.asm)

Добавление пересечения границы с исходным делением и побайтовой проверкой координаты.

Вход `#C5E7`, запись 17, смещения `#65E7..#6640`.

- Прямые вызовы: `#C88C`.
- Непосредственные чтения: `#9BA3`, `#CF0B`, `#CF0D`, `#CF1B`, `#CF2B`, `#CF2C`, `#CF2D`.
- Непосредственные записи: `#9BA3`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipIntersections.md).

## AppendTopLeftClipCorner

[Action.AppendTopLeftClipCorner](../../Source/Action/AppendTopLeftClipCorner.asm)

Добавление угла окна при нулевом CornerBlock.

Вход `#C641`, запись 17, смещения `#6641..#664B`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF03`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipPointWriters.md).

## AppendTopRightClipCorner

[Action.AppendTopRightClipCorner](../../Source/Action/AppendTopRightClipCorner.asm)

Добавление угла окна при нулевом CornerBlock.

Вход `#C64C`, запись 17, смещения `#664C..#6656`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF03`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipPointWriters.md).

## AppendBottomLeftClipCorner

[Action.AppendBottomLeftClipCorner](../../Source/Action/AppendBottomLeftClipCorner.asm)

Добавление угла окна при нулевом CornerBlock.

Вход `#C657`, запись 17, смещения `#6657..#6661`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF03`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipPointWriters.md).

## AppendBottomRightClipCorner

[Action.AppendBottomRightClipCorner](../../Source/Action/AppendBottomRightClipCorner.asm)

Добавление угла окна при нулевом CornerBlock.

Вход `#C662`, запись 17, смещения `#6662..#666C`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF03`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipPointWriters.md).

## CompareTopLeftProducts

[Action.CompareTopLeftProducts](../../Source/Action/CompareTopLeftProducts.asm)

Вычитание LeftProduct из TopProduct с передачей заёма младшего слова.

Вход `#C66D`, запись 17, смещения `#666D..#6680`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF2F`, `#CF31`, `#CF37`, `#CF39`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## CompareTopRightProducts

[Action.CompareTopRightProducts](../../Source/Action/CompareTopRightProducts.asm)

Вычитание RightProduct из TopProduct с передачей заёма младшего слова.

Вход `#C681`, запись 17, смещения `#6681..#6694`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF2B`, `#CF2D`, `#CF37`, `#CF39`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## CompareBottomLeftProducts

[Action.CompareBottomLeftProducts](../../Source/Action/CompareBottomLeftProducts.asm)

Вычитание LeftProduct из BottomProduct с передачей заёма младшего слова.

Вход `#C695`, запись 17, смещения `#6695..#66A8`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF2F`, `#CF31`, `#CF33`, `#CF35`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## CompareBottomRightProducts

[Action.CompareBottomRightProducts](../../Source/Action/CompareBottomRightProducts.asm)

Вычитание RightProduct из BottomProduct с передачей заёма младшего слова.

Вход `#C6A9`, запись 17, смещения `#66A9..#66BC`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF2B`, `#CF2D`, `#CF33`, `#CF35`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## ComputeSecondAxisDelta

[Action.ComputeSecondAxisDelta](../../Source/Action/ComputeSecondAxisDelta.asm)

Разность координат Second второй и первой точки с оборачиванием до слова.

Вход `#C6BD`, запись 17, смещения `#66BD..#66C7`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF0B`, `#CF1B`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## ComputeFirstAxisDelta

[Action.ComputeFirstAxisDelta](../../Source/Action/ComputeFirstAxisDelta.asm)

Разность координат First второй и первой точки с оборачиванием до слова.

Вход `#C6C8`, запись 17, смещения `#66C8..#66D2`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#CF0D`, `#CF1D`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipComparisons.md).

## AppendSecondClipPoint

[Action.AppendSecondClipPoint](../../Source/Action/AppendSecondClipPoint.asm)

Добавление младших байтов второй точки с общим входом записи пары DE.

Вход `#C6D3`, запись 17, смещения `#66D3..#66E9`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: `#9BA3`, `#CF1B`, `#CF1D`.
- Непосредственные записи: `#9BA3`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionClipPointWriters.md).

## ExitClipContour

[Action.ExitClipContour](../../Source/Action/ExitClipContour.asm)

Специальное завершение контура со снятием трёх служебных слов.

Вход `#C6EA`, запись 17, смещения `#66EA..#66F3`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и композиционная проверка](../ActionClipCases.md).

## MultiplySigned16

[Action.MultiplySigned16](../../Source/Action/MultiplySigned16.asm)

Знаковое произведение двух слов с тремя ядрами и исходным исключением второго операнда 8000.

Вход `#C6F4`, запись 17, смещения `#66F4..#688B`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionSignedMultiply.md).

## DivideSigned32To16

[Action.DivideSigned32To16](../../Source/Action/DivideSigned32To16.asm)

Деление числителя HL, A, альтернативного A на signed16 с исходным побитовым дополнением.

[Алгоритм, контракты и независимая модель](../ActionSignedDivision.md).

## ClipSingleEdge

[Action.ClipSingleEdge](../../Source/Action/ClipSingleEdge.asm)

Отсечение одиночного ребра с обменом внутренней первой точки и рамкой трёх возвратов.

[Алгоритм, контракты и композиционная проверка](../ActionSingleEdge.md).

## BuildRenderCoefficients

[Action.BuildRenderCoefficients](../../Source/Action/BuildRenderCoefficients.asm)

Построение девяти байтовых коэффициентов по трём фазам либо по одной фазе.

## ComposeRenderMatrix

[Action.ComposeRenderMatrix](../../Source/Action/ComposeRenderMatrix.asm)

Композиция исходной матрицы и ориентации с одноосным режимом и точными четвертями.

[Построитель и границы локального доказательства](../ActionRenderCoefficients.md).

[Алгоритм, контракты и независимая модель](../ActionRenderMatrix.md).

## UnknownCF08

[Action.UnknownCF08](../../Source/Action/UnknownCF08.asm)

Unknown, назначение этого фрагмента ещё не установлено.

Вход `#CF08`, запись 17, смещения `#6F08..#6F0A`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## ClearWorkBuffer

[Action.ClearWorkBuffer](../../Source/Action/ClearWorkBuffer.asm)

Заполнение линейного буфера 8000..8BFF байтами FF через временный SP с восстановлением CPU-стека.

Вход `#D10A`, запись 17, смещения `#710A..#712B`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#D129`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionWorkBuffer.md).

## MultiplySignedScaled

[Action.MultiplySignedScaled](../../Source/Action/MultiplySignedScaled.asm)

Знаковое произведение DE и байтового коэффициента с усечением к нулю после деления на 128 и выходом через IX.

Вход `#D12C`, запись 17, смещения `#712C..#7193`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: `JP (IX)`.

[Алгоритм, контракты и независимая модель](../ActionScaledMultiply.md).

## PolygonFillRows

[Action.PolygonFillRows](../../Source/Action/PolygonFillRows.asm)

Строковое ядро линейной заливки с развёрнутой записью, крайними масками и коррекцией двух рёбер.

[Алгоритм, точные регистры и модель](../ActionPolygonFillRows.md).

## SelectPolygonRightEdge

[Action.SelectPolygonRightEdge](../../Source/Action/SelectPolygonRightEdge.asm)

Передача управления правому обновлению без изменения контекста.

[Алгоритм, точные регистры и модель](../ActionPolygonSelectRight.md).

## WrapPolygonLeftEdge

[Action.WrapPolygonLeftEdge](../../Source/Action/WrapPolygonLeftEdge.asm)

Оборачивание обратного поиска к последней First кольца.

[Алгоритм, точные регистры и модель](../ActionPolygonWrapLeft.md).

## UpdatePolygonLeftEdge

[Action.UpdatePolygonLeftEdge](../../Source/Action/UpdatePolygonLeftEdge.asm)

Поиск восходящего левого ребра, вычисление целого шага и ошибки, выбор продолжения заливки.

[Алгоритм, точные регистры и модель](../ActionPolygonLeftEdge.md).

## WrapPolygonRightEdge

[Action.WrapPolygonRightEdge](../../Source/Action/WrapPolygonRightEdge.asm)

Оборачивание прямого поиска к первой First кольца.

[Алгоритм, точные регистры и модель](../ActionPolygonWrapRight.md).

## UpdatePolygonRightEdge

[Action.UpdatePolygonRightEdge](../../Source/Action/UpdatePolygonRightEdge.asm)

Поиск восходящего правого ребра и вычисление его упакованного шага и дробной ошибки.

[Алгоритм, точные регистры и модель](../ActionPolygonRightEdge.md).

## SelectPolygonRowLimit

[Action.SelectPolygonRowLimit](../../Source/Action/SelectPolygonRowLimit.asm)

Выбор ближайшего предела строк с приоритетом левого ребра и настройкой следующего перехода.

[Алгоритм, точные регистры и модель](../ActionPolygonRowSelection.md).

## SetShortNegativeRightStep

[Action.SetShortNegativeRightStep](../../Source/Action/SetShortNegativeRightStep.asm)

Настройка нулевого целого шага короткого отрицательного правого наклона и восстановление временного контекста.

[Алгоритм, точные регистры и модель](../ActionPolygonRightShortStep.md).

## WrapPolygonLeftTop

[Action.WrapPolygonLeftTop](../../Source/Action/WrapPolygonLeftTop.asm)

Оборачивание поиска левого конца верхней горизонтали.

[Алгоритм, точные регистры и модель](../ActionPolygonWrapLeftTop.md).

## WrapPolygonRightTop

[Action.WrapPolygonRightTop](../../Source/Action/WrapPolygonRightTop.asm)

Оборачивание поиска правого конца верхней горизонтали.

[Алгоритм, точные регистры и модель](../ActionPolygonWrapRightTop.md).

## ReturnPolygonFill

[Action.ReturnPolygonFill](../../Source/Action/ReturnPolygonFill.asm)

Восстановление сохранённого HL и внешний возврат плоского контура.

[Алгоритм, точные регистры и модель](../ActionPolygonReturn.md).

## PreparePolygonFill

[Action.PreparePolygonFill](../../Source/Action/PreparePolygonFill.asm)

Подготовка диапазона строк, верхних вершин двух цепочек, масок и временного стека заливки.

[Алгоритм, точные регистры и модель](../ActionPolygonPreparation.md).

## TransformObjectVertices

[Action.TransformObjectVertices](../../Source/Action/TransformObjectVertices.asm)

Копирование потока объекта и преобразование всех его фиксированных групп вершин.

[Алгоритм, точные регистры и модель](../ActionObjectVertices.md).

## PrepareRenderVertexProducts

[Action.PrepareRenderVertexProducts](../../Source/Action/PrepareRenderVertexProducts.asm)

Подготовка трёх пар координат и трёх глубин табличным произведением матрицы и входных компонентов.

[Алгоритм, точные регистры и модель](../ActionVertexProducts.md).

## ProjectRenderVertexGroup

[Action.ProjectRenderVertexGroup](../../Source/Action/ProjectRenderVertexGroup.asm)

Построение комбинаций координат и перспективная запись выбранной группы вершин.

[Алгоритм, точные регистры и модель](../ActionVertexGroup.md).

## ProjectRenderVertex

[Action.ProjectRenderVertex](../../Source/Action/ProjectRenderVertex.asm)

Перспективная запись одной вершины с исходной нормализацией и косвенным продолжением.

[Алгоритм, точные регистры и модель](../ActionPerspective.md).

## RenderClippedRecords

[Action.RenderClippedRecords](../../Source/Action/RenderClippedRecords.asm)

Вывод записей объекта с проверкой кодов точек и отсечением граней и открытых сегментов.

[Алгоритм, точные регистры и модель](../ActionClippedPacketRenderer.md).

## RenderInsideRecords

[Action.RenderInsideRecords](../../Source/Action/RenderInsideRecords.asm)

Вывод граней и ломаных объекта с внутренними точками без дополнительного отсечения.

[Алгоритм, точные регистры и модель](../ActionPacketRenderer.md).

## CombineListedVertexCodes

[Action.CombineListedVertexCodes](../../Source/Action/CombineListedVertexCodes.asm)

Объединение кодов границ перечисленных точек с ранним выходом по нулевому коду.

[Алгоритм, точные регистры и модель](../ActionListedCodes.md).

## DrawLinearLine

[Action.DrawLinearLine](../../Source/Action/DrawLinearLine.asm)

Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки.

[Алгоритм, точные регистры и модель](../ActionLineRaster.md).

## AbortProjectedVertexScan

[Action.AbortProjectedVertexScan](../../Source/Action/AbortProjectedVertexScan.asm)

Завершение сканирования точек по маркеру отказа перспективы без отката предыдущих кодов.

[Алгоритм, точные регистры и модель](../ActionVertexAbort.md).

## ClassifyProjectedVertices

[Action.ClassifyProjectedVertices](../../Source/Action/ClassifyProjectedVertices.asm)

Заполнение кодов границ экранных точек и накопление общего кода объекта.

[Алгоритм, точные регистры и модель](../ActionVertexCodes.md).

## CheckFaceOrientation

[Action.CheckFaceOrientation](../../Source/Action/CheckFaceOrientation.asm)

Проверка ориентации выбранной тройки экранных точек по знаку разности двух произведений.

[Алгоритм, точные регистры и модель](../ActionFaceOrientation.md).

## RenderSceneFrame

[Action.RenderSceneFrame](../../Source/Action/RenderSceneFrame.asm)

Подготовка кадра, проекция объектов и передача в очередь отрисовки.

Вход `#E020`, запись 17, смещения `#8020..#81B8`.

- Прямые вызовы: `#6A6E`, `#6B16`, `#AACC`, `#ADB7`.
- Непосредственные чтения: `#9B01`, `#9B03`, `#9B05`, `#9B07`, `#9B09`, `#9B0B`, `#9B0D`, `#9B0F`, `#9B11`, `#9B12`, `#9B14`, `#9B19`, `#9B81`, `#9B8E`, `#9B95`, `#9B97`, `#D7A2`, `#D7C4`, `#D9B6`, `#E4A7`, `#ED83`.
- Непосредственные записи: `#9B12`, `#9B13`, `#9B14`, `#9B19`, `#9B8D`, `#9B8E`, `#9B8F`, `#9B91`, `#9B93`, `#9BA1`, `#AF48`, `#AF56`, `#AF69`, `#CB3E`, `#CB54`, `#CB6F`, `#CB8B`, `#CBA1`, `#CBBC`, `#CBD8`, `#CBEE`, `#CC09`, `#E021`, `#E4A7`, `#ED83`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRenderFrameSetup.md).

## PrepareProjectionScale

[Action.PrepareProjectionScale](../../Source/Action/PrepareProjectionScale.asm)

Масштабирование мантиссы заголовка на степень двух и настройка трёх относительных переходов.

[Масштаб и границы проверки](../ActionScaleHeader.md).

## CheckCloseRecordBounds

[Action.CheckCloseRecordBounds](../../Source/Action/CheckCloseRecordBounds.asm)

Проверка трёх исходных компонент с цепочкой Carry и условная обработка близкой записи.

[Масштаб и границы проверки](../ActionScaleHeader.md).

[Алгоритм, контракты и независимая модель](../ActionCloseBounds.md).

## ClipProjectionBounds

[Action.ClipProjectionBounds](../../Source/Action/ClipProjectionBounds.asm)

Проверка глубины и двух осей с табличной поправкой масштаба и выбором следующего пути проекции.

[Граничные проверки, физическая таблица и модель](../ActionProjectionClip.md).

## PrepareProjectedBounds

[Action.PrepareProjectedBounds](../../Source/Action/PrepareProjectedBounds.asm)

Фильтрация старших байтов координат и подготовка допуска, знакового X и модулей двух проекций.

[Три отношения, ранние выходы и модели](../ActionProjectedBounds.md).

## CaptureProjectedRecord

[Action.CaptureProjectedRecord](../../Source/Action/CaptureProjectedRecord.asm)

Условная запись альтернативного HL в PendingRecord после двух проверок координатного допуска.

[Границы локального доказательства](../ActionProjectedCapture.md).

## FollowProjectedTarget

[Action.FollowProjectedTarget](../../Source/Action/FollowProjectedTarget.asm)

Сглаживание экранной точки и назначение первой свободной цели по запросу.

[Сопровождение и границы проверки](../ActionAimFollow.md).

## InsertRenderQueue

[Action.InsertRenderQueue](../../Source/Action/InsertRenderQueue.asm)

Вставка снимка объекта в связанную очередь по исходному знаковому сравнению глубины.

[Сопровождение и границы проверки](../ActionAimFollow.md).

[Алгоритм, контракты и независимая модель](../ActionRenderQueueInsert.md).

## ReadRenderQueue

[Action.ReadRenderQueue](../../Source/Action/ReadRenderQueue.asm)

Восстановление стека чтения очереди и загрузка снимка узла с обновлением AY.

Вход `#E4A6`, запись 17, смещения `#84A6..#84DA`.

- Прямые вызовы: `#ECA8`.
- Непосредственные чтения: `#9BA1`.
- Непосредственные записи: `#9B12`, `#9B14`, `#9B8D`, `#D7A2`, `#D7C4`, `#D9B6`, `#E4D6`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRenderQueueControl.md).

## RenderQueuedObject

[Action.RenderQueuedObject](../../Source/Action/RenderQueuedObject.asm)

Подготовка и вывод текущего объекта очереди с выбором рисователя и чтением следующего узла.

[Алгоритм, точные регистры и модель](../ActionRenderContinuation.md).

[Алгоритм, контракты и проверка](../ActionQueuedObject.md).

## SelectRenderQueueNode

[Action.SelectRenderQueueNode](../../Source/Action/SelectRenderQueueNode.asm)

Проверка конца очереди либо переход к загрузке выбранного узла.

Вход `#E4FF`, запись 17, смещения `#84FF..#8505`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRenderQueueControl.md).

## DispatchCloseRecord

[Action.DispatchCloseRecord](../../Source/Action/DispatchCloseRecord.asm)

Отбор близкой записи по коду запрета и классу с передачей в следующий режим либо инвертированием компонент.

[Различия трёх входов и модели](../ActionCloseRecord.md).

## CheckCloseRecordComponents

[Action.CheckCloseRecordComponents](../../Source/Action/CheckCloseRecordComponents.asm)

Дополнительный отбор по биту 4 ReuseByte и старшим байтам трёх компонент.

[Различия трёх входов и модели](../ActionCloseRecord.md).

## ReverseCloseRecordState

[Action.ReverseCloseRecordState](../../Source/Action/ReverseCloseRecordState.asm)

Уменьшение кода запрета, инвертирование масштабированных компонент и особое обнуление состояния класса 12.

[Различия трёх входов и модели](../ActionCloseRecord.md).

## PrepareRecordScale

[Action.PrepareRecordScale](../../Source/Action/PrepareRecordScale.asm)

Сохранение CPU SP, временное деление смещений класса 14 и выбор числа удвоений по заголовку модели.

Вход `#E55C`, запись 17, смещения `#855C..#859E`.

- Прямые вызовы: `#AACC`.
- Непосредственные чтения: `#E5B3`, `#E5D2`, `#E5ED`.
- Непосредственные записи: `#E59E`, `#E5B3`, `#E5D2`, `#E5ED`, `#E605`, `#E68C`, `#E692`, `#E698`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordScale.md).

## UpdateRecordComponents

[Action.UpdateRecordComponents](../../Source/Action/UpdateRecordComponents.asm)

Обновление трёх компонент с проверкой переполнения и границы, обработкой отказа и запросом предупреждения о стыковке.

Вход `#E5A0`, запись 17, смещения `#85A0..#8654`.

- Прямые вызовы: `#6040`, `#E98D`.
- Непосредственные чтения: `#9B82`.
- Непосредственные записи: `#E644`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordUpdate.md).

## FinishRecordWarning

[Action.FinishRecordWarning](../../Source/Action/FinishRecordWarning.asm)

Восстановление DE после запроса предупреждения и завершение через восстановитель смещений.

[Алгоритм, точные регистры и модель](../ActionRecordWarningReturn.md).

## RejectRecordUpdate

[Action.RejectRecordUpdate](../../Source/Action/RejectRecordUpdate.asm)

Восстановление CPU-стека, пометка записи IX для повторного использования и продолжение очистки класса 12.

Вход `#E658`, запись 17, смещения `#8658..#865E`.

- Прямые вызовы: `#F394`.
- Непосредственные чтения: `#E605`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRejectRecord.md).

## ReleaseClass12Records

[Action.ReleaseClass12Records](../../Source/Action/ReleaseClass12Records.asm)

Обнуление двух байтов состояния и пометка всех активных записей класса 12 либо хвост восстановления смещений.

[Алгоритм, точные регистры и модель](../ActionClassReuse.md).

## RestoreHalvedOffsets

[Action.RestoreHalvedOffsets](../../Source/Action/RestoreHalvedOffsets.asm)

Восстановление трёх исходных вычитаемых слов после временного арифметического деления для класса 14.

Вход `#E685`, запись 17, смещения `#8685..#869D`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#E5B3`, `#E5D2`, `#E5ED`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionOffsetRestore.md).

## SelectRecordByIndex

[Action.SelectRecordByIndex](../../Source/Action/SelectRecordByIndex.asm)

Расчёт адреса записи в IY по коду A с сохранением HL.

[Алгоритм, точные регистры и модель](../ActionRecordSelection.md).

## RecordIndexToAddress

[Action.RecordIndexToAddress](../../Source/Action/RecordIndexToAddress.asm)

Расчёт адреса записи A100 плюс входной код, умноженный на 64.

[Контракт и независимая модель](../ActionRecordIndex.md).

## RecordIXToIndex

[Action.RecordIXToIndex](../../Source/Action/RecordIXToIndex.asm)

Расчёт байтового кода записи по IX с сохранением HL.

[Контракт и независимая модель](../ActionRecordIndex.md).

## RecordIYToIndex

[Action.RecordIYToIndex](../../Source/Action/RecordIYToIndex.asm)

Расчёт байтового кода записи по IY с сохранением HL.

[Контракт и независимая модель](../ActionRecordIndex.md).


## RecordAddressToIndex

[Action.RecordAddressToIndex](../../Source/Action/RecordAddressToIndex.asm)

Расчёт байтового кода записи по HL, младшие шесть битов смещения не участвуют в коде.

[Контракт и независимая модель](../ActionRecordIndex.md).


## NextActiveRecord

[Action.NextActiveRecord](../../Source/Action/NextActiveRecord.asm)

Переход по шагу BC к следующей записи с байтом 1 не равным 80 либо к маркеру конца.

Вход `#E6D1`, запись 17, смещения `#86D1..#86E1`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRecordIterator.md).

## FindFilteredRecordOr26

[Action.FindFilteredRecordOr26](../../Source/Action/FindFilteredRecordOr26.asm)

Выбор кода 26 по потоку 10 либо поиск активного класса 1..15 или 18.

[Алгоритм, точные регистры и модель](../ActionRandomFilteredRecord.md).

## FindRecordExcept6And7

[Action.FindRecordExcept6And7](../../Source/Action/FindRecordExcept6And7.asm)

Поиск первой активной записи с классом вне пары 6 и 7.

[Алгоритм, точные регистры и модель](../ActionRecordsExcept6And7.md).

## FindRecordClass6Or7

[Action.FindRecordClass6Or7](../../Source/Action/FindRecordClass6Or7.asm)

Поиск первой активной записи с классом 6 либо 7.

[Алгоритм, точные регистры и модель](../ActionRecords6Or7.md).

## FindRecordClass5Or14

[Action.FindRecordClass5Or14](../../Source/Action/FindRecordClass5Or14.asm)

Поиск первой активной записи с классом 5 либо 14.

[Алгоритм, точные регистры и модель](../ActionRecords5Or14.md).

## PrepareLinkedRecordContext

[Action.PrepareLinkedRecordContext](../../Source/Action/PrepareLinkedRecordContext.asm)

Подготовка адреса связанной записи и трёх компонент текущей записи в операндах последующего расчёта.

[Алгоритм, точные регистры и модель](../ActionLinkedContext.md).

## LoadLinkedRecordVectors

[Action.LoadLinkedRecordVectors](../../Source/Action/LoadLinkedRecordVectors.asm)

Подготовка двух трёхсловных наборов из связанной записи либо фиксированных значений связи 1A.

[Алгоритм, точные регистры и модель](../ActionLinkedVectors.md).

## CheckAndToggleLinkedOverlay

[Action.CheckAndToggleLinkedOverlay](../../Source/Action/CheckAndToggleLinkedOverlay.asm)

Проверка связанных векторов, обновление обратной связи и XOR-вывод сегмента.

[Алгоритм, точные регистры и модель](../ActionLinkedOverlay.md).

## SpawnClass9ForClass8

[Action.SpawnClass9ForClass8](../../Source/Action/SpawnClass9ForClass8.asm)

Допуск полного класса 8 к созданию дочерних записей класса 9 с начальным состоянием 2.

[Алгоритм, точные регистры и модель](../ActionClass8SpawnGate.md).

## SpawnLinkedClass9Records

[Action.SpawnLinkedClass9Records](../../Source/Action/SpawnLinkedClass9Records.asm)

Условное создание одной либо двух записей класса 9 с индексом родителя и копией его связи.

[Алгоритм, точные регистры и модель](../ActionChildSpawn.md).

## CheckLinkedTargetTransition

[Action.CheckLinkedTargetTransition](../../Source/Action/CheckLinkedTargetTransition.asm)

Проверка допуска к выбору связанной записи либо перехода к фазовому ожиданию.

[Алгоритм, точные регистры и модель](../ActionTargetTransition.md).

## CheckObjectPhaseTransition

[Action.CheckObjectPhaseTransition](../../Source/Action/CheckObjectPhaseTransition.asm)

Проверка случайного ожидания и перехода к фазовому смещению записи.

[Алгоритм, точные регистры и модель](../ActionPhaseTransition.md).

## SelectClass8ForRecord

[Action.SelectClass8ForRecord](../../Source/Action/SelectClass8ForRecord.asm)

Поиск первой записи класса 8 и сохранение её индекса в текущей записи.

[Алгоритм, точные регистры и модель](../ActionSelectClass8.md).

## FindRecordByCode

[Action.FindRecordByCode](../../Source/Action/FindRecordByCode.asm)

Поиск от A100 первой активной записи с байтом 12 равным входному D.

Вход `#E98D`, запись 17, смещения `#898D..#89A0`.

- Прямые вызовы: `#E6D1`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRecordIterator.md).

## FindReusableRecord

[Action.FindReusableRecord](../../Source/Action/FindReusableRecord.asm)

Поиск первой записи с байтом 1 равным 80, обработка маркера конца и однократного пропуска по байту 18.

Вход `#E9A1`, запись 17, смещения `#89A1..#89C1`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionRecordSearch.md).

## FindNearestListedRecord

[Action.FindNearestListedRecord](../../Source/Action/FindNearestListedRecord.asm)

Выбор ближайшей доступной записи из списка индексов с сохранением первого равенства.

[Алгоритм, точные регистры и модель](../ActionNearestCandidate.md).

## CheckCandidateListClass

[Action.CheckCandidateListClass](../../Source/Action/CheckCandidateListClass.asm)

Проверка принадлежности полного класса списку допуска выбора цели.

[Алгоритм, точные регистры и модель](../ActionCandidateClass.md).

## CheckCandidateListReady

[Action.CheckCandidateListReady](../../Source/Action/CheckCandidateListReady.asm)

Проверка допуска класса и наличия непропущенного кандидата в списке.

[Алгоритм, точные регистры и модель](../ActionCandidateGate.md).

## PrepareLargeEffect

[Action.PrepareLargeEffect](../../Source/Action/PrepareLargeEffect.asm)

Настройка дочернего кода и чтение заголовка большого эффекта.

Вход `#EA29`, запись 17, смещения `#8A29..#8A3C`.

- Прямые вызовы: `#AACC`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#EAC4`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionLargeEffectEntry.md).

## AllocateLargeEffect

[Action.AllocateLargeEffect](../../Source/Action/AllocateLargeEffect.asm)

Выделение большого эффекта и создание дочерних записей перед освобождением объекта.

[Алгоритм, точные регистры и модель](../ActionLargeEffectContinuation.md).

## MaxRecordDeltaHigh

[Action.MaxRecordDeltaHigh](../../Source/Action/MaxRecordDeltaHigh.asm)

Максимальный старший байт модулей трёх обёрнутых разностей записей.

[Алгоритм, точные регистры и модель](../ActionRecordDistance.md).

## ToggleTargetOverlay

[Action.ToggleTargetOverlay](../../Source/Action/ToggleTargetOverlay.asm)

Проекция пары векторов, проверка общего окна и XOR-вывод соединяющего сегмента.

[Алгоритм, точные регистры и модель](../ActionOverlayPair.md).

## NextRandomWord0

[Action.NextRandomWord0](../../Source/Action/NextRandomWord0.asm)

Следующее слово независимого потока 0 с физическим состоянием Stream0.

Вход `#EB72`, запись 17, смещения `#8B72..#8B78`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionFoldedRandom.md).

## NextRandomWord3

[Action.NextRandomWord3](../../Source/Action/NextRandomWord3.asm)

Следующее слово независимого потока 3 с физическим состоянием Stream3.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord4

[Action.NextRandomWord4](../../Source/Action/NextRandomWord4.asm)

Следующее слово независимого потока 4 с физическим состоянием Stream4.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord1

[Action.NextRandomWord1](../../Source/Action/NextRandomWord1.asm)

Следующее слово независимого потока 1 с физическим состоянием Stream1.

Вход `#EB87`, запись 17, смещения `#8B87..#8B8D`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionFoldedRandom.md).

## NextRandomWord5

[Action.NextRandomWord5](../../Source/Action/NextRandomWord5.asm)

Следующее слово независимого потока 5 с физическим состоянием Stream5.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord6

[Action.NextRandomWord6](../../Source/Action/NextRandomWord6.asm)

Следующее слово независимого потока 6 с физическим состоянием Stream6.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord7

[Action.NextRandomWord7](../../Source/Action/NextRandomWord7.asm)

Следующее слово независимого потока 7 с физическим состоянием Stream7.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord8

[Action.NextRandomWord8](../../Source/Action/NextRandomWord8.asm)

Следующее слово независимого потока 8 с физическим состоянием Stream8.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord9

[Action.NextRandomWord9](../../Source/Action/NextRandomWord9.asm)

Следующее слово независимого потока 9 с физическим состоянием Stream9.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord10

[Action.NextRandomWord10](../../Source/Action/NextRandomWord10.asm)

Следующее слово независимого потока 10 с физическим состоянием Stream10.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord2

[Action.NextRandomWord2](../../Source/Action/NextRandomWord2.asm)

Следующее слово независимого потока 2 с физическим состоянием Stream2.

Вход `#EBB8`, запись 17, смещения `#8BB8..#8BBE`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionFoldedRandom.md).

## NextRandomWord11

[Action.NextRandomWord11](../../Source/Action/NextRandomWord11.asm)

Следующее слово независимого потока 11 с физическим состоянием Stream11.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord12

[Action.NextRandomWord12](../../Source/Action/NextRandomWord12.asm)

Следующее слово независимого потока 12 с физическим состоянием Stream12.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord13

[Action.NextRandomWord13](../../Source/Action/NextRandomWord13.asm)

Следующее слово независимого потока 13 с физическим состоянием Stream13.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## NextRandomWord14

[Action.NextRandomWord14](../../Source/Action/NextRandomWord14.asm)

Следующее слово независимого потока 14 с физическим состоянием Stream14.

[Алгоритм и полный договор](../ActionFoldedRandom.md).

## StepFoldedRandom

[Action.StepFoldedRandom](../../Source/Action/StepFoldedRandom.asm)

Обновление трёхбайтового состояния свёрткой переносов и возврат нового 16-битного слова через обратный EXX.

Вход `#EC08`, запись 17, смещения `#8C08..#8C53`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionFoldedRandom.md).

## ClassifyProjectedPair

[Action.ClassifyProjectedPair](../../Source/Action/ClassifyProjectedPair.asm)

Заполнение кодов двух проецированных точек и накопление их парных признаков границ.

[Алгоритм, точные регистры и модель](../ActionProjectedPairCodes.md).

## UpdateAyEffects

[Action.UpdateAyEffects](../../Source/Action/UpdateAyEffects.asm)

Вывод очередных строк потоков AY-каналов A и B и формирование канала C по R и изменяемому уровню.

Вход `#ECA8`, запись 17, смещения `#8CA8..#8D8E`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#ECA9`, `#ECAA`, `#ECF6`, `#ECF7`.
- Ввод и вывод: `IN A,(C)`, `OUT (C),A`.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и независимая модель](../ActionAyEffects.md).

## AdvanceObjectOffsetRise

[Action.AdvanceObjectOffsetRise](../../Source/Action/AdvanceObjectOffsetRise.asm)

Увеличение байта смещения и переход к обратному ходу по таймеру.

[Алгоритм, точные регистры и модель](../ActionObjectOffsetRise.md).

## AdvanceObjectOffsetFall

[Action.AdvanceObjectOffsetFall](../../Source/Action/AdvanceObjectOffsetFall.asm)

Уменьшение байта смещения и возврат сохранённого состояния по таймеру.

[Алгоритм, точные регистры и модель](../ActionObjectOffsetFall.md).

## AdvanceObjectPhaseWait

[Action.AdvanceObjectPhaseWait](../../Source/Action/AdvanceObjectPhaseWait.asm)

Обновление фазового счётчика и завершение ожидания по классу и компонентам.

[Алгоритм, точные регистры и модель](../ActionObjectPhaseWait.md).

## RefreshRecordClassAndOffsets

[Action.RefreshRecordClassAndOffsets](../../Source/Action/RefreshRecordClassAndOffsets.asm)

Повторный выбор поведения записи по классу и передача общему подготовителю смещений.

[Алгоритм, точные регистры и модель](../ActionClassRefresh.md).

## HandleLinkedRecordProximity

[Action.HandleLinkedRecordProximity](../../Source/Action/HandleLinkedRecordProximity.asm)

Проверка связи с записью полного класса 13, обработка близости и запуск эффекта по исходному биту 4.

[Алгоритм, точные регистры и модель](../ActionLinkedProximity.md).

## MarkIYRecordForReuse

[Action.MarkIYRecordForReuse](../../Source/Action/MarkIYRecordForReuse.asm)

Пометка записи по IY кодом Component0=8000 и однократным пропуском ReuseByte=FF.

[Алгоритм, точные регистры и модель](../ActionIYRecordReuse.md).

## HandleSelectedRecordProximity

[Action.HandleSelectedRecordProximity](../../Source/Action/HandleSelectedRecordProximity.asm)

Проверка выбранной записи, резервный поиск класса 8 и обработка близости.

[Алгоритм, точные регистры и модель](../ActionSelectedRecordProximity.md).

## SetClass18ObjectState

[Action.SetClass18ObjectState](../../Source/Action/SetClass18ObjectState.asm)

Установка состояния 0A у записи класса 12h перед диспетчеризацией.

Вход `#F075`, запись 17, смещения `#9075..#907B`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionObjectStateDispatch.md).

## UpdatePhaseAndNearVector

[Action.UpdatePhaseAndNearVector](../../Source/Action/UpdatePhaseAndNearVector.asm)

Обновление фазового перехода и обязательная обработка близкого широкого вектора.

[Алгоритм, точные регистры и модель](../ActionPhaseNearState.md).

## UpdateLinkedOrNearPhase

[Action.UpdateLinkedOrNearPhase](../../Source/Action/UpdateLinkedOrNearPhase.asm)

Проверка перехода к связи и условное продолжение в обработке близкого вектора.

[Алгоритм, точные регистры и модель](../ActionLinkedNearState.md).

## UpdateNearVectorPhase

[Action.UpdateNearVectorPhase](../../Source/Action/UpdateNearVectorPhase.asm)

Проверка близких широких векторов, случайного состояния 6 и шага фазы записи.

[Алгоритм, точные регистры и модель](../ActionNearPhase.md).

## StepSelectedWideVector

[Action.StepSelectedWideVector](../../Source/Action/StepSelectedWideVector.asm)

Шаг кодов движения к выбранному широкому вектору и проверка следующих состояний.

[Алгоритм, точные регистры и модель](../ActionWideVectorState.md).

## PrepareObjectOffsetTransform

[Action.PrepareObjectOffsetTransform](../../Source/Action/PrepareObjectOffsetTransform.asm)

Проверка маркера записи и подготовка смещений для вычислителя 6D06.

[Алгоритм, точные регистры и модель](../ActionObjectOffsetTransfer.md).

## HandleLinkedTargetState

[Action.HandleLinkedTargetState](../../Source/Action/HandleLinkedTargetState.asm)

Обновление связи, выбор дочерних действий и геометрическое сопровождение записи в состоянии 02.

[Алгоритм, точные регистры и модель](../ActionLinkedTargetState.md).

## CheckClass17SpawnWindow

[Action.CheckClass17SpawnWindow](../../Source/Action/CheckClass17SpawnWindow.asm)

Проверка случайного окна создания класса 17 и загрузка байта допуска по полному классу.

[Алгоритм, точные регистры и модель](../ActionSpawnWindow.md).

## SpawnLinkedClass17AndContinue

[Action.SpawnLinkedClass17AndContinue](../../Source/Action/SpawnLinkedClass17AndContinue.asm)

Создание класса 17 по текущей связи и продолжение общего расчёта смещений.

[Алгоритм, точные регистры и модель](../ActionSpawnContinue.md).

## SpawnClass17FromCurrentLink

[Action.SpawnClass17FromCurrentLink](../../Source/Action/SpawnClass17FromCurrentLink.asm)

Подготовка компонент и индексов текущей записи для общего создателя класса 17.

[Алгоритм, точные регистры и модель](../ActionSpawnCurrentLink.md).

## HandleLinkedPhaseState

[Action.HandleLinkedPhaseState](../../Source/Action/HandleLinkedPhaseState.asm)

Обновление связанной записи с отдельным случайным окном и шагом третьей фазы.

[Алгоритм, точные регистры и модель](../ActionLinkedPhaseState.md).

## HandleClass18Proximity

[Action.HandleClass18Proximity](../../Source/Action/HandleClass18Proximity.asm)

Поиск записи класса 18, освобождение текущей при близости либо подвод фазовых кодов.

[Алгоритм, точные регистры и модель](../ActionClass18Proximity.md).

## StepCodesTowardRecord

[Action.StepCodesTowardRecord](../../Source/Action/StepCodesTowardRecord.asm)

Подвод фазовых кодов текущей записи по трём компонентам выбранной записи.

[Алгоритм, точные регистры и модель](../ActionSelectedRecordStep.md).

## MarkRecordForReuse

[Action.MarkRecordForReuse](../../Source/Action/MarkRecordForReuse.asm)

Пометка записи кодом Component0=8000 и однократным пропуском ReuseByte=FF при поиске доступной записи.

Вход `#F394`, запись 17, смещения `#9394..#93A0`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordReuse.md).

## StepTimedPhasePattern

[Action.StepTimedPhasePattern](../../Source/Action/StepTimedPhasePattern.asm)

Обновление таймера и двух фаз с переходом к состоянию 10 при истечении.

[Алгоритм, точные регистры и модель](../ActionTimedPhaseState.md).

## StepTimedLinkedOverlay

[Action.StepTimedLinkedOverlay](../../Source/Action/StepTimedLinkedOverlay.asm)

Уменьшение таймера, восстановление состояния и обновление связанного сегмента либо создание класса 17.

[Алгоритм, точные регистры и модель](../ActionTimedLinkedState.md).

## SpawnPeriodicClass3Record

[Action.SpawnPeriodicClass3Record](../../Source/Action/SpawnPeriodicClass3Record.asm)

Периодическое создание одной записи класса 3 с уменьшением родительского счётчика и обязательным сбросом баз.

[Алгоритм, точные регистры и модель](../ActionPeriodicClass3State.md).

## SweepClass17AndPrepareSpawn

[Action.SweepClass17AndPrepareSpawn](../../Source/Action/SweepClass17AndPrepareSpawn.asm)

Обработка до трёх записей класса 17 и подготовка периодического создания при недостатке связей класса 3.

[Алгоритм, точные регистры и модель](../ActionClass17Sweep.md).

## UpdatePreferredClass18

[Action.UpdatePreferredClass18](../../Source/Action/UpdatePreferredClass18.asm)

Выбор опоры по R и потоку 2 либо по приоритету классов с обновлением класса 18.

Вход `#F51E`, запись 17, смещения `#951E..#9526`.

- Прямые вызовы: `#EBB8`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPreferredRecord.md).

## CheckPreferredRandomWord

[Action.CheckPreferredRandomWord](../../Source/Action/CheckPreferredRandomWord.asm)

Проверка младшего слова потока 2 и внешнего байта для выбора отдельного кода 26.

[Алгоритм, точные регистры и модель](../ActionPreferredChance.md).

## FindPreferredClass0

[Action.FindPreferredClass0](../../Source/Action/FindPreferredClass0.asm)

Поиск опорного класса 0 с продолжением к классам 7 и 5 при отсутствии.

Вход `#F535`, запись 17, смещения `#9535..#953E`.

- Прямые вызовы: `#E6BE`, `#E98D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPreferredRecord.md).

## ContinuePreferredClass0

[Action.ContinuePreferredClass0](../../Source/Action/ContinuePreferredClass0.asm)

Передача выбранного индекса класса 0 в общую проверку класса 18.

[Алгоритм, точные регистры и модель](../ActionPreferredZeroBridge.md).

## FindPreferredClass7

[Action.FindPreferredClass7](../../Source/Action/FindPreferredClass7.asm)

Поиск опорного класса 7 с продолжением к классу 5 при отсутствии.

Вход `#F541`, запись 17, смещения `#9541..#954A`.

- Прямые вызовы: `#E6BE`, `#E98D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPreferredRecord.md).

## ContinuePreferredClass7

[Action.ContinuePreferredClass7](../../Source/Action/ContinuePreferredClass7.asm)

Передача выбранного индекса класса 7 в общую проверку класса 18.

[Алгоритм, точные регистры и модель](../ActionPreferredSevenBridge.md).

## FindPreferredClass5

[Action.FindPreferredClass5](../../Source/Action/FindPreferredClass5.asm)

Поиск последнего опорного класса 5 либо переход к сбросу баз.

Вход `#F54D`, запись 17, смещения `#954D..#9556`.

- Прямые вызовы: `#E6BE`, `#E98D`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionPreferredRecord.md).

## ApplyPreferredToClass18

[Action.ApplyPreferredToClass18](../../Source/Action/ApplyPreferredToClass18.asm)

Запись выбранной опоры в первый класс 18 только при отсутствии класса 3.

[Алгоритм, точные регистры и модель](../ActionPreferredApply.md).

## ResetRecordUpdateBases

[Action.ResetRecordUpdateBases](../../Source/Action/ResetRecordUpdateBases.asm)

Обнуление трёх базовых слов в изменяемых операндах обновления компонент.

Вход `#F572`, запись 17, смещения `#9572..#957E`.

- Прямые вызовы: нет непосредственных обращений.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: `#E5B0`, `#E5CF`, `#E5EA`.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordBaseReset.md).

## ApproachTargetRecordAndResolve

[Action.ApproachTargetRecordAndResolve](../../Source/Action/ApproachTargetRecordAndResolve.asm)

Сближение с выбранной записью, обновление связи и завершение через большой эффект.

[Алгоритм, точные регистры и модель](../ActionArrivalState.md).

## StepTimedRecordDecay

[Action.StepTimedRecordDecay](../../Source/Action/StepTimedRecordDecay.asm)

Декремент времени состояния, освобождение при истечении и деление управляющего байта на два.

[Алгоритм, точные регистры и модель](../ActionTimedDecayState.md).

## StepIdleObjectOffset

[Action.StepIdleObjectOffset](../../Source/Action/StepIdleObjectOffset.asm)

Проверка управляющего байта State00, сброс баз либо полный расчёт смещений после двойного декремента.

[Алгоритм, точные регистры и модель](../ActionIdleState.md).

## EnterRandomClassGate

[Action.EnterRandomClassGate](../../Source/Action/EnterRandomClassGate.asm)

Хвостовой вход в проверку случайного допуска класса.

[Договоры и границы проверки](../ActionRandomClassGateEntry.md).

## ResetIdleRecordBases

[Action.ResetIdleRecordBases](../../Source/Action/ResetIdleRecordBases.asm)

Обнуление трёх общих базовых слов при нулевом управляющем байте State00.

[Алгоритм, точные регистры и модель](../ActionIdleBaseReset.md).

## DispatchClassOnHighRandomWord

[Action.DispatchClassOnHighRandomWord](../../Source/Action/DispatchClassOnHighRandomWord.asm)

Вызов обработчика класса только при новом слове потока 0 не меньше F000.

[Алгоритм, точные регистры и модель](../ActionRandomClassGate.md).

## StepFastRecordPhases

[Action.StepFastRecordPhases](../../Source/Action/StepFastRecordPhases.asm)

Увеличение второй и третьей фаз на два и три перед общим расчётом локальных смещений.

[Алгоритм, точные регистры и модель](../ActionFastPhaseState.md).

## AcquireLinkAndApplyOffsets

[Action.AcquireLinkAndApplyOffsets](../../Source/Action/AcquireLinkAndApplyOffsets.asm)

Выбор связи и попытка создания дочерних записей перед обязательным расчётом локальных смещений.

[Алгоритм, точные регистры и модель](../ActionAcquireLocalState.md).

## ApplyRecordLocalOffsets

[Action.ApplyRecordLocalOffsets](../../Source/Action/ApplyRecordLocalOffsets.asm)

Увеличение фазового индекса и расчёт баз по отдельным фазам из байтов 0D..0F записи.

[Алгоритм, точные регистры и модель](../ActionLocalOffsets.md).

## StartSmallRecordEffect

[Action.StartSmallRecordEffect](../../Source/Action/StartSmallRecordEffect.asm)

Создание малого эффекта по заголовку модели и переход текущей записи к состоянию затухания 7.

[Алгоритм, точные регистры и модель](../ActionSmallEffectState.md).

## UpdateObjects

[Action.UpdateObjects](../../Source/Action/UpdateObjects.asm)

Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний.

Вход `#F729`, запись 17, смещения `#9729..#9791`.

[Обход записей и продолжение F775](../ActionObjectWalk.md).

- Прямые вызовы: `#62CF`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## CheckRecordEffectThreshold

[Action.CheckRecordEffectThreshold](../../Source/Action/CheckRecordEffectThreshold.asm)

Выбор порога запуска большого эффекта для текущей записи.

Вход `#F792`, запись 17, смещения `#9792..#97BE`.

- Прямые вызовы: `#EA29`.
- Непосредственные чтения: `#9C1A`, `#9C1B`.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

[Алгоритм, контракты и проверка](../ActionRecordEffectResume.md).

## ResumeAfterRecordEffect

[Action.ResumeAfterRecordEffect](../../Source/Action/ResumeAfterRecordEffect.asm)

Сброс флагов связи и продолжение обхода объектов.

[Алгоритм, точные регистры и модель](../ActionRecordEffectResume.md).

## DispatchObjectState

[Action.DispatchObjectState](../../Source/Action/DispatchObjectState.asm)

Выбор состояния объекта, косвенный вызов обработчика и последующее обновление записи.

Вход `#F7C6`, запись 17, смещения `#97C6..#9865`.

- Прямые вызовы: `#E55C`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: `JP (HL)`.

[Алгоритм, контракты и проверка](../ActionObjectStateDispatch.md).

## ReloadActionAfterHyperJump

[Action.ReloadActionAfterHyperJump](../../Source/Action/ReloadActionAfterHyperJump.asm)

Перенесённая стадия сохранения 481 байта, вызова TR-DOS для ACTION и восстановления состояния перед новым загрузчиком.

[Договоры и границы проверки](../ActionHyperReload.md).

## QueueNumberBank1

[Action.QueueNumberBank1](../../Source/Action/QueueNumberBank1.asm) — Передача байтового числа A в очередь Controls банка 1 с фиксированным возвратом страницы 10.

Начало #6000, смещения #023D..#024C. [Проверка и границы](../ActionTextQueueCalls.md).

## PrintByteAndScrollBank1

[Action.PrintByteAndScrollBank1](../../Source/Action/PrintByteAndScrollBank1.asm)

Прямой десятичный вывод байта с обязательной прокруткой окна банка 1.

[Алгоритм, точные регистры и модель](../ActionDirectDecimalScroll.md).

## PrintByteBank1

[Action.PrintByteBank1](../../Source/Action/PrintByteBank1.asm)

Прямой десятичный вывод байта в окне банка 1 с исходной попыткой записи в ПЗУ.

[Алгоритм, точные регистры и модель](../ActionDirectDecimalPlain.md).

## QueueTextItemBank1

[Action.QueueTextItemBank1](../../Source/Action/QueueTextItemBank1.asm) — Передача записи DE в очередь Controls банка 1 с сохранением регистров и возвратом страницы 10.

Начало #6040, смещения #027D..#0290. [Проверка и границы](../ActionTextQueueCalls.md).

## ShowNoiseBeforeReload

[Action.ShowNoiseBeforeReload](../../Source/Action/ShowNoiseBeforeReload.asm) — Вывод шумовых кадров и ожидание клавиши перед загрузкой станции.

Начало #6054, смещения #0291..#02EA. [Проверка и границы](../ActionTextQueueCalls.md).

[Алгоритм, контракты и проверка](../ActionNoiseExit.md).

## CreateClass17LinkedRecord

[Общий создатель](../../Source/Action/CreateClass17LinkedRecord.asm). [Алгоритм и точный договор](../ActionClass17Spawn.md).
