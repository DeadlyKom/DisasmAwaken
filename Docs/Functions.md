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
| Action | 307 | 306 | [Факты](FunctionDetails/Action.md) |
| ThreeD | 122 | 121 | [Факты](FunctionDetails/ThreeD.md) |
| Voxel | 12 | 12 | [Факты](FunctionDetails/Voxel.md) |
| Controls | 78 | 78 | [Факты](FunctionDetails/Controls.md) |
| Final | 9 | 9 | [Факты](FunctionDetails/Final.md) |
| FinalTemplates | 2 | 2 | [Факты](FunctionDetails/FinalTemplates.md) |

Все фрагменты:

| Вход | Исходник | Назначение |
| --- | --- | --- |
| #AC74 | [Station.PrintPlayerRank](../Source/Station/PrintPlayerRank.asm) | Печать ранга по счётчику и шести порогам |
| #4200 | [StationExit.LoadAction](../Source/StationExit/LoadAction.asm) | Перенесённый выход станции, запрос ACTION и передача контекста |
| #5D41 | [Basic.ReadIntroSectors](../Source/Basic/ReadIntroSectors.asm) | Чтение 44 физических секторов через TR-DOS с возвратом на #6500 |
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
| #4000 | [StationBoot.InitializeStation](../Source/StationBoot/InitializeStation.asm) | Перенос ядра из #65CE в #6322 и очистка экрана банка 7 |
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
| #4355 | [ActionBoot.BuildExponentialTable](../Source/ActionBoot/BuildExponentialTable.asm) | Построение 256 байтов приближённой экспоненты последовательным умножением фиксированной точки |
| #438F | [ActionBoot.BuildLogarithmTable](../Source/ActionBoot/BuildLogarithmTable.asm) | Построение двух раздельных страниц приближённого логарифма через сумму 255 точных частных |
| #43CF | [ActionBoot.BuildBitmapTables](../Source/ActionBoot/BuildBitmapTables.asm) | Создание таблиц строк и битовых масок для рисования |
| #60AE | [Action.CreateMissileForTarget](../Source/Action/CreateMissileForTarget.asm) | Проверка существования записи цели, поиск свободного слота, инициализация ракеты и создание обратной связи у цели |
| #6145 | [Action.RefreshFlightPanel](../Source/Action/RefreshFlightPanel.asm) | Принудительное обновление шести шкал и четырёх пар счётчика панели полёта |
| #6172 | [Action.ReleaseClass14Records](../Source/Action/ReleaseClass14Records.asm) | Пометка всех активных записей класса 14 через повторный поиск от начала массива |
| #6265 | [Action.StepRecordTargetCodes](../Source/Action/StepRecordTargetCodes.asm) | Подвод двух байтов записи к рассчитанным кодам с различными правилами ограничения шага |
| #62CF | [Action.CountClass3LinksUpToTwo](../Source/Action/CountClass3LinksUpToTwo.asm) | Подсчёт до двух активных записей класса 3 с кодом 02 и совпадающей ссылкой |
| #6311 | [Action.ApproachWordAndAccumulate](../Source/Action/ApproachWordAndAccumulate.asm) | Приближение HL к BC по обёрнутой разности с накоплением старшего байта остатка в C' |
| #635B | [Action.ApplyPendingRecordLink](../Source/Action/ApplyPendingRecordLink.asm) | Установка бита 0 LinkFlags, замена LinkedIndex на 1A и условная поправка по ClassCode записи |
| #6380 | [Action.ApplyIndexedDelta](../Source/Action/ApplyIndexedDelta.asm) | Применение знаковой табличной поправки к байту 9BCD с ограничением и установкой бита 5 по прежнему значению |
| #64DF | [Action.DispatchRecordClass](../Source/Action/DispatchRecordClass.asm) | Косвенный переход по оборачиваемому байтовому индексу класса записи |
| #6524 | [Action.ReturnIgnoredRecordClass](../Source/Action/ReturnIgnoredRecordClass.asm) | Немедленный общий возврат исходных классов 10..25 без изменения записи |
| #6525 | [Action.ConfigureClass5Link](../Source/Action/ConfigureClass5Link.asm) | Подстановка и общий выбор связи только при новом нулевом слове потока 0 |
| #6536 | [Action.ConfigureClass8Link](../Source/Action/ConfigureClass8Link.asm) | Подстановка, состояние 12 и общий выбор связи при нулевом аппаратном предикате |
| #6549 | [Action.ConfigureClass2Link](../Source/Action/ConfigureClass2Link.asm) | Подстановка и выбор связи среди классов 6 и 7 после аппаратного порога |
| #6566 | [Action.ConfigureClass7Link](../Source/Action/ConfigureClass7Link.asm) | Подстановка и выбор связи с исключением классов 6 и 7 после аппаратного порога |
| #657F | [Action.ConfigureClass6Link](../Source/Action/ConfigureClass6Link.asm) | Подстановка с противоположными путями общего выбора и фильтра классов 6 и 7 |
| #6594 | [Action.ConfigureClass1Link](../Source/Action/ConfigureClass1Link.asm) | Подстановка и условный общий выбор связи со сменой класса на 0 после успеха |
| #65AD | [Action.ConfigureClass4Link](../Source/Action/ConfigureClass4Link.asm) | Подстановка и выбор связи среди классов 5 и 14 после аппаратного порога |
| #65C6 | [Action.ConfigureClass9Link](../Source/Action/ConfigureClass9Link.asm) | Запись кода 0D с сохранением LinkedIndex либо кода 01 со сбросом LinkedIndex в FF |
| #65DE | [Action.ConfigureClass3Link](../Source/Action/ConfigureClass3Link.asm) | Подстановка, фильтр классов 5 и 14 либо специальный код 26 по потоку 8 |
| #660E | [Action.ConfigureClass0Link](../Source/Action/ConfigureClass0Link.asm) | Применение подстановки либо выбор новой связи после порога R с общим входом SelectLink |
| #662B | [Action.CopyRecordLinkOverride](../Source/Action/CopyRecordLinkOverride.asm) | Копирование разрешённого байта подстановки в LinkedIndex и запись кода 02 |
| #6639 | [Action.DrawBankedGauge](../Source/Action/DrawBankedGauge.asm) | Выбор банка 1, вывод шестистрочной шкалы и обязательный выбор банка 0 |
| #6649 | [Action.UpdatePanelGauges](../Source/Action/UpdatePanelGauges.asm) | Условное обновление шести шкал, сброс пяти запросов и насыщение шестого значения |
| #66D2 | [Action.SubtractScaledWorkVector](../Source/Action/SubtractScaledWorkVector.asm) | Вычитание трёх знаковых масштабированных слов из рабочего 24-битного вектора до первого переполнения |
| #6727 | [Action.TransitionBodyMode](../Source/Action/TransitionBodyMode.asm) | Переключение режима тела и изменение старших слов рабочего вектора |
| #6780 | [Action.UpdateBodyMotion](../Source/Action/UpdateBodyMotion.asm) | Фазовое обновление рабочего вектора, запросов панели и широких целей |
| #6986 | [Action.CompareContextWordPairs](../Source/Action/CompareContextWordPairs.asm) | Сравнение двух пар слов контекста с ранним выходом по первой разности |
| #699C | [Action.MaxFoldedVectorHigh](../Source/Action/MaxFoldedVectorHigh.asm) | Максимум трёх старших байтов с дополнением отрицательных кодов через CPL |
| #69BE | [Action.FindFirstNearWideVector](../Source/Action/FindFirstNearWideVector.asm) | Поиск первого близкого широкого вектора и выбор его наибольшего старшего байта |
| #6A29 | [Action.CheckThreeUpperWordsNear](../Source/Action/CheckThreeUpperWordsNear.asm) | Проверка трёх знаковых верхних слов на диапазон от минус 60 до 59 |
| #6A6E | [Action.PrepareBodyTransform](../Source/Action/PrepareBodyTransform.asm) | Подготовка компонент тела и передача арифметическому преобразованию AF43 |
| #6AAD | [Action.RestoreBodyStack](../Source/Action/RestoreBodyStack.asm) | Восстановление настоящего SP после арифметического накопителя |
| #6AB0 | [Action.PublishTransformedBody](../Source/Action/PublishTransformedBody.asm) | Публикация знаковых компонент, подготовка проекции и рисование преобразованного тела |
| #6B16 | [Action.ProjectWideVectors](../Source/Action/ProjectWideVectors.asm) | Обход широких векторов с выбором масштаба, отрисовкой близких записей и публикацией выбранной |
| #6BFF | [Action.CopyAndTransformComponents](../Source/Action/CopyAndTransformComponents.asm) | Копирование трёх трёхбайтовых компонент с шагом четыре и последующее преобразование рабочего вектора |
| #6C19 | [Action.TransformWorkComponents](../Source/Action/TransformWorkComponents.asm) | Преобразование старших слов трёх рабочих компонент с очисткой Low и знаковым кодированием результата |
| #6C40 | [Action.RestoreComponentStack](../Source/Action/RestoreComponentStack.asm) | Восстановление CPU SP после вычисления рабочих компонент перед знаковым кодированием |
| #6C43 | [Action.EncodeSignedComponents](../Source/Action/EncodeSignedComponents.asm) | Кодирование трёх выходных слов в знак и модуль с обратным знаком компоненты 1 |
| #6C7E | [Action.DrawBankedProjectedBody](../Source/Action/DrawBankedProjectedBody.asm) | Проекция и рисование тела в банке CONTROL с шахматным рисунком |
| #6C8F | [Action.UpdateThirdGlyphVector](../Source/Action/UpdateThirdGlyphVector.asm) | Подготовка трёх входных слов, расчёт вектора с арифметическим SP и обновление третьего экранного знака |
| #6CB1 | [Action.RestoreThirdGlyphStack](../Source/Action/RestoreThirdGlyphStack.asm) | Восстановление CPU SP после векторного вычислителя перед публикацией третьего знака |
| #6CB4 | [Action.PublishThirdGlyphVector](../Source/Action/PublishThirdGlyphVector.asm) | Перенос четвертей двух выходных слов и знакового байта третьего слова во вход третьего экранного знака |
| #6CD6 | [Action.InitializeBankedBufferPoints](../Source/Action/InitializeBankedBufferPoints.asm) | Подготовка 35 координат точек в Controls банка 1 с возвратом полной конфигурации 10 |
| #6CE4 | [Action.TransferToStationLoader](../Source/Action/TransferToStationLoader.asm) | Выбор конфигурации 11 и хвостовая передача управления DCE3 загрузчика следующего режима |
| #6CEF | [Action.DispatchBank3Callback](../Source/Action/DispatchBank3Callback.asm) | Передача управления HL с конфигурацией банка 3, обменом AF и возвратным хвостом Runtime |
| #6D00 | [Action.RestoreRuntimePage](../Source/Action/RestoreRuntimePage.asm) | Выдача конфигурации 10 в 7FFD и возврат внешнему вызывающему после банкового обработчика |
| #6D06 | [Action.ApplyObjectOffsetVector](../Source/Action/ApplyObjectOffsetVector.asm) | Расчёт трёх базовых слов записи по коэффициентам смещения |
| #6D38 | [Action.UpdateVisualEffects](../Source/Action/UpdateVisualEffects.asm) | Обход эффектов, продвижение ресурсов и растеризация допущенных записей |
| #6DD1 | [Action.ResumeVisualEffect](../Source/Action/ResumeVisualEffect.asm) | Восстановление стека и банковый вызов рисователя эффекта при положительной глубине |
| #6E2B | [Action.ClassifyCoordinateRegion](../Source/Action/ClassifyCoordinateRegion.asm) | Классификация пары H,L по трём непересекающимся прямоугольникам с кодом 3 вне них |
| #6E6C | [Action.UpdateMotionFromControls](../Source/Action/UpdateMotionFromControls.asm) | Обработка управления и расчёт трёх смещений из знакового слова |
| #6EAC | [Action.StepNearZeroWord](../Source/Action/StepNearZeroWord.asm) | Изменение слова около нуля, запрос шестой шкалы и выключение обработки при модуле от двух |
| #6EDE | [Action.ReverseScaledVector](../Source/Action/ReverseScaledVector.asm) | Инвертирование трёх масштабированных компонент и обновление общего знакового слова с разрешением его обработки |
| #6F1D | [Action.ScanActionKeys](../Source/Action/ScanActionKeys.asm) | Обход 27 клавиатурных условий и программные вызовы обработчиков |
| #6F4E | [Action.RestoreKeyScanFrame](../Source/Action/RestoreKeyScanFrame.asm) | Восстановление IX, BC, DE и HL после обработчика клавиши и продолжение сканирования |
| #6F55 | [Action.LatchControlsAndDecay](../Source/Action/LatchControlsAndDecay.asm) | Фиксация запросов управления и фазовое приближение трёх знаковых величин к нулю |
| #704B | [Action.IgnoreKey](../Source/Action/IgnoreKey.asm) | Пустой обработчик клавиши, возврат к восстановлению рамки без изменения регистров |
| #704C | [Action.RequestMissile0](../Source/Action/RequestMissile0.asm) | Условный запрос запуска по Target0 с продолжением в общий хвост |
| #705D | [Action.CompleteMissileLaunch](../Source/Action/CompleteMissileLaunch.asm) | Создание ракеты, поправка состояния по классу цели и последующее списание запаса |
| #7075 | [Action.RequestMissile1](../Source/Action/RequestMissile1.asm) | Условный запрос запуска по Target1 с переходом в общий хвост |
| #7088 | [Action.RequestMissile2](../Source/Action/RequestMissile2.asm) | Условный запрос запуска по Target2 с переходом в общий хвост |
| #709B | [Action.ReportMissingMissileTarget](../Source/Action/ReportMissingMissileTarget.asm) | Передача в очередь сообщения об отсутствии захваченной цели с сохранением регистров |
| #70A4 | [Action.CheckMissileLaunch](../Source/Action/CheckMissileLaunch.asm) | Проверка кода захваченной цели и остатка ракет, очистка трёх захватов при пустом запасе |
| #70C6 | [Action.ConsumeMissileStock](../Source/Action/ConsumeMissileStock.asm) | Уменьшение выбранного запаса и отдельного байта 9BD2, передача сообщения о пуске и нового остатка очереди |
| #70ED | [Action.SelectMissileStock](../Source/Action/SelectMissileStock.asm) | Выбор ненулевого приоритетного остатка ракет либо запасного счётчика с возвратом адреса |
| #74FB | [Action.SelectPreferredByte](../Source/Action/SelectPreferredByte.asm) | Выбор ненулевого предпочтительного байта либо запасного значения с возвратом адреса выбранного поля |
| #7680 | [Action.IncreaseGaugeWord](../Source/Action/IncreaseGaugeWord.asm) | Увеличение слова шестой шкалы с исходными клавиатурными ограничениями |
| #76A3 | [Action.DecreaseGaugeWord](../Source/Action/DecreaseGaugeWord.asm) | Уменьшение слова шестой шкалы с исходными клавиатурными ограничениями |
| #76C7 | [Action.RequestTurnNegative](../Source/Action/RequestTurnNegative.asm) | Запрос уменьшения управления Turn с накопителем повтора и исходной знаковой границей |
| #76EA | [Action.RequestTurnPositive](../Source/Action/RequestTurnPositive.asm) | Запрос увеличения управления Turn с накопителем повтора и исходной знаковой границей |
| #770D | [Action.RequestXNegative](../Source/Action/RequestXNegative.asm) | Запрос уменьшения управления X с накопителем повтора и исходной знаковой границей |
| #7730 | [Action.RequestXPositive](../Source/Action/RequestXPositive.asm) | Запрос увеличения управления X с накопителем повтора и исходной знаковой границей |
| #7753 | [Action.RequestYNegative](../Source/Action/RequestYNegative.asm) | Запрос уменьшения управления Y с накопителем повтора и исходной знаковой границей |
| #7776 | [Action.RequestYPositive](../Source/Action/RequestYPositive.asm) | Запрос увеличения управления Y с накопителем повтора и исходной знаковой границей |
| #7859 | [Action.SpawnAlternate](../Source/Action/SpawnAlternate.asm) | Создание записей по шаблону либо по альтернативной ветке планировщика |
| #7B58 | [Action.ScheduleSpawn](../Source/Action/ScheduleSpawn.asm) | Планирование создания объекта, выбор класса, модели и начальных координат |
| #7DD4 | [Action.FinishSpawnRecord](../Source/Action/FinishSpawnRecord.asm) | Заполнение параметров новой записи и передача диспетчеру класса |
| #7E9D | [Action.SelectWideTargetAndStep](../Source/Action/SelectWideTargetAndStep.asm) | Выбор первой близкой широкой цели либо первой записи и обновление кодов текущего объекта |
| #7EB7 | [Action.StepRecordTowardWideVector](../Source/Action/StepRecordTowardWideVector.asm) | Обновление двух кодов записи по трём широким компонентам выбранной цели |
| #7F0E | [Action.ClampPatchedVectorWords](../Source/Action/ClampPatchedVectorWords.asm) | Сведение трёх изменяемых 32-битных значений к словам с исходным насыщением и знаком по биту 23 |
| #7F76 | [Action.AbsSigned32](../Source/Action/AbsSigned32.asm) | Модуль знакового 32-битного DE:HL с сохранением исходного переполнения минимального значения |
| #A82D | [Action.StartFlight](../Source/Action/StartFlight.asm) | Вывод панели из страницы 6 и инициализация полётного режима |
| #A859 | [Action.MainLoop](../Source/Action/MainLoop.asm) | Повторение процедуры полётного кадра |
| #A85E | [Action.UpdateFrame](../Source/Action/UpdateFrame.asm) | Обработка таймеров, управления, визуальных модулей и игровых объектов |
| #AACC | [Action.ReadObjectHeaderWord](../Source/Action/ReadObjectHeaderWord.asm) | Чтение слова по указателю страницы 9E из банка OBJECT3D с последующим выбором банка 0 |
| #AAE2 | [Action.CopyObjectData](../Source/Action/CopyObjectData.asm) | Копирование двухчастного потока OBJECT3D в исходный рабочий буфер с возвратом банка 0 |
| #AB1B | [Action.SelectMemoryPage](../Source/Action/SelectMemoryPage.asm) | Запись A в #7FFD с сохранением BC |
| #AB23 | [Action.UnpackResource](../Source/Action/UnpackResource.asm) | Распаковка HR-потока в полётном коде с переносом входа, LZ-ссылками, тройками и восстановлением шестибайтового конца |
| #AC38 | [Action.ReadWordFromIX](../Source/Action/ReadWordFromIX.asm) | Чтение слова младшим байтом вперёд через IX, продвижение IX на два и копирование C в B |
| #AC44 | [Action.ActivateParameterSet](../Source/Action/ActivateParameterSet.asm) | Выбор банка 0, применение набора параметров и обнуление двух слов и двух байтов состояния |
| #AC5D | [Action.ApplyParameterSet](../Source/Action/ApplyParameterSet.asm) | Применение пятнадцати полей набора к исходным адресам ACTION, поле 1 читается без записи, поле 6 используется дважды |
| #ACAB | [Action.QueueDiagnosticCounters](../Source/Action/QueueDiagnosticCounters.asm) | Постановка диагностических строк Status и Deads и трёх чисел в текстовую очередь |
| #ACEA | [Action.TransformVectorTransposed](../Source/Action/TransformVectorTransposed.asm) | Вычисление трёх выходных слов с временно транспонированной матрицей, сохранением IX/IY и восстановлением CPU-стека |
| #AD1D | [Action.SwapCodePatchWords](../Source/Action/SwapCodePatchWords.asm) | Обмен трёх пар полных слов изменяемого кода, включая байты операндов и следующие префиксы |
| #AD48 | [Action.SqrtWordBank1](../Source/Action/SqrtWordBank1.asm) | Вызов табличного корня с выбором Controls банка 1 и сохранением BC |
| #AD5A | [Action.EncodeHalfCoordinateDeltas](../Source/Action/EncodeHalfCoordinateDeltas.asm) | Два кода по трём разностям половинных координат и корню усечённых квадратов |
| #ADB7 | [Action.RotateBankedBasis](../Source/Action/RotateBankedBasis.asm) | Поворот базисных векторов через VOXAL в странице 3 |
| #ADC5 | [Action.ProjectOverlayCoordinates](../Source/Action/ProjectOverlayCoordinates.asm) | Проекция двух координат относительно общей глубины с центром 128, 48 |
| #AE15 | [Action.EncodeComponentDeltas](../Source/Action/EncodeComponentDeltas.asm) | Кодирование отношения двух разностей слов с последовательным продолжением в EncodeSignedRatio |
| #AE24 | [Action.EncodeSignedRatio](../Source/Action/EncodeSignedRatio.asm) | Табличное кодирование знакового отношения с четырьмя смещениями и исходными ограничениями |
| #AE73 | [Action.DivideScaledLogarithmic](../Source/Action/DivideScaledLogarithmic.asm) | Приближённое отношение с масштабом 256 через нормализацию, разность логарифмов и обратную таблицу |
| #AF43 | [Action.ComputePatchedVector](../Source/Action/ComputePatchedVector.asm) | Расчёт трёх компонентов по девяти коэффициентам с исходным переносом отрицательных произведений и досрочным выходом по переполнению |
| #B044 | [Action.BuildObjectOffsetCoefficients](../Source/Action/BuildObjectOffsetCoefficients.asm) | Подготовка коэффициентов смещения по трём фазовым парам |
| #B0E9 | [Action.SqrtWordCached](../Source/Action/SqrtWordCached.asm) | Целый корень в области 0000..E8FF и исходное особое поведение E900..FFFF по трём страницам таблиц |
| #C000 | [Action.ClipPolygon](../Source/Action/ClipPolygon.asm) | Обход замкнутого списка вершин с табличным отсечением и ранним завершением контура |
| #C071 | [Action.ContinueClipPolygon](../Source/Action/ContinueClipPolygon.asm) | Восстановление счётчика после ребра и продолжение либо возврат полного полигона |
| #C07A | [Action.ReturnClipCase](../Source/Action/ReturnClipCase.asm) | Завершение текущего табличного случая обычным RET |
| #C07B | [Action.ClipInsideToBottomRight](../Source/Action/ClipInsideToBottomRight.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу справа |
| #C08A | [Action.ClipRightToBottomRight](../Source/Action/ClipRightToBottomRight.asm) | Отсечение ребра, первая точка справа, вторая снизу справа |
| #C095 | [Action.ClipInsideToBottomLeft](../Source/Action/ClipInsideToBottomLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу слева |
| #C0A4 | [Action.ClipBottomToBottomLeft](../Source/Action/ClipBottomToBottomLeft.asm) | Отсечение ребра, первая точка снизу, вторая снизу слева |
| #C0AF | [Action.ClipInsideToTopRight](../Source/Action/ClipInsideToTopRight.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху справа |
| #C0BE | [Action.ClipTopToTopRight](../Source/Action/ClipTopToTopRight.asm) | Отсечение ребра, первая точка сверху, вторая сверху справа |
| #C0C9 | [Action.ClipInsideToTopLeft](../Source/Action/ClipInsideToTopLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху слева |
| #C0D8 | [Action.ClipLeftToTopLeft](../Source/Action/ClipLeftToTopLeft.asm) | Отсечение ребра, первая точка слева, вторая сверху слева |
| #C0E3 | [Action.ClipRightToInside](../Source/Action/ClipRightToInside.asm) | Отсечение ребра, первая точка справа, вторая внутри окна |
| #C0E9 | [Action.ClipRightToLeft](../Source/Action/ClipRightToLeft.asm) | Отсечение ребра, первая точка справа, вторая слева |
| #C0EF | [Action.ClipRightToBottom](../Source/Action/ClipRightToBottom.asm) | Отсечение ребра, первая точка справа, вторая снизу |
| #C101 | [Action.ClipRightToBottomLeft](../Source/Action/ClipRightToBottomLeft.asm) | Отсечение ребра, первая точка справа, вторая снизу слева |
| #C119 | [Action.ClipRightToTop](../Source/Action/ClipRightToTop.asm) | Отсечение ребра, первая точка справа, вторая сверху |
| #C12B | [Action.ClipRightToTopRight](../Source/Action/ClipRightToTopRight.asm) | Отсечение ребра, первая точка справа, вторая сверху справа |
| #C132 | [Action.ClipRightToTopLeft](../Source/Action/ClipRightToTopLeft.asm) | Отсечение ребра, первая точка справа, вторая сверху слева |
| #C144 | [Action.ClipLeftToInside](../Source/Action/ClipLeftToInside.asm) | Отсечение ребра, первая точка слева, вторая внутри окна |
| #C14A | [Action.ClipLeftToRight](../Source/Action/ClipLeftToRight.asm) | Отсечение ребра, первая точка слева, вторая справа |
| #C150 | [Action.ClipLeftToBottom](../Source/Action/ClipLeftToBottom.asm) | Отсечение ребра, первая точка слева, вторая снизу |
| #C162 | [Action.ClipLeftToBottomRight](../Source/Action/ClipLeftToBottomRight.asm) | Отсечение ребра, первая точка слева, вторая снизу справа |
| #C174 | [Action.ClipLeftToBottomLeft](../Source/Action/ClipLeftToBottomLeft.asm) | Отсечение ребра, первая точка слева, вторая снизу слева |
| #C17B | [Action.ClipLeftToTop](../Source/Action/ClipLeftToTop.asm) | Отсечение ребра, первая точка слева, вторая сверху |
| #C18D | [Action.ClipLeftToTopRight](../Source/Action/ClipLeftToTopRight.asm) | Отсечение ребра, первая точка слева, вторая сверху справа |
| #C1A5 | [Action.ClipBottomToInside](../Source/Action/ClipBottomToInside.asm) | Отсечение ребра, первая точка снизу, вторая внутри окна |
| #C1AB | [Action.ClipBottomToRight](../Source/Action/ClipBottomToRight.asm) | Отсечение ребра, первая точка снизу, вторая справа |
| #C1BD | [Action.ClipBottomToLeft](../Source/Action/ClipBottomToLeft.asm) | Отсечение ребра, первая точка снизу, вторая слева |
| #C1CF | [Action.ClipBottomToBottomRight](../Source/Action/ClipBottomToBottomRight.asm) | Отсечение ребра, первая точка снизу, вторая снизу справа |
| #C1D6 | [Action.ClipBottomToTop](../Source/Action/ClipBottomToTop.asm) | Отсечение ребра, первая точка снизу, вторая сверху |
| #C1DC | [Action.ClipBottomToTopRight](../Source/Action/ClipBottomToTopRight.asm) | Отсечение ребра, первая точка снизу, вторая сверху справа |
| #C1F1 | [Action.ClipBottomToTopLeft](../Source/Action/ClipBottomToTopLeft.asm) | Отсечение ребра, первая точка снизу, вторая сверху слева |
| #C20C | [Action.ClipBottomRightToInside](../Source/Action/ClipBottomRightToInside.asm) | Отсечение ребра, первая точка снизу справа, вторая внутри окна |
| #C228 | [Action.ClipBottomRightToRight](../Source/Action/ClipBottomRightToRight.asm) | Отсечение ребра, первая точка снизу справа, вторая справа |
| #C22F | [Action.ClipBottomRightToLeft](../Source/Action/ClipBottomRightToLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая слева |
| #C24E | [Action.ClipBottomRightToBottom](../Source/Action/ClipBottomRightToBottom.asm) | Отсечение ребра, первая точка снизу справа, вторая снизу |
| #C259 | [Action.ClipBottomRightToBottomLeft](../Source/Action/ClipBottomRightToBottomLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая снизу слева |
| #C25F | [Action.ClipBottomRightToTop](../Source/Action/ClipBottomRightToTop.asm) | Отсечение ребра, первая точка снизу справа, вторая сверху |
| #C274 | [Action.ClipBottomRightToTopLeft](../Source/Action/ClipBottomRightToTopLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая сверху слева |
| #C28D | [Action.ClipBottomLeftToInside](../Source/Action/ClipBottomLeftToInside.asm) | Отсечение ребра, первая точка снизу слева, вторая внутри окна |
| #C2A9 | [Action.ClipBottomLeftToRight](../Source/Action/ClipBottomLeftToRight.asm) | Отсечение ребра, первая точка снизу слева, вторая справа |
| #C2BE | [Action.ClipBottomLeftToLeft](../Source/Action/ClipBottomLeftToLeft.asm) | Отсечение ребра, первая точка снизу слева, вторая слева |
| #C2C9 | [Action.ClipBottomLeftToBottom](../Source/Action/ClipBottomLeftToBottom.asm) | Отсечение ребра, первая точка снизу слева, вторая снизу |
| #C2D0 | [Action.ClipBottomLeftToTop](../Source/Action/ClipBottomLeftToTop.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху |
| #C2EF | [Action.ClipBottomLeftToTopRight](../Source/Action/ClipBottomLeftToTopRight.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху справа |
| #C308 | [Action.ClipBottomLeftToTopLeft](../Source/Action/ClipBottomLeftToTopLeft.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху слева |
| #C30E | [Action.ClipTopToInside](../Source/Action/ClipTopToInside.asm) | Отсечение ребра, первая точка сверху, вторая внутри окна |
| #C314 | [Action.ClipTopToRight](../Source/Action/ClipTopToRight.asm) | Отсечение ребра, первая точка сверху, вторая справа |
| #C326 | [Action.ClipTopToLeft](../Source/Action/ClipTopToLeft.asm) | Отсечение ребра, первая точка сверху, вторая слева |
| #C338 | [Action.ClipTopToBottom](../Source/Action/ClipTopToBottom.asm) | Отсечение ребра, первая точка сверху, вторая снизу |
| #C33E | [Action.ClipTopToBottomRight](../Source/Action/ClipTopToBottomRight.asm) | Отсечение ребра, первая точка сверху, вторая снизу справа |
| #C359 | [Action.ClipTopToBottomLeft](../Source/Action/ClipTopToBottomLeft.asm) | Отсечение ребра, первая точка сверху, вторая снизу слева |
| #C36E | [Action.ClipTopToTopLeft](../Source/Action/ClipTopToTopLeft.asm) | Отсечение ребра, первая точка сверху, вторая сверху слева |
| #C375 | [Action.ClipTopRightToInside](../Source/Action/ClipTopRightToInside.asm) | Отсечение ребра, первая точка сверху справа, вторая внутри окна |
| #C391 | [Action.ClipTopRightToRight](../Source/Action/ClipTopRightToRight.asm) | Отсечение ребра, первая точка сверху справа, вторая справа |
| #C39C | [Action.ClipTopRightToLeft](../Source/Action/ClipTopRightToLeft.asm) | Отсечение ребра, первая точка сверху справа, вторая слева |
| #C3B1 | [Action.ClipTopRightToBottom](../Source/Action/ClipTopRightToBottom.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу |
| #C3D0 | [Action.ClipTopRightToBottomRight](../Source/Action/ClipTopRightToBottomRight.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу справа |
| #C3D6 | [Action.ClipTopRightToBottomLeft](../Source/Action/ClipTopRightToBottomLeft.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу слева |
| #C3EF | [Action.ClipTopRightToTop](../Source/Action/ClipTopRightToTop.asm) | Отсечение ребра, первая точка сверху справа, вторая сверху |
| #C3F6 | [Action.ClipTopLeftToInside](../Source/Action/ClipTopLeftToInside.asm) | Отсечение ребра, первая точка сверху слева, вторая внутри окна |
| #C412 | [Action.ClipTopLeftToRight](../Source/Action/ClipTopLeftToRight.asm) | Отсечение ребра, первая точка сверху слева, вторая справа |
| #C431 | [Action.ClipTopLeftToLeft](../Source/Action/ClipTopLeftToLeft.asm) | Отсечение ребра, первая точка сверху слева, вторая слева |
| #C438 | [Action.ClipTopLeftToBottom](../Source/Action/ClipTopLeftToBottom.asm) | Отсечение ребра, первая точка сверху слева, вторая снизу |
| #C44D | [Action.ClipTopLeftToBottomRight](../Source/Action/ClipTopLeftToBottomRight.asm) | Отсечение ребра, первая точка сверху слева, вторая снизу справа |
| #C466 | [Action.ClipTopLeftToTop](../Source/Action/ClipTopLeftToTop.asm) | Отсечение ребра, первая точка сверху слева, вторая сверху |
| #C471 | [Action.ClipTopLeftToTopRight](../Source/Action/ClipTopLeftToTopRight.asm) | Отсечение ребра, первая точка сверху слева, вторая сверху справа |
| #C477 | [Action.ComputeTopClipProduct](../Source/Action/ComputeTopClipProduct.asm) | Подготовка числителя пересечения (First.First-0)*(First.Second-Second.Second) исходным знаковым умножителем |
| #C496 | [Action.ComputeBottomClipProduct](../Source/Action/ComputeBottomClipProduct.asm) | Подготовка числителя пересечения (First.First-95)*(First.Second-Second.Second) исходным знаковым умножителем |
| #C4B5 | [Action.ComputeLeftClipProduct](../Source/Action/ComputeLeftClipProduct.asm) | Подготовка числителя пересечения (First.First-Second.First)*(First.Second-0) исходным знаковым умножителем |
| #C4D4 | [Action.ComputeRightClipProduct](../Source/Action/ComputeRightClipProduct.asm) | Подготовка числителя пересечения (First.First-Second.First)*(First.Second-255) исходным знаковым умножителем |
| #C4F3 | [Action.ClipInsideToTop](../Source/Action/ClipInsideToTop.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху |
| #C4F6 | [Action.AppendTopClipIntersection](../Source/Action/AppendTopClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C53D | [Action.ClipInsideToBottom](../Source/Action/ClipInsideToBottom.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу |
| #C540 | [Action.AppendBottomClipIntersection](../Source/Action/AppendBottomClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C588 | [Action.ClipInsideToLeft](../Source/Action/ClipInsideToLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая слева |
| #C58B | [Action.AppendLeftClipIntersection](../Source/Action/AppendLeftClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C5E4 | [Action.ClipInsideToRight](../Source/Action/ClipInsideToRight.asm) | Отсечение ребра, первая точка внутри окна, вторая справа |
| #C5E7 | [Action.AppendRightClipIntersection](../Source/Action/AppendRightClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C641 | [Action.AppendTopLeftClipCorner](../Source/Action/AppendTopLeftClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C64C | [Action.AppendTopRightClipCorner](../Source/Action/AppendTopRightClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C657 | [Action.AppendBottomLeftClipCorner](../Source/Action/AppendBottomLeftClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C662 | [Action.AppendBottomRightClipCorner](../Source/Action/AppendBottomRightClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C66D | [Action.CompareTopLeftProducts](../Source/Action/CompareTopLeftProducts.asm) | Вычитание LeftProduct из TopProduct с передачей заёма младшего слова |
| #C681 | [Action.CompareTopRightProducts](../Source/Action/CompareTopRightProducts.asm) | Вычитание RightProduct из TopProduct с передачей заёма младшего слова |
| #C695 | [Action.CompareBottomLeftProducts](../Source/Action/CompareBottomLeftProducts.asm) | Вычитание LeftProduct из BottomProduct с передачей заёма младшего слова |
| #C6A9 | [Action.CompareBottomRightProducts](../Source/Action/CompareBottomRightProducts.asm) | Вычитание RightProduct из BottomProduct с передачей заёма младшего слова |
| #C6BD | [Action.ComputeSecondAxisDelta](../Source/Action/ComputeSecondAxisDelta.asm) | Разность координат Second второй и первой точки с оборачиванием до слова |
| #C6C8 | [Action.ComputeFirstAxisDelta](../Source/Action/ComputeFirstAxisDelta.asm) | Разность координат First второй и первой точки с оборачиванием до слова |
| #C6D3 | [Action.AppendSecondClipPoint](../Source/Action/AppendSecondClipPoint.asm) | Добавление младших байтов второй точки с общим входом записи пары DE |
| #C6EA | [Action.ExitClipContour](../Source/Action/ExitClipContour.asm) | Специальное завершение контура со снятием трёх служебных слов |
| #C6F4 | [Action.MultiplySigned16](../Source/Action/MultiplySigned16.asm) | Знаковое произведение двух слов с тремя ядрами и исходным исключением второго операнда 8000 |
| #C88C | [Action.DivideSigned32To16](../Source/Action/DivideSigned32To16.asm) | Деление числителя HL, A, альтернативного A на signed16 с исходным побитовым дополнением |
| #C941 | [Action.ClipSingleEdge](../Source/Action/ClipSingleEdge.asm) | Отсечение одиночного ребра с обменом внутренней первой точки и рамкой трёх возвратов |
| #C99B | [Action.BuildRenderCoefficients](../Source/Action/BuildRenderCoefficients.asm) | Построение девяти байтовых коэффициентов по трём фазам либо по одной фазе |
| #CB23 | [Action.ComposeRenderMatrix](../Source/Action/ComposeRenderMatrix.asm) | Композиция исходной матрицы и ориентации с одноосным режимом и точными четвертями |
| #CF08 | [Action.UnknownCF08](../Source/Action/UnknownCF08.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D10A | [Action.ClearWorkBuffer](../Source/Action/ClearWorkBuffer.asm) | Заполнение линейного буфера 8000..8BFF байтами FF через временный SP с восстановлением CPU-стека |
| #D12C | [Action.MultiplySignedScaled](../Source/Action/MultiplySignedScaled.asm) | Знаковое произведение DE и байтового коэффициента с усечением к нулю после деления на 128 и выходом через IX |
| #D1C0 | [Action.PolygonFillRows](../Source/Action/PolygonFillRows.asm) | Строковое ядро линейной заливки с развёрнутой записью, крайними масками и коррекцией двух рёбер |
| #D268 | [Action.SelectPolygonRightEdge](../Source/Action/SelectPolygonRightEdge.asm) | Передача управления правому обновлению без изменения контекста |
| #D26B | [Action.WrapPolygonLeftEdge](../Source/Action/WrapPolygonLeftEdge.asm) | Оборачивание обратного поиска к последней First кольца |
| #D272 | [Action.UpdatePolygonLeftEdge](../Source/Action/UpdatePolygonLeftEdge.asm) | Поиск восходящего левого ребра, вычисление целого шага и ошибки, выбор продолжения заливки |
| #D3A8 | [Action.WrapPolygonRightEdge](../Source/Action/WrapPolygonRightEdge.asm) | Оборачивание прямого поиска к первой First кольца |
| #D3AD | [Action.UpdatePolygonRightEdge](../Source/Action/UpdatePolygonRightEdge.asm) | Поиск восходящего правого ребра и вычисление его упакованного шага и дробной ошибки |
| #D4C1 | [Action.SelectPolygonRowLimit](../Source/Action/SelectPolygonRowLimit.asm) | Выбор ближайшего предела строк с приоритетом левого ребра и настройкой следующего перехода |
| #D4F5 | [Action.SetShortNegativeRightStep](../Source/Action/SetShortNegativeRightStep.asm) | Настройка нулевого целого шага короткого отрицательного правого наклона и восстановление временного контекста |
| #D503 | [Action.WrapPolygonLeftTop](../Source/Action/WrapPolygonLeftTop.asm) | Оборачивание поиска левого конца верхней горизонтали |
| #D50A | [Action.WrapPolygonRightTop](../Source/Action/WrapPolygonRightTop.asm) | Оборачивание поиска правого конца верхней горизонтали |
| #D50F | [Action.ReturnPolygonFill](../Source/Action/ReturnPolygonFill.asm) | Восстановление сохранённого HL и внешний возврат плоского контура |
| #D511 | [Action.PreparePolygonFill](../Source/Action/PreparePolygonFill.asm) | Подготовка диапазона строк, верхних вершин двух цепочек, масок и временного стека заливки |
| #D5C9 | [Action.TransformObjectVertices](../Source/Action/TransformObjectVertices.asm) | Копирование потока объекта и преобразование всех его фиксированных групп вершин |
| #D5F9 | [Action.PrepareRenderVertexProducts](../Source/Action/PrepareRenderVertexProducts.asm) | Подготовка трёх пар координат и трёх глубин табличным произведением матрицы и входных компонентов |
| #D694 | [Action.ProjectRenderVertexGroup](../Source/Action/ProjectRenderVertexGroup.asm) | Построение комбинаций координат и перспективная запись выбранной группы вершин |
| #D7A0 | [Action.ProjectRenderVertex](../Source/Action/ProjectRenderVertex.asm) | Перспективная запись одной вершины с исходной нормализацией и косвенным продолжением |
| #DBBD | [Action.RenderClippedRecords](../Source/Action/RenderClippedRecords.asm) | Вывод записей объекта с проверкой кодов точек и отсечением граней и открытых сегментов |
| #DD23 | [Action.RenderInsideRecords](../Source/Action/RenderInsideRecords.asm) | Вывод граней и ломаных объекта с внутренними точками без дополнительного отсечения |
| #DDD1 | [Action.CombineListedVertexCodes](../Source/Action/CombineListedVertexCodes.asm) | Объединение кодов границ перечисленных точек с ранним выходом по нулевому коду |
| #DDF0 | [Action.DrawLinearLine](../Source/Action/DrawLinearLine.asm) | Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки |
| #DEF0 | [Action.AbortProjectedVertexScan](../Source/Action/AbortProjectedVertexScan.asm) | Завершение сканирования точек по маркеру отказа перспективы без отката предыдущих кодов |
| #DEF3 | [Action.ClassifyProjectedVertices](../Source/Action/ClassifyProjectedVertices.asm) | Заполнение кодов границ экранных точек и накопление общего кода объекта |
| #DFB6 | [Action.CheckFaceOrientation](../Source/Action/CheckFaceOrientation.asm) | Проверка ориентации выбранной тройки экранных точек по знаку разности двух произведений |
| #E020 | [Action.RenderSceneFrame](../Source/Action/RenderSceneFrame.asm) | Подготовка кадра, проекция объектов и передача в очередь отрисовки |
| #E1B9 | [Action.PrepareProjectionScale](../Source/Action/PrepareProjectionScale.asm) | Масштабирование мантиссы заголовка на степень двух и настройка трёх относительных переходов |
| #E1D1 | [Action.CheckCloseRecordBounds](../Source/Action/CheckCloseRecordBounds.asm) | Проверка трёх исходных компонент с цепочкой Carry и условная обработка близкой записи |
| #E213 | [Action.ClipProjectionBounds](../Source/Action/ClipProjectionBounds.asm) | Проверка глубины и двух осей с табличной поправкой масштаба и выбором следующего пути проекции |
| #E299 | [Action.PrepareProjectedBounds](../Source/Action/PrepareProjectedBounds.asm) | Фильтрация старших байтов координат и подготовка допуска, знакового X и модулей двух проекций |
| #E30F | [Action.CaptureProjectedRecord](../Source/Action/CaptureProjectedRecord.asm) | Условная запись альтернативного HL в PendingRecord после двух проверок координатного допуска |
| #E36A | [Action.FollowProjectedTarget](../Source/Action/FollowProjectedTarget.asm) | Сглаживание экранной точки и назначение первой свободной цели по запросу |
| #E40F | [Action.InsertRenderQueue](../Source/Action/InsertRenderQueue.asm) | Вставка снимка объекта в связанную очередь по исходному знаковому сравнению глубины |
| #E4A6 | [Action.ReadRenderQueue](../Source/Action/ReadRenderQueue.asm) | Восстановление стека чтения очереди и загрузка снимка узла с обновлением AY |
| #E4DB | [Action.RenderQueuedObject](../Source/Action/RenderQueuedObject.asm) | Подготовка и вывод текущего объекта очереди с выбором рисователя и чтением следующего узла |
| #E4FF | [Action.SelectRenderQueueNode](../Source/Action/SelectRenderQueueNode.asm) | Проверка конца очереди либо переход к загрузке выбранного узла |
| #E506 | [Action.DispatchCloseRecord](../Source/Action/DispatchCloseRecord.asm) | Отбор близкой записи по коду запрета и классу с передачей в следующий режим либо инвертированием компонент |
| #E51F | [Action.CheckCloseRecordComponents](../Source/Action/CheckCloseRecordComponents.asm) | Дополнительный отбор по биту 4 ReuseByte и старшим байтам трёх компонент |
| #E54A | [Action.ReverseCloseRecordState](../Source/Action/ReverseCloseRecordState.asm) | Уменьшение кода запрета, инвертирование масштабированных компонент и особое обнуление состояния класса 12 |
| #E55C | [Action.PrepareRecordScale](../Source/Action/PrepareRecordScale.asm) | Сохранение CPU SP, временное деление смещений класса 14 и выбор числа удвоений по заголовку модели |
| #E5A0 | [Action.UpdateRecordComponents](../Source/Action/UpdateRecordComponents.asm) | Обновление трёх компонент с проверкой переполнения и границы, обработкой отказа и запросом предупреждения о стыковке |
| #E655 | [Action.FinishRecordWarning](../Source/Action/FinishRecordWarning.asm) | Восстановление DE после запроса предупреждения и завершение через восстановитель смещений |
| #E658 | [Action.RejectRecordUpdate](../Source/Action/RejectRecordUpdate.asm) | Восстановление CPU-стека, пометка записи IX для повторного использования и продолжение очистки класса 12 |
| #E65F | [Action.ReleaseClass12Records](../Source/Action/ReleaseClass12Records.asm) | Обнуление двух байтов состояния и пометка всех активных записей класса 12 либо хвост восстановления смещений |
| #E685 | [Action.RestoreHalvedOffsets](../Source/Action/RestoreHalvedOffsets.asm) | Восстановление трёх исходных вычитаемых слов после временного арифметического деления для класса 14 |
| #E69E | [Action.SelectRecordByIndex](../Source/Action/SelectRecordByIndex.asm) | Расчёт адреса записи в IY по коду A с сохранением HL |
| #E6A7 | [Action.RecordIndexToAddress](../Source/Action/RecordIndexToAddress.asm) | Расчёт адреса записи A100 плюс входной код, умноженный на 64 |
| #E6B5 | [Action.RecordIXToIndex](../Source/Action/RecordIXToIndex.asm) | Расчёт байтового кода записи по IX с сохранением HL |
| #E6BE | [Action.RecordIYToIndex](../Source/Action/RecordIYToIndex.asm) | Расчёт байтового кода записи по IY с сохранением HL |
| #E6C7 | [Action.RecordAddressToIndex](../Source/Action/RecordAddressToIndex.asm) | Расчёт байтового кода записи по HL, младшие шесть битов смещения не участвуют в коде |
| #E6D1 | [Action.NextActiveRecord](../Source/Action/NextActiveRecord.asm) | Переход по шагу BC к следующей записи с байтом 1 не равным 80 либо к маркеру конца |
| #E6E2 | [Action.FindFilteredRecordOr26](../Source/Action/FindFilteredRecordOr26.asm) | Выбор кода 26 по потоку 10 либо поиск активного класса 1..15 или 18 |
| #E70D | [Action.FindRecordExcept6And7](../Source/Action/FindRecordExcept6And7.asm) | Поиск первой активной записи с классом вне пары 6 и 7 |
| #E729 | [Action.FindRecordClass6Or7](../Source/Action/FindRecordClass6Or7.asm) | Поиск первой активной записи с классом 6 либо 7 |
| #E745 | [Action.FindRecordClass5Or14](../Source/Action/FindRecordClass5Or14.asm) | Поиск первой активной записи с классом 5 либо 14 |
| #E97C | [Action.SelectClass8ForRecord](../Source/Action/SelectClass8ForRecord.asm) | Поиск первой записи класса 8 и сохранение её индекса в текущей записи |
| #E98D | [Action.FindRecordByCode](../Source/Action/FindRecordByCode.asm) | Поиск от A100 первой активной записи с байтом 12 равным входному D |
| #E9A1 | [Action.FindReusableRecord](../Source/Action/FindReusableRecord.asm) | Поиск первой записи с байтом 1 равным 80, обработка маркера конца и однократного пропуска по байту 18 |
| #EA29 | [Action.PrepareLargeEffect](../Source/Action/PrepareLargeEffect.asm) | Настройка дочернего кода и чтение заголовка большого эффекта |
| #EA3D | [Action.AllocateLargeEffect](../Source/Action/AllocateLargeEffect.asm) | Выделение большого эффекта и создание дочерних записей перед освобождением объекта |
| #EAE9 | [Action.MaxRecordDeltaHigh](../Source/Action/MaxRecordDeltaHigh.asm) | Максимальный старший байт модулей трёх обёрнутых разностей записей |
| #EB72 | [Action.NextRandomWord0](../Source/Action/NextRandomWord0.asm) | Следующее слово независимого потока 0 с физическим состоянием Stream0 |
| #EB79 | [Action.NextRandomWord3](../Source/Action/NextRandomWord3.asm) | Следующее слово независимого потока 3 с физическим состоянием Stream3 |
| #EB80 | [Action.NextRandomWord4](../Source/Action/NextRandomWord4.asm) | Следующее слово независимого потока 4 с физическим состоянием Stream4 |
| #EB87 | [Action.NextRandomWord1](../Source/Action/NextRandomWord1.asm) | Следующее слово независимого потока 1 с физическим состоянием Stream1 |
| #EB8E | [Action.NextRandomWord5](../Source/Action/NextRandomWord5.asm) | Следующее слово независимого потока 5 с физическим состоянием Stream5 |
| #EB95 | [Action.NextRandomWord6](../Source/Action/NextRandomWord6.asm) | Следующее слово независимого потока 6 с физическим состоянием Stream6 |
| #EB9C | [Action.NextRandomWord7](../Source/Action/NextRandomWord7.asm) | Следующее слово независимого потока 7 с физическим состоянием Stream7 |
| #EBA3 | [Action.NextRandomWord8](../Source/Action/NextRandomWord8.asm) | Следующее слово независимого потока 8 с физическим состоянием Stream8 |
| #EBAA | [Action.NextRandomWord9](../Source/Action/NextRandomWord9.asm) | Следующее слово независимого потока 9 с физическим состоянием Stream9 |
| #EBB1 | [Action.NextRandomWord10](../Source/Action/NextRandomWord10.asm) | Следующее слово независимого потока 10 с физическим состоянием Stream10 |
| #EBB8 | [Action.NextRandomWord2](../Source/Action/NextRandomWord2.asm) | Следующее слово независимого потока 2 с физическим состоянием Stream2 |
| #EBBF | [Action.NextRandomWord11](../Source/Action/NextRandomWord11.asm) | Следующее слово независимого потока 11 с физическим состоянием Stream11 |
| #EBC6 | [Action.NextRandomWord12](../Source/Action/NextRandomWord12.asm) | Следующее слово независимого потока 12 с физическим состоянием Stream12 |
| #EBCD | [Action.NextRandomWord13](../Source/Action/NextRandomWord13.asm) | Следующее слово независимого потока 13 с физическим состоянием Stream13 |
| #EBD4 | [Action.NextRandomWord14](../Source/Action/NextRandomWord14.asm) | Следующее слово независимого потока 14 с физическим состоянием Stream14 |
| #EC08 | [Action.StepFoldedRandom](../Source/Action/StepFoldedRandom.asm) | Обновление трёхбайтового состояния свёрткой переносов и возврат нового 16-битного слова через обратный EXX |
| #ECA8 | [Action.UpdateAyEffects](../Source/Action/UpdateAyEffects.asm) | Вывод очередных строк потоков AY-каналов A и B и формирование канала C по R и изменяемому уровню |
| #EF7D | [Action.AdvanceObjectOffsetRise](../Source/Action/AdvanceObjectOffsetRise.asm) | Увеличение байта смещения и переход к обратному ходу по таймеру |
| #EF9A | [Action.AdvanceObjectOffsetFall](../Source/Action/AdvanceObjectOffsetFall.asm) | Уменьшение байта смещения и возврат сохранённого состояния по таймеру |
| #EFB5 | [Action.AdvanceObjectPhaseWait](../Source/Action/AdvanceObjectPhaseWait.asm) | Обновление фазового счётчика и завершение ожидания по классу и компонентам |
| #F03D | [Action.MarkIYRecordForReuse](../Source/Action/MarkIYRecordForReuse.asm) | Пометка записи по IY кодом Component0=8000 и однократным пропуском ReuseByte=FF |
| #F04A | [Action.HandleSelectedRecordProximity](../Source/Action/HandleSelectedRecordProximity.asm) | Проверка выбранной записи, резервный поиск класса 8 и обработка близости |
| #F075 | [Action.SetClass18ObjectState](../Source/Action/SetClass18ObjectState.asm) | Установка состояния 0A у записи класса 12h перед диспетчеризацией |
| #F0F8 | [Action.PrepareObjectOffsetTransform](../Source/Action/PrepareObjectOffsetTransform.asm) | Проверка маркера записи и подготовка смещений для вычислителя 6D06 |
| #F356 | [Action.HandleClass18Proximity](../Source/Action/HandleClass18Proximity.asm) | Поиск записи класса 18, освобождение текущей при близости либо подвод фазовых кодов |
| #F36B | [Action.StepCodesTowardRecord](../Source/Action/StepCodesTowardRecord.asm) | Подвод фазовых кодов текущей записи по трём компонентам выбранной записи |
| #F394 | [Action.MarkRecordForReuse](../Source/Action/MarkRecordForReuse.asm) | Пометка записи кодом Component0=8000 и однократным пропуском ReuseByte=FF при поиске доступной записи |
| #F51E | [Action.UpdatePreferredClass18](../Source/Action/UpdatePreferredClass18.asm) | Выбор опоры по R и потоку 2 либо по приоритету классов с обновлением класса 18 |
| #F527 | [Action.CheckPreferredRandomWord](../Source/Action/CheckPreferredRandomWord.asm) | Проверка младшего слова потока 2 и внешнего байта для выбора отдельного кода 26 |
| #F535 | [Action.FindPreferredClass0](../Source/Action/FindPreferredClass0.asm) | Поиск опорного класса 0 с продолжением к классам 7 и 5 при отсутствии |
| #F53F | [Action.ContinuePreferredClass0](../Source/Action/ContinuePreferredClass0.asm) | Передача выбранного индекса класса 0 в общую проверку класса 18 |
| #F541 | [Action.FindPreferredClass7](../Source/Action/FindPreferredClass7.asm) | Поиск опорного класса 7 с продолжением к классу 5 при отсутствии |
| #F54B | [Action.ContinuePreferredClass7](../Source/Action/ContinuePreferredClass7.asm) | Передача выбранного индекса класса 7 в общую проверку класса 18 |
| #F54D | [Action.FindPreferredClass5](../Source/Action/FindPreferredClass5.asm) | Поиск последнего опорного класса 5 либо переход к сбросу баз |
| #F557 | [Action.ApplyPreferredToClass18](../Source/Action/ApplyPreferredToClass18.asm) | Запись выбранной опоры в первый класс 18 только при отсутствии класса 3 |
| #F572 | [Action.ResetRecordUpdateBases](../Source/Action/ResetRecordUpdateBases.asm) | Обнуление трёх базовых слов в изменяемых операндах обновления компонент |
| #F729 | [Action.UpdateObjects](../Source/Action/UpdateObjects.asm) | Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний |
| #F792 | [Action.CheckRecordEffectThreshold](../Source/Action/CheckRecordEffectThreshold.asm) | Выбор порога запуска большого эффекта для текущей записи |
| #F7BF | [Action.ResumeAfterRecordEffect](../Source/Action/ResumeAfterRecordEffect.asm) | Сброс флагов связи и продолжение обхода объектов |
| #F7C6 | [Action.DispatchObjectState](../Source/Action/DispatchObjectState.asm) | Выбор состояния объекта, косвенный вызов обработчика и последующее обновление записи |
| #C000 | [ThreeD.ClipPolygon](../Source/ThreeD/ClipPolygon.asm) | Обход замкнутого списка вершин с табличным отсечением и ранним завершением контура |
| #C071 | [ThreeD.ContinueClipPolygon](../Source/ThreeD/ContinueClipPolygon.asm) | Восстановление счётчика после ребра и продолжение либо возврат полного полигона |
| #C07A | [ThreeD.ReturnClipCase](../Source/ThreeD/ReturnClipCase.asm) | Завершение текущего табличного случая обычным RET |
| #C07B | [ThreeD.ClipInsideToBottomRight](../Source/ThreeD/ClipInsideToBottomRight.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу справа |
| #C08A | [ThreeD.ClipRightToBottomRight](../Source/ThreeD/ClipRightToBottomRight.asm) | Отсечение ребра, первая точка справа, вторая снизу справа |
| #C095 | [ThreeD.ClipInsideToBottomLeft](../Source/ThreeD/ClipInsideToBottomLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу слева |
| #C0A4 | [ThreeD.ClipBottomToBottomLeft](../Source/ThreeD/ClipBottomToBottomLeft.asm) | Отсечение ребра, первая точка снизу, вторая снизу слева |
| #C0AF | [ThreeD.ClipInsideToTopRight](../Source/ThreeD/ClipInsideToTopRight.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху справа |
| #C0BE | [ThreeD.ClipTopToTopRight](../Source/ThreeD/ClipTopToTopRight.asm) | Отсечение ребра, первая точка сверху, вторая сверху справа |
| #C0C9 | [ThreeD.ClipInsideToTopLeft](../Source/ThreeD/ClipInsideToTopLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху слева |
| #C0D8 | [ThreeD.ClipLeftToTopLeft](../Source/ThreeD/ClipLeftToTopLeft.asm) | Отсечение ребра, первая точка слева, вторая сверху слева |
| #C0E3 | [ThreeD.ClipRightToInside](../Source/ThreeD/ClipRightToInside.asm) | Отсечение ребра, первая точка справа, вторая внутри окна |
| #C0E9 | [ThreeD.ClipRightToLeft](../Source/ThreeD/ClipRightToLeft.asm) | Отсечение ребра, первая точка справа, вторая слева |
| #C0EF | [ThreeD.ClipRightToBottom](../Source/ThreeD/ClipRightToBottom.asm) | Отсечение ребра, первая точка справа, вторая снизу |
| #C101 | [ThreeD.ClipRightToBottomLeft](../Source/ThreeD/ClipRightToBottomLeft.asm) | Отсечение ребра, первая точка справа, вторая снизу слева |
| #C119 | [ThreeD.ClipRightToTop](../Source/ThreeD/ClipRightToTop.asm) | Отсечение ребра, первая точка справа, вторая сверху |
| #C12B | [ThreeD.ClipRightToTopRight](../Source/ThreeD/ClipRightToTopRight.asm) | Отсечение ребра, первая точка справа, вторая сверху справа |
| #C132 | [ThreeD.ClipRightToTopLeft](../Source/ThreeD/ClipRightToTopLeft.asm) | Отсечение ребра, первая точка справа, вторая сверху слева |
| #C144 | [ThreeD.ClipLeftToInside](../Source/ThreeD/ClipLeftToInside.asm) | Отсечение ребра, первая точка слева, вторая внутри окна |
| #C14A | [ThreeD.ClipLeftToRight](../Source/ThreeD/ClipLeftToRight.asm) | Отсечение ребра, первая точка слева, вторая справа |
| #C150 | [ThreeD.ClipLeftToBottom](../Source/ThreeD/ClipLeftToBottom.asm) | Отсечение ребра, первая точка слева, вторая снизу |
| #C162 | [ThreeD.ClipLeftToBottomRight](../Source/ThreeD/ClipLeftToBottomRight.asm) | Отсечение ребра, первая точка слева, вторая снизу справа |
| #C174 | [ThreeD.ClipLeftToBottomLeft](../Source/ThreeD/ClipLeftToBottomLeft.asm) | Отсечение ребра, первая точка слева, вторая снизу слева |
| #C17B | [ThreeD.ClipLeftToTop](../Source/ThreeD/ClipLeftToTop.asm) | Отсечение ребра, первая точка слева, вторая сверху |
| #C18D | [ThreeD.ClipLeftToTopRight](../Source/ThreeD/ClipLeftToTopRight.asm) | Отсечение ребра, первая точка слева, вторая сверху справа |
| #C1A5 | [ThreeD.ClipBottomToInside](../Source/ThreeD/ClipBottomToInside.asm) | Отсечение ребра, первая точка снизу, вторая внутри окна |
| #C1AB | [ThreeD.ClipBottomToRight](../Source/ThreeD/ClipBottomToRight.asm) | Отсечение ребра, первая точка снизу, вторая справа |
| #C1BD | [ThreeD.ClipBottomToLeft](../Source/ThreeD/ClipBottomToLeft.asm) | Отсечение ребра, первая точка снизу, вторая слева |
| #C1CF | [ThreeD.ClipBottomToBottomRight](../Source/ThreeD/ClipBottomToBottomRight.asm) | Отсечение ребра, первая точка снизу, вторая снизу справа |
| #C1D6 | [ThreeD.ClipBottomToTop](../Source/ThreeD/ClipBottomToTop.asm) | Отсечение ребра, первая точка снизу, вторая сверху |
| #C1DC | [ThreeD.ClipBottomToTopRight](../Source/ThreeD/ClipBottomToTopRight.asm) | Отсечение ребра, первая точка снизу, вторая сверху справа |
| #C1F1 | [ThreeD.ClipBottomToTopLeft](../Source/ThreeD/ClipBottomToTopLeft.asm) | Отсечение ребра, первая точка снизу, вторая сверху слева |
| #C20C | [ThreeD.ClipBottomRightToInside](../Source/ThreeD/ClipBottomRightToInside.asm) | Отсечение ребра, первая точка снизу справа, вторая внутри окна |
| #C228 | [ThreeD.ClipBottomRightToRight](../Source/ThreeD/ClipBottomRightToRight.asm) | Отсечение ребра, первая точка снизу справа, вторая справа |
| #C22F | [ThreeD.ClipBottomRightToLeft](../Source/ThreeD/ClipBottomRightToLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая слева |
| #C24E | [ThreeD.ClipBottomRightToBottom](../Source/ThreeD/ClipBottomRightToBottom.asm) | Отсечение ребра, первая точка снизу справа, вторая снизу |
| #C259 | [ThreeD.ClipBottomRightToBottomLeft](../Source/ThreeD/ClipBottomRightToBottomLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая снизу слева |
| #C25F | [ThreeD.ClipBottomRightToTop](../Source/ThreeD/ClipBottomRightToTop.asm) | Отсечение ребра, первая точка снизу справа, вторая сверху |
| #C274 | [ThreeD.ClipBottomRightToTopLeft](../Source/ThreeD/ClipBottomRightToTopLeft.asm) | Отсечение ребра, первая точка снизу справа, вторая сверху слева |
| #C28D | [ThreeD.ClipBottomLeftToInside](../Source/ThreeD/ClipBottomLeftToInside.asm) | Отсечение ребра, первая точка снизу слева, вторая внутри окна |
| #C2A9 | [ThreeD.ClipBottomLeftToRight](../Source/ThreeD/ClipBottomLeftToRight.asm) | Отсечение ребра, первая точка снизу слева, вторая справа |
| #C2BE | [ThreeD.ClipBottomLeftToLeft](../Source/ThreeD/ClipBottomLeftToLeft.asm) | Отсечение ребра, первая точка снизу слева, вторая слева |
| #C2C9 | [ThreeD.ClipBottomLeftToBottom](../Source/ThreeD/ClipBottomLeftToBottom.asm) | Отсечение ребра, первая точка снизу слева, вторая снизу |
| #C2D0 | [ThreeD.ClipBottomLeftToTop](../Source/ThreeD/ClipBottomLeftToTop.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху |
| #C2EF | [ThreeD.ClipBottomLeftToTopRight](../Source/ThreeD/ClipBottomLeftToTopRight.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху справа |
| #C308 | [ThreeD.ClipBottomLeftToTopLeft](../Source/ThreeD/ClipBottomLeftToTopLeft.asm) | Отсечение ребра, первая точка снизу слева, вторая сверху слева |
| #C30E | [ThreeD.ClipTopToInside](../Source/ThreeD/ClipTopToInside.asm) | Отсечение ребра, первая точка сверху, вторая внутри окна |
| #C314 | [ThreeD.ClipTopToRight](../Source/ThreeD/ClipTopToRight.asm) | Отсечение ребра, первая точка сверху, вторая справа |
| #C326 | [ThreeD.ClipTopToLeft](../Source/ThreeD/ClipTopToLeft.asm) | Отсечение ребра, первая точка сверху, вторая слева |
| #C338 | [ThreeD.ClipTopToBottom](../Source/ThreeD/ClipTopToBottom.asm) | Отсечение ребра, первая точка сверху, вторая снизу |
| #C33E | [ThreeD.ClipTopToBottomRight](../Source/ThreeD/ClipTopToBottomRight.asm) | Отсечение ребра, первая точка сверху, вторая снизу справа |
| #C359 | [ThreeD.ClipTopToBottomLeft](../Source/ThreeD/ClipTopToBottomLeft.asm) | Отсечение ребра, первая точка сверху, вторая снизу слева |
| #C36E | [ThreeD.ClipTopToTopLeft](../Source/ThreeD/ClipTopToTopLeft.asm) | Отсечение ребра, первая точка сверху, вторая сверху слева |
| #C375 | [ThreeD.ClipTopRightToInside](../Source/ThreeD/ClipTopRightToInside.asm) | Отсечение ребра, первая точка сверху справа, вторая внутри окна |
| #C391 | [ThreeD.ClipTopRightToRight](../Source/ThreeD/ClipTopRightToRight.asm) | Отсечение ребра, первая точка сверху справа, вторая справа |
| #C39C | [ThreeD.ClipTopRightToLeft](../Source/ThreeD/ClipTopRightToLeft.asm) | Отсечение ребра, первая точка сверху справа, вторая слева |
| #C3B1 | [ThreeD.ClipTopRightToBottom](../Source/ThreeD/ClipTopRightToBottom.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу |
| #C3D0 | [ThreeD.ClipTopRightToBottomRight](../Source/ThreeD/ClipTopRightToBottomRight.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу справа |
| #C3D6 | [ThreeD.ClipTopRightToBottomLeft](../Source/ThreeD/ClipTopRightToBottomLeft.asm) | Отсечение ребра, первая точка сверху справа, вторая снизу слева |
| #C3EF | [ThreeD.ClipTopRightToTop](../Source/ThreeD/ClipTopRightToTop.asm) | Отсечение ребра, первая точка сверху справа, вторая сверху |
| #C3F6 | [ThreeD.ClipTopLeftToInside](../Source/ThreeD/ClipTopLeftToInside.asm) | Отсечение ребра, первая точка сверху слева, вторая внутри окна |
| #C412 | [ThreeD.ClipTopLeftToRight](../Source/ThreeD/ClipTopLeftToRight.asm) | Отсечение ребра, первая точка сверху слева, вторая справа |
| #C431 | [ThreeD.ClipTopLeftToLeft](../Source/ThreeD/ClipTopLeftToLeft.asm) | Отсечение ребра, первая точка сверху слева, вторая слева |
| #C438 | [ThreeD.ClipTopLeftToBottom](../Source/ThreeD/ClipTopLeftToBottom.asm) | Отсечение ребра, первая точка сверху слева, вторая снизу |
| #C44D | [ThreeD.ClipTopLeftToBottomRight](../Source/ThreeD/ClipTopLeftToBottomRight.asm) | Отсечение ребра, первая точка сверху слева, вторая снизу справа |
| #C466 | [ThreeD.ClipTopLeftToTop](../Source/ThreeD/ClipTopLeftToTop.asm) | Отсечение ребра, первая точка сверху слева, вторая сверху |
| #C471 | [ThreeD.ClipTopLeftToTopRight](../Source/ThreeD/ClipTopLeftToTopRight.asm) | Отсечение ребра, первая точка сверху слева, вторая сверху справа |
| #C477 | [ThreeD.ComputeTopClipProduct](../Source/ThreeD/ComputeTopClipProduct.asm) | Подготовка числителя пересечения (First.First-0)*(First.Second-Second.Second) исходным знаковым умножителем |
| #C496 | [ThreeD.ComputeBottomClipProduct](../Source/ThreeD/ComputeBottomClipProduct.asm) | Подготовка числителя пересечения (First.First-95)*(First.Second-Second.Second) исходным знаковым умножителем |
| #C4B5 | [ThreeD.ComputeLeftClipProduct](../Source/ThreeD/ComputeLeftClipProduct.asm) | Подготовка числителя пересечения (First.First-Second.First)*(First.Second-0) исходным знаковым умножителем |
| #C4D4 | [ThreeD.ComputeRightClipProduct](../Source/ThreeD/ComputeRightClipProduct.asm) | Подготовка числителя пересечения (First.First-Second.First)*(First.Second-255) исходным знаковым умножителем |
| #C4F3 | [ThreeD.ClipInsideToTop](../Source/ThreeD/ClipInsideToTop.asm) | Отсечение ребра, первая точка внутри окна, вторая сверху |
| #C4F6 | [ThreeD.AppendTopClipIntersection](../Source/ThreeD/AppendTopClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C53D | [ThreeD.ClipInsideToBottom](../Source/ThreeD/ClipInsideToBottom.asm) | Отсечение ребра, первая точка внутри окна, вторая снизу |
| #C540 | [ThreeD.AppendBottomClipIntersection](../Source/ThreeD/AppendBottomClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C588 | [ThreeD.ClipInsideToLeft](../Source/ThreeD/ClipInsideToLeft.asm) | Отсечение ребра, первая точка внутри окна, вторая слева |
| #C58B | [ThreeD.AppendLeftClipIntersection](../Source/ThreeD/AppendLeftClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C5E4 | [ThreeD.ClipInsideToRight](../Source/ThreeD/ClipInsideToRight.asm) | Отсечение ребра, первая точка внутри окна, вторая справа |
| #C5E7 | [ThreeD.AppendRightClipIntersection](../Source/ThreeD/AppendRightClipIntersection.asm) | Добавление пересечения границы с исходным делением и побайтовой проверкой координаты |
| #C641 | [ThreeD.AppendTopLeftClipCorner](../Source/ThreeD/AppendTopLeftClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C64C | [ThreeD.AppendTopRightClipCorner](../Source/ThreeD/AppendTopRightClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C657 | [ThreeD.AppendBottomLeftClipCorner](../Source/ThreeD/AppendBottomLeftClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C662 | [ThreeD.AppendBottomRightClipCorner](../Source/ThreeD/AppendBottomRightClipCorner.asm) | Добавление угла окна при нулевом CornerBlock |
| #C66D | [ThreeD.CompareTopLeftProducts](../Source/ThreeD/CompareTopLeftProducts.asm) | Вычитание LeftProduct из TopProduct с передачей заёма младшего слова |
| #C681 | [ThreeD.CompareTopRightProducts](../Source/ThreeD/CompareTopRightProducts.asm) | Вычитание RightProduct из TopProduct с передачей заёма младшего слова |
| #C695 | [ThreeD.CompareBottomLeftProducts](../Source/ThreeD/CompareBottomLeftProducts.asm) | Вычитание LeftProduct из BottomProduct с передачей заёма младшего слова |
| #C6A9 | [ThreeD.CompareBottomRightProducts](../Source/ThreeD/CompareBottomRightProducts.asm) | Вычитание RightProduct из BottomProduct с передачей заёма младшего слова |
| #C6BD | [ThreeD.ComputeSecondAxisDelta](../Source/ThreeD/ComputeSecondAxisDelta.asm) | Разность координат Second второй и первой точки с оборачиванием до слова |
| #C6C8 | [ThreeD.ComputeFirstAxisDelta](../Source/ThreeD/ComputeFirstAxisDelta.asm) | Разность координат First второй и первой точки с оборачиванием до слова |
| #C6D3 | [ThreeD.AppendSecondClipPoint](../Source/ThreeD/AppendSecondClipPoint.asm) | Добавление младших байтов второй точки с общим входом записи пары DE |
| #C6EA | [ThreeD.ExitClipContour](../Source/ThreeD/ExitClipContour.asm) | Специальное завершение контура со снятием трёх служебных слов |
| #C6F4 | [ThreeD.MultiplySigned16](../Source/ThreeD/MultiplySigned16.asm) | Знаковое произведение двух слов с тремя ядрами и исходным исключением второго операнда 8000 |
| #C88C | [ThreeD.DivideSigned32To16](../Source/ThreeD/DivideSigned32To16.asm) | Деление числителя HL, A, альтернативного A на signed16 с исходным побитовым дополнением |
| #C941 | [ThreeD.ClipSingleEdge](../Source/ThreeD/ClipSingleEdge.asm) | Отсечение одиночного ребра с обменом внутренней первой точки и рамкой трёх возвратов |
| #C99B | [ThreeD.BuildRenderCoefficients](../Source/ThreeD/BuildRenderCoefficients.asm) | Построение девяти байтовых коэффициентов по трём фазам либо по одной фазе |
| #CB23 | [ThreeD.ComposeRenderMatrix](../Source/ThreeD/ComposeRenderMatrix.asm) | Композиция исходной матрицы и ориентации с одноосным режимом и точными четвертями |
| #CF08 | [ThreeD.UnknownCF08](../Source/ThreeD/UnknownCF08.asm) | Unknown, назначение этого фрагмента ещё не установлено |
| #D10A | [ThreeD.ClearWorkBuffer](../Source/ThreeD/ClearWorkBuffer.asm) | Заполнение линейного буфера 8000..8BFF байтами FF через временный SP с восстановлением CPU-стека |
| #D12C | [ThreeD.MultiplySignedScaled](../Source/ThreeD/MultiplySignedScaled.asm) | Знаковое произведение DE и байтового коэффициента с усечением к нулю после деления на 128 и выходом через IX |
| #D1C0 | [ThreeD.PolygonFillRows](../Source/ThreeD/PolygonFillRows.asm) | Строковое ядро линейной заливки с развёрнутой записью, крайними масками и коррекцией двух рёбер |
| #D268 | [ThreeD.SelectPolygonRightEdge](../Source/ThreeD/SelectPolygonRightEdge.asm) | Передача управления правому обновлению без изменения контекста |
| #D26B | [ThreeD.WrapPolygonLeftEdge](../Source/ThreeD/WrapPolygonLeftEdge.asm) | Оборачивание обратного поиска к последней First кольца |
| #D272 | [ThreeD.UpdatePolygonLeftEdge](../Source/ThreeD/UpdatePolygonLeftEdge.asm) | Поиск восходящего левого ребра, вычисление целого шага и ошибки, выбор продолжения заливки |
| #D3A8 | [ThreeD.WrapPolygonRightEdge](../Source/ThreeD/WrapPolygonRightEdge.asm) | Оборачивание прямого поиска к первой First кольца |
| #D3AD | [ThreeD.UpdatePolygonRightEdge](../Source/ThreeD/UpdatePolygonRightEdge.asm) | Поиск восходящего правого ребра и вычисление его упакованного шага и дробной ошибки |
| #D4C1 | [ThreeD.SelectPolygonRowLimit](../Source/ThreeD/SelectPolygonRowLimit.asm) | Выбор ближайшего предела строк с приоритетом левого ребра и настройкой следующего перехода |
| #D4F5 | [ThreeD.SetShortNegativeRightStep](../Source/ThreeD/SetShortNegativeRightStep.asm) | Настройка нулевого целого шага короткого отрицательного правого наклона и восстановление временного контекста |
| #D503 | [ThreeD.WrapPolygonLeftTop](../Source/ThreeD/WrapPolygonLeftTop.asm) | Оборачивание поиска левого конца верхней горизонтали |
| #D50A | [ThreeD.WrapPolygonRightTop](../Source/ThreeD/WrapPolygonRightTop.asm) | Оборачивание поиска правого конца верхней горизонтали |
| #D50F | [ThreeD.ReturnPolygonFill](../Source/ThreeD/ReturnPolygonFill.asm) | Восстановление сохранённого HL и внешний возврат плоского контура |
| #D511 | [ThreeD.PreparePolygonFill](../Source/ThreeD/PreparePolygonFill.asm) | Подготовка диапазона строк, верхних вершин двух цепочек, масок и временного стека заливки |
| #D5C9 | [ThreeD.TransformObjectVertices](../Source/ThreeD/TransformObjectVertices.asm) | Копирование потока объекта и преобразование всех его фиксированных групп вершин |
| #D5F9 | [ThreeD.PrepareRenderVertexProducts](../Source/ThreeD/PrepareRenderVertexProducts.asm) | Подготовка трёх пар координат и трёх глубин табличным произведением матрицы и входных компонентов |
| #D694 | [ThreeD.ProjectRenderVertexGroup](../Source/ThreeD/ProjectRenderVertexGroup.asm) | Построение комбинаций координат и перспективная запись выбранной группы вершин |
| #D7A0 | [ThreeD.ProjectRenderVertex](../Source/ThreeD/ProjectRenderVertex.asm) | Перспективная запись одной вершины с исходной нормализацией и косвенным продолжением |
| #DBBD | [ThreeD.RenderClippedRecords](../Source/ThreeD/RenderClippedRecords.asm) | Вывод записей объекта с проверкой кодов точек и отсечением граней и открытых сегментов |
| #DD23 | [ThreeD.RenderInsideRecords](../Source/ThreeD/RenderInsideRecords.asm) | Вывод граней и ломаных объекта с внутренними точками без дополнительного отсечения |
| #DDD1 | [ThreeD.CombineListedVertexCodes](../Source/ThreeD/CombineListedVertexCodes.asm) | Объединение кодов границ перечисленных точек с ранним выходом по нулевому коду |
| #DDF0 | [ThreeD.DrawLinearLine](../Source/ThreeD/DrawLinearLine.asm) | Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки |
| #DEF0 | [ThreeD.AbortProjectedVertexScan](../Source/ThreeD/AbortProjectedVertexScan.asm) | Завершение сканирования точек по маркеру отказа перспективы без отката предыдущих кодов |
| #DEF3 | [ThreeD.ClassifyProjectedVertices](../Source/ThreeD/ClassifyProjectedVertices.asm) | Заполнение кодов границ экранных точек и накопление общего кода объекта |
| #DFB6 | [ThreeD.CheckFaceOrientation](../Source/ThreeD/CheckFaceOrientation.asm) | Проверка ориентации выбранной тройки экранных точек по знаку разности двух произведений |
| #E500 | [Voxel.RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) | Последовательное преобразование трёх векторов ориентации #9B00..#9B11 по углам #9B14, #9B12 и #9B13 |
| #E8A1 | [Voxel.SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | Знаковое табличное произведение с использованием входного IY как младшей части накопителя |
| #EC00 | [Voxel.CreateSmallEffect](../Source/Voxel/CreateSmallEffect.asm) | Инициализация эффекта с ресурсом #D800 и параметрами #0C, #0C, #0D |
| #EC0E | [Voxel.ConfigureSmallEffect](../Source/Voxel/ConfigureSmallEffect.asm) | Общий хвост малого эффекта, настройка параметров #0C и #0D перед поиском свободной записи |
| #EC1B | [Voxel.CreateLargeEffect](../Source/Voxel/CreateLargeEffect.asm) | Инициализация эффекта с ресурсом #C400 и параметрами #14, #14, #08 |
| #EC33 | [Voxel.AllocateEffect](../Source/Voxel/AllocateEffect.asm) | Поиск свободной записи #12 байт по знаку и нулевому признаку в поле +7 |
| #EC7F | [Voxel.ClipSprite](../Source/Voxel/ClipSprite.asm) | Отсечение прямоугольника по горизонтали 64 и вертикали 24 с расчётом краевых смещений |
| #EE7A | [Voxel.RasterizeSprite](../Source/Voxel/RasterizeSprite.asm) | Развёрнутый проход по парам кодов спрайта с маскированием прозрачных половин и шагом по строкам |
| #F931 | [Voxel.Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | Умножение младших семи битов A на BC с результатом HL modulo #10000 |
| #F957 | [Voxel.Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | Деление младших семи битов A на E с восемью дробными битами, подтверждённый делитель 1..128 |
| #F9E9 | [Voxel.ProjectEffectPoint](../Source/Voxel/ProjectEffectPoint.asm) | Проекция точки эффекта с двумя знаковыми поправками |
| #FA3A | [Voxel.DrawProjectedEffect](../Source/Voxel/DrawProjectedEffect.asm) | Проекция двух углов эффекта и передача прямоугольника на отсечение |
| #C870 | [Controls.CopyViewportToScreen](../Source/Controls/CopyViewportToScreen.asm) | Перенос линейного растра 256 на 96 пикселей в верхнюю половину экрана |
| #C882 | [Controls.CopyScreenRows](../Source/Controls/CopyScreenRows.asm) | Стековый перенос страниц линейного растра в символьные строки экрана |
| #CA8D | [Controls.NextBufferRandom](../Source/Controls/NextBufferRandom.asm) | Получение байта из изменяемого 16-битового состояния генератора |
| #CAB3 | [Controls.InitializeBufferPoints](../Source/Controls/InitializeBufferPoints.asm) | Подготовка 35 координат Y,X с исходным ограничением диапазонов |
| #CAE3 | [Controls.XorBufferPoints](../Source/Controls/XorBufferPoints.asm) | Наложение 35 точек на линейный буфер через четыре таблицы адресации |
| #CB00 | [Controls.UpdateBufferPoints](../Source/Controls/UpdateBufferPoints.asm) | Последовательная коррекция 35 точек по Y, X и двум табличным коэффициентам |
| #CE16 | [Controls.RespawnPointIndexPos](../Source/Controls/RespawnPointIndexPos.asm) | Возврат точки с чередованием сторон для неотрицательного индекса управляющей таблицы |
| #CE5D | [Controls.RespawnPointIndexNeg](../Source/Controls/RespawnPointIndexNeg.asm) | Возврат точки с противоположным чередованием сторон для отрицательного индекса таблицы |
| #CEA4 | [Controls.FillEvenSpan](../Source/Controls/FillEvenSpan.asm) | Обратное заполнение 2*A байтов через изменяемый JR в пределах страницы |
| #CEB7 | [Controls.FillEvenSpanHead](../Source/Controls/FillEvenSpanHead.asm) | Первые 12 записей общего 30-байтового хвоста заполнителя |
| #CECF | [Controls.FillEvenSpanTail](../Source/Controls/FillEvenSpanTail.asm) | Последние 18 записей заполнителя, восстановление HL и чтение режима |
| #CEFA | [Controls.ProjectAndDrawBody](../Source/Controls/ProjectAndDrawBody.asm) | Проекция тела в режиме 0, допуск компонент и рисование заданным рисунком |
| #CF0B | [Controls.BuildBodyProjection](../Source/Controls/BuildBodyProjection.asm) | Выбор глубины, кодирование двух смещений и расчёт радиуса проекции |
| #D0CA | [Controls.EncodeProjectionRatio](../Source/Controls/EncodeProjectionRatio.asm) | Нормализация отношения модулей с возвратом из внешней проекции при отказе |
| #D10A | [Controls.ContinueProjectionRatio](../Source/Controls/ContinueProjectionRatio.asm) | Продолжение сравнения, кодирование отношения и снятие внутреннего возврата |
| #D165 | [Controls.DivideByteFraction](../Source/Controls/DivideByteFraction.asm) | Подготовка делимого A*256 и последовательное исполнение делителя |
| #D167 | [Controls.DivideWordByByte](../Source/Controls/DivideWordByByte.asm) | Восьмишаговое деление слова A:E на B с частным в D и остатком в A |
| #D18D | [Controls.DrawRightClippedHalfDown](../Source/Controls/DrawRightClippedHalfDown.asm) | Рисование нижней половины с неподвижной правой границей и переходом к двум криволинейным краям |
| #D1A2 | [Controls.DrawRightClippedHalfUp](../Source/Controls/DrawRightClippedHalfUp.asm) | Рисование верхней половины с неподвижной правой границей и переходом к двум криволинейным краям |
| #D1B6 | [Controls.DrawLeftClippedHalfDown](../Source/Controls/DrawLeftClippedHalfDown.asm) | Рисование нижней половины с неподвижной левой границей и переходом к двум криволинейным краям |
| #D1CB | [Controls.DrawLeftClippedHalfUp](../Source/Controls/DrawLeftClippedHalfUp.asm) | Рисование верхней половины с неподвижной левой границей и переходом к двум криволинейным краям |
| #D1DF | [Controls.DrawCircleHalfDown](../Source/Controls/DrawCircleHalfDown.asm) | Рисование нижней половины внутреннего сечения с исходной разностью квадратов |
| #D1F4 | [Controls.DrawCircleHalfUp](../Source/Controls/DrawCircleHalfUp.asm) | Рисование верхней половины внутреннего сечения с исходной разностью квадратов |
| #D208 | [Controls.FillInteriorRowsUp](../Source/Controls/FillInteriorRowsUp.asm) | Заливка внутренних 30 байтов строк вверх с ограничением верхним краем |
| #D211 | [Controls.FillInteriorRowsDown](../Source/Controls/FillInteriorRowsDown.asm) | Заливка внутренних 30 байтов строк вниз с ограничением нижним краем |
| #D21A | [Controls.DrawProjectedBody](../Source/Controls/DrawProjectedBody.asm) | Выбор малого профиля или большого круга по результату малого рисователя |
| #D232 | [Controls.CallLargeCircle](../Source/Controls/CallLargeCircle.asm) | Вызов большого рисователя с исходной дополнительной рамкой |
| #D236 | [Controls.DrawLargeCircle](../Source/Controls/DrawLargeCircle.asm) | Выбор и рисование большого кругового тела по спроецированным смещениям |
| #D30B | [Controls.ReadByteSquare](../Source/Controls/ReadByteSquare.asm) | Чтение 16-битного квадрата байтового индекса из двух физических плоскостей |
| #D314 | [Controls.DrawInteriorCircle](../Source/Controls/DrawInteriorCircle.asm) | Рисование верхней и нижней половин большого контура без горизонтального отсечения |
| #D320 | [Controls.BuildCircleSpan](../Source/Controls/BuildCircleSpan.asm) | Построение адресов и включающих масок двух краёв сечения большого контура |
| #D340 | [Controls.DrawFullWidthCircle](../Source/Controls/DrawFullWidthCircle.asm) | Заливка внутренних полос и двух остаточных половин широкого круга |
| #D38C | [Controls.DrawFullWidthCircleSlice](../Source/Controls/DrawFullWidthCircleSlice.asm) | Заливка внутренней полосы от вертикальной границы и одной остаточной половины |
| #D3DA | [Controls.DrawHorizontallyClippedCircle](../Source/Controls/DrawHorizontallyClippedCircle.asm) | Рисование двух половин круга с одним исходно неподвижным горизонтальным краем |
| #D404 | [Controls.DrawCornerCircleSlice](../Source/Controls/DrawCornerCircleSlice.asm) | Рисование одного сечения с вертикальным и горизонтальным отсечением |
| #D485 | [Controls.DrawVerticalCircleSlice](../Source/Controls/DrawVerticalCircleSlice.asm) | Рисование вертикально отсечённого кругового сечения с двумя криволинейными краями |
| #D4CB | [Controls.PrepareCircleRightClip](../Source/Controls/PrepareCircleRightClip.asm) | Подготовка левого криволинейного края и фиксированного правого столбца 31 |
| #D4E4 | [Controls.PrepareCircleLeftClip](../Source/Controls/PrepareCircleLeftClip.asm) | Подготовка фиксированного левого столбца 1 и правого криволинейного края |
| #D504 | [Controls.LoadCircleMidpoint](../Source/Controls/LoadCircleMidpoint.asm) | Загрузка рабочих координат, радиуса и начального состояния среднего алгоритма |
| #D515 | [Controls.BuildLeftSpanMask](../Source/Controls/BuildLeftSpanMask.asm) | Вычисление адреса пиксельного байта и маски от старшего бита до X включительно |
| #D53C | [Controls.BuildRightSpanMask](../Source/Controls/BuildRightSpanMask.asm) | Вычисление адреса пиксельного байта и маски от X до младшего бита включительно |
| #D56C | [Controls.LoadCircleClipState](../Source/Controls/LoadCircleClipState.asm) | Загрузка рабочего X и состояния сечения для отсечённого контура |
| #D57B | [Controls.PrepareInteriorSpan](../Source/Controls/PrepareInteriorSpan.asm) | Подготовка полной внутренней маски и общие входы заливки строк |
| #D609 | [Controls.SqrtSquareDiff](../Source/Controls/SqrtSquareDiff.asm) | Целый корень разности квадратов с исходным входным Carry и оборачиванием слова |
| #D633 | [Controls.CircleRasterCore](../Source/Controls/CircleRasterCore.asm) | Двухфазное сужение кругового сечения с двумя криволинейными краями |
| #D727 | [Controls.ResumeCirclePushSpan](../Source/Controls/ResumeCirclePushSpan.asm) | Восстановление CPU-стека после обычной PUSH-заливки и продолжение горизонтальной фазы |
| #D73B | [Controls.LeftClippedCircleCore](../Source/Controls/LeftClippedCircleCore.asm) | Двухфазное сужение с неподвижным левым краем до совпадения порога Aprime |
| #D833 | [Controls.RightClippedCircleCore](../Source/Controls/RightClippedCircleCore.asm) | Двухфазное сужение с неподвижным правым краем до совпадения порога Aprime |
| #D925 | [Controls.AdvanceRasterUp](../Source/Controls/AdvanceRasterUp.asm) | Шаг на строку вверх с чередованием рисунка и нелокальным выходом за верхним краем |
| #D940 | [Controls.AdvanceRasterDown](../Source/Controls/AdvanceRasterDown.asm) | Шаг на строку вниз с чередованием рисунка и нелокальным выходом за нижним краем |
| #D95F | [Controls.ProjectAndCheckComponents](../Source/Controls/ProjectAndCheckComponents.asm) | Построение проекции и проверка двух компонент относительно постоянной опоры Component2 |
| #D9B0 | [Controls.BuildSmallBodyMasks](../Source/Controls/BuildSmallBodyMasks.asm) | Подготовка строковых масок малой фигуры из упакованной затравки радиуса |
| #D9DE | [Controls.DrawSmallBody](../Source/Controls/DrawSmallBody.asm) | Рисование малой симметричной фигуры радиуса 2..8 строковыми масками в линейном растре |
| #DAB9 | [Controls.CompareComponents](../Source/Controls/CompareComponents.asm) | Сравнение двух компонентов после перехода IY к следующей трёхбайтовой записи |
| #DADE | [Controls.RunTemporaryModule](../Source/Controls/RunTemporaryModule.asm) | Сохранение памяти по банкам, распаковка временного модуля и восстановление полётного кода |
| #DC9B | [Controls.RelocateStationReload](../Source/Controls/RelocateStationReload.asm) | Копирование 256 байтов блока загрузки STATIONF в общую RAM и передача управления 4000 |
| #DCE3 | [Controls.PrepareStationReload](../Source/Controls/PrepareStationReload.asm) | Очистка атрибутов, сохранение 512 байтов состояния и перенос следующей стадии загрузки станции |
| #DD5D | [Controls.StepWordRandom](../Source/Controls/StepWordRandom.asm) | Обновление двухсловного состояния генератора и возврат XOR его четырёх байтов |
| #DE0A | [Controls.BuildAndActivateParameters](../Source/Controls/BuildAndActivateParameters.asm) | Подготовка параметров в банке 1 и хвостовая активация набора с выбором банка 0 |
| #DE10 | [Controls.BuildParameterTables](../Source/Controls/BuildParameterTables.asm) | Формирование пятнадцати параметров и девяти строковых значений по зерну и исходным таблицам |
| #DE9A | [Controls.BuildSeededIndices](../Source/Controls/BuildSeededIndices.asm) | Формирование четырёх индексов из двухсловного зерна, координатной области и числа шагов генератора |
| #E021 | [Controls.UpdateGlyphIndicators](../Source/Controls/UpdateGlyphIndicators.asm) | Очистка двух экранных зон и обновление до трёх трёхстрочных знаков с точными байтовыми ограничениями |
| #E14E | [Controls.OrThreeRowGlyph](../Source/Controls/OrThreeRowGlyph.asm) | Наложение трёхстрочного фазового знака операцией OR на два байта каждой строки экрана |
| #E291 | [Controls.DrawRadar](../Source/Controls/DrawRadar.asm) | Фазовый фон радара, центральная метка и вывод объектов со знаковыми линиями |
| #E8FD | [Controls.DrawSixRowGauge](../Source/Controls/DrawSixRowGauge.asm) | Вывод шестистрочной шкалы узором AA, частичного столбца и нулевого хвоста |
| #E97A | [Controls.ToggleTargetOverlay](../Source/Controls/ToggleTargetOverlay.asm) | XOR рамки и спроецированных значков объектов в линейном буфере |
| #EC0E | [Controls.InitializeTextWindow](../Source/Controls/InitializeTextWindow.asm) | Сброс курсоров очереди и настройка тридцати строк стековой прокрутки |
| #EC56 | [Controls.QueueNumber](../Source/Controls/QueueNumber.asm) | Подготовка числовой записи типа 2 из A и продолжение в производителе текстовой очереди |
| #EC59 | [Controls.QueueTextItem](../Source/Controls/QueueTextItem.asm) | Ограниченный поиск свободной записи очереди и сохранение числа либо указателя строки |
| #ECA2 | [Controls.ConsumeTextQueue](../Source/Controls/ConsumeTextQueue.asm) | Вывод очередного числа либо символа активной строки текстовой очереди |
| #ECF3 | [Controls.PrintByteDecimal](../Source/Controls/PrintByteDecimal.asm) | Десятичный вывод байта с минимальной шириной два знака |
| #ED28 | [Controls.ScrollTextWindow](../Source/Controls/ScrollTextWindow.asm) | Перенос пяти рядов текста вверх через SP и очистка нижнего ряда |
| #EFC4 | [Controls.PrintTextGlyph](../Source/Controls/PrintTextGlyph.asm) | Подготовка вывода знака 4 на 6 пикселей с проверкой правой границы |
| #EFF1 | [Controls.DrawGlyphRows](../Source/Controls/DrawGlyphRows.asm) | Слияние шести строк упакованного знака с выбранной тетрадой экрана |
| #F094 | [Controls.XorBufferMarker](../Source/Controls/XorBufferMarker.asm) | Наложение одиннадцати байтов маркера на линейный буфер через XOR |
| #F10D | [Controls.TickBcdCounter](../Source/Controls/TickBcdCounter.asm) | Вращение восьмитактового делителя и инкремент четырёх BCD-пар с частичным выводом |
| #F142 | [Controls.DrawBcdCounter](../Source/Controls/DrawBcdCounter.asm) | Вывод младшей BCD-пары и старших пар, выбранных цепочкой переносов |
| #F188 | [Controls.DrawCounterNibble](../Source/Controls/DrawCounterNibble.asm) | Рисование младшей тетрады через общую пару знаков с сохранением основных регистров |
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
| #6000 | [Action.QueueNumberBank1](../Source/Action/QueueNumberBank1.asm) | Передача байтового числа A в очередь Controls банка 1 с фиксированным возвратом страницы 10 |
| #6010 | [Action.PrintByteAndScrollBank1](../Source/Action/PrintByteAndScrollBank1.asm) | Прямой десятичный вывод байта с обязательной прокруткой окна банка 1 |
| #6029 | [Action.PrintByteBank1](../Source/Action/PrintByteBank1.asm) | Прямой десятичный вывод байта в окне банка 1 с исходной попыткой записи в ПЗУ |
| #6040 | [Action.QueueTextItemBank1](../Source/Action/QueueTextItemBank1.asm) | Передача записи DE в очередь Controls банка 1 с сохранением регистров и возвратом страницы 10 |
| #6054 | [Action.ShowNoiseBeforeReload](../Source/Action/ShowNoiseBeforeReload.asm) | Вывод шумовых кадров и ожидание клавиши перед загрузкой станции |
