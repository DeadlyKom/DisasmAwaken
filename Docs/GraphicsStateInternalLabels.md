# Внутренние входы графики и управления состоянием

Имена относятся к исходным операциям и сохраняют фактические адреса.
Изменений инструкций и новых областей памяти нет.

| Процедура | Адрес | Имя | Назначение входа |
| --- | --- | --- | --- |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E52E | RotateFirst | ненулевой первый угол, смешивание компонент 0 и 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E636 | CheckSecond | проверка второго угла перед смешиванием компонент 1 и 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E664 | RotateSecond | ненулевой второй угол |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E76C | CheckThird | проверка третьего угла перед смешиванием компонент 0 и 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E798 | RotateThird | ненулевой третий угол |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E566 | Stage1V0C0 | запись компоненты 0 вектора 0 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E58F | Stage1V0C1 | запись компоненты 1 вектора 0 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E5B8 | Stage1V1C0 | запись компоненты 0 вектора 1 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E5E1 | Stage1V1C1 | запись компоненты 1 вектора 1 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E60A | Stage1V2C0 | запись компоненты 0 вектора 2 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E633 | Stage1V2C1 | запись компоненты 1 вектора 2 на этапе 1 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E69C | Stage2V0C1 | запись компоненты 1 вектора 0 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E6C5 | Stage2V0C2 | запись компоненты 2 вектора 0 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E6EE | Stage2V1C1 | запись компоненты 1 вектора 1 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E717 | Stage2V1C2 | запись компоненты 2 вектора 1 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E740 | Stage2V2C1 | запись компоненты 1 вектора 2 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E769 | Stage2V2C2 | запись компоненты 2 вектора 2 на этапе 2 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E7D0 | Stage3V0C0 | запись компоненты 0 вектора 0 на этапе 3 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E7F9 | Stage3V0C2 | запись компоненты 2 вектора 0 на этапе 3 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E822 | Stage3V1C0 | запись компоненты 0 вектора 1 на этапе 3 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E84B | Stage3V1C2 | запись компоненты 2 вектора 1 на этапе 3 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E874 | Stage3V2C0 | запись компоненты 0 вектора 2 на этапе 3 |
| [RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | #E89D | Stage3V2C2 | запись компоненты 2 вектора 2 на этапе 3 |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECBC | CheckPositiveX | проверка неотрицательного X относительно окна |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECC1 | CheckRight | расчёт и проверка правой границы |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECCB | TrimRight | сокращение ширины по правой границе |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECD1 | BeginVertical | восстановление исходного Y из операнда |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECF1 | CheckPositiveY | проверка неотрицательного Y относительно окна |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ECF6 | CheckBottom | расчёт и проверка нижней границы |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED00 | TrimBottom | сокращение высоты по нижней границе |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED06 | BeginSteps | выбор видимого начала и шагов ресурса |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED0F | CheckTopTrim | проверка признака верхнего отсечения |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED19 | BufferAddress | адрес видимого начала в попарном буфере |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED30 | StoreParityOp | запись JR NC либо JR C по чётности левого края |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED5C | WideStride | 32-байтовый шаг строки широкого ресурса |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED5E | SkipTopRows | расчёт пропущенных строк исходного ресурса |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED7C | CheckLeftTrim | проверка горизонтального среза ресурса |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDC6 | ApplyLeftSkip | добавление целой части горизонтального среза к источнику |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDD0 | SaveStack | сохранение CPU-стека перед размещением шага в SP |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE0D | FinishRowStep | выделение байтов рассчитанного шага по строкам |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE13 | StoreRowStep | запись старшего байта шага и подготовка правой маски |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE26 | PartialMask | нулевая маска последней неполной пары |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE27 | StoreRightMask | запись масок обоих вариантов последней пары |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE36 | PairEntryIndex | перевод числа пропущенных пар в смещение развёрнутого кода |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE53 | SaveMaskPatch | запоминание места временного изменения левой маски |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE67 | StoreHalfOp | выбор операции полустроки и начальной палитры |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED90 | LeftSkipShift1 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #ED99 | LeftSkipShift2 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDA2 | LeftSkipShift3 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDAB | LeftSkipShift4 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDB4 | LeftSkipShift5 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDBD | LeftSkipShift6 | сдвиг накопителя горизонтального среза |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDEF | RowStepShift1 | сдвиг произведения целого шага Y на длину строки |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDF4 | RowStepShift2 | сдвиг произведения целого шага Y на длину строки |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDF9 | RowStepShift3 | сдвиг произведения целого шага Y на длину строки |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EDFE | RowStepShift4 | сдвиг произведения целого шага Y на длину строки |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE03 | RowStepShift5 | сдвиг произведения целого шага Y на длину строки |
| [ClipSprite](../Source/Voxel/ClipSprite.asm) | #EE08 | RowStepShift6 | сдвиг произведения целого шага Y на длину строки |
| [UpdateObjects](../Source/Action/UpdateObjects.asm) | #F72F | CheckEnd | проверка первого байта при уже найденном втором байте ограничителя |
| [UpdateObjects](../Source/Action/UpdateObjects.asm) | #F735 | NextRecord | переход к следующей физической записи |
| [UpdateObjects](../Source/Action/UpdateObjects.asm) | #F759 | CheckLinks | выбор обновления по LinkFlags |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A867 | BeginScene | создание объектов и начало подготовки кадра |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A8B2 | StepGaugePhase | накопитель фазы третьей шкалы |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A8C8 | UpdateRecords | обновление объектов, движения и эффектов |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A919 | ApplyEventCost | списание стоимости события из первой шкалы |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A928 | CheckBlink | проверка бита события мигания |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A93E | StoreBlink | запись выбранного атрибута мигания |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A948 | ClearBlink | обычный атрибут при отсутствии события мигания |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A94D | CheckDrain | проверка события списания сорока единиц |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A965 | StepRegenPhase | накопитель фазы восстановления первой шкалы |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #A97E | BeginEffects | обновление звука и параметров модели банка 4 |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #AA96 | StorePanelAttr | запись атрибута панели и последующий вывод |
| [UpdateFrame](../Source/Action/UpdateFrame.asm) | #AAC4 | ReloadStation | передача межбанковому загрузчику станции |
| [StartStation](../Source/StationBoot/StartStation.asm) | #414C | SumLengths | суммирование длин предыдущих упакованных экранов |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4153 | LocateScreen | расчёт положения выбранного экрана в секторах |
| [StartStation](../Source/StationBoot/StartStation.asm) | #41BD | StoreLineAddr | запись разнесённых байтов адреса экранной строки |
| [StartStation](../Source/StationBoot/StartStation.asm) | #41D2 | CountLineAddr | продолжение после коррекции экранной адресации |
| [StartStation](../Source/StationBoot/StartStation.asm) | #41D8 | ColumnGroup | начало группы повторений номера столбца |
| [StartStation](../Source/StationBoot/StartStation.asm) | #41DA | RepeatColumn | запись восьми одинаковых индексов столбца |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4212 | ApplyJoystick | сочетание результата опроса с настройкой джойстика |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4228 | ProbeMouseIdle | второй опрос порта мыши после первого результата |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4232 | CombineMouse | объединение результатов двух опросов и настройки мыши |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4260 | BindItemIndex | привязка последовательного индекса к callback элемента |
| [StartStation](../Source/StationBoot/StartStation.asm) | #4278 | PrepareWorld | подготовка мирового ключа и возврат к станционному циклу |
| [DrawGlyph](../Source/Station/DrawGlyph.asm) | #AEF0 | BuildRouteIdx | расчёт индекса таблицы FGlyphRoute после учёта границы знакоместа |

Положение меток сверяет [CheckSourceLabels](../Tools/Disasm/Research/CheckSourceLabels.py).
Инструкции сверяет [VerifySources](../Tools/Disasm/VerifySources.py), без запуска сборки.
