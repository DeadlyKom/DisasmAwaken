"""Ручная разметка подтверждённых механизмов, не участвует в сборке."""

# Имя файла и описание задаются по исходному коду, неизвестное не переименовывается в гипотезу.
FUNCTIONS = {
    "Map": {
        0xE57E: ("PreviousRasterRow", "Переход на предыдущую строку Spectrum с проверкой верхней границы и нелокальным завершением растрового вызова"),
        0xE5AC: ("NextRasterRow", "Переход на следующую строку Spectrum с проверкой нижней границы и нелокальным завершением растрового вызова"),
        0xE666: ("ResetRasterDown", "Сброс альтернативного состояния растрового обхода и выбор движения вниз"),
        0xE674: ("ResetRasterUp", "Сброс альтернативного состояния растрового обхода и выбор движения вверх"),
        0xE65D: ("LookupSquare", "Чтение квадрата A из двух раздельных страниц младших и старших байтов с сохранением Carry"),
        0xE554: ("SqrtSquareDiff", "Поразрядный целочисленный корень из 16-битной разности D в квадрате, A в квадрате и входного Carry"),
    },
    "Basic": {
        0x5CD1: ("ReadIntroSectors", "Чтение 44 физических секторов через TR-DOS с возвратом на #6500"),
    },
    "Intro": {
        0x661E: ("DrawFinalTextureFrame", "Настройка смещения и параметров последнего текстурного эффекта вступления"),
        0x6638: ("BuildAlternatingTexture", "Построение текстуры с чередованием исходного байта и байта, уменьшенного в четыре раза, копия в банк 6"),
        0x66A3: ("DrawScrolledTexture", "Обновление двух смещений modulo 64, выбор строки текстуры и вывод двух половин кадра"),
        0x66E2: ("SampleTextureRows", "Выборка 16 строк текстуры через генерируемый обработчик в #7E00 и временный SP"),
        0x66F3: ("NextSampledRow", "Продолжение генерируемого обработчика, переход к следующей строке и восстановление SP"),
        0x66FB: ("InitializeScrolledTexture", "Создание 64 развёрнутых выборок по шаблону #6722, подготовка текстуры и экранной раскладки"),
        0x6729: ("ExpandTextureRows", "Добавление IXL к 4096 байтам банка 4 и четырёхкратное повторение каждой 64-байтовой строки"),
        0x6757: ("CopyTextureToBank", "Копирование #4000 байт из #8000 в окно текущего банка #C000"),
        0x6763: ("BuildTextureLookup", "Построение двухбайтовой таблицы выборок по координатам из #6400 и заполнение её пропусков"),
        0x67F1: ("PresentInterlacedFrame", "Чередование двух раскладок, синхронизация с кадром и перенос данных текстуры в экран"),
        0x6827: ("ScatterTextureToScreen", "Копирование 38 строк по 32 байта, адреса источников берутся из временного стека"),
        0x68A4: ("RunAttributeWriter", "Выполнение 32 генерируемых пар POP HL и LD (nn),HL с восстановлением SP"),
        0x692D: ("BuildAttributeWriter", "Создание развёрнутого писателя, таблицы выборок и двух таблиц экранных атрибутов"),
        0x6964: ("CombineAttributeNibbles", "Объединение восьми младших полубайтов HL с восемью старшими полубайтами BC в 64 атрибута DE"),
        0x6983: ("PresentAttributes", "Ожидание кадра, выбор таблицы #60C0 либо #61C0 и вызов генерируемого писателя"),
        0x69A3: ("BuildPairedPointers", "Запись A пар одинаковых указателей в соседние страницы с шагом BC по значению"),
        0x6AC1: ("InitializeColumnEffect", "Создание обработчика #D000, таблиц выбора столбцов и суммированной текстуры для эффекта"),
        0x6B93: ("DrawLookupTextureFrame", "Ожидание кадра, обновление масштаба и фаз перед формированием текстурного кадра"),
        0x6B9C: ("RenderLookupTexture", "Подготовка табличных фаз, исполнение #9900 и перенос результата через генерируемый код #A800"),
        0x6BBC: ("PresentLookupTexture", "Восстановление SP после #A800, две серии выборок и общий вывод кадра"),
        0x6BE3: ("RunTextureSampler", "Запуск развёрнутого обработчика #9100 со стеком указателей источников"),
        0x6BED: ("NextTextureSampleRow", "Продолжение после #9100, следующий столбец BC и строка источников до восстановления SP"),
        0x6BF6: ("AdvanceTexturePhases", "Обновление трёх фаз и четвёртого смещения по таблице #6400 в операндах текстурного обработчика"),
        0x6C21: ("AdvanceTextureScale", "Начальное нарастание масштаба и последующий циклический выбор из таблицы #6C62"),
        0x6C53: ("SelectTexturePointerRow", "Выбор строки #F000 + 16*A для генерируемого переноса #A800"),
        0x6C9C: ("InitializeLookupEffect", "Создание трёх развёрнутых обработчиков, фазовых таблиц и таблицы указателей эффекта"),
        0x6D6A: ("BuildPhaseTable", "Запись 256 выборок исходной таблицы со сдвигом вправо на два бита и шагом C по индексу"),
        0x6500: ("InitializeIntro", "Перенос завершающего загрузчика, вывод экрана и создание таблиц вступления"),
        0x65B7: ("LoadStation", "Переносимая завершающая стадия, поиск STATIONF.C и чтение #C0 секторов"),
        0x69B6: ("BuildScreenTables", "Построение таблиц адресов экранных строк и зеркальной половины таблицы"),
        0x69FE: ("WriteJump", "Создание инструкции JP DE по адресу HL, HL увеличивается на три"),
        0x6A05: ("WriteIndexJump", "Создание инструкции JP (IX) в генерируемом коде"),
        0x6A0B: ("SelectIntroPage", "Выбор страницы 1 с записью #11 в порт #7FFD"),
        0x6A0D: ("SelectMemoryPage", "Запись A в порт #7FFD, BC получает номер порта"),
        0x6A13: ("WaitInterrupt", "Разрешение прерываний, ожидание HALT и повторный запрет прерываний"),
        0x6A17: ("FillForward", "Заполнение области через начальный байт A и перекрывающееся копирование LDIR"),
        0x6A1E: ("RepeatPattern", "Повторение образца длиной C байт B раз в область DE"),
        0x6A2C: ("AdvanceParameters", "Обновление двух первых слов шестибайтового состояния через временный стек, третье слово сохраняется"),
        0x6A4B: ("RunTimedEffect", "Повторение обработчика HL в течение BC шагов с проверкой клавиши Space"),
        0x6A67: ("FillBitmap", "Заполнение 128 экранных строк байтом C с учётом адресации Spectrum"),
        0x6D8D: ("BuildIntroTexture", "Преобразование текстуры и копирование #1300 байт в страницу 4"),
        0x6DB6: ("BuildMirroredTexture", "Построение отражённой текстуры и перенос результата в страницу 4"),
    },
    "IntroTemplates": {
        0x6722: ("ScrolledSample", "Семибайтовый образец выборки, 64 копии исполняются по адресу #7E00"),
        0x6B5A: ("ColumnSample", "25-байтовый образец выборки и семи вертикальных записей, 64 копии по адресу #D000"),
        0x6D78: ("PointerSample", "Шестибайтовый образец косвенной выборки, 64 копии по адресу #9100"),
        0x6D7E: ("PhaseSum", "15-байтовый образец суммы четырёх таблиц, 256 копий по адресу #9900"),
    },
    "IntroUnpack": {
        0x6E31: ("UnpackScreen", "Распаковка экранного потока после переноса из #8931 в #6E31"),
    },
    "StationBoot": {
        0x4070: ("StartStation", "Загрузка банков карты, музыки, справки, 3D и языка, выбор фона, настройка устройств и запуск цикла станции"),
        0x6300: ("RelocateBootstrap", "Очистка атрибутов и перенос #02B5 байт загрузчика в #4000"),
        0x4000: ("InitializeStation", "Перенос ядра из #65CE в #6322, загрузка банков и создание таблиц"),
    },
    "Station": {
        0xBDA6: ("MeasureTextRun", "Измерение пиксельной ширины текста до CR, LF или разделителя B с продвижением HL"),
        0xBDCA: ("MeasureTextRunSaved", "Измерение пиксельной ширины текста до CR, LF или разделителя B с сохранением HL"),
        0xBFAD: ("RegisterAndFillItem", "Регистрация видимых знакомест элемента и заливка его bitmap с возвратом указателя Flags"),
        0xBEAE: ("RegisterItemCells", "Замена регистрации элемента индексной парой и заполнение видимого прямоугольника кодом владельца"),
        0x9DA6: ("GetCellOwner", "Получение адреса и байта владельца знакоместа по координатам строки и колонки"),
        0x9D96: ("GetPointerOwner", "Преобразование пиксельных координат указателя в знакоместо и чтение его владельца"),
        0xBE91: ("InvalidateItemIndex", "Поиск первой совпавшей индексной пары и запись #FF в её старший байт"),
        0xC233: ("SetupInsetTextWindow", "Настройка внутреннего текстового окна с пиксельными отступами и начальным курсором X=1"),
        0xBFF5: ("FillItemBitmap", "Чтение геометрии интерфейсного элемента, настройка текстового окна и заполнение видимой части bitmap"),
        0xC000: ("FinishItemFill", "Продолжение заполнения интерфейсного элемента, чтение высоты и отсечение прямоугольника"),
        0xC039: ("SetupTextWindow", "Настройка пиксельных размеров и знакового начала текстового окна по координатам знакомест"),
        0xA3FF: ("SaveTextWindow", "Сохранение девяти байтов текстового окна в операндах одноместного восстановителя"),
        0xA436: ("RestoreTextWindow", "Восстановление девяти байтов текстового окна из изменяемых операндов LD A"),
        0x9EED: ("GetItemField", "Вычисление адреса поля шестнадцатибайтовой записи станционного интерфейса"),
        0xC626: ("FillRectangle", "Заполнение прямоугольника знакомест нулевыми или единичными пикселями без отсечения"),
        0xC093: ("DrawBandFrame", "Рисование рамки с выбираемой верхней полосой и горизонтальным разделителем"),
        0xC0C9: ("FinishBandFrame", "Продолжение верхней полосы, средние строки и замыкание нижнего края рамки"),
        0xC436: ("DrawInsetFrame", "Рисование рамки с заполненными верхней и нижней строками, внутренними скосами и пустой серединой"),
        0xBF4E: ("PrepareFrameRaster", "Настройка кодов краёв, обрезка внутренней ширины и табличное вычисление адреса рамки"),
        0xC17B: ("DrawSpanRow", "Запись левого края, заданного числа средних байтов и правого края с переходом на следующую пиксельную строку"),
        0xC165: ("AdvanceClipRow", "Продвижение знакового счётчика строки рамки с проверкой 24 видимых строк знакомест"),
        0xC16F: ("NextCharRow", "Коррекция экранного адреса при переходе после восьми пиксельных строк к следующей строке знакомест"),
        0xC1C0: ("SetOutlinePattern", "Выбор нулевой середины и одиночных боковых пикселей с подавлением краёв по AF'"),
        0xC1CF: ("SetCutoutPattern", "Выбор заполненной середины и краёв с раздельными пропусками по AF'"),
        0xC1DE: ("SetSixBitPattern", "Выбор заполненной середины и шести средних пикселей крайних байтов по AF'"),
        0xC1ED: ("ClearSpanPattern", "Подготовка нулевых байтов левого края, середины и правого края полосы"),
        0xC1F2: ("SetInsetPattern", "Выбор заполненной середины и краёв с двумя внешними пропусками по AF'"),
        0xC21F: ("FillSpanPattern", "Подготовка заполненных байтов левого края, середины и правого края полосы"),
        0xC224: ("SetOutlineCopy", "Исходная копия выбора нулевой середины и одиночных боковых пикселей по AF'"),
        0x6322: ("BuildSpriteLineTable", "Построение адресов строк спрайта с обработкой смещения внутри знакоместа"),
        0x6364: ("ToggleScreenOperands", "Переключение экранной области изменением старших байтов операндов рисования"),
        0x6396: ("SelectRamBank", "Объединение старших пяти битов теневого #7FFD со всем входным A и запись результата в порт"),
        0x639F: ("SelectMemoryPage", "Сохранение теневого #7FFD и переключение страницы с сохранением BC"),
        0x63AA: ("StopMusic", "Остановка музыкального модуля в странице 3 и восстановление IM 1"),
        0x63F1: ("TestMotionParameters", "Объединение четырёх слов параметров в признак нулевого движения"),
        0x9A58: ("EmptyCallback", "Исходный RET для временно отключённых обратных вызовов"),
        0x9A59: ("MainLoop", "Цикл станции, интерпретатор событий, ожидание кадра и обработка пользовательских действий"),
        0x9AEA: ("Interrupt", "Обработчик IM 2, сохранение регистров, обслуживание кадра и музыкального банка"),
        0x9D25: ("RestoreBackground", "Восстановление фона по карте #8600 из восьмибайтовых знакомест банка 3 и атрибутов #D800"),
        0x9C77: ("RebuildInterface", "Очистка рабочих таблиц, упорядочение списка элементов и вызов обработчиков перерисовки"),
        0x9DBA: ("DispatchInterfaceEvent", "Выбор элемента по таблице попадания и переход к его обработчику события"),
        0x9EC4: ("ClearWorkspace", "Обнуление #0300 байт рабочей области начиная с #8600"),
        0x9ED7: ("ResetIndexTable", "Заполнение #0080 байт таблицы #8500 значением #FF"),
        0x9EEB: ("IndexRecord", "Получение адреса шестнадцатибайтовой записи по индексу HL"),
        0x9EFF: ("UnpackResource", "Распаковка ресурса с заголовком, переносом упакованного потока и обработкой ссылок"),
        0xCBA9: ("RestoreInterfaceBounds", "Восстановление X, Y, Width и Height элемента из сохранённых полей +8..+11"),
        0xCC21: ("ActivateInterfaceCallback", "Подготовка элемента и установка изменяемого обработчика обратного вызова"),
    },
    "Text": {
        0xC900: ("GetEquipIndex", "Сложение выбранной строки и смещения списка оснащения, байтовый индекс возвращается в BC"),
        0xC918: ("GetCargoIndex", "Сложение выбранной строки и смещения списка товаров, байтовый индекс возвращается в BC"),
        0xC79C: ("EmitOperator", "Поиск символа бинарной операции и запись адреса её обработчика по альтернативному HL"),
        0xC825: ("CallExpression", "Извлечение левого операнда, обработчика и правого операнда из стека выражений с возвратом результата через PushExpressionWord"),
        0xC6EA: ("ReadDecimal5", "Чтение от одной до пяти ASCII-цифр, десятичное число в HL по модулю 65536"),
        0xC000: ("RunMarketScript", "Выполнение сценария торговли из #CA8F с сохранением исходного SP"),
        0xC00C: ("NextCommand", "Возврат к сохранённому стеку и чтение следующей команды сценария"),
        0xC01B: ("SkipLine", "Пропуск строки до CR и обработка признака завершения"),
        0xC039: ("TestExpression", "Разбор условного выражения после символа вопроса и пропуск невыбранного блока"),
        0xC090: ("ApplyAddFieldOperation", "Выбор режима операции плюс и вызов обработчика выбранного поля сценария"),
        0xC09C: ("ApplyRemoveFieldOperation", "Выбор режима операции минус и вызов обработчика выбранного поля сценария"),
        0xC09F: ("AssignValue", "Разбор присваивания и вызов обработчика выбранного поля"),
        0xC0E7: ("FinishScript", "Завершение интерпретатора с восстановлением первоначального SP"),
        0xC7B6: ("DispatchUnaryField", "Выбор обработчика поля по семи трёхбайтовым записям таблицы #CA4F"),
        0xC7C3: ("DispatchWriteField", "Выбор обработчика записи по семи записям таблицы #CA3A"),
        0xC7D0: ("DispatchReadField", "Выбор обработчика чтения по 36 записям таблицы #C980"),
        0xC7DA: ("DispatchToken", "Поиск токена и косвенная передача управления на адрес из таблицы"),
        0xC7E3: ("FindToken", "Поиск A в B трёхбайтовых записях со смещением на три от HL"),
        0xC7EE: ("ParseFieldSuffix", "Разбор цифрового индекса и суффикса поля, выход через изменяемый переход"),
        0xC1B5: ("ReadCredits", "Чтение кредитов из #984E и помещение слова в стек выражений"),
        0xC057: ("ApplyCondition", "Обработка разделителя условия, продолжение или пропуск блока по значению выражения"),
        0xC080: ("ApplyInverseCondition", "Обработка обратной ветви условия по слову в стеке выражений"),
        0xC0D5: ("BeginBlock", "Обработка открывающей фигурной скобки с переходом к следующей команде"),
        0xC0D8: ("EndBlock", "Обработка закрывающей фигурной скобки с переходом к следующей команде"),
        0xC0DB: ("RecomputeTonnage", "Расчёт занятой грузоподъёмности и сохранение результата в #9850"),
        0xC1B9: ("PushExpressionWord", "Запись DE по указателю HL альтернативного набора и продвижение стека выражений"),
        0xC252: ("PushTrue", "Помещение значения один в стек выражений"),
        0xC257: ("PushFalse", "Помещение нулевого значения в стек выражений"),
        0xC25B: ("ReadEventCode", "Чтение номера события из #983A и помещение в стек выражений"),
        0xC3D5: ("CompareEqual", "Сравнение DE и BC на равенство, логический результат возвращается в DE"),
        0xC3DF: ("MultiplyWithChecks", "Двоичное умножение DE и BC с проверками переноса после сдвигов, часть переполнений сложения не выявляется"),
        0xC488: ("AddSaturated", "Сложение DE и BC с ограничением результата сверху значением #FFFF"),
        0xC491: ("SubtractSaturated", "Вычитание BC из DE с ограничением результата снизу нулём"),
        0xC49C: ("CompareLess", "Беззнаковая проверка DE меньше BC, результат ноль или один в DE"),
        0xC4A6: ("CompareGreater", "Беззнаковая проверка DE больше BC, результат ноль или один в DE"),
        0xC4B1: ("CompareNotGreater", "Беззнаковая проверка DE не больше BC, результат ноль или один в DE"),
        0xC4BC: ("CompareNotLess", "Беззнаковая проверка DE не меньше BC, результат ноль или один в DE"),
        0xC4C6: ("AndWords", "Побитовое AND двух слов DE и BC с результатом в DE"),
        0xC4CD: ("OrWords", "Побитовое OR двух слов DE и BC с результатом в DE"),
        0xC4D4: ("CopyRightOperand", "Возврат правого операнда BC в DE"),
    },
    "Help": {
        0xDB00: ("IndexTextLines", "Создание таблицы указателей максимум на 1024 строки текста"),
        0xDB42: ("PrintIndexedLine", "Получение указателя по индексу HL и передача непустой строки процедуре печати"),
        0xDB57: ("SelectText", "Изменение номера текста в непосредственном операнде инициализатора"),
        0xDB5B: ("FormatNumber", "Печать числа через общий форматировщик и расчёт длины в знакоместах"),
    },
    "Music": {
        0xE6AE: ("SetToneSlideC", "Чтение задержки и шага скольжения тона C, настройка изменяемых операндов и отключение счётчика чередования"),
        0xDB00: ("Initialize", "Начальный вход проигрывателя с адресом модуля #E700"),
        0xDB05: ("PlayFrame", "Кадровый вход проигрывателя, переход к изменяемому диспетчеру #DE1F"),
        0xDB08: ("Stop", "Остановка звука обнулением регистров AY с номерами 13..0"),
        0xDB0A: ("InitializeModule", "Чтение заголовка и относительных указателей PT3, сброс внутренних состояний и регистров AY"),
        0xDB7C: ("ClearAyRegisters", "Запись нуля во все 14 музыкальных регистров AY через порты #FFFD и #BFFD"),
        0xDDCA: ("ReadGateTimingA", "Чтение двух длительностей переключения канала A из потока паттерна"),
        0xDDD2: ("SetGateTimingA", "Настройка двух длительностей канала A и замена JR в #DE90 на LD B,n"),
        0xDE0A: ("ReadGateTimingC", "Чтение двух длительностей переключения канала C из потока паттерна"),
        0xDE12: ("SetGateTimingC", "Установка счётчика и длительностей чередования включённого и выключенного состояния канала C"),
        0xDE1F: ("TickDispatch", "Изменяемый вход музыкального тика, исходный JP выбирает синтез без обновления строки паттерна"),
        0xDF7F: ("AdvancePatternA", "Обновление счётчика нот канала A, перехода позиции и трёх указателей паттернов"),
        0xDFE3: ("RenderChannelA", "Начало кадрового синтеза канала A, сэмпл, орнамент, тон, шум и амплитуда"),
    },
    "ActionBoot": {
        0x42AB: ("GetFileLocation", "Поиск девятибайтового имени, чтение заголовка каталога и возврат числа секторов и начального положения"),
        0x42C6: ("LoadFileToBank", "Загрузка выбранного файла по адресу #C000 в уже подключённый банк"),
        0x42C9: ("LoadFileAtAddress", "Загрузка выбранного файла по адресу HL через TR-DOS, A=3 и C=#0E"),
        0x4306: ("InitializeRandomStates", "Начальное заполнение слов состояний от регистра R и повторных вызовов обработчика #EB72"),
        0x6000: ("RelocateBootstrap", "Подготовка экранов и перенос #01FA байт загрузчика в #4200"),
        0x4200: ("InitializeFlight", "Перенос ядра в #6000, загрузка графических банков и запуск полётного режима"),
        0x4355: ("BuildProjectionTable", "Создание таблицы в #9300 с вычислением через сдвиги и сложение"),
        0x438F: ("BuildReciprocalTable", "Создание двух страниц таблицы через двоичное деление"),
        0x43CF: ("BuildBitmapTables", "Создание таблиц строк и битовых масок для рисования"),
    },
    "Action": {
        0xA82D: ("StartFlight", "Вывод панели из страницы 6 и инициализация полётного режима"),
        0xA859: ("MainLoop", "Повторение процедуры полётного кадра"),
        0xA85E: ("UpdateFrame", "Обработка таймеров, управления, визуальных модулей и игровых объектов"),
        0xAB1B: ("SelectMemoryPage", "Запись A в #7FFD с сохранением BC"),
        0xAB23: ("UnpackResource", "Полётная копия распаковщика ресурсов с обработкой ссылок"),
        0xC000: ("DispatchEdges", "Выбор вершин и обработчика ребра по раздельной таблице младших и старших байтов"),
        0xF729: ("UpdateObjects", "Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний"),
    },
    "ThreeD": {
        0xC000: ("DispatchEdges", "Перебор индексов вершин и вызов обработчиков из таблиц #CF00 и #D000"),
        0xC071: ("NextEdge", "Возврат косвенного обработчика и продолжение перебора рёбер"),
        0xD10A: ("ClearWorkBuffer", "Заполнение #0C00 байт до #8C00 значением #FF через стек с восстановлением SP"),
        0xD12C: ("MultiplySignedScaled", "Знаковое умножение с масштабом 1/128 для коэффициента от -127 до 127, выход через JP (IX)"),
    },
    "Voxel": {
        0xE500: ("RotateBasisVectors", "Последовательное преобразование трёх векторов ориентации #9B00..#9B11 по углам #9B14, #9B12 и #9B13"),
        0xE8A1: ("SignedSeededProduct", "Знаковое табличное произведение с использованием входного IY как младшей части накопителя"),
        0xEC0E: ("ConfigureSmallEffect", "Общий хвост малого эффекта, настройка параметров #0C и #0D перед поиском свободной записи"),
        0xF931: ("Multiply7BitWord", "Умножение младших семи битов A на BC с результатом HL modulo #10000"),
        0xF957: ("Divide7BitFixed", "Деление младших семи битов A на E с восемью дробными битами, подтверждённый делитель 1..128"),
        0xEC00: ("CreateSmallEffect", "Инициализация эффекта с ресурсом #D800 и параметрами #0C, #0C, #0D"),
        0xEC1B: ("CreateLargeEffect", "Инициализация эффекта с ресурсом #C400 и параметрами #14, #14, #08"),
        0xEC33: ("AllocateEffect", "Поиск свободной записи #12 байт по знаку и нулевому признаку в поле +7"),
        0xEC7F: ("ClipSprite", "Отсечение прямоугольника по горизонтали 64 и вертикали 24 с расчётом краевых смещений"),
    },
    "Controls": {
        0xDADE: ("RunTemporaryModule", "Сохранение памяти по банкам, распаковка временного модуля и восстановление полётного кода"),
    },
    "Final": {
        0x6123: ("ReadSpeedKeys", "Изменение счётчика задержки клавишами Q и A с границами 0..100"),
        0x6148: ("HaltFinal", "Выбор страниц и режима IM 0, очистка атрибутов теневого экрана и остановка через DI и HALT"),
        0x61DF: ("BuildDisplayChain", "Создание 24 групп по восемь bitmap-строк и полосе атрибутов с двумя местами вставки синхронизации"),
        0x620E: ("EmitBitmapLine", "Копирование 52-байтового образца переноса строки и обновление четырёх адресов SP"),
        0x6234: ("EmitAttributeRow", "Копирование 23-байтового образца атрибутов и переход к следующему 32-байтовому ряду"),
        0x6296: ("NextBitmapLine", "Переход к следующей пиксельной строке в экранной раскладке Spectrum"),
        0x6000: ("InitializeFinal", "Подготовка трёх экранных банков, таблицы IM 2 и финальной анимации"),
        0x616C: ("Interrupt", "Обработчик прерывания финальной сцены"),
        0x6196: ("PrepareFrame", "Подготовка изменяемой цепочки команд финальной анимации"),
    },
    "FinalTemplates": {
        0x6247: ("BitmapLine", "52-байтовый образец переноса 32 байтов строки через два набора регистров и временный SP"),
        0x627D: ("AttributeRow", "23-байтовый образец заполнения 32 атрибутов байтом из альтернативного A"),
    },
}

REGIONS = {
    "Basic": "машинный запуск внутри BASIC",
    "Intro": "инициализация и эффекты вступления",
    "IntroTemplates": "образцы кода, копируемые и изменяемые при подготовке эффектов вступления",
    "IntroUnpack": "перенесённый распаковщик экрана",
    "StationBoot": "перенос и загрузка станции",
    "Station": "ядро станции и общие экранные процедуры",
    "Text": "интерпретатор языка торговли",
    "Map": "карта звёздных систем",
    "Help": "индексация и печать справочного текста",
    "Music": "музыкальный проигрыватель и модуль",
    "ActionBoot": "загрузка полётного режима",
    "Action": "полётное ядро и его исходная страница 0",
    "ThreeD": "диспетчер и обработчики рёбер",
    "Voxel": "записи и рисование эффектов файла VOXAL, не доказательство воксельного алгоритма",
    "Controls": "временный модуль управления с сохранением банков",
    "Final": "финальная экранная анимация",
    "FinalTemplates": "образцы создаваемого кода bitmap и атрибутов финальной сцены",
}

from GlyphFacts import FUNCTIONS as GLYPH_FUNCTIONS
FUNCTIONS['Station'].update(GLYPH_FUNCTIONS)

from NumberFacts import FUNCTIONS as NUMBER_FUNCTIONS
FUNCTIONS['Station'].update(NUMBER_FUNCTIONS)

from TextStreamFacts import FUNCTIONS as STREAM_FUNCTIONS
FUNCTIONS['Station'].update(STREAM_FUNCTIONS)

from WordFacts import FUNCTIONS as WORD_FUNCTIONS
FUNCTIONS['Station'].update(WORD_FUNCTIONS)

from JustifyFacts import FUNCTIONS as JUSTIFY_FUNCTIONS
FUNCTIONS['Station'].update(JUSTIFY_FUNCTIONS)

from TextSelectFacts import FUNCTIONS as SELECT_FUNCTIONS
FUNCTIONS['Station'].update(SELECT_FUNCTIONS)

from PaginationFacts import FUNCTIONS as PAGINATION_FUNCTIONS
FUNCTIONS['Station'].update(PAGINATION_FUNCTIONS)

from InnerFrameFacts import FUNCTIONS as INNER_FUNCTIONS
FUNCTIONS['Station'].update(INNER_FUNCTIONS)

from CenteredItemFacts import FUNCTIONS as CENTERED_FUNCTIONS
FUNCTIONS['Station'].update(CENTERED_FUNCTIONS)

from CaptionItemFacts import FUNCTIONS as CAPTION_FUNCTIONS
FUNCTIONS['Station'].update(CAPTION_FUNCTIONS)

from DrawAdapterFacts import FUNCTIONS as ADAPTER_FUNCTIONS
FUNCTIONS['Station'].update(ADAPTER_FUNCTIONS)

from ItemRectFacts import FUNCTIONS as RECT_FUNCTIONS
FUNCTIONS['Station'].update(RECT_FUNCTIONS)

from BandModeFacts import FUNCTIONS as BAND_MODE_FUNCTIONS
FUNCTIONS['Station'].update(BAND_MODE_FUNCTIONS)

from DrawListFacts import FUNCTIONS as DRAW_LIST_FUNCTIONS
FUNCTIONS['Station'].update(DRAW_LIST_FUNCTIONS)

from MoveDrawFacts import FUNCTIONS as MOVE_DRAW_FUNCTIONS
FUNCTIONS['Station'].update(MOVE_DRAW_FUNCTIONS)

from BoundsFacts import FUNCTIONS as BOUNDS_FUNCTIONS
FUNCTIONS['Station'].update(BOUNDS_FUNCTIONS)

from PointerFacts import FUNCTIONS as POINTER_FUNCTIONS
FUNCTIONS["Station"].update(POINTER_FUNCTIONS)

from ToggleFacts import FUNCTIONS as TOGGLE_FUNCTIONS
FUNCTIONS["Station"].update(TOGGLE_FUNCTIONS)

from InterfaceStateFacts import FUNCTIONS as INTERFACE_STATE_FUNCTIONS
FUNCTIONS["Station"].update(INTERFACE_STATE_FUNCTIONS)

from CloseItemFacts import FUNCTIONS as CLOSE_FUNCTIONS
FUNCTIONS["Station"].update(CLOSE_FUNCTIONS)

from ActiveItemFacts import FUNCTIONS as ACTIVE_FUNCTIONS
FUNCTIONS["Station"].update(ACTIVE_FUNCTIONS)

from BoundsToggleFacts import FUNCTIONS as BOUNDS_TOGGLE_FUNCTIONS
FUNCTIONS["Station"].update(BOUNDS_TOGGLE_FUNCTIONS)

from XorOutlineFacts import FUNCTIONS as XOR_OUTLINE_FUNCTIONS
FUNCTIONS["Station"].update(XOR_OUTLINE_FUNCTIONS)

from RemoveDrawFacts import FUNCTIONS as REMOVE_DRAW_FUNCTIONS
FUNCTIONS["Station"].update(REMOVE_DRAW_FUNCTIONS)

from TrackGeometryFacts import FUNCTIONS as TRACK_FUNCTIONS
FUNCTIONS["Station"].update(TRACK_FUNCTIONS)

from ScreenUpdateFacts import FUNCTIONS as SCREEN_UPDATE_FUNCTIONS
FUNCTIONS["Station"].update(SCREEN_UPDATE_FUNCTIONS)

from InterfaceActionFacts import FUNCTIONS as INTERFACE_ACTION_FUNCTIONS
FUNCTIONS["Station"].update(INTERFACE_ACTION_FUNCTIONS)

from RepaintChainFacts import FUNCTIONS as REPAINT_FUNCTIONS
FUNCTIONS["Station"].update(REPAINT_FUNCTIONS)

from MouseInputFacts import FUNCTIONS as MOUSE_FUNCTIONS
FUNCTIONS["Station"].update(MOUSE_FUNCTIONS)

from PointerInputFacts import FUNCTIONS as POINTER_INPUT_FUNCTIONS
FUNCTIONS["Station"].update(POINTER_INPUT_FUNCTIONS)

from StationInterruptFacts import FUNCTIONS as STATION_IRQ_FUNCTIONS
FUNCTIONS["Station"].update(STATION_IRQ_FUNCTIONS)

from WindowGraphicsFacts import FUNCTIONS as WINDOW_GRAPHICS_FUNCTIONS
FUNCTIONS["Station"].update(WINDOW_GRAPHICS_FUNCTIONS)

from MatrixKeyFacts import FUNCTIONS as MATRIX_KEY_FUNCTIONS
FUNCTIONS["Station"].update(MATRIX_KEY_FUNCTIONS)

from SettingsLabelFacts import FUNCTIONS as SETTINGS_LABEL_FUNCTIONS
FUNCTIONS["Station"].update(SETTINGS_LABEL_FUNCTIONS)

from PopupFacts import FUNCTIONS as POPUP_FUNCTIONS
FUNCTIONS["Station"].update(POPUP_FUNCTIONS)

from RowSelectionFacts import FUNCTIONS as ROW_SELECTION_FUNCTIONS
FUNCTIONS["Station"].update(ROW_SELECTION_FUNCTIONS)

from SelectionBandFacts import FUNCTIONS as SELECTION_BAND_FUNCTIONS
FUNCTIONS["Map"].update(SELECTION_BAND_FUNCTIONS)

from RowHighlightFacts import FUNCTIONS as ROW_HIGHLIGHT_FUNCTIONS
FUNCTIONS["Station"].update(ROW_HIGHLIGHT_FUNCTIONS)

from RowHoverFacts import FUNCTIONS as ROW_HOVER_FUNCTIONS
FUNCTIONS["Station"].update(ROW_HOVER_FUNCTIONS)

from ContextMenuDrawFacts import FUNCTIONS as CONTEXT_MENU_DRAW_FUNCTIONS
FUNCTIONS["Station"].update(CONTEXT_MENU_DRAW_FUNCTIONS)

from MenuCommandFacts import FUNCTIONS as MENU_COMMAND_FUNCTIONS
FUNCTIONS["Station"].update(MENU_COMMAND_FUNCTIONS)

from BackgroundFacts import FUNCTIONS as BACKGROUND_FUNCTIONS
FUNCTIONS["Station"].update(BACKGROUND_FUNCTIONS)

from RebuildFacts import FUNCTIONS as REBUILD_FUNCTIONS
FUNCTIONS["Station"].update(REBUILD_FUNCTIONS)

from EventDispatchFacts import FUNCTIONS as EVENT_DISPATCH_FUNCTIONS
FUNCTIONS["Station"].update(EVENT_DISPATCH_FUNCTIONS)

from RandomStateFacts import FUNCTIONS as RANDOM_STATE_FUNCTIONS
FUNCTIONS["Station"].update(RANDOM_STATE_FUNCTIONS)

from WorldSignatureFacts import FUNCTIONS as SIGNATURE_FUNCTIONS, MAP_FUNCTIONS as SIGNATURE_MAP_FUNCTIONS
FUNCTIONS["Station"].update(SIGNATURE_FUNCTIONS)
FUNCTIONS["Map"].update(SIGNATURE_MAP_FUNCTIONS)

from MarketFacts import FUNCTIONS as MARKET_FUNCTIONS
FUNCTIONS["Station"].update(MARKET_FUNCTIONS)

from MarketAccessFacts import FUNCTIONS as MARKET_ACCESS_FUNCTIONS
FUNCTIONS["Text"].update(MARKET_ACCESS_FUNCTIONS)

from FieldSuffixFacts import FUNCTIONS as FIELD_SUFFIX_FUNCTIONS
FUNCTIONS["Text"].update(FIELD_SUFFIX_FUNCTIONS)

from WeightedLoadFacts import FUNCTIONS as WEIGHTED_LOAD_FUNCTIONS
FUNCTIONS["Text"].update(WEIGHTED_LOAD_FUNCTIONS)

from MarketFieldFacts import FUNCTIONS as MARKET_FIELD_FUNCTIONS
FUNCTIONS["Text"].update(MARKET_FIELD_FUNCTIONS)

from DelimitedRecordFacts import FUNCTIONS as DELIMITED_RECORD_FUNCTIONS
FUNCTIONS["Text"].update(DELIMITED_RECORD_FUNCTIONS)

from SignatureReturnFacts import FUNCTIONS as SIGNATURE_RETURN_FUNCTIONS
FUNCTIONS["Station"].update(SIGNATURE_RETURN_FUNCTIONS)

from KeyChoiceFacts import FUNCTIONS as KEY_CHOICE_FUNCTIONS
FUNCTIONS["Text"].update(KEY_CHOICE_FUNCTIONS)

from StrideFiveFacts import FUNCTIONS as STRIDE_FIVE_FUNCTIONS
FUNCTIONS["Text"].update(STRIDE_FIVE_FUNCTIONS)

from MembershipFlagsFacts import FUNCTIONS as MEMBERSHIP_FLAGS_FUNCTIONS
FUNCTIONS["Text"].update(MEMBERSHIP_FLAGS_FUNCTIONS)

from ThresholdSetFacts import FUNCTIONS as THRESHOLD_SET_FUNCTIONS
FUNCTIONS["Text"].update(THRESHOLD_SET_FUNCTIONS)

from ActiveNeighborFacts import FUNCTIONS as ACTIVE_NEIGHBOR_FUNCTIONS
FUNCTIONS["Text"].update(ACTIVE_NEIGHBOR_FUNCTIONS)

from CargoFieldFacts import FUNCTIONS as CARGO_FIELD_FUNCTIONS
FUNCTIONS["Text"].update(CARGO_FIELD_FUNCTIONS)

from WeightFieldFacts import FUNCTIONS as WEIGHT_FIELD_FUNCTIONS
FUNCTIONS["Text"].update(WEIGHT_FIELD_FUNCTIONS)

from EntryThresholdFacts import FUNCTIONS as ENTRY_THRESHOLD_FUNCTIONS
FUNCTIONS["Text"].update(ENTRY_THRESHOLD_FUNCTIONS)

from Bank4IndexFacts import FUNCTIONS as BANK4_INDEX_FUNCTIONS
FUNCTIONS["Station"].update(BANK4_INDEX_FUNCTIONS)

from KeyFieldSelectorFacts import FUNCTIONS as KEY_FIELD_SELECTOR_FUNCTIONS
FUNCTIONS["Text"].update(KEY_FIELD_SELECTOR_FUNCTIONS)

from RecordFieldSelectorFacts import FUNCTIONS as RECORD_FIELD_SELECTOR_FUNCTIONS
FUNCTIONS["Text"].update(RECORD_FIELD_SELECTOR_FUNCTIONS)

from ExpressionPushFacts import FUNCTIONS as EXPRESSION_PUSH_FUNCTIONS
FUNCTIONS["Text"].update(EXPRESSION_PUSH_FUNCTIONS)

from MultiplyFacts import FUNCTIONS as MULTIPLY_FUNCTIONS
FUNCTIONS["Text"].update(MULTIPLY_FUNCTIONS)

from NumericFieldFacts import FUNCTIONS as NUMERIC_FIELD_FUNCTIONS
FUNCTIONS["Text"].update(NUMERIC_FIELD_FUNCTIONS)

from ScalarWriterFacts import FUNCTIONS as SCALAR_WRITER_FUNCTIONS
FUNCTIONS["Text"].update(SCALAR_WRITER_FUNCTIONS)

from IndexedWriterFacts import FUNCTIONS as INDEXED_WRITER_FUNCTIONS
FUNCTIONS["Text"].update(INDEXED_WRITER_FUNCTIONS)

from AssignmentPipelineFacts import FUNCTIONS as ASSIGNMENT_PIPELINE_FUNCTIONS
FUNCTIONS["Text"].update(ASSIGNMENT_PIPELINE_FUNCTIONS)

from UnaryModeFacts import FUNCTIONS as UNARY_MODE_FUNCTIONS
FUNCTIONS["Text"].update(UNARY_MODE_FUNCTIONS)

from QueuedTextFacts import STATION_FUNCTIONS as QUEUED_TEXT_STATION_FUNCTIONS, TEXT_FUNCTIONS as QUEUED_TEXT_FUNCTIONS
FUNCTIONS["Station"].update(QUEUED_TEXT_STATION_FUNCTIONS)
FUNCTIONS["Text"].update(QUEUED_TEXT_FUNCTIONS)

from ScriptControlFacts import FUNCTIONS as SCRIPT_CONTROL_FUNCTIONS
FUNCTIONS["Text"].update(SCRIPT_CONTROL_FUNCTIONS)

from ExpressionControlFacts import FUNCTIONS as EXPRESSION_CONTROL_FUNCTIONS
FUNCTIONS["Text"].update(EXPRESSION_CONTROL_FUNCTIONS)

from TonnageCommandFacts import FUNCTIONS as TONNAGE_COMMAND_FUNCTIONS
FUNCTIONS["Text"].update(TONNAGE_COMMAND_FUNCTIONS)

from StationTransitionFacts import STATION_FUNCTIONS as TRANSITION_STATION_FUNCTIONS, TEXT_FUNCTIONS as TRANSITION_TEXT_FUNCTIONS
FUNCTIONS["Station"].update(TRANSITION_STATION_FUNCTIONS)
FUNCTIONS["Text"].update(TRANSITION_TEXT_FUNCTIONS)

from StationExitFacts import FUNCTIONS as STATION_EXIT_FUNCTIONS
FUNCTIONS["StationExit"] = STATION_EXIT_FUNCTIONS
REGIONS["StationExit"] = "перенесённый в 4200 выход станции и загрузка ACTION"

from MainLoopControlFacts import FUNCTIONS as MAIN_LOOP_CONTROL_FUNCTIONS
FUNCTIONS["Station"].update(MAIN_LOOP_CONTROL_FUNCTIONS)

from CounterDrawFacts import FUNCTIONS as COUNTER_DRAW_FUNCTIONS
FUNCTIONS["Station"].update(COUNTER_DRAW_FUNCTIONS)

from SignedMultiplyFacts import FUNCTIONS as SIGNED_MULTIPLY_FUNCTIONS
FUNCTIONS["Map"].update(SIGNED_MULTIPLY_FUNCTIONS)

from SeededRootFacts import FUNCTIONS as SEEDED_ROOT_FUNCTIONS
FUNCTIONS["Map"].update(SEEDED_ROOT_FUNCTIONS)

from SignedDivisionFacts import FUNCTIONS as SIGNED_DIVISION_FUNCTIONS
FUNCTIONS["Map"].update(SIGNED_DIVISION_FUNCTIONS)

from CoordinateDistanceFacts import FUNCTIONS as COORDINATE_DISTANCE_FUNCTIONS
FUNCTIONS["Map"].update(COORDINATE_DISTANCE_FUNCTIONS)

from PlayerRankFacts import FUNCTIONS as PLAYER_RANK_FUNCTIONS
FUNCTIONS["Station"].update(PLAYER_RANK_FUNCTIONS)

from MissionOfferFacts import FUNCTIONS as MISSION_OFFER_FUNCTIONS
FUNCTIONS["Station"].update(MISSION_OFFER_FUNCTIONS)

from SystemNameFacts import FUNCTIONS as SYSTEM_NAME_FUNCTIONS
FUNCTIONS["Map"].update(SYSTEM_NAME_FUNCTIONS)

from MissionHoverFacts import FUNCTIONS as MISSION_HOVER_FUNCTIONS
FUNCTIONS["Station"].update(MISSION_HOVER_FUNCTIONS)

from MissionNameDrawFacts import FUNCTIONS as MISSION_NAME_DRAW_FUNCTIONS
FUNCTIONS["Station"].update(MISSION_NAME_DRAW_FUNCTIONS)

from MissionCompletionFacts import FUNCTIONS as MISSION_COMPLETION_FUNCTIONS
FUNCTIONS["Station"].update(MISSION_COMPLETION_FUNCTIONS)

from StatusDrawFacts import FUNCTIONS as STATUS_DRAW_FUNCTIONS
FUNCTIONS["Station"].update(STATUS_DRAW_FUNCTIONS)

from MissionActionFacts import FUNCTIONS as MISSION_ACTION_FUNCTIONS
FUNCTIONS["Station"].update(MISSION_ACTION_FUNCTIONS)

from StoredMapPointFacts import FUNCTIONS as STORED_MAP_POINT_FUNCTIONS
FUNCTIONS["Map"].update(STORED_MAP_POINT_FUNCTIONS)

from MapViewCenterFacts import FUNCTIONS as MAP_VIEW_CENTER_FUNCTIONS
FUNCTIONS["Map"].update(MAP_VIEW_CENTER_FUNCTIONS)

from VariantLabelFacts import FUNCTIONS as VARIANT_LABEL_FUNCTIONS
FUNCTIONS["Map"].update(VARIANT_LABEL_FUNCTIONS)

from MapSectorTableFacts import FUNCTIONS as MAP_SECTOR_TABLE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_SECTOR_TABLE_FUNCTIONS)

from MapScreenTableFacts import FUNCTIONS as MAP_SCREEN_TABLE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_SCREEN_TABLE_FUNCTIONS)

from MapPointMarkerFacts import FUNCTIONS as MAP_POINT_MARKER_FUNCTIONS
FUNCTIONS["Map"].update(MAP_POINT_MARKER_FUNCTIONS)

from VariantResourceFacts import FUNCTIONS as VARIANT_RESOURCE_FUNCTIONS
FUNCTIONS["Map"].update(VARIANT_RESOURCE_FUNCTIONS)

from SecondaryPointOrderFacts import FUNCTIONS as SECONDARY_POINT_ORDER_FUNCTIONS
FUNCTIONS["Map"].update(SECONDARY_POINT_ORDER_FUNCTIONS)

from RasterPreparationFacts import FUNCTIONS as RASTER_PREPARATION_FUNCTIONS
FUNCTIONS["Map"].update(RASTER_PREPARATION_FUNCTIONS)

from MapPointOutcodeFacts import FUNCTIONS as MAP_POINT_OUTCODE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_POINT_OUTCODE_FUNCTIONS)

from ClipProductFacts import FUNCTIONS as CLIP_PRODUCT_FUNCTIONS
FUNCTIONS["Map"].update(CLIP_PRODUCT_FUNCTIONS)

from ClipIntersectionFacts import FUNCTIONS as CLIP_INTERSECTION_FUNCTIONS
FUNCTIONS["Map"].update(CLIP_INTERSECTION_FUNCTIONS)

from ClipTailFacts import FUNCTIONS as CLIP_TAIL_FUNCTIONS
FUNCTIONS["Map"].update(CLIP_TAIL_FUNCTIONS)

from ArcPreparationFacts import FUNCTIONS as ARC_PREPARATION_FUNCTIONS
FUNCTIONS["Map"].update(ARC_PREPARATION_FUNCTIONS)

from MapLineFacts import FUNCTIONS as MAP_LINE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_LINE_FUNCTIONS)

from MapPointChainFacts import FUNCTIONS as MAP_POINT_CHAIN_FUNCTIONS
FUNCTIONS["Map"].update(MAP_POINT_CHAIN_FUNCTIONS)

from ClipCaseFacts import FUNCTIONS as CLIP_ENTRY_FUNCTIONS
FUNCTIONS["Map"].update(CLIP_ENTRY_FUNCTIONS)

from SumSquares8Facts import FUNCTIONS as SUM_SQUARES8_FUNCTIONS
FUNCTIONS["Map"].update(SUM_SQUARES8_FUNCTIONS)

from MapRasterSetupFacts import FUNCTIONS as MAP_RASTER_SETUP_FUNCTIONS
FUNCTIONS["Map"].update(MAP_RASTER_SETUP_FUNCTIONS)

from MapDistanceMinimumFacts import FUNCTIONS as MAP_DISTANCE_MINIMUM_FUNCTIONS
FUNCTIONS["Map"].update(MAP_DISTANCE_MINIMUM_FUNCTIONS)

from NearestMapVariantFacts import FUNCTIONS as NEAREST_MAP_VARIANT_FUNCTIONS
FUNCTIONS["Map"].update(NEAREST_MAP_VARIANT_FUNCTIONS)

from VisibleMapPointsFacts import FUNCTIONS as VISIBLE_MAP_POINTS_FUNCTIONS
FUNCTIONS["Map"].update(VISIBLE_MAP_POINTS_FUNCTIONS)

from NearestVisiblePointFacts import FUNCTIONS as NEAREST_VISIBLE_POINT_FUNCTIONS
FUNCTIONS["Map"].update(NEAREST_VISIBLE_POINT_FUNCTIONS)

from ArcKernelFacts import FUNCTIONS as ARC_KERNEL_FUNCTIONS
FUNCTIONS["Map"].update(ARC_KERNEL_FUNCTIONS)

from ArcDispatcherFacts import FUNCTIONS as ARC_DISPATCHER_FUNCTIONS
FUNCTIONS["Map"].update(ARC_DISPATCHER_FUNCTIONS)

from MapSceneFacts import FUNCTIONS as MAP_SCENE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_SCENE_FUNCTIONS)

from MapClipCasesFacts import FUNCTIONS as MAP_CLIP_CASE_FUNCTIONS
FUNCTIONS["Map"].update(MAP_CLIP_CASE_FUNCTIONS)

from AnimatedVariantFacts import FUNCTIONS as ANIMATED_VARIANT_FUNCTIONS
FUNCTIONS["Map"].update(ANIMATED_VARIANT_FUNCTIONS)

from VariantCountFacts import FUNCTIONS as VARIANT_COUNT_FUNCTIONS
FUNCTIONS["Station"].update(VARIANT_COUNT_FUNCTIONS)

from ItemContourSwitchFacts import FUNCTIONS as ITEM_CONTOUR_SWITCH_FUNCTIONS
FUNCTIONS["Station"].update(ITEM_CONTOUR_SWITCH_FUNCTIONS)

from PeriodicVariantFacts import FUNCTIONS as PERIODIC_VARIANT_FUNCTIONS
FUNCTIONS["Station"].update(PERIODIC_VARIANT_FUNCTIONS)

from MapPanelFacts import FUNCTIONS as MAP_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(MAP_PANEL_FUNCTIONS)

from ItemMoveGuardFacts import FUNCTIONS as ITEM_MOVE_GUARD_FUNCTIONS
FUNCTIONS["Station"].update(ITEM_MOVE_GUARD_FUNCTIONS)

from MapPanFacts import FUNCTIONS as MAP_PAN_FUNCTIONS
FUNCTIONS["Station"].update(MAP_PAN_FUNCTIONS)

from SystemTraitsFacts import FUNCTIONS as SYSTEM_TRAITS_FUNCTIONS
FUNCTIONS["Station"].update(SYSTEM_TRAITS_FUNCTIONS)

from SystemInfoPanelFacts import FUNCTIONS as SYSTEM_INFO_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(SYSTEM_INFO_PANEL_FUNCTIONS)

from MapSelectionPanelFacts import FUNCTIONS as MAP_SELECTION_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(MAP_SELECTION_PANEL_FUNCTIONS)

from MapPanelEventFacts import FUNCTIONS as MAP_PANEL_EVENT_FUNCTIONS
FUNCTIONS["Station"].update(MAP_PANEL_EVENT_FUNCTIONS)

from StoredPointEditFacts import FUNCTIONS as STORED_POINT_EDIT_FUNCTIONS
FUNCTIONS["Station"].update(STORED_POINT_EDIT_FUNCTIONS)

from StoredPointControlFacts import FUNCTIONS as STORED_POINT_CONTROL_FUNCTIONS
FUNCTIONS["Station"].update(STORED_POINT_CONTROL_FUNCTIONS)

from DecodedMessageFacts import FUNCTIONS as DECODED_MESSAGE_FUNCTIONS
FUNCTIONS["Station"].update(DECODED_MESSAGE_FUNCTIONS)

from FinalExitFacts import FUNCTIONS as FINAL_EXIT_FUNCTIONS
FUNCTIONS["StationFinalExit"]=FINAL_EXIT_FUNCTIONS
REGIONS["StationFinalExit"]="перенесённый в 4000 финальный выход станции и запрос FINALF"

from DecodedPanelFacts import FUNCTIONS as DECODED_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(DECODED_PANEL_FUNCTIONS)

from MessagePanelFacts import FUNCTIONS as MESSAGE_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(MESSAGE_PANEL_FUNCTIONS)

from MarketPanelHelperFacts import FUNCTIONS as MARKET_PANEL_HELPER_FUNCTIONS
FUNCTIONS["Station"].update(MARKET_PANEL_HELPER_FUNCTIONS)

from PanelHoverFacts import FUNCTIONS as PANEL_HOVER_FUNCTIONS
FUNCTIONS["Station"].update(PANEL_HOVER_FUNCTIONS)

from TradeNumericColumnFacts import FUNCTIONS as TRADE_NUMERIC_COLUMN_FUNCTIONS
FUNCTIONS["Station"].update(TRADE_NUMERIC_COLUMN_FUNCTIONS)

from SettingsParserFacts import FUNCTIONS as SETTINGS_PARSER_FUNCTIONS
FUNCTIONS["Station"].update(SETTINGS_PARSER_FUNCTIONS)

from ScrollBodyClearFacts import FUNCTIONS as SCROLL_BODY_CLEAR_FUNCTIONS
FUNCTIONS["Station"].update(SCROLL_BODY_CLEAR_FUNCTIONS)

from ScrollWindowFacts import FUNCTIONS as SCROLL_WINDOW_FUNCTIONS
FUNCTIONS["Station"].update(SCROLL_WINDOW_FUNCTIONS)

from TradePanelFacts import FUNCTIONS as TRADE_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(TRADE_PANEL_FUNCTIONS)

from ControlPanelGroupFacts import FUNCTIONS as CONTROL_PANEL_GROUP_FUNCTIONS
FUNCTIONS["Station"].update(CONTROL_PANEL_GROUP_FUNCTIONS)

from D3DClipFacts import FUNCTIONS as D3D_CLIP_FUNCTIONS
FUNCTIONS.setdefault("D3D", {}).update(D3D_CLIP_FUNCTIONS)

from D3DThirdFacts import FUNCTIONS as D3D_THIRD_FUNCTIONS
FUNCTIONS["D3D"].update(D3D_THIRD_FUNCTIONS)

from SpriteLineTableFacts import FUNCTIONS as SPRITE_LINE_TABLE_FUNCTIONS
FUNCTIONS["Station"].update(SPRITE_LINE_TABLE_FUNCTIONS)

from D3DSetupFacts import FUNCTIONS as D3D_SETUP_FUNCTIONS
FUNCTIONS["D3D"].update(D3D_SETUP_FUNCTIONS)

from PreviewFaceFillFacts import FUNCTIONS as PREVIEW_FACE_FILL_FUNCTIONS
FUNCTIONS["Station"].update(PREVIEW_FACE_FILL_FUNCTIONS)

from D3DDescriptionFacts import FUNCTIONS as D3D_DESCRIPTION_FUNCTIONS
FUNCTIONS["D3D"].update(D3D_DESCRIPTION_FUNCTIONS)

from D3DPriceFacts import FUNCTIONS as D3D_PRICE_FUNCTIONS
FUNCTIONS["D3D"].update(D3D_PRICE_FUNCTIONS)

from ModelListPanelFacts import FUNCTIONS as MODEL_LIST_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(MODEL_LIST_PANEL_FUNCTIONS)

from DescriptionBankFacts import FUNCTIONS as DESCRIPTION_BANK_FUNCTIONS
FUNCTIONS["Station"].update(DESCRIPTION_BANK_FUNCTIONS)

from DescriptionPanelFacts import FUNCTIONS as DESCRIPTION_PANEL_FUNCTIONS
FUNCTIONS["Station"].update(DESCRIPTION_PANEL_FUNCTIONS)

from DescriptionActionFacts import FUNCTIONS as DESCRIPTION_ACTION_FUNCTIONS
FUNCTIONS["Station"].update(DESCRIPTION_ACTION_FUNCTIONS)

from PreviewHoverFacts import FUNCTIONS as PREVIEW_HOVER_FUNCTIONS
FUNCTIONS["Station"].update(PREVIEW_HOVER_FUNCTIONS)

from PreviewActionFacts import FUNCTIONS as PREVIEW_ACTION_FUNCTIONS
FUNCTIONS["Station"].update(PREVIEW_ACTION_FUNCTIONS)

from PreviewMultiplyFacts import FUNCTIONS as PREVIEW_MULTIPLY_FUNCTIONS
FUNCTIONS["D3D"].update(PREVIEW_MULTIPLY_FUNCTIONS)

from PreviewTransformFacts import FUNCTIONS as PREVIEW_TRANSFORM_FUNCTIONS
FUNCTIONS["D3D"].update(PREVIEW_TRANSFORM_FUNCTIONS)
