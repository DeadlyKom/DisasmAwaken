# Форматы данных

Объявления находятся в `Includes/Structs/Include.inc`.

| Тип | Размер | Подтверждённое назначение |
| --- | --- | --- |
| FActionAyFrame | #04 | 88 физических строк семи потоков и 7 терминаторов, см. [ActionAyStreams](ActionAyStreams.md) |
| FActionAimPoint | #02 | Физические байты X и Y, см. [сопровождение](ActionAimFollow.md) |
| FActionRenderNode | #0E | Создаваемый runtime-узел с неизвестными байтами 01 и 02, см. [очередь](ActionRenderQueueInsert.md) |
| FRenderPhases | #03 | Три физических фазы и вложенный снимок узла, см. [коэффициенты](ActionRenderCoefficients.md) |
| FObjectDataPointer | #02 | 128 физических указателей банка 4, см. [OBJECT3D](ActionObjectPointers.md) |
| FClipProduct | #04 | Четыре физических произведения ACTION внутри разнесённой таблицы, см. [числители](ActionClipProducts.md) |
| FLinePixelMask | #01 | 16 физических прямых и инверсных масок пиксельных фаз, см. [растеризатор](ActionLineRaster.md) |
| FRenderProjectedPoint | #05 | Runtime-точка Second, First и парный ClipCode, [коды границ](ActionVertexCodes.md) и [два физических экземпляра CF0B/CF1B](ActionClipProducts.md) |
| FActionRecord | #40 | 25 физических исходных слотов и маркер, вложенные компоненты и явные неизвестные поля, см. [ActionObjectRecords](ActionObjectRecords.md) |
| FSymmetricSquareValue | #01 | 256 физических нормированных квадратов, см. [ActionProjectionClip](ActionProjectionClip.md) |
| FIndexedDelta | #01 | шестнадцать физических поправок signed8, игровое соответствие индексов неизвестно, см. [ActionTypeDelta](ActionTypeDelta.md) |
| FMissileTargets | #03 | три физических кода захвата Target0..Target2, FF означает отсутствие цели, см. [ActionMissileLaunch](ActionMissileLaunch.md) |
| FMissileStock | #02 | физические Fallback и Preferred запаса ракет, виды запасов не установлены, см. [ActionMissileStock](ActionMissileStock.md) |
| FKeyHandlerPointer | #02 | 26 отдельных слов адресов, перекрывающееся чтение описано отдельно, см. [ActionKeyDispatchPrefix](ActionKeyDispatchPrefix.md) |
| FKeyScanInput | #02 | 27 физических RowSelect и InputMask, см. [ActionKeyDispatchPrefix](ActionKeyDispatchPrefix.md) |
| FPreferredBytePair | #02 | физические Preferred и Fallback ACTION, см. [ActionPreferredByte](ActionPreferredByte.md) |
| FGaugePartialMask | #01 | 7 физических масок шестистрочной шкалы, см. [ControlsSixRowGauge](ControlsSixRowGauge.md) |
| FObjectGlyphPointer | #02 | 20 физических указателей на 12 форм, см. [ControlsObjectProjection](ControlsObjectProjection.md) |
| FObjectPixelMask | #01 | 8 одиночных пиксельных масок, см. [ControlsObjectProjection](ControlsObjectProjection.md) |
| FObjectGlyphClearPhase | #06 | 8 масок очистки, поля Unknown02..Unknown05 не установлены, см. [ControlsObjectProjection](ControlsObjectProjection.md) |
| FTrDosEntry | #10 | исходная запись каталога |
| FPackedHeader | #06 | HR, распакованная и упакованная длины |
| FPackedFinalBytes | #06 | три пары финальных байтов, [20 физических экземпляров](PackedResourcePrefix.md) |
| FMusicEffectTarget | #02 | поле Handler, [21 физический указатель отложенных музыкальных команд](MusicEffects.md) |
| FMusicDeferredPairFrame | #06 | [динамическая рамка двух отложенных обработчиков и внешнего возврата](MusicEffects.md) |
| FMusicLoopHeader | #02 | LoopPosition и Length исходных сэмплов и орнаментов, [порядок обхода](MusicSynthesis.md) |
| FMusicSampleStep | #04 | ShiftControl, LevelModes и ToneDelta, [алгоритм синтеза и схема битов](MusicSynthesis.md) |
| FMusicDataPointer | #02 | [48 физических указателей сэмплов и орнаментов](MusicPlayerData.md) |
| FMusicAyRegisters | #0E | [единственный буфер регистров AY](MusicPlayerData.md) |
| FMusicRowCounter | #01 | [три физических счётчика строк](MusicPlayerData.md) |
| FMusicVolumeRow | #10 | [15 физических строк громкости, нулевая строка наложена на AY](MusicPlayerData.md) |
| FMusicNotePeriod | #02 | [96 физических слов периодов](MusicPlayerData.md) |
| FMusicModuleHeader | #69 | [физический заголовок композиции, включая Unknown63](MusicComposition.md) |
| FMusicRelativePointer | #02 | [48 физических относительных адресов](MusicComposition.md) |
| FMusicPositionByte | #01 | [28 позиций и отдельный маркер FF](MusicComposition.md) |
| FMusicPatternPointers | #06 | [19 физических троек указателей A/B/C](MusicComposition.md) |
| FMusicOrnamentStep | #01 | [57 физических поправок индекса ноты](MusicComposition.md) |
| FTextQueueItem | #02 | [16 физических записей банка 1 и отдельный конечный маркер](TextQueueProducer.md) |
| FTextQueueInsertFrame | #08 | [динамическая рамка HL, BC, AF и внешнего возврата](TextQueueProducer.md) |
| FActionTextQueueFrame | #08 | [собственная рамка межбанковой обёртки, SavedHL, SavedBC, SavedAF, возврат](ActionTextQueueCalls.md) |
| FVisualEffect | #12 | запись эффекта, свободное состояние +7 |
| FInterfaceItem | #10 | прямоугольник, флаги и два обработчика интерфейса |
| FProjectedPoint | #05 | X, Y и составной код отсечения вершины |
| FScriptToken | #03 | символ и указатель обработчика, 102 физических экземпляра |
| FExpressionCall | #06 | левый операнд, адрес операции и правый операнд на стеке выражений |
| FTexturePhase | #06 | фаза, её приращение и изменение приращения, три физических экземпляра |
| FGlyphRoute | #04 | два адреса участков глифа, 128 физических экземпляров |
| FGlyphFrame | #10 | семь сохранённых пар регистров и адрес возврата на CPU-стеке |

Поля Unknown сохраняют неустановленное назначение. Объявление структуры
само по себе не выделяет новую область памяти.

В [исходной композиции](MusicComposition.md) оформлены 26 физических FMusicLoopHeader
и 77 FMusicSampleStep. Смещения полей и потребление исходным ядром проверены.

В данных интерфейса сохранены 46 физических инициализаторов, затем #80.
В `Source/Screens` сохранены 20 упакованных блоков с заголовками и хвостами.
Физические экземпляры FScriptToken находятся в
[TokenBindings.asm](../Source/Text/Data/TokenBindings.asm), а записи FExpressionCall
создаются во время выполнения языка. Форматы и потребители разобраны в
[ScriptLanguage](ScriptLanguage.md).
Таблица [Squares.bin](../Source/Map/Resources/Squares.bin) хранит младшие
и старшие байты 256 квадратов в двух последовательных страницах,
подробности в [MapMath](MapMath.md).
Ресурсы [FontWidths.bin](../Source/Station/Resources/FontWidths.bin) и
[FontGlyphs.bin](../Source/Station/Resources/FontGlyphs.bin) содержат
256 ширин и 256 восьмибайтовых глифов, подробности в [Font](Font.md).
Остальные неклассифицированные диапазоны нельзя считать автоматически ресурсами
или автоматически кодом, даже если они находятся в Source/Resources.

| Запись | Имя | Параметр | Длина | Секторов | Хвост |
| --- | --- | --- | ---: | ---: | ---: |
| 0 | _XTime15.B (удалена) | #0147 | 327 | 237 | 60345 |
| 1 | _xt.char.t (удалена) | #05C7 | 8205 | 33 | 243 |
| 2 | _L->TXT.H (удалена) | #0000 | 521 | 3 | 247 |
| 3 | AWAKEN.B | #0077 | 119 | 45 | 11401 |
| 4 | STATIONF.C | #6000 | 40960 | 160 | 0 |
| 5 | LANG.C | #C000 | 3864 | 16 | 232 |
| 6 | D3D.C | #C000 | 15978 | 63 | 150 |
| 7 | KARTA.C | #C000 | 11776 | 46 | 0 |
| 8 | HELP.C | #DB00 | 5921 | 24 | 223 |
| 9 | stscr.C | #C000 | 3230 | 239 | 57954 |
| 10 | MUZ1.C | #DB00 | 7209 | 29 | 215 |
| 11 | SAVE1.s | #6000 | 512 | 2 | 0 |
| 12 | SAVE2.s | #6000 | 512 | 2 | 0 |
| 13 | SAVE3.s | #6000 | 512 | 2 | 0 |
| 14 | SAVE4.s | #6000 | 512 | 2 | 0 |
| 15 | SAVE5.s | #6000 | 512 | 2 | 0 |
| 16 | SAVE0.s | #6000 | 512 | 2 | 0 |
| 17 | ACTION.C | #6000 | 40960 | 160 | 0 |
| 18 | DATAS.C | #8C00 | 7213 | 29 | 211 |
| 19 | 3DPART.C | #C000 | 8224 | 33 | 224 |
| 20 | VOXAL0.C | #C000 | 11264 | 44 | 0 |
| 21 | VOXAL.C | #EC00 | 3784 | 15 | 56 |
| 22 | CONTROL0.C | #C000 | 6878 | 27 | 34 |
| 23 | CONTROL.C | #DADE | 6474 | 26 | 182 |
| 24 | OBJECT3D.C | #C000 | 10580 | 42 | 172 |
| 25 | PANEL.C | #6373 | 1463 | 6 | 73 |
| 26 | PANELF.C | #2020 | 1436 | 6 | 100 |
| 27 | PANELMET.C | #2020 | 1423 | 6 | 113 |
| 28 | PANELFF.C | #7263 | 1543 | 7 | 249 |
| 29 | FINALF.C | #6000 | 19114 | 75 | 86 |
| 30 | scene1po.s | #7270 | 18676 | 73 | 12 |
| 31 | choose1.C | #2020 | 6912 | 27 | 0 |
| 32 | choose2.C | #2020 | 6912 | 27 | 0 |
| 33 | BANK0.C | #C000 | 16384 | 64 | 0 |
| 34 | BANK1.C | #C000 | 16384 | 64 | 0 |
| 35 | BANK2.C | #C000 | 16384 | 64 | 0 |
| 36 | BANK3.C | #C000 | 16384 | 64 | 0 |
| 37 | BANK4.C | #C000 | 16384 | 64 | 0 |
| 38 | BANK5.C | #C000 | 16384 | 64 | 0 |
| 39 | BAR.C | #8000 | 3076 | 13 | 252 |
| 40 | BD0.C | #C000 | 16268 | 64 | 116 |
| 41 | BD1.C | #C000 | 16152 | 64 | 232 |
| 42 | BD2.C | #C000 | 16248 | 64 | 136 |
| 43 | BD3.C | #C000 | 12048 | 48 | 240 |

FCenteredItemFrame описывает десятибайтовый динамический CPU-стек обработчика,
см. [CenteredItem](CenteredItem.md). Статический экземпляр и новая память не создаются.

FCaptionItemFrame и FBandWaitFrame описывают динамические кадры 12 и 8 байтов,
см. [CaptionItem](CaptionItem.md). Их создают исходные PUSH, статической памяти нет.

FDrawListEntry описывает двухбайтовый указатель runtime-списка обработчиков.
Его старший байт 1 является ограничителем, см. [DrawAdapters](DrawAdapters.md).

FDrawMoveFrame, FDrawShiftFrame и FRestoreBoundsFrame описывают динамические
кадры изменения списка и восстановления геометрии, см. [MoveDrawItem](MoveDrawItem.md) и [InterfaceBounds](InterfaceBounds.md).

## Исходная синусоида

[SineTable](../Source/Action/Data/SineTable.asm) содержит 256 физических
`FFixedSineValue` размером один байт, единственное поле Value имеет смещение 0.
Знаковые значения -127..127 с масштабом 128 сохранены из ACTION 3900..39FF,
соответствующих RAM 9900..99FF. Подробности и потребители описаны в
[ActionSineTable](ActionSineTable.md).

## Квадраты байтовых индексов

[Squares](../Source/Controls/Data/Squares.asm) содержит 512 физических
`FSquareTableByte` с однобайтовым полем Value. Первые 256 записей Low00..LowFF
хранят младшие байты квадратов, следующие High00..HighFF старшие.
Исходные страницы C3 и C4 банка 1 сохранены. Это раздельные плоскости,
а не чередующаяся последовательность слов. Потребители и форматы описаны в
[ControlsSquares](ControlsSquares.md).

## Компонент сравниваемой последовательности

`FComponent24` размером три байта описывает динамическую запись по IX или IY.
Поля Low, Middle и High имеют смещения 0, 1 и 2. Сравнение не читает Low,
исключает разряд 7 High и использует оставшийся 15-битовый ключ.
Статическая память под этот формат не выделяется, общий смысл исключённого
разряда пока не доказан. Подробности приведены в
[ControlsComponentCompare](ControlsComponentCompare.md).

## Маски малых фигур и вход проекции

[SmallMaskSeeds](../Source/Controls/Data/SmallMaskSeeds.asm) содержит 18 физических
`FSmallMaskSeed` с однобайтовым Packed, маска F8 выделяет пиксельную часть,
07 числовое количество сдвигов. [SmallMaskRows](../Source/Controls/Data/SmallMaskRows.asm)
содержит 12 `FSmallMaskRow` с полем Mask по смещению 0 и исходными нулями.
Следующие 20 байтов остаются неизвестными. Подробности приведены в
[ControlsSmallMasks](ControlsSmallMasks.md).

[BodyProjection.Value](../Source/Controls/Data/BodyProjection.asm) является
физическим экземпляром `FBodyProjection` размером четыре байта. OffsetY,
OffsetX, Flags и Radius расположены по смещениям 0, 1, 2 и 3.
Назначение всех разрядов Flags не объявляется установленным, малый рисователь
использует только два направления. Следующие 12 рабочих байтов оформлены
как физическая [FCircleRasterWork](ControlsCircleWork.md), полный игровой смысл Mode ещё не установлен. См. [ControlsSmallBodies](ControlsSmallBodies.md).

## Строки указателя

[BufferPoints](../Source/Controls/Data/BufferPoints.asm) содержит 35 физических
`FBufferPoint` размером два байта, Y по смещению 0, X по смещению 1.
Исходные нулевые значения всех 70 байтов C500..C545 банка 1 сохранены.
Подготовка и XOR-потребитель описаны в [ControlsBufferPoints](ControlsBufferPoints.md).

Таблица [MarkerPhaseMasks](../Source/Controls/Data/MarkerPhaseMasks.asm) содержит
восемь физических `FMarkerPhaseMasks` размером четыре байта. Поля Vertical,
CentralLeft, CentralMiddle и CentralRight занимают смещения 0, 1, 2 и 3.
Всего сохранены 32 байта F0ED..F10C банка 1. Значения являются пиксельными
XOR-масками, а не флагами состояния. Потребитель и граничная адресация
описаны в [ControlsMarker](ControlsMarker.md).

[PointerSprites](../Source/Station/Data/PointerSprites.asm) содержит 192 физических FPointerRasterRow по четыре байта, MaskLeft, XorLeft, MaskRight, XorRight. Три страницы по восемь фаз сдвига и восемь строк каждой фазы сохраняют исходные #6000..#62FF. [PointerBackground](../Source/Station/Data/PointerBackground.asm) содержит восемь физических FPointerSavedRow по два байта Left, Right по #6575..#6584. Инициализаторы сохранены побайтно, во время работы заменяются сохранёнными экранными байтами. Динамический FPointerGuardFrame размером 12 байтов создаётся на CPU-стеке обёртками, отдельного статического экземпляра не имеет. Подробности и ограничения приведены в [Pointer](Pointer.md).

## Рабочие записи большого контура и генератора

[CircleWork](../Source/Controls/Data/CircleWork.asm) содержит физическую `FCircleRasterWork` размером 12 байтов D181..D18C, поля и границы доказательства описаны в [ControlsCircleWork](ControlsCircleWork.md).

[WordRandomState](../Source/Action/Data/WordRandomState.asm) содержит физическую `FWordRandomState` размером 4 байта, First по смещению 0 и Second по смещению 2. Исходные нули ACTION по 9B15..9B18 сохранены. Потребитель и рекурсия описаны в [ControlsWordRandom](ControlsWordRandom.md).

[ParameterCoefficients](../Source/Controls/Data/ParameterCoefficients.asm) содержит 15 физических `FParameterCoefficient` по три байта, Base по смещению 0, SlopeCode по смещению 1, ShiftMask по смещению 2. Исходные 45 байтов DF64..DF90 и перекрытие шаблонного чтения H=4 сохранены. Алгоритм описан в [ControlsParameterTables](ControlsParameterTables.md).

[ThreeRowGlyphs](../Source/Controls/Data/ThreeRowGlyphs.asm) содержит 32 физических `FThreeRowGlyphPhase` размером шесть байтов, три строки по паре Left,Right. Исходные 192 байта четырёх знаков и восьми фаз сохранены, следующие 32 байта оформлены отдельной таблицей RasterReturns, полный рисователь ещё не разобран. Потребитель и границы координат описаны в [ControlsThreeRowGlyph](ControlsThreeRowGlyph.md).

[GlyphIndicatorState](../Source/Action/Data/GlyphIndicatorState.asm) содержит четыре физические записи по три байта. FGlyphIndicatorControl хранит FirstMode, ThirdGate, Unknown83, два FGlyphIndicatorXY хранят X,Y,SignSource, FGlyphIndicatorYX третьего входа хранит Y перед X. Исходные 12 байтов 9B81..9B8C сохранены, Unknown83 и полный игровой смысл векторов остаются неустановленными. Локальный алгоритм и режимы описаны в [ControlsGlyphIndicators](ControlsGlyphIndicators.md).

[RasterReturns](../Source/Controls/Data/RasterReturns.asm) содержит 16 физических `FReturnDispatchEntry` по два байта, поле Target хранит адрес кодового хвоста банка 1. Исходные 32 байта E271..E290 сохранены, диспетчер E2BB проверен 65536 сценариями до первого RET. Полные обработчики и внешний E291 остаются Unknown, границы описаны в [ControlsRasterReturns](ControlsRasterReturns.md).

Пятнадцать физических `FFoldedRandomState` по три байта занимают EBDB..EC07, всего 45 исходных байтов. LowWord по смещениям 0..1 и FoldByte по смещению 2 являются числовым состоянием. Все экземпляры, исходные значения, входы и ограничения приведены в [ActionFoldedRandom](ActionFoldedRandom.md).

## Физические страницы табличного корня

| Структура | Размер | Назначение |
|---|---|---|
| FRootCacheByte | #01 | 768 физических байтов трёх плоскостей корня, см. [ActionCachedRoot](ActionCachedRoot.md) |

## Физические компоненты преобразования

[ComponentWork](../Source/Action/Data/ComponentWork.asm) содержит три физических FComponent24 по три байта, Low/Middle/High имеют смещения 0/1/2. Старшее слово хранит знаковый код и верхние 15 разрядов модуля после [кодирования](ActionComponentEncoding.md), Low дополняет их до 23 бит в фазе [проекции](ControlsBodyProjection.md), физические девять исходных нулей сохранены.

## Указатели классов ACTION

[ClassHandlers](../Source/Action/Data/ClassHandlers.asm) содержит 26 физических FClassHandler размером два байта. Handler расположен по смещению 0, слова занимают 64F0..6523. Потребитель и поведение индексов вне таблицы описаны в [диспетчере](ActionClassDispatch.md). Соседние байты кода частью таблицы не являются.

## Исходные коды знакового отношения

[SignedRatioCodes](../Source/Action/Data/SignedRatioCodes.asm) содержит 256 физических FSignedRatioCode размером один байт, поле Code по смещению 0. Исходные значения 9A00..9AFF сохранены буквально, потребитель описан в [кодировщике отношения](ActionSignedRatioCode.md). Стандартная тригонометрическая формула для генерации сборочных данных не применяется.

## Физические широкие векторы ACTION

[WideVectors](../Source/Action/Data/WideVectors.asm) содержит шесть физических FActionWideVector по 12 байтов, каждый состоит из трёх FActionWideComponent по четыре байта. Все 72 исходных байта и little-endian порядок сохранены. Шесть записей описывают этот физический участок, допустимый игровой счётчик этим не ограничивается. См. [формат и потребители](ActionWideVectors.md).

## Знаковый рабочий вектор ACTION

[WorkVector24](../Source/Action/Data/WorkVector24.asm) содержит физический FActionWorkVector24 с тремя FActionWorkComponent24. Каждая компонента состоит из LowWord и High в дополнительном коде, всего сохранены девять байтов 9B78..9B80. Это другой числовой формат, чем знак и модуль FComponent24. См. [вычитание и ранние выходы](ActionSubtractWorkVector.md).
