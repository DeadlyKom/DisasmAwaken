# Реестр исходных фрагментов

Число файловых фрагментов не равно числу логических процедур. Фрагмент
может содержать общий хвост, дополнительный вход или продолжение после
косвенного вызова. Статус Unknown означает неустановленное назначение,
его нельзя считать выполненным семантическим разбором.

| Регион | Фрагментов | Описано | Подробности |
| --- | ---: | ---: | --- |
| Basic | 1 | 1 | [Факты](FunctionDetails/Basic.md) |
| Intro | 42 | 42 | [Факты](FunctionDetails/Intro.md) |
| IntroTemplates | 4 | 4 | [Факты](FunctionDetails/IntroTemplates.md) |
| IntroUnpack | 1 | 1 | [Факты](FunctionDetails/IntroUnpack.md) |
| StationBoot | 3 | 3 | [Факты](FunctionDetails/StationBoot.md) |
| StationExit | 1 | 1 | [Факты](FunctionDetails/StationExit.md) |
| StationFinalExit | 1 | 1 | [Факты](FunctionDetails/StationFinalExit.md) |
| Station | 423 | 423 | [Факты](FunctionDetails/Station.md) |
| Text | 126 | 126 | [Факты](FunctionDetails/Text.md) |
| D3D | 70 | 70 | [Факты](FunctionDetails/D3D.md) |
| Map | 89 | 89 | [Факты](FunctionDetails/Map.md) |
| Help | 4 | 4 | [Факты](FunctionDetails/Help.md) |
| Music | 49 | 49 | [Факты](FunctionDetails/Music.md) |
| ActionBoot | 9 | 9 | [Факты](FunctionDetails/ActionBoot.md) |
| Action | 178 | 81 | [Факты](FunctionDetails/Action.md) |
| ThreeD | 98 | 75 | [Факты](FunctionDetails/ThreeD.md) |
| Voxel | 9 | 9 | [Факты](FunctionDetails/Voxel.md) |
| Controls | 67 | 1 | [Факты](FunctionDetails/Controls.md) |
| Final | 9 | 9 | [Факты](FunctionDetails/Final.md) |
| FinalTemplates | 2 | 2 | [Факты](FunctionDetails/FinalTemplates.md) |

Все фрагменты:

| Вход | Исходник | Назначение |
| --- | --- | --- |
| #AC74 | [Station.PrintPlayerRank](../Source/Station/PrintPlayerRank.asm) | Печать ранга по счётчику и шести порогам |
| #4200 | [StationExit.LoadAction](../Source/StationExit/LoadAction.asm) | Перенесённый выход станции, запрос ACTION и передача контекста |
| #5CD1 | [Basic.ReadIntroSectors](../Source/Basic/ReadIntroSectors.asm) | Чтение 44 физических секторов через TR-DOS с возвратом на #6500 |
| #6500 | [Intro.InitializeIntro](../Source/Intro/InitializeIntro.asm) | Перенос завершающего загрузчика, вывод экрана и создание таблиц вступления |
| #65B7 | [Intro.LoadStation](../Source/Intro/LoadStation.asm) | Переносимая завершающая стадия, поиск STATIONF.C и чтение #C0 секторов |
| #661E | [Intro.DrawFinalTextureFrame](../Source/Intro/DrawFinalTextureFrame.asm) | Настройка смещения и параметров последнего текстурного эффекта вступления |
| #6638 | [Intro.BuildAlternatingTexture](../Source/Intro/BuildAlternatingTexture.asm) | Построение текстуры с чередованием исходного байта и байта, уменьшенного в четыре раза, копия в банк 6 |
| #66A3 | [Intro.DrawScrolledTexture](../Source/Intro/DrawScrolledTexture.asm) | Обновление двух смещений modulo 64, выбор строки текстуры и вывод двух половин кадра |
| #66E2 | [Intro.SampleTextureRows](../Source/Intro/SampleTextureRows.asm) | Выборка 16 строк текстуры через генерируемый обработчик в #7E00 и временный SP |
| #66F3 | [Intro.NextSampledRow](../Source/Intro/NextSampledRow.asm) | Продолжение генерируемого обработчика, переход к следующей строке и восстановление SP |
| #66FB | [Intro.InitializeScrolledTexture](../Source/Intro/InitializeScrolledTexture.asm) | Создание 64 развёрнутых выборок по шаблону #6722, подготовка текстуры и экранной раскладки |
| #6729 | [Intro.ExpandTextureRows](../Source/Intro/ExpandTextureRows.asm) | Добавление IXL к 4096 байтам банка 4 и четырёхкратное повторение каждой 64-байтовой строки |
| #6757 | [Intro.CopyTextureToBank](../Source/Intro/CopyTextureToBank.asm) | Копирование #4000 байт из #8000 в окно текущего банка #C000 |
| #6763 | [Intro.BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | Построение двухбайтовой таблицы выборок по координатам из #6400 и заполнение её пропусков |
| #67F1 | [Intro.PresentInterlacedFrame](../Source/Intro/PresentInterlacedFrame.asm) | Чередование двух раскладок, синхронизация с кадром и перенос данных текстуры в экран |
| #6827 | [Intro.ScatterTextureToScreen](../Source/Intro/ScatterTextureToScreen.asm) | Копирование 38 строк по 32 байта, адреса источников берутся из временного стека |
| #68A4 | [Intro.RunAttributeWriter](../Source/Intro/RunAttributeWriter.asm) | Выполнение 32 генерируемых пар POP HL и LD (nn),HL с восстановлением SP |
| #692D | [Intro.BuildAttributeWriter](../Source/Intro/BuildAttributeWriter.asm) | Создание развёрнутого писателя, таблицы выборок и двух таблиц экранных атрибутов |
| #6964 | [Intro.CombineAttributeNibbles](../Source/Intro/CombineAttributeNibbles.asm) | Объединение восьми младших полубайтов HL с восемью старшими полубайтами BC в 64 атрибута DE |
| #6983 | [Intro.PresentAttributes](../Source/Intro/PresentAttributes.asm) | Ожидание кадра, выбор таблицы #60C0 либо #61C0 и вызов генерируемого писателя |
| #69A3 | [Intro.BuildPairedPointers](../Source/Intro/BuildPairedPointers.asm) | Запись A пар одинаковых указателей в соседние страницы с шагом BC по значению |
| #69B6 | [Intro.BuildScreenTables](../Source/Intro/BuildScreenTables.asm) | Построение таблиц адресов экранных строк и зеркальной половины таблицы |
| #69FE | [Intro.WriteJump](../Source/Intro/WriteJump.asm) | Создание инструкции JP DE по адресу HL, HL увеличивается на три |
| #6A05 | [Intro.WriteIndexJump](../Source/Intro/WriteIndexJump.asm) | Создание инструкции JP (IX) в генерируемом коде |
| #6A0B | [Intro.SelectIntroPage](../Source/Intro/SelectIntroPage.asm) | Выбор страницы 1 с записью #11 в порт #7FFD |
| #6A0D | [Intro.SelectMemoryPage](../Source/Intro/SelectMemoryPage.asm) | Запись A в порт #7FFD, BC получает номер порта |
| #6A13 | [Intro.WaitInterrupt](../Source/Intro/WaitInterrupt.asm) | Разрешение прерываний, ожидание HALT и повторный запрет прерываний |
| #6A17 | [Intro.FillForward](../Source/Intro/FillForward.asm) | Заполнение области через начальный байт A и перекрывающееся копирование LDIR |
| #6A1E | [Intro.RepeatPattern](../Source/Intro/RepeatPattern.asm) | Повторение образца длиной C байт B раз в область DE |
| #6A2C | [Intro.AdvanceParameters](../Source/Intro/AdvanceParameters.asm) | Обновление двух первых слов шестибайтового состояния через временный стек, третье слово сохраняется |
| #6A4B | [Intro.RunTimedEffect](../Source/Intro/RunTimedEffect.asm) | Повторение обработчика HL в течение BC шагов с проверкой клавиши Space |
| #6A67 | [Intro.FillBitmap](../Source/Intro/FillBitmap.asm) | Заполнение 128 экранных строк байтом C с учётом адресации Spectrum |
| #6AC1 | [Intro.InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | Создание обработчика #D000, таблиц выбора столбцов и суммированной текстуры для эффекта |
| #6B93 | [Intro.DrawLookupTextureFrame](../Source/Intro/DrawLookupTextureFrame.asm) | Ожидание кадра, обновление масштаба и фаз перед формированием текстурного кадра |
| #6B9C | [Intro.RenderLookupTexture](../Source/Intro/RenderLookupTexture.asm) | Подготовка табличных фаз, исполнение #9900 и перенос результата через генерируемый код #A800 |
| #6BBC | [Intro.PresentLookupTexture](../Source/Intro/PresentLookupTexture.asm) | Восстановление SP после #A800, две серии выборок и общий вывод кадра |
| #6BE3 | [Intro.RunTextureSampler](../Source/Intro/RunTextureSampler.asm) | Запуск развёрнутого обработчика #9100 со стеком указателей источников |
| #6BED | [Intro.NextTextureSampleRow](../Source/Intro/NextTextureSampleRow.asm) | Продолжение после #9100, следующий столбец BC и строка источников до восстановления SP |
| #6BF6 | [Intro.AdvanceTexturePhases](../Source/Intro/AdvanceTexturePhases.asm) | Обновление трёх фаз и четвёртого смещения по таблице #6400 в операндах текстурного обработчика |
| #6C21 | [Intro.AdvanceTextureScale](../Source/Intro/AdvanceTextureScale.asm) | Начальное нарастание масштаба и последующий циклический выбор из таблицы #6C62 |
| #6C53 | [Intro.SelectTexturePointerRow](../Source/Intro/SelectTexturePointerRow.asm) | Выбор строки #F000 + 16*A для генерируемого переноса #A800 |
| #6C9C | [Intro.InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | Создание трёх развёрнутых обработчиков, фазовых таблиц и таблицы указателей эффекта |
| #6D6A | [Intro.BuildPhaseTable](../Source/Intro/BuildPhaseTable.asm) | Запись 256 выборок исходной таблицы со сдвигом вправо на два бита и шагом C по индексу |
| #6D8D | [Intro.BuildIntroTexture](../Source/Intro/BuildIntroTexture.asm) | Преобразование текстуры и копирование #1300 байт в страницу 4 |
| #6DB6 | [Intro.BuildMirroredTexture](../Source/Intro/BuildMirroredTexture.asm) | Построение отражённой текстуры и перенос результата в страницу 4 |
| #6722 | [IntroTemplates.ScrolledSample](../Source/IntroTemplates/ScrolledSample.asm) | Семибайтовый образец выборки, 64 копии исполняются по адресу #7E00 |
| #6B5A | [IntroTemplates.ColumnSample](../Source/IntroTemplates/ColumnSample.asm) | 25-байтовый образец выборки и семи вертикальных записей, 64 копии по адресу #D000 |
| #6D78 | [IntroTemplates.PointerSample](../Source/IntroTemplates/PointerSample.asm) | Шестибайтовый образец косвенной выборки, 64 копии по адресу #9100 |
| #6D7E | [IntroTemplates.PhaseSum](../Source/IntroTemplates/PhaseSum.asm) | 15-байтовый образец суммы четырёх таблиц, 256 копий по адресу #9900 |
| #6E31 | [IntroUnpack.UnpackScreen](../Source/IntroUnpack/UnpackScreen.asm) | Распаковка экранного потока после переноса из #8931 в #6E31 |
| #6300 | [StationBoot.RelocateBootstrap](../Source/StationBoot/RelocateBootstrap.asm) | Очистка атрибутов и перенос #02B5 байт загрузчика в #4000 |
| #4000 | [StationBoot.InitializeStation](../Source/StationBoot/InitializeStation.asm) | Перенос ядра из #65CE в #6322, загрузка банков и создание таблиц |
| #4070 | [StationBoot.StartStation](../Source/StationBoot/StartStation.asm) | Загрузка банков карты, музыки, справки, 3D и языка, выбор фона, настройка устройств и запуск цикла станции |
| #6322 | [Station.BuildSpriteLineTable](../Source/Station/BuildSpriteLineTable.asm) | Построение 256 адресов строк и 256 байтовых колонок просмотра без экранного отсечения |
| #6364 | [Station.TogglePreviewFaceFill](../Source/Station/TogglePreviewFaceFill.asm) | Переключение шаблона заполнения семи четырёхугольных и шести треугольных граней по двум опорным заголовкам |
| #6396 | [Station.SelectRamBank](../Source/Station/SelectRamBank.asm) | Объединение старших пяти битов теневого #7FFD со всем входным A и запись результата в порт |
| #639F | [Station.SelectMemoryPage](../Source/Station/SelectMemoryPage.asm) | Сохранение теневого #7FFD и переключение страницы с сохранением BC |
| #63AA | [Station.StopMusic](../Source/Station/StopMusic.asm) | Глушение AY в банке музыки, установка IM 1 и выход через двухсловную CPU-рамку |
| #63C3 | [Station.SuspendPointer](../Source/Station/SuspendPointer.asm) | Запрет периодического обновления указателя с восстановлением его фона |
| #63D8 | [Station.ResumePointer](../Source/Station/ResumePointer.asm) | Рисование указателя с сохранением регистров и разрешением периодического обновления |
| #63F1 | [Station.TestMotionParameters](../Source/Station/TestMotionParameters.asm) | Объединение четырёх слов параметров в признак нулевого движения |
| #640C | [Station.UpdatePointer](../Source/Station/UpdatePointer.asm) | Восстановление старого указателя и рисование нового при ненулевых параметрах движения |
| #6413 | [Station.DrawPointer](../Source/Station/DrawPointer.asm) | Выбор формы и обработчика наведения, сохранение фона и рисование AND/XOR-указателя |
| #6547 | [Station.RestorePointer](../Source/Station/RestorePointer.asm) | Восстановление двух сохранённых байтов каждой видимой строки указателя |
| #658E | [Station.ConfigureMouseButtons](../Source/Station/ConfigureMouseButtons.asm) | Одноразовый выбор соответствия двух кнопок и замена настроечного JR двумя NOP |
| #65A7 | [Station.PollMouse](../Source/Station/PollMouse.asm) | Опрос кнопок и счётчиков мыши, очистка её входных флагов и обновление координат |
| #65C9 | [Station.DecodeMouseButtons](../Source/Station/DecodeMouseButtons.asm) | Преобразование двух младших кнопок в выбранные настройкой байты действия |
| #65D3 | [Station.DecodeThirdButton](../Source/Station/DecodeThirdButton.asm) | Декодирование третьей кнопки перед общим чтением счётчиков |
| #65D8 | [Station.ReadMouseMotion](../Source/Station/ReadMouseMotion.asm) | Разности двух аппаратных счётчиков, удвоение шага и одностороннее насыщение координат |
| #6638 | [Station.PollJoystick](../Source/Station/PollJoystick.asm) | Условный опрос порта #001F с общим накоплением флагов и шагом указателя |
| #6641 | [Station.PollKeys](../Source/Station/PollKeys.asm) | Проверка шести настроенных клавиш и формирование общего байта направлений и действий |
| #6688 | [Station.ApplyPointerInput](../Source/Station/ApplyPointerInput.asm) | Накопление шести независимых флагов и выбор шага по младшим четырём направлениям |
| #66D3 | [Station.CommitPointerInput](../Source/Station/CommitPointerInput.asm) | Запись координат после возврата обработчика выбранного направления |
| #66D8 | [Station.ClearInputFlags](../Source/Station/ClearInputFlags.asm) | Очистка шести накопленных байтов направлений и действий клавиатуры и джойстика |
| #670E | [Station.StepUpLeft](../Source/Station/StepUpLeft.asm) | Ограниченный шаг указателя влево и вверх |
| #671C | [Station.StepDownLeft](../Source/Station/StepDownLeft.asm) | Ограниченный шаг указателя влево и вниз |
| #672A | [Station.StepUpRight](../Source/Station/StepUpRight.asm) | Ограниченный шаг указателя вправо и вверх |
| #673D | [Station.StepDownRight](../Source/Station/StepDownRight.asm) | Ограниченный шаг указателя вправо и вниз |
| #6750 | [Station.StepLeft](../Source/Station/StepLeft.asm) | Ограниченный шаг указателя влево |
| #6757 | [Station.StepRight](../Source/Station/StepRight.asm) | Ограниченный шаг указателя вправо |
| #6762 | [Station.NoPointerMotion](../Source/Station/NoPointerMotion.asm) | Возврат без изменения координат для пустой либо противоречивой комбинации направлений |
| #6763 | [Station.StepUp](../Source/Station/StepUp.asm) | Ограниченный шаг указателя вверх |
| #676A | [Station.StepDown](../Source/Station/StepDown.asm) | Ограниченный шаг указателя вниз |
| #6771 | [Station.HandleShipListHover](../Source/Station/HandleShipListHover.asm) | Хвостовая передача наведения списка моделей кораблей в UpdateShipListHover |
| #6780 | [Station.DropShipDetailPanels](../Source/Station/DropShipDetailPanels.asm) | Отключение периодического просмотра и последовательное удаление пяти связанных панелей |
| #67D0 | [Station.UpdateShipListHover](../Source/Station/UpdateShipListHover.asm) | Обновление XOR-полосы списка Корабли с сохранением номера только по Z=0 |
| #67E0 | [Station.DrawModelListPanel](../Source/Station/DrawModelListPanel.asm) | Рисование списка рыночных либо текущих кораблей и скимеров с обновлением высоты наведения |
| #6837 | [Station.IgnoreModelPreviewHover](../Source/Station/IgnoreModelPreviewHover.asm) | Пустой вход наведения панели 3D-просмотра с хвостовым переходом к возврату |
| #686F | [Station.ReturnModelPreviewHover](../Source/Station/ReturnModelPreviewHover.asm) | Общий пустой возврат наведения панели 3D-просмотра |
| #6877 | [Station.DrawShipPreview](../Source/Station/DrawShipPreview.asm) | Рамка корабельного просмотра, выбор периодического callback, настройка банка 4 и первый кадр |
| #6913 | [Station.HandleModelDescriptionHover](../Source/Station/HandleModelDescriptionHover.asm) | Пустой трёхбайтовый вход наведения панели описания, действие начинается отдельно через Entry+3 |
| #693D | [Station.ReturnModelDescriptionHover](../Source/Station/ReturnModelDescriptionHover.asm) | Возврат без действий из ветви наведения панели описания |
| #6945 | [Station.DrawModelDescriptionPanel](../Source/Station/DrawModelDescriptionPanel.asm) | Рамка и банковая печать выбранного описания с сохранённой начальной строкой |
| #6952 | [Station.PrintModelDescription](../Source/Station/PrintModelDescription.asm) | Банковая печать выбранного описания модели с возвратом в станционный банк |
| #6978 | [Station.HandleHelpTextHover](../Source/Station/HandleHelpTextHover.asm) | Пустая JP-обёртка наведения панели текста справки |
| #69A7 | [Station.IgnoreHelpTextHover](../Source/Station/IgnoreHelpTextHover.asm) | Пустой обработчик наведения текста справки с немедленным RET |
| #69A8 | [Station.DrawHelpText](../Source/Station/DrawHelpText.asm) | Рамка панели справки, повторное индексирование выбранной записи и печать от TopLine |
| #69B8 | [Station.IndexHelpText](../Source/Station/IndexHelpText.asm) | Выбор банка HELP, индексирование LF-записи и сохранение полного числа строк |
| #69CF | [Station.PrintHelpLine](../Source/Station/PrintHelpLine.asm) | Межбанковая печать по индексу таблицы HELP с возвратом банка станции |
| #69DD | [Station.HandleHelpIndexHover](../Source/Station/HandleHelpIndexHover.asm) | Хвостовая передача наведения разделов справки в UpdateIndexListHover |
| #6A4B | [Station.UpdateIndexListHover](../Source/Station/UpdateIndexListHover.asm) | Обновление XOR-полосы списка Индекс с сохранением номера только по Z=0 |
| #6A5B | [Station.DrawHelpContents](../Source/Station/DrawHelpContents.asm) | Рамка списка разделов справки, сброс подсветки и пересчёт числа видимых CR-заголовков |
| #6A7E | [Station.DisableTextWrap](../Source/Station/DisableTextWrap.asm) | Отключение переноса текста, при отказе ширины печататель пропускает остаток строки |
| #6A83 | [Station.HandleEquipmentInfoHover](../Source/Station/HandleEquipmentInfoHover.asm) | Пустая JP-обёртка наведения документации оснащения |
| #6AAE | [Station.IgnoreEquipmentInfoHover](../Source/Station/IgnoreEquipmentInfoHover.asm) | Пустое наведение документации оснащения с немедленным RET |
| #6AB6 | [Station.DrawEquipmentInfo](../Source/Station/DrawEquipmentInfo.asm) | Рамка документации оснащения, поиск и подсчёт LF-текста, печать от TopRow |
| #6AC6 | [Station.UpdateEquipmentInfo](../Source/Station/UpdateEquipmentInfo.asm) | Поиск LF-описания оснащения, сохранение его начала и полного числа визуальных строк |
| #6ADE | [Station.PrintEquipmentInfo](../Source/Station/PrintEquipmentInfo.asm) | Печать сохранённого описания оснащения с байтовым числом пропускаемых строк |
| #6AE9 | [Station.HandleEnvironmentHover](../Source/Station/HandleEnvironmentHover.asm) | Передача наведения среды в обработчик её динамического числа строк |
| #6B8E | [Station.UpdateEnvironmentHover](../Source/Station/UpdateEnvironmentHover.asm) | Обновление XOR-полосы установок среды с сохранением номера только по Z=0 |
| #6BA5 | [Station.DrawEnvironmentPanel](../Source/Station/DrawEnvironmentPanel.asm) | Рамка установок среды, сброс подсветки и сохранение числа обработанных значений |
| #6BBE | [Station.PrintEnvironmentRows](../Source/Station/PrintEnvironmentRows.asm) | CR-подписи установок среды и общий цикл текущих значений со счётчиком в A' |
| #6C00 | [Station.SetupEnvironmentText](../Source/Station/SetupEnvironmentText.asm) | Запрет переноса установок среды и выбор колонки значений X=66 |
| #6C0A | [Station.HandleGalaxyMapHover](../Source/Station/HandleGalaxyMapHover.asm) | Пустая JP-обёртка наведения панели карты галактики |
| #6D43 | [Station.IgnoreGalaxyMapHover](../Source/Station/IgnoreGalaxyMapHover.asm) | Игнорирование наведения панели карты галактики с полным сохранением контекста |
| #6D58 | [Station.DrawMapPanelContents](../Source/Station/DrawMapPanelContents.asm) | Настройка размеров карты, условное построение таблиц и банковое рисование C000 |
| #6DA8 | [Station.DrawMapPanel](../Source/Station/DrawMapPanel.asm) | Рисование полосовой рамки карты, установка трёх запросов и последовательный вход содержимого |
| #6DC2 | [Station.HandleDecodedMessageHover](../Source/Station/HandleDecodedMessageHover.asm) | Передача события наведения пустому обработчику панели расшифровки |
| #6DD3 | [Station.ReturnDecodedMessageHover](../Source/Station/ReturnDecodedMessageHover.asm) | Пустой возврат события наведения панели расшифровки |
| #6DD4 | [Station.DrawDecodedMessagePanel](../Source/Station/DrawDecodedMessagePanel.asm) | Рисование сообщения расшифровки либо перенос финального загрузчика при точном ключе и коде FE |
| #6E76 | [Station.PrintDecodedMessage](../Source/Station/PrintDecodedMessage.asm) | Выбор и печать сообщения расшифровки по числовому полю MessageIndex предложения |
| #6E7F | [Station.HandleQueuedMessageHover](../Source/Station/HandleQueuedMessageHover.asm) | Передача события наведения пустому обработчику уведомления |
| #6E89 | [Station.ReturnQueuedMessageHover](../Source/Station/ReturnQueuedMessageHover.asm) | Пустой возврат события наведения уведомления |
| #6E8A | [Station.DrawQueuedMessagePanel](../Source/Station/DrawQueuedMessagePanel.asm) | Рамка уведомления и вывод выбранной изменяемым операндом строки с выравниванием |
| #6E99 | [Station.HandleItem31](../Source/Station/HandleItem31.asm) | Вход наведения элемента 31, хвостовое обновление подсветки миссии |
| #6F4D | [Station.UpdateMissionRowHover](../Source/Station/UpdateMissionRowHover.asm) | Обновление подсветки двух строк элемента миссии с хранением номера в операнде |
| #6FC5 | [Station.DrawItem31](../Source/Station/DrawItem31.asm) | Рамка элемента цели миссии, сброс строки наведения и печать сформированного имени |
| #6FEE | [Station.HandleTradePanelHover](../Source/Station/HandleTradePanelHover.asm) | Хвостовой вход обновления торговой строки наведения |
| #7044 | [Station.RunTradeEventAndRedraw](../Source/Station/RunTradeEventAndRedraw.asm) | Запись торгового кода события, запуск LANG и обновление статуса и торговой панели |
| #7071 | [Station.DrawTradePanel](../Source/Station/DrawTradePanel.asm) | Рамка и торговые колонки с сохранением числа начатых строк в операнде подсветки |
| #7096 | [Station.DrawTradeNumericColumns](../Source/Station/DrawTradeNumericColumns.asm) | Наименования товаров и четыре числовые колонки с двумя отдельными байтами количества и цены |
| #7154 | [Station.SetMarketTextColumns](../Source/Station/SetMarketTextColumns.asm) | Отключение переноса текста и установка пяти пиксельных позиций торговых колонок |
| #7172 | [Station.HandleEquipmentListHover](../Source/Station/HandleEquipmentListHover.asm) | JP-обёртка наведения оснащения с текущим счётчиком попыток рисователя |
| #7210 | [Station.UpdateEquipmentHover](../Source/Station/UpdateEquipmentHover.asm) | Обновление XOR-полосы оснащения корабля с сохранением номера только по Z=0 |
| #7227 | [Station.DrawEquipmentList](../Source/Station/DrawEquipmentList.asm) | Рамка оснащения, заголовки колонок и сохранение счётчика попыток вывода |
| #724C | [Station.PrintEquipmentRows](../Source/Station/PrintEquipmentRows.asm) | Имена оснащения и четыре параллельные колонки количества, цены, веса и проверки типа корабля |
| #733F | [Station.SetupEquipmentColumns](../Source/Station/SetupEquipmentColumns.asm) | Подготовка четырёх X-колонок оснащения и сохранение характеристики L текущего ключа |
| #741E | [Station.HandleSaveSlotHover](../Source/Station/HandleSaveSlotHover.asm) | Хвостовая передача наведения позиций записи состояния в UpdateToPositionHover |
| #7482 | [Station.UpdateToPositionHover](../Source/Station/UpdateToPositionHover.asm) | Обновление XOR-полосы списка В позицию 1..5 с сохранением номера только по Z=0 |
| #7492 | [Station.DrawSaveSlotPanel](../Source/Station/DrawSaveSlotPanel.asm) | Рамка и пять строк выбора позиции записи, без выполнения дискового протокола |
| #74A7 | [Station.HandleLoadSlotHover](../Source/Station/HandleLoadSlotHover.asm) | Хвостовая передача наведения позиций чтения состояния в UpdateFromPositionHover |
| #750B | [Station.UpdateFromPositionHover](../Source/Station/UpdateFromPositionHover.asm) | Обновление XOR-полосы списка С позиции 1..5 с сохранением номера только по Z=0 |
| #751B | [Station.DrawLoadSlotPanel](../Source/Station/DrawLoadSlotPanel.asm) | Рамка и пять строк выбора позиции чтения, без выполнения дискового протокола |
| #7539 | [Station.HandleItem40](../Source/Station/HandleItem40.asm) | Вход наведения контекстного меню с хвостовым переходом в HoverContextMenu |
| #753C | [Station.ActivateContextMenu](../Source/Station/ActivateContextMenu.asm) | Развилка действия меню после перерисовки и выполнение команды выбранной строки |
| #7573 | [Station.HoverContextMenu](../Source/Station/HoverContextMenu.asm) | Обновление выбранной строки контекстного меню и сохранение результата в операнде |
| #7583 | [Station.DrawItem40](../Source/Station/DrawItem40.asm) | Регистрация и рамка контекстного меню, сброс выделения и печать восьми команд |
| #7599 | [Station.HandleGameSettingsHover](../Source/Station/HandleGameSettingsHover.asm) | Передача наведения игры в обработчик её динамического числа строк |
| #7620 | [Station.UpdateGameSettingsHover](../Source/Station/UpdateGameSettingsHover.asm) | Обновление XOR-полосы установок игры с сохранением номера только по Z=0 |
| #7637 | [Station.DrawGameSettings](../Source/Station/DrawGameSettings.asm) | Рамка установок игры, сброс подсветки и сохранение числа обработанных значений |
| #7650 | [Station.PrintGameSettingsRows](../Source/Station/PrintGameSettingsRows.asm) | CR-подписи игровых клавиш и передача значений в общий цикл среды |
| #766C | [Station.SetupGameSettingsText](../Source/Station/SetupGameSettingsText.asm) | Запрет переноса установок игры и выбор колонки значений X=110 |
| #7676 | [Station.HandleSystemInfoHover](../Source/Station/HandleSystemInfoHover.asm) | Пустая JP-обёртка наведения панели информации о системе |
| #7687 | [Station.IgnoreSystemInfoHover](../Source/Station/IgnoreSystemInfoHover.asm) | Игнорирование наведения панели информации о системе с полным сохранением контекста |
| #7688 | [Station.TryDrawSystemInfo](../Source/Station/TryDrawSystemInfo.asm) | Проверка присутствия панели систем перед последовательным рисованием её содержимого |
| #768F | [Station.DrawSystemInfoPanel](../Source/Station/DrawSystemInfoPanel.asm) | Рисование дальности топлива, расстояния, выбранной и текущей систем с перечнем планет |
| #7838 | [Station.HandleSystemMapHover](../Source/Station/HandleSystemMapHover.asm) | Пустая JP-обёртка наведения панели карты системы |
| #7884 | [Station.IgnoreSystemMapHover](../Source/Station/IgnoreSystemMapHover.asm) | Игнорирование наведения панели карты системы с полным сохранением контекста |
| #788C | [Station.DrawVariantPanel](../Source/Station/DrawVariantPanel.asm) | Рисование полосовой панели, установка периодического callback и подготовка ресурсов вариантов |
| #7948 | [Station.HandleWelcomeHover](../Source/Station/HandleWelcomeHover.asm) | Пустая JP-обёртка наведения панели приветствия |
| #7954 | [Station.IgnoreWelcomeHover](../Source/Station/IgnoreWelcomeHover.asm) | Игнорирование наведения панели приветствия с полным сохранением контекста |
| #7955 | [Station.DrawWelcomePanel](../Source/Station/DrawWelcomePanel.asm) | Вывод приветствия станции, её модели, имени системы и почасовой ставки 5×L |
| #79BD | [Station.InstallShipTradeCallback](../Source/Station/InstallShipTradeCallback.asm) | Установка отложенной цели ConfirmShipModelTrade через общий обработчик активации элемента |
| #79C7 | [Station.ConfirmShipModelTrade](../Source/Station/ConfirmShipModelTrade.asm) | Передача выбранной модели событию LANG и закрытие списка с пятью связанными панелями |
| #7A15 | [Station.DrawItem30](../Source/Station/DrawItem30.asm) | Обёртка рисования элемента 30 через изменяемый индекс и DrawCenteredItem |
| #7A1B | [Station.HandleShipSaleButton](../Source/Station/HandleShipSaleButton.asm) | Установка callback и последовательный вход в SelectSaleMode после общего действия кнопки |
| #7A24 | [Station.SelectSaleMode](../Source/Station/SelectSaleMode.asm) | Выбор продажи собственного корабля либо скимера с возвратом к покупке при типе FF |
| #7A55 | [Station.DrawSaleModeButton](../Source/Station/DrawSaleModeButton.asm) | Центрируемая кнопка продажи с изменяемым индексом FInterfaceItem 28 |
| #7A5B | [Station.HandleShipPurchaseButton](../Source/Station/HandleShipPurchaseButton.asm) | Установка callback и последовательный вход в SelectPurchaseMode после общего действия кнопки |
| #7A64 | [Station.SelectPurchaseMode](../Source/Station/SelectPurchaseMode.asm) | Выбор каталога покупки, сброс строки просмотра и переключение контура кнопок |
| #7A82 | [Station.DrawPurchaseModeButton](../Source/Station/DrawPurchaseModeButton.asm) | Центрируемая кнопка покупки с изменяемым индексом FInterfaceItem 29 |
| #7A88 | [Station.InstallHelpPanelsCallback](../Source/Station/InstallHelpPanelsCallback.asm) | Установка отложенной цели OpenHelpPanels через общий обработчик активации элемента |
| #7A92 | [Station.OpenHelpPanels](../Source/Station/OpenHelpPanels.asm) | Перенос текстовой панели и списка справки в конец рисования с восстановлением их сохранённой геометрии |
| #7A9E | [Station.DrawItem09](../Source/Station/DrawItem09.asm) | Обёртка рисования элемента 9 через изменяемый индекс и DrawCenteredItem |
| #7AA4 | [Station.InstallGalaxyNewsCallback](../Source/Station/InstallGalaxyNewsCallback.asm) | Установка отложенного открытия через OpenGalaxyNewsPanel |
| #7AAE | [Station.OpenGalaxyNewsPanel](../Source/Station/OpenGalaxyNewsPanel.asm) | Перенос панели галактических новостей в конец рисования и восстановление сохранённой геометрии |
| #7AB4 | [Station.DrawItem02](../Source/Station/DrawItem02.asm) | Обёртка рисования элемента 2 через изменяемый индекс и DrawCenteredItem |
| #7ABA | [Station.InstallMapPanelsCallback](../Source/Station/InstallMapPanelsCallback.asm) | Установка отложенного открытия через OpenMapPanelGroup |
| #7AC4 | [Station.OpenMapPanelGroup](../Source/Station/OpenMapPanelGroup.asm) | Подготовка группы из одиннадцати панелей карты с восстановлением геометрии и запросом обновления |
| #7B0B | [Station.DrawItem03](../Source/Station/DrawItem03.asm) | Обёртка рисования элемента 3 через изменяемый индекс и DrawCenteredItem |
| #7B11 | [Station.HandleEquipmentPurchaseButton](../Source/Station/HandleEquipmentPurchaseButton.asm) | Установка callback и последовательный вход в SelectEquipmentPurchase после общего действия кнопки |
| #7B1A | [Station.SelectEquipmentPurchase](../Source/Station/SelectEquipmentPurchase.asm) | Выбор покупки оборудования и переключение контура с продажи на покупку |
| #7B25 | [Station.DrawEquipmentPurchase](../Source/Station/DrawEquipmentPurchase.asm) | Центрируемая кнопка покупки оборудования с изменяемым индексом 37 |
| #7B2B | [Station.HandleEquipmentSaleButton](../Source/Station/HandleEquipmentSaleButton.asm) | Установка callback и последовательный вход в SelectEquipmentSale после общего действия кнопки |
| #7B34 | [Station.SelectEquipmentSale](../Source/Station/SelectEquipmentSale.asm) | Выбор продажи оборудования и переключение контура с покупки на продажу |
| #7B40 | [Station.DrawEquipmentSale](../Source/Station/DrawEquipmentSale.asm) | Центрируемая кнопка продажи оборудования с изменяемым индексом 36 |
| #7B46 | [Station.InstallFlightButtonCallback](../Source/Station/InstallFlightButtonCallback.asm) | Установка пустого callback кнопки с исходной подписью Перелет |
| #7B50 | [Station.EmptyFlightCallback](../Source/Station/EmptyFlightCallback.asm) | Пустой RET callback элемента 21, установленный обработчиком кнопки Перелет |
| #7B51 | [Station.DrawFlightButton](../Source/Station/DrawFlightButton.asm) | Центрируемая кнопка Перелет, исходный текст 40 и изменяемый индекс элемента 21 |
| #7B57 | [Station.HandleStoredPointToggle](../Source/Station/HandleStoredPointToggle.asm) | Подготовка callback переключения A через общий выбор геометрии либо активации |
| #7B61 | [Station.ToggleStoredMapPoint](../Source/Station/ToggleStoredMapPoint.asm) | Удаление выбранного ключа из первого списка либо запись в его первую пустую запись |
| #7BA8 | [Station.DrawStoredPointToggle](../Source/Station/DrawStoredPointToggle.asm) | Рисование элемента переключения первого списка через общий центрированный рисователь |
| #7BB6 | [Station.HandleSecondaryPointToggle](../Source/Station/HandleSecondaryPointToggle.asm) | Подготовка callback переключения B через общий выбор геометрии либо активации |
| #7BC0 | [Station.ToggleSecondaryMapPoint](../Source/Station/ToggleSecondaryMapPoint.asm) | Удаление найденной точки B либо вставка относительно курсора с исходной особенностью сдвига |
| #7C1E | [Station.DrawSecondaryPointToggle](../Source/Station/DrawSecondaryPointToggle.asm) | Рисование элемента переключения второго списка через общий центрированный рисователь |
| #7C5A | [Station.HandleSecondaryClear](../Source/Station/HandleSecondaryClear.asm) | Подготовка callback очистки B через общий выбор геометрии либо активации |
| #7C64 | [Station.ClearSecondaryMapPoints](../Source/Station/ClearSecondaryMapPoints.asm) | Очистка первых байтов второго списка до точного маркера 80 и обновление панелей |
| #7C7E | [Station.DrawItem14](../Source/Station/DrawItem14.asm) | Обёртка рисования элемента 14 через изменяемый индекс и DrawCenteredItem |
| #7C84 | [Station.HandleStoredPointCycle](../Source/Station/HandleStoredPointCycle.asm) | Подготовка callback циклического выбора A через геометрию либо активацию |
| #7C8E | [Station.CycleStoredMapPoint](../Source/Station/CycleStoredMapPoint.asm) | Циклический переход по первому списку с пропуском FF и центрированием выбранного ключа |
| #7CB6 | [Station.DrawItem15](../Source/Station/DrawItem15.asm) | Обёртка рисования элемента 15 через изменяемый индекс и DrawCenteredItem |
| #7CBC | [Station.InstallContractMapCallback](../Source/Station/InstallContractMapCallback.asm) | Установка отложенного центрирования карты кнопкой Контракт |
| #7CC6 | [Station.CenterContractMap](../Source/Station/CenterContractMap.asm) | Выбор четырёхбайтового ключа и центрирование карты контракта с исходными абсолютными чтениями ROM |
| #7CF8 | [Station.DrawContractButton](../Source/Station/DrawContractButton.asm) | Центрируемая кнопка Контракт с исходным текстовым индексом 20 и изменяемым индексом элемента 18 |
| #7CFE | [Station.HandleCurrentMapCenter](../Source/Station/HandleCurrentMapCenter.asm) | Подготовка callback центрирования текущего ключа через геометрию либо активацию |
| #7D08 | [Station.CenterCurrentMapPoint](../Source/Station/CenterCurrentMapPoint.asm) | Чтение двух слов текущего ключа перед общим выбором и центрированием карты |
| #7D24 | [Station.DrawItem17](../Source/Station/DrawItem17.asm) | Обёртка рисования элемента 17 через изменяемый индекс и DrawCenteredItem |
| #7D2A | [Station.HandleSecondaryCursor](../Source/Station/HandleSecondaryCursor.asm) | Подготовка callback установки курсора B через геометрию либо активацию |
| #7D34 | [Station.SelectSecondaryListCursor](../Source/Station/SelectSecondaryListCursor.asm) | Установка курсора второго списка на первую совпавшую с выбранным ключом запись |
| #7D53 | [Station.DrawItem16](../Source/Station/DrawItem16.asm) | Обёртка рисования элемента 16 через изменяемый индекс и DrawCenteredItem |
| #7D59 | [Station.HandleSellControl](../Source/Station/HandleSellControl.asm) | Подготовка отложенного callback продажи текущей строки |
| #7D63 | [Station.SellCurrentCargo](../Source/Station/SellCurrentCargo.asm) | Продажа текущей строки груза событием 11 с принудительным выбором строки 0 после перерисовки |
| #7D77 | [Station.DrawSellControl](../Source/Station/DrawSellControl.asm) | Рисование управляющего элемента продажи через изменяемый индекс 35 |
| #7D7D | [Station.HandleContractsControl](../Source/Station/HandleContractsControl.asm) | Подготовка отложенного callback открытия панелей контракта |
| #7D87 | [Station.OpenContractPanels](../Source/Station/OpenContractPanels.asm) | Восстановление границ и порядка панелей контракта 31, 33, 32 |
| #7D99 | [Station.DrawItem04](../Source/Station/DrawItem04.asm) | Обёртка рисования элемента 4 через изменяемый индекс и DrawCenteredItem |
| #7D9F | [Station.HandleTradeControl](../Source/Station/HandleTradeControl.asm) | Подготовка отложенного callback открытия товарных панелей |
| #7DA9 | [Station.OpenTradePanels](../Source/Station/OpenTradePanels.asm) | Восстановление границ управляющего элемента продажи и товарной панели |
| #7DB5 | [Station.DrawItem05](../Source/Station/DrawItem05.asm) | Обёртка рисования элемента 5 через изменяемый индекс и DrawCenteredItem |
| #7DBB | [Station.HandleEquipmentControl](../Source/Station/HandleEquipmentControl.asm) | Подготовка отложенного callback открытия панелей оснащения |
| #7DC5 | [Station.OpenEquipmentPanels](../Source/Station/OpenEquipmentPanels.asm) | Сброс индекса текста оснащения и восстановление панелей 39, 36, 37, 38 |
| #7DE1 | [Station.DrawItem06](../Source/Station/DrawItem06.asm) | Обёртка рисования элемента 6 через изменяемый индекс и DrawCenteredItem |
| #7DE7 | [Station.HandleShipControl](../Source/Station/HandleShipControl.asm) | Подготовка отложенного callback открытия корабельных панелей |
| #7DF1 | [Station.OpenShipPanels](../Source/Station/OpenShipPanels.asm) | Сброс выбора и восстановление шести корабельных панелей в исходном порядке |
| #7E19 | [Station.DrawShipControl](../Source/Station/DrawShipControl.asm) | Рисование управляющего элемента корабля через изменяемый индекс 7 |
| #7E1F | [Station.ResetShipPanelSelection](../Source/Station/ResetShipPanelSelection.asm) | Сброс режима списка, рамок выбора и первого компонента индекса банка 4 |
| #7E53 | [Station.HandleItem08](../Source/Station/HandleItem08.asm) | Активация элемента 8 и подготовка перенесённого перехода из станции |
| #7F11 | [Station.DrawItem08](../Source/Station/DrawItem08.asm) | Обёртка рисования элемента 8 через изменяемый индекс и DrawCenteredItem |
| #7F17 | [Station.HandleStatusPanelAction](../Source/Station/HandleStatusPanelAction.asm) | Геометрия по входному Z, перенос статусного элемента и условный рисунок с восстановлением AF |
| #7F33 | [Station.RestoreActionAF](../Source/Station/RestoreActionAF.asm) | Снятие сохранённого AF из динамического кадра и возврат внешнему обработчику |
| #7F35 | [Station.DrawItem00](../Source/Station/DrawItem00.asm) | Заливка статусного элемента и вывод полицейского статуса, денег, тоннажа и ранга |
| #9A58 | [Station.EmptyCallback](../Source/Station/EmptyCallback.asm) | Исходный RET для временно отключённых обратных вызовов |
| #9A59 | [Station.MainLoop](../Source/Station/MainLoop.asm) | Цикл станции, начальный и периодический сценарии, сравнение кодов ввода и событий |
| #9AEA | [Station.Interrupt](../Source/Station/Interrupt.asm) | Обслуживание ввода, указателя, музыки и BCD-счётчика с восстановлением CPU-контекста и стека рисователя |
| #9C43 | [Station.MergeActionInputs](../Source/Station/MergeActionInputs.asm) | Объединение четырёх входных байтов с удвоением первой пары по модулю 256 |
| #9C59 | [Station.DisableDrawList](../Source/Station/DisableDrawList.asm) | Отключение обработчиков списка заменой их первого байта на RET |
| #9C68 | [Station.EnableDrawList](../Source/Station/EnableDrawList.asm) | Включение обработчиков списка восстановлением первого байта LD HL,nn |
| #9C77 | [Station.RebuildInterface](../Source/Station/RebuildInterface.asm) | Перестроение станционного интерфейса, изменение порядка, вызов рисователей и восстановление фона |
| #9D25 | [Station.RestoreBackground](../Source/Station/RestoreBackground.asm) | Восстановление свободных и потерявших владельца знакомест из банка 3 с обновлением атрибутов |
| #9D96 | [Station.GetPointerOwner](../Source/Station/GetPointerOwner.asm) | Преобразование пиксельных координат указателя в знакоместо и чтение его владельца |
| #9DA6 | [Station.GetCellOwner](../Source/Station/GetCellOwner.asm) | Получение адреса и байта владельца знакоместа по координатам строки и колонки |
| #9DBA | [Station.DispatchInterfaceEvent](../Source/Station/DispatchInterfaceEvent.asm) | Выбор владельца события, удаление других всплывающих элементов и переход во вход действия обработчика |
| #9E1F | [Station.RemoveOtherPopups](../Source/Station/RemoveOtherPopups.asm) | Удаление обработчиков группы #20 с сохранением исключённого индекса и перезапуском поиска |
| #9E4E | [Station.PrepareContextMenu](../Source/Station/PrepareContextMenu.asm) | Привязка сохранённой позиции контекстного элемента 40 к указателю и запрос перестроения |
| #9E77 | [Station.CloseActiveItem](../Source/Station/CloseActiveItem.asm) | Закрытие активного элемента, перенос в конец списка и вызов завершающего callback |
| #9E97 | [Station.GetItemFrameBit](../Source/Station/GetItemFrameBit.asm) | Чтение бита 0 Flags элемента по индексу в DE с сохранением контекста |
| #9EA5 | [Station.ToggleItemFrame](../Source/Station/ToggleItemFrame.asm) | Переключение бита контура элемента и полная перерисовка с защитой указателя |
| #9EC4 | [Station.ClearWorkspace](../Source/Station/ClearWorkspace.asm) | Обнуление #0300 байт рабочей области начиная с #8600 |
| #9ED7 | [Station.ResetIndexTable](../Source/Station/ResetIndexTable.asm) | Заполнение #0080 байт таблицы #8500 значением #FF |
| #9EEB | [Station.GetItemFlags](../Source/Station/GetItemFlags.asm) | Получение адреса поля Flags элемента через последовательный вход GetItemField |
| #9EED | [Station.GetItemField](../Source/Station/GetItemField.asm) | Вычисление адреса поля шестнадцатибайтовой записи станционного интерфейса |
| #9EFF | [Station.UnpackResource](../Source/Station/UnpackResource.asm) | Распаковка HR-потока со словным битовым резервуаром, LZ-ссылками, тройками и сохранённым шестибайтовым концом |
| #A014 | [Station.RefillPackedBits](../Source/Station/RefillPackedBits.asm) | Чтение очередного слова битового потока из IX с восстановлением счётчика B из C без изменения флагов |
| #A020 | [Station.CopyWindowIcon](../Source/Station/CopyWindowIcon.asm) | Копирование 128 байтов иконки в 32 экранные строки по таблицам адресации |
| #A05B | [Station.FillWindowBody](../Source/Station/FillWindowBody.asm) | Заливка внутреннего тела окна группами восьми строк через таблицу CPU-возвратов |
| #A0C4 | [Station.FillBodyRow](../Source/Station/FillBodyRow.asm) | Развёрнутая запись до 30 байтов одной строки с восстановлением младшего адреса и RET |
| #A116 | [Station.ReadMatrixKey](../Source/Station/ReadMatrixKey.asm) | Ожидание десяти пробуждений HALT и первой нажатой клавиши с табличным кодом |
| #A14A | [Station.LookupMatrixKey](../Source/Station/LookupMatrixKey.asm) | Циклический поиск пары строки и маски с преобразованием позиции в код |
| #A163 | [Station.FormatSettingsLabel](../Source/Station/FormatSettingsLabel.asm) | Замена символов шаблона кодами числовых, N/Y и клавиатурных двухбайтовых настроек |
| #A280 | [Station.GetRowHitData](../Source/Station/GetRowHitData.asm) | Получение PointerY и байтового начала области строк из Y элемента и отступа |
| #A28F | [Station.ClampRowHeight](../Source/Station/ClampRowHeight.asm) | Перевод числа строк в пиксели и ограничение доступной высотой элемента |
| #A2A4 | [Station.GetPointerRow](../Source/Station/GetPointerRow.asm) | Проверка вертикального попадания и получение восьмипиксельной строки указателя |
| #A2B4 | [Station.XorPointerRow](../Source/Station/XorPointerRow.asm) | Проверка PointerY и инверсия соответствующей строки через банк 1 |
| #A2BB | [Station.XorItemRow](../Source/Station/XorItemRow.asm) | Инверсия заданной строки элемента с горизонтальным отсечением через банк 1 |
| #A311 | [Station.UpdateRowHover](../Source/Station/UpdateRowHover.asm) | Обновление XOR-выделения строки верхнего элемента с ограничением высоты |
| #A341 | [Station.UpdatePixelHover](../Source/Station/UpdatePixelHover.asm) | Обновление XOR-выделения строки верхнего элемента по пиксельной высоте |
| #A36E | [Station.PrintAfterCR](../Source/Station/PrintAfterCR.asm) | Пропуск A+1 ограничителей CR и печать следующего текстового потока |
| #A374 | [Station.JustifyAfterLF](../Source/Station/JustifyAfterLF.asm) | Пропуск A+1 ограничителей LF и вывод оставшегося текста с выравниванием |
| #A37A | [Station.PrintAfterLF](../Source/Station/PrintAfterLF.asm) | Пропуск A+1 ограничителей LF и печать следующего текстового потока |
| #A380 | [Station.SkipCrRecords](../Source/Station/SkipCrRecords.asm) | Пропуск A+1 ограничителей CR с восстановлением LF в операнде поиска |
| #A390 | [Station.SkipLfRecords](../Source/Station/SkipLfRecords.asm) | Пропуск A+1 ограничителей из изменяемого операнда, обычно LF |
| #A3A1 | [Station.PrintSystemTraits](../Source/Station/PrintSystemTraits.asm) | Вывод строя, типа экономики и уровня либо двух дефисов для необитаемой и неизвестной системы |
| #A3FF | [Station.SaveTextWindow](../Source/Station/SaveTextWindow.asm) | Сохранение девяти байтов текстового окна в операндах одноместного восстановителя |
| #A436 | [Station.RestoreTextWindow](../Source/Station/RestoreTextWindow.asm) | Восстановление девяти байтов текстового окна из изменяемых операндов LD A |
| #A464 | [Station.DescribeCurrentKey](../Source/Station/DescribeCurrentKey.asm) | Чтение текущего пятибайтового ключа и получение его банковой характеристики |
| #A46E | [Station.DescribeKeyBanked](../Source/Station/DescribeKeyBanked.asm) | Характеристика числового ключа через банк 1 с сохранением AF результата |
| #A480 | [Station.DescribeCurrentKeyForLang](../Source/Station/DescribeCurrentKeyForLang.asm) | Характеристика текущего ключа с возвратом банка языка 6 |
| #A48B | [Station.DescribeKeyForLang](../Source/Station/DescribeKeyForLang.asm) | Характеристика входного ключа с возвратом банка языка 6 |
| #A496 | [Station.EndScreenUpdate](../Source/Station/EndScreenUpdate.asm) | Возобновление указателя и переключение отображения на обновлённый базовый экран |
| #A49F | [Station.BeginScreenUpdate](../Source/Station/BeginScreenUpdate.asm) | Копирование старого экрана в банк 7 перед восстановлением фона указателя и скрытым обновлением |
| #A6C4 | [Station.CheckItemRect](../Source/Station/CheckItemRect.asm) | Проверка неотрицательного начала, экранных границ и минимального размера элемента |
| #A6EA | [Station.IgnoreCounterEvent](../Source/Station/IgnoreCounterEvent.asm) | Пустой обработчик события счётчика, исходный JP во внутренний RET без изменения данных |
| #A6EE | [Station.DrawItem01](../Source/Station/DrawItem01.asm) | Заполнение элемента 1 и вывод восьми разрядов станционного BCD-счётчика |
| #A770 | [Station.HideAllItems](../Source/Station/HideAllItems.asm) | Отключение периодического callback и установка состояния скрытого интерфейса |
| #A781 | [Station.CloseAllItems](../Source/Station/CloseAllItems.asm) | Удаление разрешённых флагами элементов из текущего списка рисования |
| #A7B7 | [Station.RememberItemBounds](../Source/Station/RememberItemBounds.asm) | Копирование текущей геометрии всех записей в SavedX..SavedHeight |
| #A7E0 | [Station.ArrangeAllItems](../Source/Station/ArrangeAllItems.asm) | Восстановление геометрии всех элементов из сохранённых полей |
| #A7E3 | [Station.OpenEnvOptions](../Source/Station/OpenEnvOptions.asm) | Перенос окна установок среды в конец списка и восстановление его геометрии |
| #A7E9 | [Station.OpenGameOptions](../Source/Station/OpenGameOptions.asm) | Перенос окна установок игры в конец списка и восстановление его геометрии |
| #A7EF | [Station.OpenRestoreDialog](../Source/Station/OpenRestoreDialog.asm) | Перенос окна восстановления в конец списка и восстановление его геометрии |
| #A7F5 | [Station.GetSelectedVariantCount](../Source/Station/GetSelectedVariantCount.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #A82D | [Station.CountTextRows](../Source/Station/CountTextRows.asm) | Подсчёт сухих проходов выровненной строки до установленного Carry |
| #A843 | [Station.PrintFromRow](../Source/Station/PrintFromRow.asm) | Пропуск E выровненных строк и печать остатка из заданной позиции курсора |
| #A85F | [Station.QueueTextRow](../Source/Station/QueueTextRow.asm) | Выбор строки текста DrawItem10 и восстановление элемента в списке |
| #A86B | [Station.QueueTextRowForLang](../Source/Station/QueueTextRowForLang.asm) | Подготовка строки текста в банке 0 с возвратом банка языка 6 |
| #A87B | [Station.NextRandom1](../Source/Station/NextRandom1.asm) | Следующее слово независимого трёхбайтового потока 1 |
| #A882 | [Station.NextRandom0](../Source/Station/NextRandom0.asm) | Следующее слово независимого трёхбайтового потока 0 |
| #A889 | [Station.NextRandom4](../Source/Station/NextRandom4.asm) | Следующее слово независимого трёхбайтового потока 4 |
| #A890 | [Station.NextRandom5](../Source/Station/NextRandom5.asm) | Следующее слово независимого трёхбайтового потока 5 |
| #A897 | [Station.NextRandom6](../Source/Station/NextRandom6.asm) | Следующее слово независимого трёхбайтового потока 6 |
| #A89E | [Station.NextRandom2](../Source/Station/NextRandom2.asm) | Следующее слово независимого трёхбайтового потока 2 |
| #A8A5 | [Station.NextRandom3](../Source/Station/NextRandom3.asm) | Следующее слово независимого трёхбайтового потока 3 |
| #A8C1 | [Station.StepRandomState](../Source/Station/StepRandomState.asm) | Шаг трёхбайтового состояния с переносами и возвратом слова в другом наборе регистров |
| #A90D | [Station.ClearMarketRows](../Source/Station/ClearMarketRows.asm) | Обнуление шестидесяти байтов тридцати двухбайтовых записей рынка |
| #A91B | [Station.GenerateMarket](../Source/Station/GenerateMarket.asm) | Генерация запасов, маркеров и цен тридцати двухбайтовых строк рынка |
| #A9F3 | [Station.StepSignatureKey](../Source/Station/StepSignatureKey.asm) | Обновление двух слов рабочего ключа с байтовым смешиванием и XOR-свёрткой |
| #AA1D | [Station.SumBank4Index](../Source/Station/SumBank4Index.asm) | Сумма двух байтов банка 4 с возвратом банка языка 6 |
| #AA33 | [Station.InstallMissionOfferCallback](../Source/Station/InstallMissionOfferCallback.asm) | Установка отложенной цели RefreshMissionOfferPanels через общий обработчик активации элемента |
| #AA3D | [Station.RefreshMissionOfferPanels](../Source/Station/RefreshMissionOfferPanels.asm) | Генерация нового предложения и последовательное обновление цели, условий миссии и статуса |
| #AA4F | [Station.DrawItem33](../Source/Station/DrawItem33.asm) | Обёртка рисования элемента 33 через изменяемый индекс и DrawCenteredItem |
| #AA55 | [Station.HandleContractHover](../Source/Station/HandleContractHover.asm) | Пустая JP-обёртка наведения панели контракта |
| #AA84 | [Station.IgnoreContractHover](../Source/Station/IgnoreContractHover.asm) | Игнорирование наведения панели контракта с полным сохранением контекста |
| #AA85 | [Station.DrawItem32](../Source/Station/DrawItem32.asm) | Вывод условий миссии и однократное завершение с наградой при достижении цели |
| #AC14 | [Station.GenerateMissionOffer](../Source/Station/GenerateMissionOffer.asm) | Генерация координат предложения, требуемого тоннажа и награды по расстоянию |
| #AD35 | [Station.SkipJustifyRow](../Source/Station/SkipJustifyRow.asm) | Пропуск одной выровненной строки через продвижение глифа без пикселей |
| #ADA7 | [Station.PrintTextWord](../Source/Station/PrintTextWord.asm) | Печать до пробела, CR, LF либо отказа с остановкой после переноса по ширине |
| #ADCD | [Station.PrintJustified](../Source/Station/PrintJustified.asm) | Вывод текста с распределением свободной ширины между словами каждой строки |
| #AE2A | [Station.PrintWrapWord](../Source/Station/PrintWrapWord.asm) | Печать до границы слова с отдельным статусом успешного переноса по ширине |
| #AE55 | [Station.AdvanceTextRow](../Source/Station/AdvanceTextRow.asm) | Продвижение относительного текстового курсора на восемь пикселей с байтовым переполнением |
| #AE6B | [Station.GlyphHeightError](../Source/Station/GlyphHeightError.asm) | Возврат кода 2 при достижении относительной высоты текстового окна |
| #AE71 | [Station.GlyphWidthError](../Source/Station/GlyphWidthError.asm) | Возврат кода 3 при переполнении или достижении относительной ширины окна |
| #AE77 | [Station.GlyphOriginXError](../Source/Station/GlyphOriginXError.asm) | Обработка ненулевого старшего байта физического начала глифа по X |
| #AE7F | [Station.GlyphOriginYError](../Source/Station/GlyphOriginYError.asm) | Обработка ненулевого старшего байта физического начала глифа по Y |
| #AE88 | [Station.GlyphBottomError](../Source/Station/GlyphBottomError.asm) | Возврат кода 1 при верхней строке глифа не меньше 185 |
| #AE8D | [Station.DrawGlyph](../Source/Station/DrawGlyph.asm) | Вывод восьмистрочного глифа через таблицу сдвигов и двухчастных переходов экранной раскладки |
| #AF0C | [Station.DrawGlyphShift0](../Source/Station/DrawGlyphShift0.asm) | XOR строк глифа, сдвиг вправо на 0 пикселей, до двух соседних байтов |
| #AF36 | [Station.SplitGlyphShift0](../Source/Station/SplitGlyphShift0.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 0 пикселей, до двух соседних байтов |
| #AF67 | [Station.DrawGlyphShift1](../Source/Station/DrawGlyphShift1.asm) | XOR строк глифа, сдвиг вправо на 1 пикселей, до двух соседних байтов |
| #AFE0 | [Station.SplitGlyphShift1](../Source/Station/SplitGlyphShift1.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 1 пикселей, до двух соседних байтов |
| #B057 | [Station.DrawGlyphEdge1](../Source/Station/DrawGlyphEdge1.asm) | XOR строк глифа, сдвиг вправо на 1 пикселей, только крайний байт экрана |
| #B089 | [Station.SplitGlyphEdge1](../Source/Station/SplitGlyphEdge1.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 1 пикселей, только крайний байт экрана |
| #B0C1 | [Station.DrawGlyphShift2](../Source/Station/DrawGlyphShift2.asm) | XOR строк глифа, сдвиг вправо на 2 пикселей, до двух соседних байтов |
| #B152 | [Station.SplitGlyphShift2](../Source/Station/SplitGlyphShift2.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 2 пикселей, до двух соседних байтов |
| #B1DE | [Station.DrawGlyphEdge2](../Source/Station/DrawGlyphEdge2.asm) | XOR строк глифа, сдвиг вправо на 2 пикселей, только крайний байт экрана |
| #B220 | [Station.SplitGlyphEdge2](../Source/Station/SplitGlyphEdge2.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 2 пикселей, только крайний байт экрана |
| #B266 | [Station.DrawGlyphShift3](../Source/Station/DrawGlyphShift3.asm) | XOR строк глифа, сдвиг вправо на 3 пикселей, до двух соседних байтов |
| #B30F | [Station.SplitGlyphShift3](../Source/Station/SplitGlyphShift3.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 3 пикселей, до двух соседних байтов |
| #B3B0 | [Station.DrawGlyphEdge3](../Source/Station/DrawGlyphEdge3.asm) | XOR строк глифа, сдвиг вправо на 3 пикселей, только крайний байт экрана |
| #B402 | [Station.SplitGlyphEdge3](../Source/Station/SplitGlyphEdge3.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 3 пикселей, только крайний байт экрана |
| #B456 | [Station.DrawGlyphShift4](../Source/Station/DrawGlyphShift4.asm) | XOR строк глифа, сдвиг вправо на 4 пикселей, до двух соседних байтов |
| #B514 | [Station.ReturnGlyph](../Source/Station/ReturnGlyph.asm) | Общий успешный выход и восстановление сохранённого кадра регистров глифа |
| #B521 | [Station.SplitGlyphShift4](../Source/Station/SplitGlyphShift4.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 4 пикселей, до двух соседних байтов |
| #B5D7 | [Station.DrawGlyphEdge4](../Source/Station/DrawGlyphEdge4.asm) | XOR строк глифа, сдвиг вправо на 4 пикселей, только крайний байт экрана |
| #B631 | [Station.SplitGlyphEdge4](../Source/Station/SplitGlyphEdge4.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 4 пикселей, только крайний байт экрана |
| #B68C | [Station.DrawGlyphShift5](../Source/Station/DrawGlyphShift5.asm) | XOR строк глифа, сдвиг вправо на 5 пикселей, до двух соседних байтов |
| #B735 | [Station.SplitGlyphShift5](../Source/Station/SplitGlyphShift5.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 5 пикселей, до двух соседних байтов |
| #B7D6 | [Station.DrawGlyphEdge5](../Source/Station/DrawGlyphEdge5.asm) | XOR строк глифа, сдвиг вправо на 5 пикселей, только крайний байт экрана |
| #B828 | [Station.SplitGlyphEdge5](../Source/Station/SplitGlyphEdge5.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 5 пикселей, только крайний байт экрана |
| #B87C | [Station.DrawGlyphShift6](../Source/Station/DrawGlyphShift6.asm) | XOR строк глифа, сдвиг вправо на 6 пикселей, до двух соседних байтов |
| #B90D | [Station.SplitGlyphShift6](../Source/Station/SplitGlyphShift6.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 6 пикселей, до двух соседних байтов |
| #B999 | [Station.DrawGlyphEdge6](../Source/Station/DrawGlyphEdge6.asm) | XOR строк глифа, сдвиг вправо на 6 пикселей, только крайний байт экрана |
| #B9E3 | [Station.SplitGlyphEdge6](../Source/Station/SplitGlyphEdge6.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 6 пикселей, только крайний байт экрана |
| #BA30 | [Station.DrawGlyphShift7](../Source/Station/DrawGlyphShift7.asm) | XOR строк глифа, сдвиг вправо на 7 пикселей, до двух соседних байтов |
| #BAA9 | [Station.SplitGlyphShift7](../Source/Station/SplitGlyphShift7.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 7 пикселей, до двух соседних байтов |
| #BB20 | [Station.DrawGlyphEdge7](../Source/Station/DrawGlyphEdge7.asm) | XOR строк глифа, сдвиг вправо на 7 пикселей, только крайний байт экрана |
| #BB62 | [Station.SplitGlyphEdge7](../Source/Station/SplitGlyphEdge7.asm) | XOR префикса глифа до следующего знакоместа, сдвиг вправо на 7 пикселей, только крайний байт экрана |
| #BBA8 | [Station.PrintMin4](../Source/Station/PrintMin4.asm) | Вывод старым числовым ядром с дополнением слева минимум до четырёх символов |
| #BBBE | [Station.PrintMin2](../Source/Station/PrintMin2.asm) | Вывод старым числовым ядром с дополнением слева минимум до двух символов |
| #BBD7 | [Station.PrintMin3](../Source/Station/PrintMin3.asm) | Вывод старым числовым ядром с дополнением слева минимум до трёх символов |
| #BC01 | [Station.PrintWord](../Source/Station/PrintWord.asm) | Десятичный вывод беззнакового слова с байтовым бюджетом ведущих нулей |
| #BCAB | [Station.Print4DigitCore](../Source/Station/Print4DigitCore.asm) | Вывод частного тысяч и трёх десятичных разрядов с подавлением ведущих нулей |
| #BD01 | [Station.RecoverTextX](../Source/Station/RecoverTextX.asm) | Продолжение текстового потока после отказа физического X глифа |
| #BD08 | [Station.PrintText](../Source/Station/PrintText.asm) | Вывод байтового текстового потока с управляющими позициями и переносом строки |
| #BDA6 | [Station.MeasureTextRun](../Source/Station/MeasureTextRun.asm) | Измерение пиксельной ширины текста до CR, LF или разделителя B с продвижением HL |
| #BDCA | [Station.MeasureTextRunSaved](../Source/Station/MeasureTextRunSaved.asm) | Измерение пиксельной ширины текста до CR, LF или разделителя B с сохранением HL |
| #BDF0 | [Station.DrawKeyLabel](../Source/Station/DrawKeyLabel.asm) | Вывод одного глифа либо четырёх байтов обозначения Enter, Symbol Shift или Space |
| #BE38 | [Station.MoveItemToTail](../Source/Station/MoveItemToTail.asm) | Поиск обработчика по индексу, перенос к концу списка либо добавление новой обёртки |
| #BE91 | [Station.InvalidateItemIndex](../Source/Station/InvalidateItemIndex.asm) | Поиск первой совпавшей индексной пары и запись #FF в её старший байт |
| #BEAE | [Station.RegisterItemCells](../Source/Station/RegisterItemCells.asm) | Замена регистрации элемента индексной парой и заполнение видимого прямоугольника кодом владельца |
| #BF4E | [Station.PrepareFrameRaster](../Source/Station/PrepareFrameRaster.asm) | Настройка кодов краёв, обрезка внутренней ширины и табличное вычисление адреса рамки |
| #BFAD | [Station.RegisterAndFillItem](../Source/Station/RegisterAndFillItem.asm) | Регистрация видимых знакомест элемента и заливка его bitmap с возвратом указателя Flags |
| #BFF5 | [Station.FillItemBitmap](../Source/Station/FillItemBitmap.asm) | Чтение геометрии интерфейсного элемента, настройка текстового окна и заполнение видимой части bitmap |
| #C000 | [Station.FinishItemFill](../Source/Station/FinishItemFill.asm) | Продолжение заполнения интерфейсного элемента, чтение высоты и отсечение прямоугольника |
| #C039 | [Station.SetupTextWindow](../Source/Station/SetupTextWindow.asm) | Настройка пиксельных размеров и знакового начала текстового окна по координатам знакомест |
| #C084 | [Station.DrawBandSync](../Source/Station/DrawBandSync.asm) | Ожидание пробуждения HALT и рисование полосовой рамки с сохранением HL и альтернативных HL, DE |
| #C093 | [Station.DrawBandFrame](../Source/Station/DrawBandFrame.asm) | Рисование рамки с выбираемой верхней полосой и горизонтальным разделителем |
| #C0C9 | [Station.FinishBandFrame](../Source/Station/FinishBandFrame.asm) | Продолжение верхней полосы, средние строки и замыкание нижнего края рамки |
| #C165 | [Station.AdvanceClipRow](../Source/Station/AdvanceClipRow.asm) | Продвижение знакового счётчика строки рамки с проверкой 24 видимых строк знакомест |
| #C16F | [Station.NextCharRow](../Source/Station/NextCharRow.asm) | Коррекция экранного адреса при переходе после восьми пиксельных строк к следующей строке знакомест |
| #C17B | [Station.DrawSpanRow](../Source/Station/DrawSpanRow.asm) | Запись левого края, заданного числа средних байтов и правого края с переходом на следующую пиксельную строку |
| #C1C0 | [Station.SetOutlinePattern](../Source/Station/SetOutlinePattern.asm) | Выбор нулевой середины и одиночных боковых пикселей с подавлением краёв по AF' |
| #C1CF | [Station.SetCutoutPattern](../Source/Station/SetCutoutPattern.asm) | Выбор заполненной середины и краёв с раздельными пропусками по AF' |
| #C1DE | [Station.SetSixBitPattern](../Source/Station/SetSixBitPattern.asm) | Выбор заполненной середины и шести средних пикселей крайних байтов по AF' |
| #C1ED | [Station.ClearSpanPattern](../Source/Station/ClearSpanPattern.asm) | Подготовка нулевых байтов левого края, середины и правого края полосы |
| #C1F2 | [Station.SetInsetPattern](../Source/Station/SetInsetPattern.asm) | Выбор заполненной середины и краёв с двумя внешними пропусками по AF' |
| #C201 | [Station.SetDeepInset](../Source/Station/SetDeepInset.asm) | Выбор заполненной середины и краёв с тремя внешними пропусками |
| #C210 | [Station.SetInnerOutline](../Source/Station/SetInnerOutline.asm) | Выбор пустой середины и боковых пикселей на два бита от внешнего края |
| #C21F | [Station.FillSpanPattern](../Source/Station/FillSpanPattern.asm) | Подготовка заполненных байтов левого края, середины и правого края полосы |
| #C224 | [Station.SetOutlineCopy](../Source/Station/SetOutlineCopy.asm) | Исходная копия выбора нулевой середины и одиночных боковых пикселей по AF' |
| #C233 | [Station.SetupInsetTextWindow](../Source/Station/SetupInsetTextWindow.asm) | Настройка внутреннего текстового окна с пиксельными отступами и начальным курсором X=1 |
| #C287 | [Station.DrawCaptionItem](../Source/Station/DrawCaptionItem.asm) | Регистрация элемента, полосовая рамка, заголовок и установка курсора содержимого |
| #C2DF | [Station.DrawCenteredItem](../Source/Station/DrawCenteredItem.asm) | Регистрация и рисование рамки элемента с центрированием CR-строк и выравниванием последнего абзаца |
| #C325 | [Station.CenterItemLine](../Source/Station/CenterItemLine.asm) | Внутреннее продолжение центрирования строки и общий выход стекового кадра элемента |
| #C34B | [Station.SetupCenterText](../Source/Station/SetupCenterText.asm) | Настройка окна центрируемого текста с отступами X=3 и Y=4 и нулевым курсором |
| #C39E | [Station.DrawFrameKeepHL](../Source/Station/DrawFrameKeepHL.asm) | Рисование выбранного контура рамки с сохранением исходного HL |
| #C3A4 | [Station.DrawFrameType](../Source/Station/DrawFrameType.asm) | Выбор скосов либо внутреннего контура рамки по биту 0 типа |
| #C436 | [Station.DrawInsetFrame](../Source/Station/DrawInsetFrame.asm) | Рисование рамки с заполненными верхней и нижней строками, внутренними скосами и пустой серединой |
| #C4BE | [Station.XorRectOutline](../Source/Station/XorRectOutline.asm) | Обратимое рисование четырёх граней временного прямоугольника с отсечением |
| #C566 | [Station.XorOutlineRow](../Source/Station/XorOutlineRow.asm) | Инверсия видимой горизонтальной грани через изменяемый JR в развёртку 32 байтов |
| #C5F2 | [Station.XorOutlineColumn](../Source/Station/XorOutlineColumn.asm) | Инверсия вертикальной грани по маске во всех пиксельных строках заданных знакомест |
| #C626 | [Station.FillRectangle](../Source/Station/FillRectangle.asm) | Заполнение прямоугольника знакомест нулевыми или единичными пикселями без отсечения |
| #C85E | [Station.CloseMenuOnRow](../Source/Station/CloseMenuOnRow.asm) | Удаление элемента при совпадении строки указателя и текстового начала |
| #C873 | [Station.DropItemDraw](../Source/Station/DropItemDraw.asm) | Удаление обработчика по индексу с запросом перестроения только при совпадении |
| #C87C | [Station.TrackItemGeometry](../Source/Station/TrackItemGeometry.asm) | Выбор и полный цикл изменения позиции либо размера элемента с XOR-предпросмотром |
| #CA04 | [Station.FinishGeometry](../Source/Station/FinishGeometry.asm) | Запрос перестроения и возврат исходного контекста с Carry после изменения геометрии |
| #CA11 | [Station.MarkGeometry](../Source/Station/MarkGeometry.asm) | Внутренний выход с удалением кадра попадания и запросом перестроения |
| #CA15 | [Station.CancelHitFrame](../Source/Station/CancelHitFrame.asm) | Удаление двух слов кадра попадания перед возвратом без изменения геометрии |
| #CA17 | [Station.ReturnGeometry](../Source/Station/ReturnGeometry.asm) | Возврат исходных регистров и исходного A с очисткой Carry через AND A |
| #CA1F | [Station.ResizeGeometry](../Source/Station/ResizeGeometry.asm) | Внутреннее продолжение изменения размера с ограничениями класса и видимого пересечения |
| #CB1C | [Station.RemoveItemDraw](../Source/Station/RemoveItemDraw.asm) | Удаление первого обработчика с заданным индексом через фиксированный сдвиг 128 байтов |
| #CB52 | [Station.GetLastDraw](../Source/Station/GetLastDraw.asm) | Получение последнего указателя перед ограничителем текущего списка рисования |
| #CB64 | [Station.TestDrawPointer](../Source/Station/TestDrawPointer.asm) | Проверка наличия указателя в текущем списке без изменения исходного HL |
| #CB7F | [Station.RestoreAllBounds](../Source/Station/RestoreAllBounds.asm) | Восстановление первых четырёх полей каждой записи из SavedX..SavedHeight до X=#80 |
| #CBA9 | [Station.RestoreItemBounds](../Source/Station/RestoreItemBounds.asm) | Перенос обработчика в конец списка и восстановление геометрии его элемента |
| #CBE0 | [Station.RepaintAndTrack](../Source/Station/RepaintAndTrack.asm) | Выбор AND A для выхода перерисовки и разрешение обработки младших семи битов селектора |
| #CBEB | [Station.RepaintAndFlag](../Source/Station/RepaintAndFlag.asm) | Выбор SCF для выхода перерисовки с сохранением полного селектора |
| #CBF2 | [Station.RepaintItemCore](../Source/Station/RepaintItemCore.asm) | Закрытие активного элемента, перенос выбранного, скрытая перерисовка и условная интерактивная геометрия |
| #CC21 | [Station.ActivateInterfaceCallback](../Source/Station/ActivateInterfaceCallback.asm) | Сохранение callback и выбор интерактивной геометрии, переключения границ либо активации |
| #CC2C | [Station.FinishItemAction](../Source/Station/FinishItemAction.asm) | Условное завершение действия, выбор активации либо переключения геометрии |
| #CC30 | [Station.ToggleItemBounds](../Source/Station/ToggleItemBounds.asm) | Возврат сохранённой геометрии либо установка исходного большого прямоугольника |
| #CC81 | [Station.ActivateItem](../Source/Station/ActivateItem.asm) | Перенос элемента в конец списка, условная смена активного индекса и установка callback |
| #CCAF | [Station.SetBandFillMode](../Source/Station/SetBandFillMode.asm) | Настройка заполненного либо обычного режима полосовой рамки по биту 0 FillMode |
| #CCD4 | [Station.ResetBandMode](../Source/Station/ResetBandMode.asm) | Восстановление шести исходных операндов обычной полосовой рамки |
| #C000 | [Text.RunMarketScript](../Source/Text/RunMarketScript.asm) | Инициализация интерпретатора и последовательный вход в чтение команд |
| #C00C | [Text.NextCommand](../Source/Text/NextCommand.asm) | Восстановление стека сценария, чтение команды и выбор обработчика |
| #C01B | [Text.SkipLine](../Source/Text/SkipLine.asm) | Пропуск до CR, проверка завершения строки и общий хвост диспетчера |
| #C039 | [Text.TestExpression](../Source/Text/TestExpression.asm) | Вычисление условия слева направо до непотреблённого разделителя ветви |
| #C057 | [Text.ApplyCondition](../Source/Text/ApplyCondition.asm) | Продолжение при ненулевом выражении либо пропуск строки или блока |
| #C080 | [Text.ApplyInverseCondition](../Source/Text/ApplyInverseCondition.asm) | Продолжение при нулевом выражении либо общий пропуск ветви |
| #C08D | [Text.Command2C](../Source/Text/Command2C.asm) | Разделитель команд, хвостовое продолжение интерпретатора |
| #C090 | [Text.ApplyAddFieldOperation](../Source/Text/ApplyAddFieldOperation.asm) | Установка режима 1 и вызов унарного поля перед NextCommand |
| #C09C | [Text.ApplyRemoveFieldOperation](../Source/Text/ApplyRemoveFieldOperation.asm) | Установка режима 0 и вызов унарного поля перед NextCommand |
| #C09F | [Text.AssignValue](../Source/Text/AssignValue.asm) | Присваивание через физическую запись Writer, Operator, Right и возврат к NextCommand |
| #C0D5 | [Text.BeginBlock](../Source/Text/BeginBlock.asm) | Открывающая скобка, хвостовое продолжение интерпретатора |
| #C0D8 | [Text.EndBlock](../Source/Text/EndBlock.asm) | Закрывающая скобка, хвостовое продолжение интерпретатора |
| #C0DB | [Text.RecomputeTonnage](../Source/Text/RecomputeTonnage.asm) | Запись байтовой взвешенной суммы в поле загрузки и продолжение сценария |
| #C0E7 | [Text.FinishScript](../Source/Text/FinishScript.asm) | Возврат вызывающему сценарию через первоначально сохранённый SP |
| #C0EC | [Text.QueueTextAndStopAtLine](../Source/Text/QueueTextAndStopAtLine.asm) | Подготовка строки текста с завершением сценария на следующем CR |
| #C100 | [Text.QueueTextCommand](../Source/Text/QueueTextCommand.asm) | Подготовка строки текста без изменения признака завершения строки |
| #C103 | [Text.Command57](../Source/Text/Command57.asm) | Команда W, установка байта события и вход в станционный переход |
| #C10B | [Text.Command23](../Source/Text/Command23.asm) | Команда решётки, хвостовое продолжение интерпретатора |
| #C10E | [Text.ActivateResourceRecord](../Source/Text/ActivateResourceRecord.asm) | Поиск совпавшего заголовка и запись 1 в ресурс при ненулевом режиме |
| #C177 | [Text.WriteIndexedPMode](../Source/Text/WriteIndexedPMode.asm) | Запись байтового режима по базе #9A1D и десятичному смещению |
| #C181 | [Text.WriteIndexedVMode](../Source/Text/WriteIndexedVMode.asm) | Запись байтового режима по базе #9A1E и десятичному смещению |
| #C189 | [Text.WriteIndexedMMode](../Source/Text/WriteIndexedMMode.asm) | Запись байтового режима по базе #9A32 и десятичному смещению |
| #C191 | [Text.WriteIndexedEMode](../Source/Text/WriteIndexedEMode.asm) | Запись байтового режима по базе #9A41 и десятичному смещению |
| #C199 | [Text.SetPrimarySelection](../Source/Text/SetPrimarySelection.asm) | Выбор первичной записи по индексу банка 4 либо коду FF |
| #C1A7 | [Text.SetSecondarySelection](../Source/Text/SetSecondarySelection.asm) | Выбор вторичной записи по индексу банка 4 либо коду FF |
| #C1B5 | [Text.ReadCredits](../Source/Text/ReadCredits.asm) | Чтение исходного слова #984E и добавление его в стек выражений |
| #C1B9 | [Text.PushExpressionWord](../Source/Text/PushExpressionWord.asm) | Запись DE по указателю HL альтернативного набора и продвижение стека выражений |
| #C1C2 | [Text.ReadFieldLowero](../Source/Text/ReadFieldLowero.asm) | Получение результата через ReadEquipmentWeight и запись слова в стек выражений |
| #C1C8 | [Text.ReadEquipmentWeight](../Source/Text/ReadEquipmentWeight.asm) | Чтение кодированного веса оснащения либо его свойства s или n |
| #C1E6 | [Text.ReadFieldLoweri](../Source/Text/ReadFieldLoweri.asm) | Получение результата через ReadSecondWeight и запись слова в стек выражений |
| #C1EC | [Text.ReadSecondWeight](../Source/Text/ReadSecondWeight.asm) | Чтение кодированного веса второго набора либо его свойства s или n |
| #C201 | [Text.ReadFieldLowerk](../Source/Text/ReadFieldLowerk.asm) | Получение результата через ReadSelectedPrimaryFields и запись слова в стек выражений |
| #C207 | [Text.ReadSelectedPrimaryFields](../Source/Text/ReadSelectedPrimaryFields.asm) | Чтение свойств первого набора по байту выбранной записи |
| #C221 | [Text.ReadFieldLowerr](../Source/Text/ReadFieldLowerr.asm) | Получение результата через ReadSelectedSecondaryFields и запись слова в стек выражений |
| #C227 | [Text.ReadSelectedSecondaryFields](../Source/Text/ReadSelectedSecondaryFields.asm) | Чтение свойств второго набора по байту выбранной записи |
| #C241 | [Text.ReadFieldLowerj](../Source/Text/ReadFieldLowerj.asm) | Добавление байта #9850 в стек выражений через общий байтовый вход |
| #C24C | [Text.ReadFieldUpperJ](../Source/Text/ReadFieldUpperJ.asm) | Добавление байта #9851 в стек выражений |
| #C252 | [Text.PushTrue](../Source/Text/PushTrue.asm) | Добавление логической единицы в стек выражений без изменения F |
| #C257 | [Text.PushFalse](../Source/Text/PushFalse.asm) | Добавление нуля в стек выражений с F=#44 |
| #C25B | [Text.ReadEventCode](../Source/Text/ReadEventCode.asm) | Добавление байтового кода события #983A в стек выражений |
| #C261 | [Text.ReadFieldLoweru](../Source/Text/ReadFieldLoweru.asm) | Добавление байта #984B в стек выражений |
| #C267 | [Text.ReadFieldUpperG](../Source/Text/ReadFieldUpperG.asm) | Получение результата через ReadMarketField и запись слова в стек выражений |
| #C26D | [Text.ReadMarketField](../Source/Text/ReadMarketField.asm) | Чтение количества рынка либо точечного свойства c, s, m |
| #C289 | [Text.ReadFieldUpperO](../Source/Text/ReadFieldUpperO.asm) | Получение результата через CheckEquipmentThreshold и запись слова в стек выражений |
| #C28F | [Text.CheckEquipmentThreshold](../Source/Text/CheckEquipmentThreshold.asm) | Сравнение порога записи оснащения с признаком L текущего ключа |
| #C2B5 | [Text.ReadFieldUpperI](../Source/Text/ReadFieldUpperI.asm) | Получение результата через CheckSecondEntryThreshold и запись слова в стек выражений |
| #C2BB | [Text.CheckSecondEntryThreshold](../Source/Text/CheckSecondEntryThreshold.asm) | Сравнение порога записи второго набора с признаком L текущего ключа |
| #C2D0 | [Text.ReadFieldUpperK](../Source/Text/ReadFieldUpperK.asm) | Получение результата через ReadBank4PrimaryFields и запись слова в стек выражений |
| #C2D6 | [Text.ReadBank4PrimaryFields](../Source/Text/ReadBank4PrimaryFields.asm) | Чтение свойств первого набора по индексу банка 4 |
| #C2EA | [Text.ReadFieldUpperR](../Source/Text/ReadFieldUpperR.asm) | Получение результата через ReadBank4SecondaryFields и запись слова в стек выражений |
| #C2F0 | [Text.ReadBank4SecondaryFields](../Source/Text/ReadBank4SecondaryFields.asm) | Чтение свойств второго набора по индексу банка 4 |
| #C304 | [Text.ReadFieldLowerg](../Source/Text/ReadFieldLowerg.asm) | Получение результата через ReadCargoField и запись слова в стек выражений |
| #C30A | [Text.ReadCargoField](../Source/Text/ReadCargoField.asm) | Чтение первого байта грузовой записи либо её второго байта через суффикс c |
| #C323 | [Text.ReadFieldCode1](../Source/Text/ReadFieldCode1.asm) | Чтение десятичного литерала с возвратом курсора на первую цифру и запись слова выражения |
| #C32C | [Text.ReadFieldCode28](../Source/Text/ReadFieldCode28.asm) | Вычисление скобочного поля с заменой выражения одним словом |
| #C342 | [Text.ReadFieldLowere](../Source/Text/ReadFieldLowere.asm) | Чтение байта по десятичному смещению от #9A42 и добавление в стек выражений |
| #C34D | [Text.ReadFieldLowerm](../Source/Text/ReadFieldLowerm.asm) | Чтение байта по десятичному смещению от #9A33 и добавление в стек выражений |
| #C355 | [Text.ReadFieldLowert](../Source/Text/ReadFieldLowert.asm) | Чтение байта ресурса с сохранёнными счётчиками FF/FE и десятичным смещением |
| #C362 | [Text.ReadFieldLowerp](../Source/Text/ReadFieldLowerp.asm) | Чтение байта ресурса по трём десятичным компонентам |
| #C37D | [Text.ReadFieldUpperL](../Source/Text/ReadFieldUpperL.asm) | Получение результата через ReadCurrentKeyParams и запись слова в стек выражений |
| #C383 | [Text.ReadCurrentKeyParams](../Source/Text/ReadCurrentKeyParams.asm) | Выбор текущего ключа по умолчанию и группы s, c, u |
| #C393 | [Text.ReadFieldLowerl](../Source/Text/ReadFieldLowerl.asm) | Получение результата через ReadOtherKeyParams и запись слова в стек выражений |
| #C399 | [Text.ReadOtherKeyParams](../Source/Text/ReadOtherKeyParams.asm) | Выбор второго ключа по умолчанию и группы s, c, u |
| #C3A9 | [Text.ReadFieldUpperY](../Source/Text/ReadFieldUpperY.asm) | Получение результата через ReadCurrentKeyCodes и запись слова в стек выражений |
| #C3AF | [Text.ReadCurrentKeyCodes](../Source/Text/ReadCurrentKeyCodes.asm) | Выбор текущего ключа по умолчанию и группы p, g |
| #C3BF | [Text.ReadFieldLowery](../Source/Text/ReadFieldLowery.asm) | Получение результата через ReadOtherKeyCodes и запись слова в стек выражений |
| #C3C5 | [Text.ReadOtherKeyCodes](../Source/Text/ReadOtherKeyCodes.asm) | Выбор второго ключа по умолчанию и группы p, g |
| #C3D5 | [Text.CompareEqual](../Source/Text/CompareEqual.asm) | Сравнение DE и BC на равенство, логический результат возвращается в DE |
| #C3DF | [Text.MultiplyWithChecks](../Source/Text/MultiplyWithChecks.asm) | Развёрнутое умножение с отказом только по переносам удвоения накопителя |
| #C488 | [Text.AddSaturated](../Source/Text/AddSaturated.asm) | Сложение DE и BC с ограничением результата сверху значением #FFFF |
| #C491 | [Text.SubtractSaturated](../Source/Text/SubtractSaturated.asm) | Вычитание BC из DE с ограничением результата снизу нулём |
| #C49C | [Text.CompareLess](../Source/Text/CompareLess.asm) | Беззнаковая проверка DE меньше BC, результат ноль или один в DE |
| #C4A6 | [Text.CompareGreater](../Source/Text/CompareGreater.asm) | Беззнаковая проверка DE больше BC, результат ноль или один в DE |
| #C4B1 | [Text.CompareNotGreater](../Source/Text/CompareNotGreater.asm) | Беззнаковая проверка DE не больше BC, результат ноль или один в DE |
| #C4BC | [Text.CompareNotLess](../Source/Text/CompareNotLess.asm) | Беззнаковая проверка DE не меньше BC, результат ноль или один в DE |
| #C4C6 | [Text.AndWords](../Source/Text/AndWords.asm) | Побитовое AND двух слов DE и BC с результатом в DE |
| #C4CD | [Text.OrWords](../Source/Text/OrWords.asm) | Побитовое OR двух слов DE и BC с результатом в DE |
| #C4D4 | [Text.CopyRightOperand](../Source/Text/CopyRightOperand.asm) | Возврат правого операнда BC в DE |
| #C4D7 | [Text.ReadStridedWord](../Source/Text/ReadStridedWord.asm) | Чтение слова с шагом два по индексу из CPU-стека |
| #C4E3 | [Text.ReadStridedByte](../Source/Text/ReadStridedByte.asm) | Чтение байта с шагом два по индексу из CPU-стека |
| #C4EF | [Text.CheckThresholdSet30](../Source/Text/CheckThresholdSet30.asm) | Проверка 30 активных строк по числовому признаку L текущего ключа |
| #C51A | [Text.HasActiveNeighbor](../Source/Text/HasActiveNeighbor.asm) | Поиск активного соседа по двум кодированным границам первого набора |
| #C558 | [Text.IsByteMissingFromFour](../Source/Text/IsByteMissingFromFour.asm) | Проверка отсутствия выбранного байта в четырёхбайтовой записи |
| #C577 | [Text.GetHighBitCode](../Source/Text/GetHighBitCode.asm) | Возврат кода 127 при снятом bit7 либо 1 при установленном |
| #C58A | [Text.Property070](../Source/Text/Property070.asm) | Чтение слова с шагом два по базе #95D4 |
| #C590 | [Text.Property071](../Source/Text/Property071.asm) | Чтение байта с шагом два по базе #9633 |
| #C596 | [Text.CheckThresholdSet14](../Source/Text/CheckThresholdSet14.asm) | Проверка 14 строк с исходным порядком баз #98F6 и #9632 |
| #C5A9 | [Text.HasSecondActiveNeighbor](../Source/Text/HasSecondActiveNeighbor.asm) | Поиск активного соседа по границам второго набора |
| #C5B2 | [Text.Property072](../Source/Text/Property072.asm) | Проверка отсутствия байта #984A в записи таблицы #9484 |
| #C5BB | [Text.Property073](../Source/Text/Property073.asm) | Чтение кода старшего разряда по базе #98F6 |
| #C5C1 | [Text.GetCargoSecondByte](../Source/Text/GetCargoSecondByte.asm) | Чтение второго байта двухбайтовой грузовой записи по стековому индексу |
| #C5C7 | [Text.GetMarketPrice](../Source/Text/GetMarketPrice.asm) | Чтение текущей цены строки рынка по стековому индексу |
| #C5CD | [Text.IsMarketSaleLegal](../Source/Text/IsMarketSaleLegal.asm) | Проверка разрешённой продажи товара по снятому bit7 рыночной записи |
| #C5DF | [Text.GetIndexedLoad](../Source/Text/GetIndexedLoad.asm) | Взвешенная сумма с выбранной строкой из младшего байта стекового индекса |
| #C5E9 | [Text.ReadStrideFiveWord](../Source/Text/ReadStrideFiveWord.asm) | Чтение слова по индексу из CPU-стека с шагом пять и базой #9803 |
| #C5F9 | [Text.ReadStrideFiveByte](../Source/Text/ReadStrideFiveByte.asm) | Чтение байта по индексу из CPU-стека с шагом пять и базой #9802 |
| #C609 | [Text.Property080](../Source/Text/Property080.asm) | Чтение байта по индексу из CPU-стека с шагом пять и базой #9806 |
| #C60F | [Text.Property086](../Source/Text/Property086.asm) | Чтение слова по индексу из CPU-стека с шагом пять и базой #9826 |
| #C615 | [Text.Property087](../Source/Text/Property087.asm) | Чтение байта по индексу из CPU-стека с шагом пять и базой #9829 |
| #C61B | [Text.GetKeyMajor](../Source/Text/GetKeyMajor.asm) | Чтение поля характеристики ключа, старший числовой признак H |
| #C623 | [Text.GetKeyMinor](../Source/Text/GetKeyMinor.asm) | Чтение поля характеристики ключа, младший двухбитовый признак E |
| #C62A | [Text.GetKeySize](../Source/Text/GetKeySize.asm) | Чтение поля характеристики ключа, числовой признак L в диапазоне 1..16 |
| #C632 | [Text.GetKeyFingerprint](../Source/Text/GetKeyFingerprint.asm) | Чтение поля характеристики ключа, исходная свёртка ключа из A |
| #C63A | [Text.GetKeyRegion](../Source/Text/GetKeyRegion.asm) | Чтение поля характеристики ключа, код геометрической области D |
| #C642 | [Text.PushWordFieldWriter](../Source/Text/PushWordFieldWriter.asm) | Создание указателя писателя слова по #984E |
| #C657 | [Text.PushByteUWriter](../Source/Text/PushByteUWriter.asm) | Создание указателя писателя байта по #984B |
| #C66E | [Text.PushByteJWriter](../Source/Text/PushByteJWriter.asm) | Создание указателя писателя байта по #9851 |
| #C685 | [Text.PushCargo7BitWriter](../Source/Text/PushCargo7BitWriter.asm) | Создание захватывающего писателя семибитового поля через ReadCargoField |
| #C6B6 | [Text.PushMarket7BitWriter](../Source/Text/PushMarket7BitWriter.asm) | Создание захватывающего писателя семибитового поля через ReadMarketField |
| #C6BC | [Text.PushEquipmentWeightWriter](../Source/Text/PushEquipmentWeightWriter.asm) | Создание захватывающего писателя кодированного веса через ReadEquipmentWeight |
| #C6E4 | [Text.PushSecondWeightWriter](../Source/Text/PushSecondWeightWriter.asm) | Создание захватывающего писателя кодированного веса через ReadSecondWeight |
| #C6EA | [Text.ReadDecimal5](../Source/Text/ReadDecimal5.asm) | Чтение от одной до пяти ASCII-цифр, десятичное число в HL по модулю 65536 |
| #C79C | [Text.EmitOperator](../Source/Text/EmitOperator.asm) | Поиск символа бинарной операции и запись адреса её обработчика по альтернативному HL |
| #C7B6 | [Text.DispatchUnaryField](../Source/Text/DispatchUnaryField.asm) | Выбор одного из семи унарных обработчиков по байту поля |
| #C7C3 | [Text.DispatchWriteField](../Source/Text/DispatchWriteField.asm) | Выбор одного из семи создателей исполняемого писателя |
| #C7D0 | [Text.DispatchReadField](../Source/Text/DispatchReadField.asm) | Выбор читателя по 36 физическим записям с 35 различными символами |
| #C7DA | [Text.DispatchToken](../Source/Text/DispatchToken.asm) | Поиск токена и косвенная передача управления на адрес из таблицы |
| #C7E3 | [Text.FindToken](../Source/Text/FindToken.asm) | Поиск A в B трёхбайтовых записях со смещением на три от HL |
| #C7EE | [Text.ParseFieldSuffix](../Source/Text/ParseFieldSuffix.asm) | Разбор необязательного индекса и точечного суффикса с хвостовой передачей управления |
| #C825 | [Text.CallExpression](../Source/Text/CallExpression.asm) | Извлечение левого операнда, обработчика и правого операнда из стека выражений с возвратом результата через PushExpressionWord |
| #C849 | [Text.FindDelimitedRecord](../Source/Text/FindDelimitedRecord.asm) | Поиск записи через заданное число разделителей FF и FE и байтовое смещение |
| #C86F | [Text.ComputeWeightedLoad](../Source/Text/ComputeWeightedLoad.asm) | Байтовая взвешенная сумма трёх таблиц с добавлением выбранной строки |
| #C900 | [Text.GetEquipIndex](../Source/Text/GetEquipIndex.asm) | Сложение выбранной строки и смещения списка оснащения, байтовый индекс возвращается в BC |
| #C90C | [Text.SumSecondaryIndex](../Source/Text/SumSecondaryIndex.asm) | Суммирование двух исходных компонент вторичного индекса по модулю 256 |
| #C918 | [Text.GetCargoIndex](../Source/Text/GetCargoIndex.asm) | Сложение выбранной строки и смещения списка товаров, байтовый индекс возвращается в BC |
| #C924 | [Text.DescribeKeyChoice](../Source/Text/DescribeKeyChoice.asm) | Характеристика второго ключа при C=1 либо текущего ключа при остальных значениях |
| #C000 | [Map.DrawMapScene](../Source/Map/DrawMapScene.asm) | XOR-композиция дуги, шести видов маркеров, цепочки и видимых секторных точек карты |
| #C231 | [Map.XorMapPointMarker](../Source/Map/XorMapPointMarker.asm) | Отсечение и XOR семистрочного фазового маркера точки карты |
| #C325 | [Map.SelectMapPoint](../Source/Map/SelectMapPoint.asm) | Запись выбранного ключа, поиск его пятого байта и центрирование карты |
| #C333 | [Map.CenterMapView](../Source/Map/CenterMapView.asm) | Центрирование начала карты относительно упакованной точки с исходным отсечением по Sign |
| #C40F | [Map.ReadStoredMapVariant](../Source/Map/ReadStoredMapVariant.asm) | Поиск выбранного ключа в первом списке и запись пятого байта либо нуля |
| #C49B | [Map.BuildMapScreenTables](../Source/Map/BuildMapScreenTables.asm) | Построение адресов 256 строк карты, горизонтальных колонок и битовых масок |
| #C781 | [Map.PrepareVariantResources](../Source/Map/PrepareVariantResources.asm) | Подготовка до шести изменяемых указателей ресурсов вариантов выбранной точки |
| #C7B4 | [Map.SelectVariantResource](../Source/Map/SelectVariantResource.asm) | Выбор ресурса текущего, выбранного, сохранённого либо прочего варианта |
| #C88F | [Map.FindSecondaryMapPoint](../Source/Map/FindSecondaryMapPoint.asm) | Проверка наличия выбранного ключа во втором списке сохранённых точек |
| #C894 | [Map.FindStoredMapPoint](../Source/Map/FindStoredMapPoint.asm) | Проверка наличия выбранного ключа в первом списке сохранённых точек |
| #C8C2 | [Map.PrintSelectedVariantLabel](../Source/Map/PrintSelectedVariantLabel.asm) | Чтение выбранного ключа и последовательный вывод подписи его варианта |
| #C8C9 | [Map.PrintVariantLabel](../Source/Map/PrintVariantLabel.asm) | Вывод дефиса либо детерминированной буквы и номера варианта ключа |
| #C908 | [Map.XorSelectionBand](../Source/Map/XorSelectionBand.asm) | Инверсия восьми пиксельных строк с 0..31 полными байтами и попарными флагами краёв |
| #C9B9 | [Map.DescribeKey](../Source/Map/DescribeKey.asm) | Числовые признаки ключа через область и 1..256 шагов рабочего состояния |
| #C9FB | [Map.RefreshSecondaryPointOrder](../Source/Map/RefreshSecondaryPointOrder.asm) | Нормализация указателя второго списка, пересчёт количества и плотных смещений |
| #D1AC | [Map.DrawMapPointChain](../Source/Map/DrawMapPointChain.asm) | Построение относительных точек и рисование открытой индексированной цепочки из N-1 отрезков |
| #D2EE | [Map.RasterizeMapLine](../Source/Map/RasterizeMapLine.asm) | Рисование отрезка Брезенхэма в режимах Clear, Set и Xor без последнего конца |
| #D430 | [Map.BuildMapPointOutcodes](../Source/Map/BuildMapPointOutcodes.asm) | Классификация рабочих точек по изменяемым верхним порогам и OR кодов границ |
| #D48B | [Map.DispatchMapClipEdge](../Source/Map/DispatchMapClipEdge.asm) | Обмен внутреннего первого конца и диспетчеризация отсечения на трёх подставных возвратах |
| #DB63 | [Map.MultiplySigned16](../Source/Map/MultiplySigned16.asm) | Знаковое произведение HL и DE с двумя словами результата с тремя ядрами и исходным случаем 8000 |
| #DCFB | [Map.DivideSigned32To16](../Source/Map/DivideSigned32To16.asm) | Деление 32-битного числителя на слово DE с исходной обработкой знака дополнением |
| #DFC3 | [Map.DrawClippedMapArc](../Source/Map/DrawClippedMapArc.asm) | Выбор отсечённых проходов дуги по положению центра и пересечениям границ окна |
| #E208 | [Map.PrepareArcFullSpan](../Source/Map/PrepareArcFullSpan.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E248 | [Map.PrepareArcLeftEdge](../Source/Map/PrepareArcLeftEdge.asm) | Подготовка левого края дуги и изменяемой правой колонки |
| #E260 | [Map.PrepareArcRightEdge](../Source/Map/PrepareArcRightEdge.asm) | Подготовка правого края дуги и изменяемой левой колонки |
| #E278 | [Map.LoadArcRasterInputs](../Source/Map/LoadArcRasterInputs.asm) | Загрузка смещений и радиуса с подготовкой C'=-Radius и E'=0 |
| #E299 | [Map.LoadClippedArcInputs](../Source/Map/LoadClippedArcInputs.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E514 | [Map.PrepareLeftRasterPoint](../Source/Map/PrepareLeftRasterPoint.asm) | Адрес левой растровой точки и одноразрядная маска в B |
| #E52E | [Map.PrepareRightRasterPoint](../Source/Map/PrepareRightRasterPoint.asm) | Адрес правой растровой точки и маска C с сохранением левой B |
| #E554 | [Map.SqrtSquareDiff](../Source/Map/SqrtSquareDiff.asm) | Поразрядный целочисленный корень из 16-битной разности D в квадрате, A в квадрате и входного Carry |
| #E57E | [Map.PreviousRasterRow](../Source/Map/PreviousRasterRow.asm) | Переход на предыдущую строку Spectrum с проверкой верхней границы и нелокальным завершением растрового вызова |
| #E5AC | [Map.NextRasterRow](../Source/Map/NextRasterRow.asm) | Переход на следующую строку Spectrum с проверкой нижней границы и нелокальным завершением растрового вызова |
| #E5D8 | [Map.ResetRasterSpanEdges](../Source/Map/ResetRasterSpanEdges.asm) | Маски полного растрового пролёта и изменяемая левая колонка |
| #E5E3 | [Map.SeekRasterRowUp](../Source/Map/SeekRasterRowUp.asm) | Обычный поиск до B строк вверх с включённой верхней границей |
| #E621 | [Map.SeekRasterRowDown](../Source/Map/SeekRasterRowDown.asm) | Обычный поиск до B строк вниз с адресом исключённой нижней границы |
| #E65D | [Map.LookupSquare](../Source/Map/LookupSquare.asm) | Чтение квадрата A из двух раздельных страниц младших и старших байтов с сохранением Carry |
| #E666 | [Map.ResetRasterDown](../Source/Map/ResetRasterDown.asm) | Сброс альтернативного состояния растрового обхода и выбор движения вниз |
| #E674 | [Map.ResetRasterUp](../Source/Map/ResetRasterUp.asm) | Сброс альтернативного состояния растрового обхода и выбор движения вверх |
| #E681 | [Map.DrawArcLeftDown](../Source/Map/DrawArcLeftDown.asm) | Сохранение AF, сброс рекурсии и проход от левого края вниз |
| #E688 | [Map.DrawArcLeftUp](../Source/Map/DrawArcLeftUp.asm) | Сохранение AF, сброс рекурсии и проход от левого края вверх |
| #E68F | [Map.DrawArcRightDown](../Source/Map/DrawArcRightDown.asm) | Сохранение AF, сброс рекурсии и проход от правого края вниз |
| #E696 | [Map.DrawArcRightUp](../Source/Map/DrawArcRightUp.asm) | Сохранение AF, сброс рекурсии и проход от правого края вверх |
| #E69D | [Map.DrawArcBothDown](../Source/Map/DrawArcBothDown.asm) | Сохранение AF, сброс рекурсии и проход двух краёв вниз |
| #E6A4 | [Map.DrawArcBothUp](../Source/Map/DrawArcBothUp.asm) | Сохранение AF, сброс рекурсии и проход двух краёв вверх |
| #E6AB | [Map.BuildSystemName](../Source/Map/BuildSystemName.asm) | Формирование LF-имени системы в старом буфере загрузчика с обменом наборов |
| #E6F6 | [Map.AppendCompactDecimal](../Source/Map/AppendCompactDecimal.asm) | Запись байта десятичными разрядами с подавлением нулевых сотен и десятков |
| #E779 | [Map.ClassifyKeyRegion](../Source/Map/ClassifyKeyRegion.asm) | Классификация байтов H и L по трём прямоугольникам и внешней области |
| #E7BA | [Map.MeasureCoordinateDistance](../Source/Map/MeasureCoordinateDistance.asm) | Расстояние упакованных координат с делением суммы квадратов на 9 и кодом FF |
| #E838 | [Map.SeededSqrt16](../Source/Map/SeededSqrt16.asm) | Целый корень через табличное начальное приближение с исходной верхней областью таблиц |
| #DB00 | [Help.IndexTextLines](../Source/Help/IndexTextLines.asm) | Индексирование выбранной LF-записи по правилам переноса строк и обнуление остатка таблицы |
| #DB42 | [Help.PrintIndexedLine](../Source/Help/PrintIndexedLine.asm) | Печать по физическому указателю строки с начальной позицией X=0, Y=8 |
| #DB57 | [Help.SelectText](../Source/Help/SelectText.asm) | Подготовка номера LF-записи в операнде IndexTextLines без немедленного вывода |
| #DB5B | [Help.PrintCrRecordAndRows](../Source/Help/PrintCrRecordAndRows.asm) | Печать выбранного CR-заголовка и возврат байтового числа занятых строк в A' |
| #DB00 | [Music.Initialize](../Source/Music/Initialize.asm) | Выбор исходной композиции E700 и инициализация модуля с глушением аппаратного AY |
| #DB05 | [Music.PlayFrame](../Source/Music/PlayFrame.asm) | Кадровый вход проигрывателя, переход к изменяемому диспетчеру #DE1F |
| #DB08 | [Music.Stop](../Source/Music/Stop.asm) | Глушение аппаратных регистров AY без изменения RAM и запрета последующих кадров |
| #DB0A | [Music.InitializeModule](../Source/Music/InitializeModule.asm) | Перенос полей модуля, 48 указателей и начальных состояний с восстановлением SP и глушением AY |
| #DB7C | [Music.ClearAyRegisters](../Source/Music/ClearAyRegisters.asm) | Последовательная запись нуля в аппаратные регистры AY 13..0 без изменения RAM |
| #DDCA | [Music.ReadGateTimingA](../Source/Music/ReadGateTimingA.asm) | Чтение двух длительностей переключения канала A из потока паттерна |
| #DDD2 | [Music.SetGateTimingA](../Source/Music/SetGateTimingA.asm) | Настройка двух длительностей канала A и замена JR в #DE90 на LD B,n |
| #DE0A | [Music.ReadGateTimingC](../Source/Music/ReadGateTimingC.asm) | Чтение двух длительностей переключения канала C из потока паттерна |
| #DE12 | [Music.SetGateTimingC](../Source/Music/SetGateTimingC.asm) | Установка счётчика и длительностей чередования включённого и выключенного состояния канала C |
| #DE1F | [Music.TickDispatch](../Source/Music/TickDispatch.asm) | Изменяемый вход тика, выбор синтеза либо перенос подготовленных параметров строки A |
| #DE90 | [Music.StageGateAndSampleA](../Source/Music/StageGateAndSampleA.asm) | Применение отложенных длительностей чередования и позиции сэмпла канала A |
| #DEAE | [Music.StageOrnamentA](../Source/Music/StageOrnamentA.asm) | Применение отложенной позиции орнамента канала A |
| #DEB9 | [Music.StageChannelBRow](../Source/Music/StageChannelBRow.asm) | Сброс накопленного скольжения, подготовка ноты, орнамента и параметров скольжения строки B |
| #DF1E | [Music.StageGateB](../Source/Music/StageGateB.asm) | Применение отложенных длительностей чередования канала B |
| #DF31 | [Music.StageSampleB](../Source/Music/StageSampleB.asm) | Применение отложенной позиции сэмпла канала B |
| #DF3C | [Music.StageOrnamentB](../Source/Music/StageOrnamentB.asm) | Применение отложенной позиции орнамента канала B |
| #DF47 | [Music.StageEnvelopeAndNoise](../Source/Music/StageEnvelopeAndNoise.asm) | Подготовка формы огибающей и шума, перезапуск её периода и отложенного скольжения |
| #DF70 | [Music.CommitEnvelopeSlide](../Source/Music/CommitEnvelopeSlide.asm) | Фиксация шага и задержки скольжения огибающей перед продолжением разбора канала A |
| #DF7F | [Music.AdvancePatternA](../Source/Music/AdvancePatternA.asm) | Счётчик строки A, переход позиции, чтение трёх указателей через SP и подготовка маркеров строки A |
| #DFE3 | [Music.RenderChannelA](../Source/Music/RenderChannelA.asm) | Синтез сэмпла, орнамента, тона, шума и огибающей A с подготовкой общего кадрового контекста |
| #E0CD | [Music.FinishChannelA](../Source/Music/FinishChannelA.asm) | Завершение счётчика скольжения A, восстановление амплитуды и обновление чередования |
| #E1CD | [Music.FinishChannelB](../Source/Music/FinishChannelB.asm) | Завершение счётчика скольжения B, восстановление амплитуды и обновление чередования |
| #E2CB | [Music.FinishChannelC](../Source/Music/FinishChannelC.asm) | Завершение счётчика скольжения C, восстановление амплитуды и обновление чередования |
| #E6AE | [Music.SetToneSlideC](../Source/Music/SetToneSlideC.asm) | Чтение задержки и шага скольжения тона C, настройка изменяемых операндов и отключение счётчика чередования |
| #6000 | [ActionBoot.RelocateBootstrap](../Source/ActionBoot/RelocateBootstrap.asm) | Подготовка экранов и перенос #01FA байт загрузчика в #4200 |
| #4200 | [ActionBoot.InitializeFlight](../Source/ActionBoot/InitializeFlight.asm) | Перенос ядра в #6000, загрузка графических банков и запуск полётного режима |
| #42AB | [ActionBoot.GetFileLocation](../Source/ActionBoot/GetFileLocation.asm) | Поиск девятибайтового имени, чтение заголовка каталога и возврат числа секторов и начального положения |
| #42C6 | [ActionBoot.LoadFileToBank](../Source/ActionBoot/LoadFileToBank.asm) | Загрузка выбранного файла по адресу #C000 в уже подключённый банк |
| #42C9 | [ActionBoot.LoadFileAtAddress](../Source/ActionBoot/LoadFileAtAddress.asm) | Загрузка выбранного файла по адресу HL через TR-DOS, A=3 и C=#0E |
| #4306 | [ActionBoot.InitializeRandomStates](../Source/ActionBoot/InitializeRandomStates.asm) | Начальное заполнение слов состояний от регистра R и повторных вызовов обработчика #EB72 |
| #4355 | [ActionBoot.BuildProjectionTable](../Source/ActionBoot/BuildProjectionTable.asm) | Создание таблицы в #9300 с вычислением через сдвиги и сложение |
| #438F | [ActionBoot.BuildReciprocalTable](../Source/ActionBoot/BuildReciprocalTable.asm) | Создание двух страниц таблицы через двоичное деление |
| #43CF | [ActionBoot.BuildBitmapTables](../Source/ActionBoot/BuildBitmapTables.asm) | Создание таблиц строк и битовых масок для рисования |
| #6000 | [Action.Unknown6000](../Source/Action/Unknown6000.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6040 | [Action.Unknown6040](../Source/Action/Unknown6040.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6145 | [Action.Unknown6145](../Source/Action/Unknown6145.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6172 | [Action.Unknown6172](../Source/Action/Unknown6172.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6265 | [Action.Unknown6265](../Source/Action/Unknown6265.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #62CF | [Action.Unknown62CF](../Source/Action/Unknown62CF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #635B | [Action.Unknown635B](../Source/Action/Unknown635B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #64DF | [Action.Unknown64DF](../Source/Action/Unknown64DF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6639 | [Action.Unknown6639](../Source/Action/Unknown6639.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6649 | [Action.Unknown6649](../Source/Action/Unknown6649.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #66D2 | [Action.Unknown66D2](../Source/Action/Unknown66D2.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6780 | [Action.Unknown6780](../Source/Action/Unknown6780.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6986 | [Action.Unknown6986](../Source/Action/Unknown6986.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #699C | [Action.Unknown699C](../Source/Action/Unknown699C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #69BE | [Action.Unknown69BE](../Source/Action/Unknown69BE.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6A29 | [Action.Unknown6A29](../Source/Action/Unknown6A29.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6A6E | [Action.Unknown6A6E](../Source/Action/Unknown6A6E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6AB0 | [Action.Unknown6AB0](../Source/Action/Unknown6AB0.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6B16 | [Action.Unknown6B16](../Source/Action/Unknown6B16.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6BFF | [Action.Unknown6BFF](../Source/Action/Unknown6BFF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6C19 | [Action.Unknown6C19](../Source/Action/Unknown6C19.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6C43 | [Action.Unknown6C43](../Source/Action/Unknown6C43.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6C7E | [Action.Unknown6C7E](../Source/Action/Unknown6C7E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6C8F | [Action.Unknown6C8F](../Source/Action/Unknown6C8F.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6CB4 | [Action.Unknown6CB4](../Source/Action/Unknown6CB4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6CD6 | [Action.Unknown6CD6](../Source/Action/Unknown6CD6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6CEF | [Action.Unknown6CEF](../Source/Action/Unknown6CEF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6D38 | [Action.Unknown6D38](../Source/Action/Unknown6D38.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6E2B | [Action.Unknown6E2B](../Source/Action/Unknown6E2B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6E6C | [Action.Unknown6E6C](../Source/Action/Unknown6E6C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6EAC | [Action.Unknown6EAC](../Source/Action/Unknown6EAC.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6F1D | [Action.Unknown6F1D](../Source/Action/Unknown6F1D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6F55 | [Action.Unknown6F55](../Source/Action/Unknown6F55.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #74FB | [Action.Unknown74FB](../Source/Action/Unknown74FB.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7859 | [Action.Unknown7859](../Source/Action/Unknown7859.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7B58 | [Action.Unknown7B58](../Source/Action/Unknown7B58.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7E9D | [Action.Unknown7E9D](../Source/Action/Unknown7E9D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7EB7 | [Action.Unknown7EB7](../Source/Action/Unknown7EB7.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7F0E | [Action.Unknown7F0E](../Source/Action/Unknown7F0E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #7F76 | [Action.Unknown7F76](../Source/Action/Unknown7F76.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #A82D | [Action.StartFlight](../Source/Action/StartFlight.asm) | Вывод панели из страницы 6 и инициализация полётного режима |
| #A859 | [Action.MainLoop](../Source/Action/MainLoop.asm) | Повторение процедуры полётного кадра |
| #A85E | [Action.UpdateFrame](../Source/Action/UpdateFrame.asm) | Обработка таймеров, управления, визуальных модулей и игровых объектов |
| #AACC | [Action.UnknownAACC](../Source/Action/UnknownAACC.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AB1B | [Action.SelectMemoryPage](../Source/Action/SelectMemoryPage.asm) | Запись A в #7FFD с сохранением BC |
| #AB23 | [Action.UnpackResource](../Source/Action/UnpackResource.asm) | Полётная копия распаковщика ресурсов с обработкой ссылок |
| #AC38 | [Action.UnknownAC38](../Source/Action/UnknownAC38.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AC5D | [Action.UnknownAC5D](../Source/Action/UnknownAC5D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AD48 | [Action.UnknownAD48](../Source/Action/UnknownAD48.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AD5A | [Action.UnknownAD5A](../Source/Action/UnknownAD5A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #ADB7 | [Action.UnknownADB7](../Source/Action/UnknownADB7.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AE24 | [Action.UnknownAE24](../Source/Action/UnknownAE24.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #AE73 | [Action.UnknownAE73](../Source/Action/UnknownAE73.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #B0E9 | [Action.UnknownB0E9](../Source/Action/UnknownB0E9.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C000 | [Action.DispatchEdges](../Source/Action/DispatchEdges.asm) | Выбор вершин и обработчика ребра по раздельной таблице младших и старших байтов |
| #C071 | [Action.NextEdge](../Source/Action/NextEdge.asm) | Возврат косвенного обработчика и продолжение перебора рёбер |
| #C07A | [Action.EdgeCase11](../Source/Action/EdgeCase11.asm) | обработчик ребра для индексов таблицы #11, #22, #44, #55, #66, #88, #99, #AA |
| #C07B | [Action.EdgeCase05](../Source/Action/EdgeCase05.asm) | обработчик ребра для индексов таблицы #05 |
| #C08A | [Action.EdgeCase15](../Source/Action/EdgeCase15.asm) | обработчик ребра для индексов таблицы #15 |
| #C095 | [Action.EdgeCase06](../Source/Action/EdgeCase06.asm) | обработчик ребра для индексов таблицы #06 |
| #C0A4 | [Action.EdgeCase46](../Source/Action/EdgeCase46.asm) | обработчик ребра для индексов таблицы #46 |
| #C0AF | [Action.EdgeCase09](../Source/Action/EdgeCase09.asm) | обработчик ребра для индексов таблицы #09 |
| #C0BE | [Action.EdgeCase89](../Source/Action/EdgeCase89.asm) | обработчик ребра для индексов таблицы #89 |
| #C0C9 | [Action.EdgeCase0A](../Source/Action/EdgeCase0A.asm) | обработчик ребра для индексов таблицы #0A |
| #C0D8 | [Action.EdgeCase2A](../Source/Action/EdgeCase2A.asm) | обработчик ребра для индексов таблицы #2A |
| #C0E3 | [Action.EdgeCase10](../Source/Action/EdgeCase10.asm) | обработчик ребра для индексов таблицы #10 |
| #C0E9 | [Action.EdgeCase12](../Source/Action/EdgeCase12.asm) | обработчик ребра для индексов таблицы #12 |
| #C0EF | [Action.EdgeCase14](../Source/Action/EdgeCase14.asm) | обработчик ребра для индексов таблицы #14 |
| #C101 | [Action.EdgeCase16](../Source/Action/EdgeCase16.asm) | обработчик ребра для индексов таблицы #16 |
| #C119 | [Action.EdgeCase18](../Source/Action/EdgeCase18.asm) | обработчик ребра для индексов таблицы #18 |
| #C12B | [Action.EdgeCase19](../Source/Action/EdgeCase19.asm) | обработчик ребра для индексов таблицы #19 |
| #C132 | [Action.EdgeCase1A](../Source/Action/EdgeCase1A.asm) | обработчик ребра для индексов таблицы #1A |
| #C144 | [Action.EdgeCase20](../Source/Action/EdgeCase20.asm) | обработчик ребра для индексов таблицы #20 |
| #C14A | [Action.EdgeCase21](../Source/Action/EdgeCase21.asm) | обработчик ребра для индексов таблицы #21 |
| #C150 | [Action.EdgeCase24](../Source/Action/EdgeCase24.asm) | обработчик ребра для индексов таблицы #24 |
| #C162 | [Action.EdgeCase25](../Source/Action/EdgeCase25.asm) | обработчик ребра для индексов таблицы #25 |
| #C174 | [Action.EdgeCase26](../Source/Action/EdgeCase26.asm) | обработчик ребра для индексов таблицы #26 |
| #C17B | [Action.EdgeCase28](../Source/Action/EdgeCase28.asm) | обработчик ребра для индексов таблицы #28 |
| #C18D | [Action.EdgeCase29](../Source/Action/EdgeCase29.asm) | обработчик ребра для индексов таблицы #29 |
| #C1A5 | [Action.EdgeCase40](../Source/Action/EdgeCase40.asm) | обработчик ребра для индексов таблицы #40 |
| #C1AB | [Action.EdgeCase41](../Source/Action/EdgeCase41.asm) | обработчик ребра для индексов таблицы #41 |
| #C1BD | [Action.EdgeCase42](../Source/Action/EdgeCase42.asm) | обработчик ребра для индексов таблицы #42 |
| #C1CF | [Action.EdgeCase45](../Source/Action/EdgeCase45.asm) | обработчик ребра для индексов таблицы #45 |
| #C1D6 | [Action.EdgeCase48](../Source/Action/EdgeCase48.asm) | обработчик ребра для индексов таблицы #48 |
| #C1DC | [Action.EdgeCase49](../Source/Action/EdgeCase49.asm) | обработчик ребра для индексов таблицы #49 |
| #C1F1 | [Action.EdgeCase4A](../Source/Action/EdgeCase4A.asm) | обработчик ребра для индексов таблицы #4A |
| #C20C | [Action.EdgeCase50](../Source/Action/EdgeCase50.asm) | обработчик ребра для индексов таблицы #50 |
| #C228 | [Action.EdgeCase51](../Source/Action/EdgeCase51.asm) | обработчик ребра для индексов таблицы #51 |
| #C22F | [Action.EdgeCase52](../Source/Action/EdgeCase52.asm) | обработчик ребра для индексов таблицы #52 |
| #C24E | [Action.EdgeCase54](../Source/Action/EdgeCase54.asm) | обработчик ребра для индексов таблицы #54 |
| #C259 | [Action.EdgeCase56](../Source/Action/EdgeCase56.asm) | обработчик ребра для индексов таблицы #56 |
| #C25F | [Action.EdgeCase58](../Source/Action/EdgeCase58.asm) | обработчик ребра для индексов таблицы #58 |
| #C274 | [Action.EdgeCase5A](../Source/Action/EdgeCase5A.asm) | обработчик ребра для индексов таблицы #5A |
| #C28D | [Action.EdgeCase60](../Source/Action/EdgeCase60.asm) | обработчик ребра для индексов таблицы #60 |
| #C2A9 | [Action.EdgeCase61](../Source/Action/EdgeCase61.asm) | обработчик ребра для индексов таблицы #61 |
| #C2BE | [Action.EdgeCase62](../Source/Action/EdgeCase62.asm) | обработчик ребра для индексов таблицы #62 |
| #C2C9 | [Action.EdgeCase64](../Source/Action/EdgeCase64.asm) | обработчик ребра для индексов таблицы #64 |
| #C2D0 | [Action.EdgeCase68](../Source/Action/EdgeCase68.asm) | обработчик ребра для индексов таблицы #68 |
| #C2EF | [Action.EdgeCase69](../Source/Action/EdgeCase69.asm) | обработчик ребра для индексов таблицы #69 |
| #C308 | [Action.EdgeCase6A](../Source/Action/EdgeCase6A.asm) | обработчик ребра для индексов таблицы #6A |
| #C30E | [Action.EdgeCase80](../Source/Action/EdgeCase80.asm) | обработчик ребра для индексов таблицы #80 |
| #C314 | [Action.EdgeCase81](../Source/Action/EdgeCase81.asm) | обработчик ребра для индексов таблицы #81 |
| #C326 | [Action.EdgeCase82](../Source/Action/EdgeCase82.asm) | обработчик ребра для индексов таблицы #82 |
| #C338 | [Action.EdgeCase84](../Source/Action/EdgeCase84.asm) | обработчик ребра для индексов таблицы #84 |
| #C33E | [Action.EdgeCase85](../Source/Action/EdgeCase85.asm) | обработчик ребра для индексов таблицы #85 |
| #C359 | [Action.EdgeCase86](../Source/Action/EdgeCase86.asm) | обработчик ребра для индексов таблицы #86 |
| #C36E | [Action.EdgeCase8A](../Source/Action/EdgeCase8A.asm) | обработчик ребра для индексов таблицы #8A |
| #C375 | [Action.EdgeCase90](../Source/Action/EdgeCase90.asm) | обработчик ребра для индексов таблицы #90 |
| #C391 | [Action.EdgeCase91](../Source/Action/EdgeCase91.asm) | обработчик ребра для индексов таблицы #91 |
| #C39C | [Action.EdgeCase92](../Source/Action/EdgeCase92.asm) | обработчик ребра для индексов таблицы #92 |
| #C3B1 | [Action.EdgeCase94](../Source/Action/EdgeCase94.asm) | обработчик ребра для индексов таблицы #94 |
| #C3D0 | [Action.EdgeCase95](../Source/Action/EdgeCase95.asm) | обработчик ребра для индексов таблицы #95 |
| #C3D6 | [Action.EdgeCase96](../Source/Action/EdgeCase96.asm) | обработчик ребра для индексов таблицы #96 |
| #C3EF | [Action.EdgeCase98](../Source/Action/EdgeCase98.asm) | обработчик ребра для индексов таблицы #98 |
| #C3F6 | [Action.EdgeCaseA0](../Source/Action/EdgeCaseA0.asm) | обработчик ребра для индексов таблицы #A0 |
| #C412 | [Action.EdgeCaseA1](../Source/Action/EdgeCaseA1.asm) | обработчик ребра для индексов таблицы #A1 |
| #C431 | [Action.EdgeCaseA2](../Source/Action/EdgeCaseA2.asm) | обработчик ребра для индексов таблицы #A2 |
| #C438 | [Action.EdgeCaseA4](../Source/Action/EdgeCaseA4.asm) | обработчик ребра для индексов таблицы #A4 |
| #C44D | [Action.EdgeCaseA5](../Source/Action/EdgeCaseA5.asm) | обработчик ребра для индексов таблицы #A5 |
| #C466 | [Action.EdgeCaseA8](../Source/Action/EdgeCaseA8.asm) | обработчик ребра для индексов таблицы #A8 |
| #C471 | [Action.EdgeCaseA9](../Source/Action/EdgeCaseA9.asm) | обработчик ребра для индексов таблицы #A9 |
| #C477 | [Action.UnknownC477](../Source/Action/UnknownC477.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C496 | [Action.UnknownC496](../Source/Action/UnknownC496.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4B5 | [Action.UnknownC4B5](../Source/Action/UnknownC4B5.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4D4 | [Action.UnknownC4D4](../Source/Action/UnknownC4D4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4F3 | [Action.EdgeCase08](../Source/Action/EdgeCase08.asm) | обработчик ребра для индексов таблицы #08 |
| #C4F6 | [Action.UnknownC4F6](../Source/Action/UnknownC4F6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C53D | [Action.EdgeCase04](../Source/Action/EdgeCase04.asm) | обработчик ребра для индексов таблицы #04 |
| #C540 | [Action.UnknownC540](../Source/Action/UnknownC540.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C588 | [Action.EdgeCase02](../Source/Action/EdgeCase02.asm) | обработчик ребра для индексов таблицы #02 |
| #C58B | [Action.UnknownC58B](../Source/Action/UnknownC58B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C5E4 | [Action.EdgeCase01](../Source/Action/EdgeCase01.asm) | обработчик ребра для индексов таблицы #01 |
| #C5E7 | [Action.UnknownC5E7](../Source/Action/UnknownC5E7.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C641 | [Action.UnknownC641](../Source/Action/UnknownC641.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C64C | [Action.UnknownC64C](../Source/Action/UnknownC64C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C657 | [Action.UnknownC657](../Source/Action/UnknownC657.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C662 | [Action.UnknownC662](../Source/Action/UnknownC662.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C66D | [Action.UnknownC66D](../Source/Action/UnknownC66D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C681 | [Action.UnknownC681](../Source/Action/UnknownC681.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C695 | [Action.UnknownC695](../Source/Action/UnknownC695.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6A9 | [Action.UnknownC6A9](../Source/Action/UnknownC6A9.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6BD | [Action.UnknownC6BD](../Source/Action/UnknownC6BD.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6C8 | [Action.UnknownC6C8](../Source/Action/UnknownC6C8.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6D3 | [Action.EdgeCase00](../Source/Action/EdgeCase00.asm) | обработчик ребра для индексов таблицы #00 |
| #C6EA | [Action.EdgeCase59](../Source/Action/EdgeCase59.asm) | обработчик ребра для индексов таблицы #59, #65, #9A, #A6 |
| #C6F4 | [Action.UnknownC6F4](../Source/Action/UnknownC6F4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C88C | [Action.UnknownC88C](../Source/Action/UnknownC88C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CF08 | [Action.UnknownCF08](../Source/Action/UnknownCF08.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D10A | [Action.ClearWorkBuffer](../Source/Action/ClearWorkBuffer.asm) | Заполнение #0C00 байт до #8C00 значением #FF через стек с восстановлением SP |
| #D12C | [Action.MultiplySignedScaled](../Source/Action/MultiplySignedScaled.asm) | Знаковое умножение с масштабом 1/128 для коэффициента от -127 до 127, выход через JP (IX) |
| #E020 | [Action.UnknownE020](../Source/Action/UnknownE020.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E4A6 | [Action.UnknownE4A6](../Source/Action/UnknownE4A6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E4FF | [Action.UnknownE4FF](../Source/Action/UnknownE4FF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E55C | [Action.UnknownE55C](../Source/Action/UnknownE55C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E5A0 | [Action.UnknownE5A0](../Source/Action/UnknownE5A0.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E658 | [Action.UnknownE658](../Source/Action/UnknownE658.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E685 | [Action.UnknownE685](../Source/Action/UnknownE685.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E6BE | [Action.UnknownE6BE](../Source/Action/UnknownE6BE.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E6C7 | [Action.UnknownE6C7](../Source/Action/UnknownE6C7.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E6D1 | [Action.UnknownE6D1](../Source/Action/UnknownE6D1.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E98D | [Action.UnknownE98D](../Source/Action/UnknownE98D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E9A1 | [Action.UnknownE9A1](../Source/Action/UnknownE9A1.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EA29 | [Action.UnknownEA29](../Source/Action/UnknownEA29.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EB72 | [Action.UnknownEB72](../Source/Action/UnknownEB72.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EB87 | [Action.UnknownEB87](../Source/Action/UnknownEB87.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EBB8 | [Action.UnknownEBB8](../Source/Action/UnknownEBB8.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EC08 | [Action.UnknownEC08](../Source/Action/UnknownEC08.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #ECA8 | [Action.UnknownECA8](../Source/Action/UnknownECA8.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F075 | [Action.UnknownF075](../Source/Action/UnknownF075.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F394 | [Action.UnknownF394](../Source/Action/UnknownF394.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F51E | [Action.UnknownF51E](../Source/Action/UnknownF51E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F535 | [Action.UnknownF535](../Source/Action/UnknownF535.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F541 | [Action.UnknownF541](../Source/Action/UnknownF541.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F54D | [Action.UnknownF54D](../Source/Action/UnknownF54D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F572 | [Action.UnknownF572](../Source/Action/UnknownF572.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F729 | [Action.UpdateObjects](../Source/Action/UpdateObjects.asm) | Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний |
| #F792 | [Action.UnknownF792](../Source/Action/UnknownF792.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F7C6 | [Action.UnknownF7C6](../Source/Action/UnknownF7C6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C000 | [ThreeD.DispatchEdges](../Source/ThreeD/DispatchEdges.asm) | Перебор индексов вершин и вызов обработчиков из таблиц #CF00 и #D000 |
| #C071 | [ThreeD.NextEdge](../Source/ThreeD/NextEdge.asm) | Возврат косвенного обработчика и продолжение перебора рёбер |
| #C07A | [ThreeD.EdgeCase11](../Source/ThreeD/EdgeCase11.asm) | обработчик ребра для индексов таблицы #11, #22, #44, #55, #66, #88, #99, #AA |
| #C07B | [ThreeD.EdgeCase05](../Source/ThreeD/EdgeCase05.asm) | обработчик ребра для индексов таблицы #05 |
| #C08A | [ThreeD.EdgeCase15](../Source/ThreeD/EdgeCase15.asm) | обработчик ребра для индексов таблицы #15 |
| #C095 | [ThreeD.EdgeCase06](../Source/ThreeD/EdgeCase06.asm) | обработчик ребра для индексов таблицы #06 |
| #C0A4 | [ThreeD.EdgeCase46](../Source/ThreeD/EdgeCase46.asm) | обработчик ребра для индексов таблицы #46 |
| #C0AF | [ThreeD.EdgeCase09](../Source/ThreeD/EdgeCase09.asm) | обработчик ребра для индексов таблицы #09 |
| #C0BE | [ThreeD.EdgeCase89](../Source/ThreeD/EdgeCase89.asm) | обработчик ребра для индексов таблицы #89 |
| #C0C9 | [ThreeD.EdgeCase0A](../Source/ThreeD/EdgeCase0A.asm) | обработчик ребра для индексов таблицы #0A |
| #C0D8 | [ThreeD.EdgeCase2A](../Source/ThreeD/EdgeCase2A.asm) | обработчик ребра для индексов таблицы #2A |
| #C0E3 | [ThreeD.EdgeCase10](../Source/ThreeD/EdgeCase10.asm) | обработчик ребра для индексов таблицы #10 |
| #C0E9 | [ThreeD.EdgeCase12](../Source/ThreeD/EdgeCase12.asm) | обработчик ребра для индексов таблицы #12 |
| #C0EF | [ThreeD.EdgeCase14](../Source/ThreeD/EdgeCase14.asm) | обработчик ребра для индексов таблицы #14 |
| #C101 | [ThreeD.EdgeCase16](../Source/ThreeD/EdgeCase16.asm) | обработчик ребра для индексов таблицы #16 |
| #C119 | [ThreeD.EdgeCase18](../Source/ThreeD/EdgeCase18.asm) | обработчик ребра для индексов таблицы #18 |
| #C12B | [ThreeD.EdgeCase19](../Source/ThreeD/EdgeCase19.asm) | обработчик ребра для индексов таблицы #19 |
| #C132 | [ThreeD.EdgeCase1A](../Source/ThreeD/EdgeCase1A.asm) | обработчик ребра для индексов таблицы #1A |
| #C144 | [ThreeD.EdgeCase20](../Source/ThreeD/EdgeCase20.asm) | обработчик ребра для индексов таблицы #20 |
| #C14A | [ThreeD.EdgeCase21](../Source/ThreeD/EdgeCase21.asm) | обработчик ребра для индексов таблицы #21 |
| #C150 | [ThreeD.EdgeCase24](../Source/ThreeD/EdgeCase24.asm) | обработчик ребра для индексов таблицы #24 |
| #C162 | [ThreeD.EdgeCase25](../Source/ThreeD/EdgeCase25.asm) | обработчик ребра для индексов таблицы #25 |
| #C174 | [ThreeD.EdgeCase26](../Source/ThreeD/EdgeCase26.asm) | обработчик ребра для индексов таблицы #26 |
| #C17B | [ThreeD.EdgeCase28](../Source/ThreeD/EdgeCase28.asm) | обработчик ребра для индексов таблицы #28 |
| #C18D | [ThreeD.EdgeCase29](../Source/ThreeD/EdgeCase29.asm) | обработчик ребра для индексов таблицы #29 |
| #C1A5 | [ThreeD.EdgeCase40](../Source/ThreeD/EdgeCase40.asm) | обработчик ребра для индексов таблицы #40 |
| #C1AB | [ThreeD.EdgeCase41](../Source/ThreeD/EdgeCase41.asm) | обработчик ребра для индексов таблицы #41 |
| #C1BD | [ThreeD.EdgeCase42](../Source/ThreeD/EdgeCase42.asm) | обработчик ребра для индексов таблицы #42 |
| #C1CF | [ThreeD.EdgeCase45](../Source/ThreeD/EdgeCase45.asm) | обработчик ребра для индексов таблицы #45 |
| #C1D6 | [ThreeD.EdgeCase48](../Source/ThreeD/EdgeCase48.asm) | обработчик ребра для индексов таблицы #48 |
| #C1DC | [ThreeD.EdgeCase49](../Source/ThreeD/EdgeCase49.asm) | обработчик ребра для индексов таблицы #49 |
| #C1F1 | [ThreeD.EdgeCase4A](../Source/ThreeD/EdgeCase4A.asm) | обработчик ребра для индексов таблицы #4A |
| #C20C | [ThreeD.EdgeCase50](../Source/ThreeD/EdgeCase50.asm) | обработчик ребра для индексов таблицы #50 |
| #C228 | [ThreeD.EdgeCase51](../Source/ThreeD/EdgeCase51.asm) | обработчик ребра для индексов таблицы #51 |
| #C22F | [ThreeD.EdgeCase52](../Source/ThreeD/EdgeCase52.asm) | обработчик ребра для индексов таблицы #52 |
| #C24E | [ThreeD.EdgeCase54](../Source/ThreeD/EdgeCase54.asm) | обработчик ребра для индексов таблицы #54 |
| #C259 | [ThreeD.EdgeCase56](../Source/ThreeD/EdgeCase56.asm) | обработчик ребра для индексов таблицы #56 |
| #C25F | [ThreeD.EdgeCase58](../Source/ThreeD/EdgeCase58.asm) | обработчик ребра для индексов таблицы #58 |
| #C274 | [ThreeD.EdgeCase5A](../Source/ThreeD/EdgeCase5A.asm) | обработчик ребра для индексов таблицы #5A |
| #C28D | [ThreeD.EdgeCase60](../Source/ThreeD/EdgeCase60.asm) | обработчик ребра для индексов таблицы #60 |
| #C2A9 | [ThreeD.EdgeCase61](../Source/ThreeD/EdgeCase61.asm) | обработчик ребра для индексов таблицы #61 |
| #C2BE | [ThreeD.EdgeCase62](../Source/ThreeD/EdgeCase62.asm) | обработчик ребра для индексов таблицы #62 |
| #C2C9 | [ThreeD.EdgeCase64](../Source/ThreeD/EdgeCase64.asm) | обработчик ребра для индексов таблицы #64 |
| #C2D0 | [ThreeD.EdgeCase68](../Source/ThreeD/EdgeCase68.asm) | обработчик ребра для индексов таблицы #68 |
| #C2EF | [ThreeD.EdgeCase69](../Source/ThreeD/EdgeCase69.asm) | обработчик ребра для индексов таблицы #69 |
| #C308 | [ThreeD.EdgeCase6A](../Source/ThreeD/EdgeCase6A.asm) | обработчик ребра для индексов таблицы #6A |
| #C30E | [ThreeD.EdgeCase80](../Source/ThreeD/EdgeCase80.asm) | обработчик ребра для индексов таблицы #80 |
| #C314 | [ThreeD.EdgeCase81](../Source/ThreeD/EdgeCase81.asm) | обработчик ребра для индексов таблицы #81 |
| #C326 | [ThreeD.EdgeCase82](../Source/ThreeD/EdgeCase82.asm) | обработчик ребра для индексов таблицы #82 |
| #C338 | [ThreeD.EdgeCase84](../Source/ThreeD/EdgeCase84.asm) | обработчик ребра для индексов таблицы #84 |
| #C33E | [ThreeD.EdgeCase85](../Source/ThreeD/EdgeCase85.asm) | обработчик ребра для индексов таблицы #85 |
| #C359 | [ThreeD.EdgeCase86](../Source/ThreeD/EdgeCase86.asm) | обработчик ребра для индексов таблицы #86 |
| #C36E | [ThreeD.EdgeCase8A](../Source/ThreeD/EdgeCase8A.asm) | обработчик ребра для индексов таблицы #8A |
| #C375 | [ThreeD.EdgeCase90](../Source/ThreeD/EdgeCase90.asm) | обработчик ребра для индексов таблицы #90 |
| #C391 | [ThreeD.EdgeCase91](../Source/ThreeD/EdgeCase91.asm) | обработчик ребра для индексов таблицы #91 |
| #C39C | [ThreeD.EdgeCase92](../Source/ThreeD/EdgeCase92.asm) | обработчик ребра для индексов таблицы #92 |
| #C3B1 | [ThreeD.EdgeCase94](../Source/ThreeD/EdgeCase94.asm) | обработчик ребра для индексов таблицы #94 |
| #C3D0 | [ThreeD.EdgeCase95](../Source/ThreeD/EdgeCase95.asm) | обработчик ребра для индексов таблицы #95 |
| #C3D6 | [ThreeD.EdgeCase96](../Source/ThreeD/EdgeCase96.asm) | обработчик ребра для индексов таблицы #96 |
| #C3EF | [ThreeD.EdgeCase98](../Source/ThreeD/EdgeCase98.asm) | обработчик ребра для индексов таблицы #98 |
| #C3F6 | [ThreeD.EdgeCaseA0](../Source/ThreeD/EdgeCaseA0.asm) | обработчик ребра для индексов таблицы #A0 |
| #C412 | [ThreeD.EdgeCaseA1](../Source/ThreeD/EdgeCaseA1.asm) | обработчик ребра для индексов таблицы #A1 |
| #C431 | [ThreeD.EdgeCaseA2](../Source/ThreeD/EdgeCaseA2.asm) | обработчик ребра для индексов таблицы #A2 |
| #C438 | [ThreeD.EdgeCaseA4](../Source/ThreeD/EdgeCaseA4.asm) | обработчик ребра для индексов таблицы #A4 |
| #C44D | [ThreeD.EdgeCaseA5](../Source/ThreeD/EdgeCaseA5.asm) | обработчик ребра для индексов таблицы #A5 |
| #C466 | [ThreeD.EdgeCaseA8](../Source/ThreeD/EdgeCaseA8.asm) | обработчик ребра для индексов таблицы #A8 |
| #C471 | [ThreeD.EdgeCaseA9](../Source/ThreeD/EdgeCaseA9.asm) | обработчик ребра для индексов таблицы #A9 |
| #C477 | [ThreeD.UnknownC477](../Source/ThreeD/UnknownC477.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C496 | [ThreeD.UnknownC496](../Source/ThreeD/UnknownC496.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4B5 | [ThreeD.UnknownC4B5](../Source/ThreeD/UnknownC4B5.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4D4 | [ThreeD.UnknownC4D4](../Source/ThreeD/UnknownC4D4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C4F3 | [ThreeD.EdgeCase08](../Source/ThreeD/EdgeCase08.asm) | обработчик ребра для индексов таблицы #08 |
| #C4F6 | [ThreeD.UnknownC4F6](../Source/ThreeD/UnknownC4F6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C53D | [ThreeD.EdgeCase04](../Source/ThreeD/EdgeCase04.asm) | обработчик ребра для индексов таблицы #04 |
| #C540 | [ThreeD.UnknownC540](../Source/ThreeD/UnknownC540.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C588 | [ThreeD.EdgeCase02](../Source/ThreeD/EdgeCase02.asm) | обработчик ребра для индексов таблицы #02 |
| #C58B | [ThreeD.UnknownC58B](../Source/ThreeD/UnknownC58B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C5E4 | [ThreeD.EdgeCase01](../Source/ThreeD/EdgeCase01.asm) | обработчик ребра для индексов таблицы #01 |
| #C5E7 | [ThreeD.UnknownC5E7](../Source/ThreeD/UnknownC5E7.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C641 | [ThreeD.UnknownC641](../Source/ThreeD/UnknownC641.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C64C | [ThreeD.UnknownC64C](../Source/ThreeD/UnknownC64C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C657 | [ThreeD.UnknownC657](../Source/ThreeD/UnknownC657.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C662 | [ThreeD.UnknownC662](../Source/ThreeD/UnknownC662.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C66D | [ThreeD.UnknownC66D](../Source/ThreeD/UnknownC66D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C681 | [ThreeD.UnknownC681](../Source/ThreeD/UnknownC681.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C695 | [ThreeD.UnknownC695](../Source/ThreeD/UnknownC695.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6A9 | [ThreeD.UnknownC6A9](../Source/ThreeD/UnknownC6A9.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6BD | [ThreeD.UnknownC6BD](../Source/ThreeD/UnknownC6BD.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6C8 | [ThreeD.UnknownC6C8](../Source/ThreeD/UnknownC6C8.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C6D3 | [ThreeD.EdgeCase00](../Source/ThreeD/EdgeCase00.asm) | обработчик ребра для индексов таблицы #00 |
| #C6EA | [ThreeD.EdgeCase59](../Source/ThreeD/EdgeCase59.asm) | обработчик ребра для индексов таблицы #59, #65, #9A, #A6 |
| #C6F4 | [ThreeD.UnknownC6F4](../Source/ThreeD/UnknownC6F4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C88C | [ThreeD.UnknownC88C](../Source/ThreeD/UnknownC88C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CAB3 | [ThreeD.UnknownCAB3](../Source/ThreeD/UnknownCAB3.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CAE3 | [ThreeD.UnknownCAE3](../Source/ThreeD/UnknownCAE3.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CF08 | [ThreeD.UnknownCF08](../Source/ThreeD/UnknownCF08.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D10A | [ThreeD.ClearWorkBuffer](../Source/ThreeD/ClearWorkBuffer.asm) | Заполнение #0C00 байт до #8C00 значением #FF через стек с восстановлением SP |
| #D12C | [ThreeD.MultiplySignedScaled](../Source/ThreeD/MultiplySignedScaled.asm) | Знаковое умножение с масштабом 1/128 для коэффициента от -127 до 127, выход через JP (IX) |
| #E500 | [Voxel.RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | Последовательное преобразование трёх векторов ориентации #9B00..#9B11 по углам #9B14, #9B12 и #9B13 |
| #E8A1 | [Voxel.SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | Знаковое табличное произведение с использованием входного IY как младшей части накопителя |
| #EC00 | [Voxel.CreateSmallEffect](../Source/Voxel/CreateSmallEffect.asm) | Инициализация эффекта с ресурсом #D800 и параметрами #0C, #0C, #0D |
| #EC0E | [Voxel.ConfigureSmallEffect](../Source/Voxel/ConfigureSmallEffect.asm) | Общий хвост малого эффекта, настройка параметров #0C и #0D перед поиском свободной записи |
| #EC1B | [Voxel.CreateLargeEffect](../Source/Voxel/CreateLargeEffect.asm) | Инициализация эффекта с ресурсом #C400 и параметрами #14, #14, #08 |
| #EC33 | [Voxel.AllocateEffect](../Source/Voxel/AllocateEffect.asm) | Поиск свободной записи #12 байт по знаку и нулевому признаку в поле +7 |
| #EC7F | [Voxel.ClipSprite](../Source/Voxel/ClipSprite.asm) | Отсечение прямоугольника по горизонтали 64 и вертикали 24 с расчётом краевых смещений |
| #F931 | [Voxel.Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | Умножение младших семи битов A на BC с результатом HL modulo #10000 |
| #F957 | [Voxel.Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | Деление младших семи битов A на E с восемью дробными битами, подтверждённый делитель 1..128 |
| #C870 | [Controls.UnknownC870](../Source/Controls/UnknownC870.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #C882 | [Controls.UnknownC882](../Source/Controls/UnknownC882.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CA8D | [Controls.UnknownCA8D](../Source/Controls/UnknownCA8D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CAB3 | [Controls.UnknownCAB3](../Source/Controls/UnknownCAB3.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CAE3 | [Controls.UnknownCAE3](../Source/Controls/UnknownCAE3.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CB00 | [Controls.UnknownCB00](../Source/Controls/UnknownCB00.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CE16 | [Controls.UnknownCE16](../Source/Controls/UnknownCE16.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CEA4 | [Controls.UnknownCEA4](../Source/Controls/UnknownCEA4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CECF | [Controls.UnknownCECF](../Source/Controls/UnknownCECF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CEFA | [Controls.UnknownCEFA](../Source/Controls/UnknownCEFA.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #CF0B | [Controls.UnknownCF0B](../Source/Controls/UnknownCF0B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D0CA | [Controls.UnknownD0CA](../Source/Controls/UnknownD0CA.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D10A | [Controls.UnknownD10A](../Source/Controls/UnknownD10A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D165 | [Controls.UnknownD165](../Source/Controls/UnknownD165.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D167 | [Controls.UnknownD167](../Source/Controls/UnknownD167.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D18D | [Controls.UnknownD18D](../Source/Controls/UnknownD18D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D1A2 | [Controls.UnknownD1A2](../Source/Controls/UnknownD1A2.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D1B6 | [Controls.UnknownD1B6](../Source/Controls/UnknownD1B6.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D1CB | [Controls.UnknownD1CB](../Source/Controls/UnknownD1CB.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D1DF | [Controls.UnknownD1DF](../Source/Controls/UnknownD1DF.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D1F4 | [Controls.UnknownD1F4](../Source/Controls/UnknownD1F4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D208 | [Controls.UnknownD208](../Source/Controls/UnknownD208.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D211 | [Controls.UnknownD211](../Source/Controls/UnknownD211.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D21A | [Controls.UnknownD21A](../Source/Controls/UnknownD21A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D232 | [Controls.UnknownD232](../Source/Controls/UnknownD232.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D236 | [Controls.UnknownD236](../Source/Controls/UnknownD236.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D30B | [Controls.UnknownD30B](../Source/Controls/UnknownD30B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D320 | [Controls.UnknownD320](../Source/Controls/UnknownD320.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D4CB | [Controls.UnknownD4CB](../Source/Controls/UnknownD4CB.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D4E4 | [Controls.UnknownD4E4](../Source/Controls/UnknownD4E4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D504 | [Controls.UnknownD504](../Source/Controls/UnknownD504.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D515 | [Controls.UnknownD515](../Source/Controls/UnknownD515.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D53C | [Controls.UnknownD53C](../Source/Controls/UnknownD53C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D56C | [Controls.UnknownD56C](../Source/Controls/UnknownD56C.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D57B | [Controls.UnknownD57B](../Source/Controls/UnknownD57B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D609 | [Controls.UnknownD609](../Source/Controls/UnknownD609.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D727 | [Controls.UnknownD727](../Source/Controls/UnknownD727.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D833 | [Controls.UnknownD833](../Source/Controls/UnknownD833.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D925 | [Controls.UnknownD925](../Source/Controls/UnknownD925.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D940 | [Controls.UnknownD940](../Source/Controls/UnknownD940.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D95F | [Controls.UnknownD95F](../Source/Controls/UnknownD95F.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D9B0 | [Controls.UnknownD9B0](../Source/Controls/UnknownD9B0.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D9DE | [Controls.UnknownD9DE](../Source/Controls/UnknownD9DE.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DAB9 | [Controls.UnknownDAB9](../Source/Controls/UnknownDAB9.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DADE | [Controls.RunTemporaryModule](../Source/Controls/RunTemporaryModule.asm) | Сохранение памяти по банкам, распаковка временного модуля и восстановление полётного кода |
| #DC9B | [Controls.UnknownDC9B](../Source/Controls/UnknownDC9B.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DD5D | [Controls.UnknownDD5D](../Source/Controls/UnknownDD5D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DE0A | [Controls.UnknownDE0A](../Source/Controls/UnknownDE0A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DE10 | [Controls.UnknownDE10](../Source/Controls/UnknownDE10.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #DE9A | [Controls.UnknownDE9A](../Source/Controls/UnknownDE9A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E021 | [Controls.UnknownE021](../Source/Controls/UnknownE021.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E14E | [Controls.UnknownE14E](../Source/Controls/UnknownE14E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E291 | [Controls.UnknownE291](../Source/Controls/UnknownE291.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E8FD | [Controls.UnknownE8FD](../Source/Controls/UnknownE8FD.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #E97A | [Controls.UnknownE97A](../Source/Controls/UnknownE97A.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EC0E | [Controls.UnknownEC0E](../Source/Controls/UnknownEC0E.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EC56 | [Controls.UnknownEC56](../Source/Controls/UnknownEC56.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EC59 | [Controls.UnknownEC59](../Source/Controls/UnknownEC59.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #ECA2 | [Controls.UnknownECA2](../Source/Controls/UnknownECA2.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #ECF3 | [Controls.UnknownECF3](../Source/Controls/UnknownECF3.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #ED28 | [Controls.UnknownED28](../Source/Controls/UnknownED28.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EFC4 | [Controls.UnknownEFC4](../Source/Controls/UnknownEFC4.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #EFF1 | [Controls.UnknownEFF1](../Source/Controls/UnknownEFF1.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F094 | [Controls.UnknownF094](../Source/Controls/UnknownF094.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F10D | [Controls.UnknownF10D](../Source/Controls/UnknownF10D.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F142 | [Controls.UnknownF142](../Source/Controls/UnknownF142.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #F188 | [Controls.UnknownF188](../Source/Controls/UnknownF188.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #6000 | [Final.InitializeFinal](../Source/Final/InitializeFinal.asm) | Подготовка трёх экранных банков, таблицы IM 2 и финальной анимации |
| #6123 | [Final.ReadSpeedKeys](../Source/Final/ReadSpeedKeys.asm) | Изменение счётчика задержки клавишами Q и A с границами 0..100 |
| #6148 | [Final.HaltFinal](../Source/Final/HaltFinal.asm) | Выбор страниц и режима IM 0, очистка атрибутов теневого экрана и остановка через DI и HALT |
| #616C | [Final.Interrupt](../Source/Final/Interrupt.asm) | Обработчик прерывания финальной сцены |
| #6196 | [Final.PrepareFrame](../Source/Final/PrepareFrame.asm) | Подготовка изменяемой цепочки команд финальной анимации |
| #61DF | [Final.BuildDisplayChain](../Source/Final/BuildDisplayChain.asm) | Создание 24 групп по восемь bitmap-строк и полосе атрибутов с двумя местами вставки синхронизации |
| #620E | [Final.EmitBitmapLine](../Source/Final/EmitBitmapLine.asm) | Копирование 52-байтового образца переноса строки и обновление четырёх адресов SP |
| #6234 | [Final.EmitAttributeRow](../Source/Final/EmitAttributeRow.asm) | Копирование 23-байтового образца атрибутов и переход к следующему 32-байтовому ряду |
| #6296 | [Final.NextBitmapLine](../Source/Final/NextBitmapLine.asm) | Переход к следующей пиксельной строке в экранной раскладке Spectrum |
| #6247 | [FinalTemplates.BitmapLine](../Source/FinalTemplates/BitmapLine.asm) | 52-байтовый образец переноса 32 байтов строки через два набора регистров и временный SP |
| #627D | [FinalTemplates.AttributeRow](../Source/FinalTemplates/AttributeRow.asm) | 23-байтовый образец заполнения 32 атрибутов байтом из альтернативного A |

## DescribeCurrentKeyForLang

[DescribeCurrentKeyForLang](../Source/Station/DescribeCurrentKeyForLang.asm) — Характеристика текущего ключа с возвратом банка языка 6. CPU #A480, 11 исходных байтов. Подробный контракт находится в исходнике и документе SignatureReturn.md.

## DescribeKeyForLang

[DescribeKeyForLang](../Source/Station/DescribeKeyForLang.asm) — Характеристика входного ключа с возвратом банка языка 6. CPU #A48B, 11 исходных байтов. Подробный контракт находится в исходнике и документе SignatureReturn.md.

| #6E9C | [Station.ProcessMissionAction](../Source/Station/ProcessMissionAction.asm) | Проверка селектора и строки, принятие либо расторжение миссии с общей перерисовкой |

| #6F5D | [Station.CancelMission](../Source/Station/CancelMission.asm) | Расторжение миссии на сохранённом кадре, пересчёт загрузки и денежный штраф |

| #C44A | [Map.BuildMapQuadrantTables](../Source/Map/BuildMapQuadrantTables.asm) | Построение четырёх 256-байтовых таблиц соседних секторов карты |

| #C474 | [Map.BuildMapSectorTable](../Source/Map/BuildMapSectorTable.asm) | Формирование таблицы одного сектора с возвратом в противоположном общем наборе |

| #D4DD | [Map.MapClipCases](../Source/Map/MapClipCases.asm) | Unknown, группа косвенных обработчиков, смысловой разбор продолжается |

| #D8E2 | [Map.ComputeTopClipProduct](../Source/Map/ComputeTopClipProduct.asm) | Произведение (Y1-MinY)*(X1-X2) для верхней границы окна |

| #D901 | [Map.ComputeBottomClipProduct](../Source/Map/ComputeBottomClipProduct.asm) | Произведение (Y1-MaxY)*(X1-X2) для нижней границы окна |

| #D920 | [Map.ComputeLeftClipProduct](../Source/Map/ComputeLeftClipProduct.asm) | Произведение (Y1-Y2)*(X1-MinX) для левой границы окна |

| #D93F | [Map.ComputeRightClipProduct](../Source/Map/ComputeRightClipProduct.asm) | Произведение (Y1-Y2)*(X1-MaxX) для правой границы окна |

| #D95E | [Map.AppendTopClipIntersection](../Source/Map/AppendTopClipIntersection.asm) | Добавление пересечения с верхней границей окна в выходной список |

| #D9A9 | [Map.AppendBottomClipIntersection](../Source/Map/AppendBottomClipIntersection.asm) | Добавление пересечения с нижней границей окна в выходной список |

| #D9F4 | [Map.AppendLeftClipIntersection](../Source/Map/AppendLeftClipIntersection.asm) | Добавление пересечения с левой границей окна в выходной список |

| #DA52 | [Map.AppendRightClipIntersection](../Source/Map/AppendRightClipIntersection.asm) | Добавление пересечения с правой границей окна в выходной список |

| #DAB0 | [Map.AppendTopLeftCorner](../Source/Map/AppendTopLeftCorner.asm) | Условное добавление верхнего левого угла окна |

| #DABB | [Map.AppendTopRightCorner](../Source/Map/AppendTopRightCorner.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DAC6 | [Map.AppendBottomLeftCorner](../Source/Map/AppendBottomLeftCorner.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DAD1 | [Map.AppendBottomRightCorner](../Source/Map/AppendBottomRightCorner.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DADC | [Map.SubtractTopLeftProducts](../Source/Map/SubtractTopLeftProducts.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DAF0 | [Map.SubtractTopRightProducts](../Source/Map/SubtractTopRightProducts.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB04 | [Map.SubtractBottomLeftProducts](../Source/Map/SubtractBottomLeftProducts.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB18 | [Map.SubtractBottomRightProducts](../Source/Map/SubtractBottomRightProducts.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB2C | [Map.SubtractClipPointX](../Source/Map/SubtractClipPointX.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB37 | [Map.SubtractClipPointY](../Source/Map/SubtractClipPointY.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB42 | [Map.AppendSecondClipPoint](../Source/Map/AppendSecondClipPoint.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

| #DB59 | [Map.UnwindClipFrame](../Source/Map/UnwindClipFrame.asm) | Unknown, самостоятельный вход общего хвоста отсечения |

[DrawClippedArcPair](../Source/Map/DrawClippedArcPair.asm) — Unknown, растровый вход после самостоятельной подготовки.

[RasterizeArcEdges](../Source/Map/RasterizeArcEdges.asm) — Unknown, растровый вход после самостоятельной подготовки.

| #6774 | [Station.HandleShipModelAction](../Source/Station/HandleShipModelAction.asm) | Развилка действия списка моделей после перерисовки, выбор строки либо закрытие группы |

| #67A9 | [Station.ShipModelChoice](../Source/Station/ShipModelChoice.asm) | Пустая ветвь действия и отдельное применение выбранной строки с отложенной перерисовкой |

| #683A | [Station.HandleModelPreviewClick](../Source/Station/HandleModelPreviewClick.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6916 | [Station.HandleModelDescriptionClick](../Source/Station/HandleModelDescriptionClick.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6963 | [Station.CountModelDescriptionRows](../Source/Station/CountModelDescriptionRows.asm) | Unknown, новый вход действия или его достижимый помощник |

| #697B | [Station.HandleHelpTextAction](../Source/Station/HandleHelpTextAction.asm) | Закрытие связанной пары либо прокрутка LF-текста, выбор единицей ничего не делает |

| #69E0 | [Station.HandleHelpContentsAction](../Source/Station/HandleHelpContentsAction.asm) | Закрытие пары, прокрутка CR-заголовков либо выбор раздела с перерисовкой обеих панелей |

| #6A86 | [Station.HandleEquipmentInfoAction](../Source/Station/HandleEquipmentInfoAction.asm) | Закрытие либо прокрутка документации оснащения, выбор единицей пустой |

| #6AAF | [Station.TryDrawEquipmentInfo](../Source/Station/TryDrawEquipmentInfo.asm) | Условное рисование документации только при точном указателе в списке |

| #6AEC | [Station.HandleEnvironmentAction](../Source/Station/HandleEnvironmentAction.asm) | Закрытие с применением настроек среды, прокрутка, Y/N и ограниченный ввод клавиш или цветов |

| #6B9E | [Station.TryDrawEnvironmentPanel](../Source/Station/TryDrawEnvironmentPanel.asm) | Условное рисование установок среды при точном указателе панели в списке |

| #6C0D | [Station.HandleMapPanelEvent](../Source/Station/HandleMapPanelEvent.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6D44 | [Station.RefreshMapPanel](../Source/Station/RefreshMapPanel.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6D4E | [Station.ClearAndDrawMapPanel](../Source/Station/ClearAndDrawMapPanel.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6DC5 | [Station.HandleDecodedMessageClick](../Source/Station/HandleDecodedMessageClick.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6E82 | [Station.HandleQueuedMessageClick](../Source/Station/HandleQueuedMessageClick.asm) | Unknown, новый вход действия или его достижимый помощник |

| #6FF1 | [Station.HandleTradePanelClick](../Source/Station/HandleTradePanelClick.asm) | Unknown, новый вход действия или его достижимый помощник |

| #7175 | [Station.HandleEquipmentListAction](../Source/Station/HandleEquipmentListAction.asm) | Выбор описания либо подтверждение сделки оснащения, закрытие группы и прокрутка списка |

| #7220 | [Station.TryDrawEquipmentList](../Source/Station/TryDrawEquipmentList.asm) | Условное рисование списка оснащения только при точном указателе в списке |

| #7421 | [Station.HandleSaveSlotAction](../Source/Station/HandleSaveSlotAction.asm) | Выбор позиции и запись двух секторов блока состояния в существующий SAVE-файл |

| #74AA | [Station.HandleLoadSlotAction](../Source/Station/HandleLoadSlotAction.asm) | Выбор позиции и чтение двух секторов существующего SAVE-файла в блок состояния |

| #759C | [Station.HandleGameSettingsAction](../Source/Station/HandleGameSettingsAction.asm) | Закрытие с применением игровых настроек, прокрутка и редактирование переключателя или клавиши |

| #7630 | [Station.TryDrawGameSettings](../Source/Station/TryDrawGameSettings.asm) | Условное рисование установок игры при точном указателе панели в списке |

| #7679 | [Station.HandleSystemInfoAction](../Source/Station/HandleSystemInfoAction.asm) | Общая перерисовка и закрытие информационного окна, селектор 1 не меняет содержимое |

| #783B | [Station.HandleSystemMapAction](../Source/Station/HandleSystemMapAction.asm) | Выбор ближайшего варианта системы либо закрытие карты с отключением её периодического обновления |

| #7885 | [Station.TryDrawVariantPanel](../Source/Station/TryDrawVariantPanel.asm) | Unknown, новый вход действия или его достижимый помощник |

| #794B | [Station.HandleWelcomeAction](../Source/Station/HandleWelcomeAction.asm) | Общая перерисовка и закрытие приветствия, селектор 1 не меняет содержимое |

| #A191 | [Station.ParseSettingsLabel](../Source/Station/ParseSettingsLabel.asm) | Unknown, новый вход действия или его достижимый помощник |

| #A1D6 | [Station.ScrollWindowRows](../Source/Station/ScrollWindowRows.asm) | Unknown, новый вход действия или его достижимый помощник |

| #A26F | [Station.XorRowIfSelected](../Source/Station/XorRowIfSelected.asm) | Unknown, новый вход действия или его достижимый помощник |

| #AA58 | [Station.HandleMissionGroupAction](../Source/Station/HandleMissionGroupAction.asm) | Общее действие панели миссии и условное закрытие трёх связанных панелей |

| #BE27 | [Station.MoveItemToTailIfListed](../Source/Station/MoveItemToTailIfListed.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C6B0 | [Station.ClearScrollWindowBody](../Source/Station/ClearScrollWindowBody.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C368 | [Map.SumSquares8](../Source/Map/SumSquares8.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C38C | [Map.SelectNearestVisiblePoint](../Source/Map/SelectNearestVisiblePoint.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C4E5 | [Map.BuildVisibleMapPoints](../Source/Map/BuildVisibleMapPoints.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C5E8 | [Map.SelectNearestMapVariant](../Source/Map/SelectNearestMapVariant.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C653 | [Map.UpdateMapDistanceMinimum](../Source/Map/UpdateMapDistanceMinimum.asm) | Unknown, новый вход действия или его достижимый помощник |

| #D0C3 | [Map.SetupMapRasterWindow](../Source/Map/SetupMapRasterWindow.asm) | Unknown, новый вход действия или его достижимый помощник |

| #C677 | [Map.DrawVariantCluster](../Source/Map/DrawVariantCluster.asm) | XOR центральной пятистрочной метки и последовательная анимация не более шести вариантов |

| #C6C0 | [Map.AnimateVariant0](../Source/Map/AnimateVariant0.asm) | Анимационный шаг варианта 0 и последующее исполнение оставшихся обёрток |

| #C6DD | [Map.AnimateVariant1](../Source/Map/AnimateVariant1.asm) | Анимационный шаг варианта 1 и последующее исполнение оставшихся обёрток |

| #C6FA | [Map.AnimateVariant2](../Source/Map/AnimateVariant2.asm) | Анимационный шаг варианта 2 и последующее исполнение оставшихся обёрток |

| #C717 | [Map.AnimateVariant3](../Source/Map/AnimateVariant3.asm) | Анимационный шаг варианта 3 и последующее исполнение оставшихся обёрток |

| #C734 | [Map.AnimateVariant4](../Source/Map/AnimateVariant4.asm) | Анимационный шаг варианта 4 и последующее исполнение оставшихся обёрток |

| #C751 | [Map.AnimateVariant5](../Source/Map/AnimateVariant5.asm) | Анимационный шаг варианта 5 и последующее исполнение оставшихся обёрток |

| #C76E | [Map.SelectBlinkingVariant](../Source/Map/SelectBlinkingVariant.asm) | Циклическое мигание выбранного варианта заменой ресурса по младшему биту маски |

| #C827 | [Map.XorVariantPhase](../Source/Map/XorVariantPhase.asm) | Чтение пары смещений, уменьшение альтернативного счётчика и XOR трёхстрочной фазы |

| #A806 | [Station.SwitchItemContour](../Source/Station/SwitchItemContour.asm) | Unknown, независимый соседний вход |

| #78BD | [Station.RefreshVariantPanel](../Source/Station/RefreshVariantPanel.asm) | Отложенный перенос панели в конец списка и перерисовка через теневой экран |

| #78D6 | [Station.UpdateVariantPanel](../Source/Station/UpdateVariantPanel.asm) | Периодическая очистка и банковая анимация панели с отдельной ветвью отложенного обновления |

| #6C6E | [Station.PanMapView](../Source/Station/PanMapView.asm) | Unknown, самостоятельный исходный вход |

| #6D0D | [Station.SelectMapPointAndRefresh](../Source/Station/SelectMapPointAndRefresh.asm) | Unknown, самостоятельный исходный вход |

| #7B9B | [Station.RefreshStoredMapPanels](../Source/Station/RefreshStoredMapPanels.asm) | Unknown, самостоятельный вход |

| #7BAE | [Station.RemoveFoundStoredPoint](../Source/Station/RemoveFoundStoredPoint.asm) | Unknown, самостоятельный вход |

| #7C24 | [Station.RemoveFoundSecondaryPoint](../Source/Station/RemoveFoundSecondaryPoint.asm) | Unknown, самостоятельный вход |

| #7C4A | [Station.RefreshSecondaryListPanels](../Source/Station/RefreshSecondaryListPanels.asm) | Unknown, самостоятельный вход |

| #7D14 | [Station.CenterKeyAndRefreshMap](../Source/Station/CenterKeyAndRefreshMap.asm) | Unknown, самостоятельный вход |

| #4000 | [StationFinalExit.LoadFinal](../Source/StationFinalExit/LoadFinal.asm) | Перенесённый загрузчик FINALF с повторной инициализацией музыки и ожиданием точного байта клавиатуры |

| #A1CD | [Station.RestoreScrollPointer](../Source/Station/RestoreScrollPointer.asm) | Unknown, самостоятельный вход |

| #7061 | [Station.UpdateTradeRowHover](../Source/Station/UpdateTradeRowHover.asm) | Unknown, самостоятельный вход |

## Дополнительно обнаруженный корабельный код

| Адрес | Исходник | Статус |
| --- | --- | --- |
| #6870 | [Station.TryDrawShipPreview](../Source/Station/TryDrawShipPreview.asm) | Рисование корабельного просмотра только при наличии точного указателя обработчика |
| #68CC | [Station.RefreshShipPanels](../Source/Station/RefreshShipPanels.asm) | Отложенное обновление списка моделей, описания и перенесённого в конец корабельного просмотра |
| #68EA | [Station.AnimateShipPreview](../Source/Station/AnimateShipPreview.asm) | Периодическое рисование кадра последней корабельной панели либо переход к её отложенному обновлению |
| #693E | [Station.TryDrawModelDescription](../Source/Station/TryDrawModelDescription.asm) | Unknown, полный контракт ещё не доказан |

| #E011, банк 4 | [D3D.ConfigurePreviewClip](../Source/D3D/ConfigurePreviewClip.asm) | Настройка четырёх углов и повторённых операндов границ корабельного просмотра |

| #E0B5, банк 4 | [D3D.AdjustPreviewThird](../Source/D3D/AdjustPreviewThird.asm) | Изменение третьей координаты записи просмотра с принятием обёрнутой суммы только в 512..4095 |

| #E13C, банк 4 | [D3D.SetupPreviewModel](../Source/D3D/SetupPreviewModel.asm) | Настройка границ и трёх таблиц просмотра с выбором байтового смещения модели |

| #E124, банк 4 | [D3D.CountPreviewTextRows](../Source/D3D/CountPreviewTextRows.asm) | Подсчёт выровненных строк выбранного описания корабля либо скимера |

| #E154, банк 4 | [D3D.PrintPreviewTextRows](../Source/D3D/PrintPreviewTextRows.asm) | Печать выбранного описания корабля либо скимера с байтовым пропуском строк |

| #E0C5, банк 4 | [D3D.DrawPreviewPrices](../Source/D3D/DrawPreviewPrices.asm) | Вывод цен доступных моделей либо одной собственной модели с временным ограничителем текста |

| #EB10, банк 4 | [D3D.MultiplyPreviewCoordinate](../Source/D3D/MultiplyPreviewCoordinate.asm) | Знаковое произведение 16-битной координаты и 7-битного коэффициента с усечением после деления на 128 и переходным возвратом |

| #EB7E, банк 4 | [D3D.TransformPreviewCoords](../Source/D3D/TransformPreviewCoords.asm) | Три скалярных произведения с переносом знакового умножителя, ранним переполнением и продолжением через IY |

| #EE24, банк 4 | [D3D.InsertPreviewQueue](../Source/D3D/InsertPreviewQueue.asm) | Вставка четырнадцатибайтового узла по двум ключам с выбором по биту 7 и прекращением обхода при заполнении |

| #D518, банк 4 | [D3D.LookupPreviewProductE](../Source/D3D/LookupPreviewProductE.asm) | Табличная аппроксимация произведения байтов A и E через разность свёрнутых квадратов |

| #D525, банк 4 | [D3D.LookupPreviewProductB](../Source/D3D/LookupPreviewProductB.asm) | Табличная аппроксимация произведения байтов A и B через разность свёрнутых квадратов |

| #D532, банк 4 | [D3D.LookupPreviewProductC](../Source/D3D/LookupPreviewProductC.asm) | Табличная аппроксимация произведения байтов A и C через разность свёрнутых квадратов |

| #D53F, банк 4 | [D3D.LookupPreviewProductD](../Source/D3D/LookupPreviewProductD.asm) | Табличная аппроксимация произведения байтов A и D через разность свёрнутых квадратов |

| #EDB0, банк 4 | [D3D.CheckPreviewBounds](../Source/D3D/CheckPreviewBounds.asm) | Проверка четырёх обёрнутых знаковых границ с табличными размерами и продолжением во вставку очереди |

| #EC28, банк 4 | [D3D.BuildPreviewQueue](../Source/D3D/BuildPreviewQueue.asm) | Подготовка коэффициентов, обход исходных записей с шагом 64, преобразование, отбор и сборка очереди перед рисованием |

| #EF5E, банк 4 | [D3D.BuildPreviewModelMatrix](../Source/D3D/BuildPreviewModelMatrix.asm) | Матрица ориентации модели по трём байтовым углам либо упрощённая матрица по второму углу |

| #D54C, банк 4 | [D3D.ComposePreviewMatrix](../Source/D3D/ComposePreviewMatrix.asm) | Композиция матрицы сцены и модели с отражаемой арифметикой, одноосной ветвью и точными четвертьоборотами |

| #DBD9, банк 4 | [D3D.ConfigurePreviewProjectionScale](../Source/D3D/ConfigurePreviewProjectionScale.asm) | Настройка трёх последовательностей масштаба проекции по показателю заголовка модели |

| #DA14, банк 4 | [D3D.ProjectPreviewVertex](../Source/D3D/ProjectPreviewVertex.asm) | Перспектива одной вершины с двумя знаковыми делениями, маркерами отказа и пятибайтовым шагом рабочего SP |

| #D908, банк 4 | [D3D.ProjectPreviewVertexGroup](../Source/D3D/ProjectPreviewVertexGroup.asm) | Генерация комбинаций вершин по маске с настоящей перспективой, рабочим стеком и восстановлением CPU-возврата |

| #D85E, банк 4 | [D3D.ProjectPlanarVertexGroup](../Source/D3D/ProjectPlanarVertexGroup.asm) | Произведения плоской группы с прямой второй компонентой и переходом к генератору вершин |

| #D8BE, банк 4 | [D3D.PreparePreviewVertexProducts](../Source/D3D/PreparePreviewVertexProducts.asm) | Девять табличных произведений общей матрицы с последовательным продолжением в генератор группы |

| #D819, банк 4 | [D3D.ProjectPlanarModelGroups](../Source/D3D/ProjectPlanarModelGroups.asm) | Подготовка относительного угла плоского входа и проекция всех физических групп выбранной модели |

| #D896, банк 4 | [D3D.ProjectPreviewModelGroups](../Source/D3D/ProjectPreviewModelGroups.asm) | Проекция всех физических групп выбранной модели через общую матрицу и восстановление CPU-стека |

| #DF46, банк 4 | [D3D.ClassifyPreviewVertices](../Source/D3D/ClassifyPreviewVertices.asm) | Коды сторон окна для спроецированных вершин, инверсная старшая тетрада и ранний отказ по маркеру 80 |

| #E869, банк 4 | [D3D.MultiplyPreviewSignedWords](../Source/D3D/MultiplyPreviewSignedWords.asm) | Знаковое произведение слов с тремя размерными ветвями и особым длинным случаем второго слова 8000 |

| #DFA6, банк 4 | [D3D.ComputePreviewFaceOrientation](../Source/D3D/ComputePreviewFaceOrientation.asm) | Ориентация по трём вершинам с выбором индексов, цепочкой заёмов и двумя настоящими произведениями |

| #DDFD, банк 4 | [D3D.CollectPreviewFaceCodes](../Source/D3D/CollectPreviewFaceCodes.asm) | Общий OR кодов вершин грани с ранним Carry по нулевому коду и восстановлением счётчика |

| #DE1C, банк 4 | [D3D.RasterizePreviewEdge](../Source/D3D/RasterizePreviewEdge.asm) | Растровое ребро с исключённым концом, четырьмя ветвями, режимами XOR/OR/AND и точными флагами |

| #D4DF, банк 4 | [D3D.DividePreviewSlopeByte](../Source/D3D/DividePreviewSlopeByte.asm) | Восемь шагов деления горизонтальной длины ребра с дополненным частным и остатком |

| #D207, банк 4 | [D3D.StepPreviewPolygonRow](../Source/D3D/StepPreviewPolygonRow.asm) | Продвижение двух рёбер, экранной строки и шаблона, вывод полосы и общий возврат |

| #D1C0, банк 4 | [D3D.WritePreviewPolygonSpan](../Source/D3D/WritePreviewPolygonSpan.asm) | Развёрнутая запись 0..31 полного байта и маскированный правый край с продолжением в цикл строк |

| #D282, банк 4 | [D3D.SelectPreviewRightEdge](../Source/D3D/SelectPreviewRightEdge.asm) | Переход к обновлению прямой правой цепочки без CPU-вызова |

| #D285, банк 4 | [D3D.WrapPreviewLeftEdge](../Source/D3D/WrapPreviewLeftEdge.asm) | Переход обратной цепочки к последней строковой координате контура |

| #D28C, банк 4 | [D3D.UpdatePreviewLeftEdge](../Source/D3D/UpdatePreviewLeftEdge.asm) | Выбор восходящего левого ребра, деление наклона и подготовка шага и ошибки |

| #D34B, банк 4 | [D3D.WrapPreviewRightEdge](../Source/D3D/WrapPreviewRightEdge.asm) | Переход прямой цепочки к первой строковой координате контура |

| #D350, банк 4 | [D3D.UpdatePreviewRightEdge](../Source/D3D/UpdatePreviewRightEdge.asm) | Выбор восходящего правого ребра и подготовка его шага, ошибки и следующей строки |

| #D40F, банк 4 | [D3D.WrapPreviewTopLeft](../Source/D3D/WrapPreviewTopLeft.asm) | Переход верхнего обратного поиска к последней строке контура через AF' |

| #D416, банк 4 | [D3D.WrapPreviewTopRight](../Source/D3D/WrapPreviewTopRight.asm) | Переход верхнего прямого поиска к первой строке контура |

| #D41B, банк 4 | [D3D.FillPreviewPolygon](../Source/D3D/FillPreviewPolygon.asm) | Подготовка двух границ и шаблона, временного стека и полный проход заливки многоугольника |

| #DD4F, банк 4 | [D3D.RenderPreviewInsideFaces](../Source/D3D/RenderPreviewInsideFaces.asm) | Обход граней и полилиний без отсечения с сохранённым кодом ориентации и тремя режимами рёбер |

| #E85D, банк 4 | [D3D.UnwindPreviewClipFrame](../Source/D3D/UnwindPreviewClipFrame.asm) | Снятие трёх служебных слов отсечения и возврат по настоящему CPU-адресу с Carry |

| #E84E, банк 4 | [D3D.AppendPreviewClipPoint](../Source/D3D/AppendPreviewClipPoint.asm) | Запись упакованной точки в страницу C8 с байтовым оборачиванием размера |

| #E846, банк 4 | [D3D.AppendPreviewClipSecond](../Source/D3D/AppendPreviewClipSecond.asm) | Упаковка младших байтов второго конца и последовательный вход в запись точки |

| #E830, банк 4 | [D3D.SubtractPreviewClipColumns](../Source/D3D/SubtractPreviewClipColumns.asm) | Разность знаковых слов колонок второго и первого конца с точными флагами SBC |

| #E83B, банк 4 | [D3D.SubtractPreviewClipRows](../Source/D3D/SubtractPreviewClipRows.asm) | Разность знаковых слов строк второго и первого конца с точными флагами SBC |

| #E7B4, банк 4 | [D3D.AppendPreviewClipTopLeft](../Source/D3D/AppendPreviewClipTopLeft.asm) | Добавление угла сверху слева при нулевом запрете углов |

| #E7BF, банк 4 | [D3D.AppendPreviewClipTopRight](../Source/D3D/AppendPreviewClipTopRight.asm) | Добавление угла сверху справа при нулевом запрете углов |

| #E7CA, банк 4 | [D3D.AppendPreviewClipBottomLeft](../Source/D3D/AppendPreviewClipBottomLeft.asm) | Добавление угла снизу слева при нулевом запрете углов |

| #E7D5, банк 4 | [D3D.AppendPreviewClipBottomRight](../Source/D3D/AppendPreviewClipBottomRight.asm) | Добавление угла снизу справа при нулевом запрете углов |

| #E7E0, банк 4 | [D3D.SubtractPreviewClipTopLeft](../Source/D3D/SubtractPreviewClipTopLeft.asm) | Разность кэшей Top и Left с заёмом младшего слова и возвратом старшего |

| #E7F4, банк 4 | [D3D.SubtractPreviewClipTopRight](../Source/D3D/SubtractPreviewClipTopRight.asm) | Разность кэшей Top и Right с заёмом младшего слова и возвратом старшего |

| #E808, банк 4 | [D3D.SubtractPreviewClipBottomLeft](../Source/D3D/SubtractPreviewClipBottomLeft.asm) | Разность кэшей Bottom и Left с заёмом младшего слова и возвратом старшего |

| #E81C, банк 4 | [D3D.SubtractPreviewClipBottomRight](../Source/D3D/SubtractPreviewClipBottomRight.asm) | Разность кэшей Bottom и Right с заёмом младшего слова и возвратом старшего |

| #E5E8, банк 4 | [D3D.BuildPreviewClipTopProduct](../Source/D3D/BuildPreviewClipTopProduct.asm) | Формирование кэша Top относительно границы с исходным порядком аргументов умножения |

| #E607, банк 4 | [D3D.BuildPreviewClipBottomProduct](../Source/D3D/BuildPreviewClipBottomProduct.asm) | Формирование кэша Bottom относительно границы с исходным порядком аргументов умножения |

| #E626, банк 4 | [D3D.BuildPreviewClipLeftProduct](../Source/D3D/BuildPreviewClipLeftProduct.asm) | Формирование кэша Left относительно границы с исходным порядком аргументов умножения |

| #E645, банк 4 | [D3D.BuildPreviewClipRightProduct](../Source/D3D/BuildPreviewClipRightProduct.asm) | Формирование кэша Right относительно границы с исходным порядком аргументов умножения |

| #EA01, банк 4 | [D3D.DividePreviewClip32To16](../Source/D3D/DividePreviewClip32To16.asm) | Деление HL:A:A' на DE с входным знаком делителя и однокомплементными отрицательными значениями |

| #E664, банк 4 | [D3D.AppendPreviewClipTopIntersection](../Source/D3D/AppendPreviewClipTopIntersection.asm) | Пересечение с границей Top и запись исходной байтовой проекции в контур C8 |

| #E6AF, банк 4 | [D3D.AppendPreviewClipBottomIntersection](../Source/D3D/AppendPreviewClipBottomIntersection.asm) | Пересечение с границей Bottom и запись исходной байтовой проекции в контур C8 |

| #E6FA, банк 4 | [D3D.AppendPreviewClipLeftIntersection](../Source/D3D/AppendPreviewClipLeftIntersection.asm) | Пересечение с границей Left и запись исходной байтовой проекции в контур C8 |

| #E757, банк 4 | [D3D.AppendPreviewClipRightIntersection](../Source/D3D/AppendPreviewClipRightIntersection.asm) | Пересечение с границей Right и запись исходной байтовой проекции в контур C8 |

| #E1EB, банк 4 | [D3D.PreviewClipCases](../Source/D3D/PreviewClipCases.asm) | Решения отсечения по паре зон, порядок пересечений и накопление отметок углов |

| #EAB6, банк 4 | [D3D.DispatchPreviewClipSegment](../Source/D3D/DispatchPreviewClipSegment.asm) | Перестановка внутреннего первого конца и табличное отсечение отдельного сегмента |

| #E171, банк 4 | [D3D.ClipPreviewPolygon](../Source/D3D/ClipPreviewPolygon.asm) | Замкнутый обход индексов проекции, отсечение каждого ребра и приём контура по размеру |

| #DBE9, банк 4 | [D3D.RenderPreviewClippedFaces](../Source/D3D/RenderPreviewClippedFaces.asm) | Полный поток граней и полилиний с кодами сторон и обоими отсекателями |

| #EEF1, банк 4 | [D3D.RenderPreviewQueue](../Source/D3D/RenderPreviewQueue.asm) | Обход связанной очереди, загрузка параметров узла и выбор внутреннего либо отсечённого рисователя |

| #EEEE, банк 4 | [D3D.RestorePreviewStack](../Source/D3D/RestorePreviewStack.asm) | Восстановление CPU-SP из изменяемого операнда и последовательный вход в рисование очереди |

| #E07F, банк 4 | [D3D.RenderPreviewFrame](../Source/D3D/RenderPreviewFrame.asm) | Изменение ориентации первой записи, полный графический проход, EI и переключение заполнения граней |

| Адрес | Процедура | Назначение |
| --- | --- | --- |
| #7F30 | [Station.ResumeActionPointer](../Source/Station/ResumeActionPointer.asm) | Возобновление указателя после RET непрямого рисователя с продолжением восстановления AF |

[StageEnvelopeAndNoise](../Source/Music/StageEnvelopeAndNoise.asm) — Подготовка формы огибающей и шума, перезапуск её периода и отложенного скольжения.

[CommitEnvelopeSlide](../Source/Music/CommitEnvelopeSlide.asm) — Фиксация шага и задержки скольжения огибающей перед продолжением разбора канала A.

| #DB8C | [Music.ReadEnvelopeSlide](../Source/Music/ReadEnvelopeSlide.asm) | Чтение задержки и знакового слова шага, включение отложенного скольжения огибающей |

| #E2EB | [Music.OutputAyFrame](../Source/Music/OutputAyFrame.asm) | Расчёт общей огибающей, восстановление стека и вывод регистров AY |


[Music.ReadGateTimingB](../Source/Music/ReadGateTimingB.asm) — Чтение двух длительностей чередования канала B. [Договор и проверка](MusicEffects.md).

[Music.SetGateTimingB](../Source/Music/SetGateTimingB.asm) — Установка двух подготовленных длительностей чередования канала B. [Договор и проверка](MusicEffects.md).

[Music.SetToneSlideA](../Source/Music/SetToneSlideA.asm) — Чтение задержки и шага неограниченного скольжения тона A. [Договор и проверка](MusicEffects.md).

[Music.SetTonePortamentoA](../Source/Music/SetTonePortamentoA.asm) — Настройка ограниченного скольжения от прежней ноты к новой цели A. [Договор и проверка](MusicEffects.md).

[Music.SetSamplePositionA](../Source/Music/SetSamplePositionA.asm) — Чтение позиции сэмпла канала A. [Договор и проверка](MusicEffects.md).

[Music.SetOrnamentPositionA](../Source/Music/SetOrnamentPositionA.asm) — Чтение позиции орнамента канала A. [Договор и проверка](MusicEffects.md).

[Music.SetToneSlideB](../Source/Music/SetToneSlideB.asm) — Чтение задержки и шага неограниченного скольжения тона B. [Договор и проверка](MusicEffects.md).

[Music.SetTonePortamentoB](../Source/Music/SetTonePortamentoB.asm) — Настройка ограниченного скольжения от прежней ноты к новой цели B. [Договор и проверка](MusicEffects.md).

[Music.SetSamplePositionB](../Source/Music/SetSamplePositionB.asm) — Чтение позиции сэмпла канала B. [Договор и проверка](MusicEffects.md).

[Music.SetOrnamentPositionB](../Source/Music/SetOrnamentPositionB.asm) — Чтение позиции орнамента канала B. [Договор и проверка](MusicEffects.md).

[Music.SetTonePortamentoC](../Source/Music/SetTonePortamentoC.asm) — Настройка ограниченного скольжения от прежней ноты к новой цели C. [Договор и проверка](MusicEffects.md).

[Music.SetSamplePositionC](../Source/Music/SetSamplePositionC.asm) — Чтение позиции сэмпла канала C. [Договор и проверка](MusicEffects.md).

[Music.SetOrnamentPositionC](../Source/Music/SetOrnamentPositionC.asm) — Чтение позиции орнамента канала C. [Договор и проверка](MusicEffects.md).

[Music.SetRowTempo](../Source/Music/SetRowTempo.asm) — Чтение и установка изменяемого темпа музыкальной строки. [Договор и проверка](MusicEffects.md).

| #E0ED | [Music.RenderChannelB](../Source/Music/RenderChannelB.asm) | Синтез сэмпла, орнамента, тона, шума и огибающей канала B |

| #E1ED | [Music.RenderChannelC](../Source/Music/RenderChannelC.asm) | Синтез сэмпла, орнамента, тона, шума и огибающей канала C |
| #E37C | [Music.AdvancePatternBC](../Source/Music/AdvancePatternBC.asm) | Распределение фаз разбора B и C, счётчиков строк и кодов подготовки следующего кадра |
| #E3DC | [Music.PatternCommandsA](../Source/Music/PatternCommandsA.asm) | Внутренние входы нот, громкости, огибающей и выбора сэмпла и орнамента A |
| #E439 | [Music.DecodePatternA](../Source/Music/DecodePatternA.asm) | Декодирование строки A с накоплением отложенных эффектов на CPU-стеке |
| #E489 | [Music.PatternCommandsB](../Source/Music/PatternCommandsB.asm) | Внутренние входы нот, громкости, огибающей и выбора сэмпла и орнамента B |
| #E4E6 | [Music.DecodePatternB](../Source/Music/DecodePatternB.asm) | Декодирование строки B, включая отдельную команду базового шума и отложенные эффекты |
| #E53D | [Music.PatternCommandsC](../Source/Music/PatternCommandsC.asm) | Внутренние входы громкости, выключения, огибающей и указателей канала C |
| #E583 | [Music.DecodePatternC](../Source/Music/DecodePatternC.asm) | Декодирование строки C с непосредственным сбросом новой ноты и отложенными эффектами |
