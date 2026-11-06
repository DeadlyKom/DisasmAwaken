# Шумовые кадры перед загрузкой станции

[ShowNoiseBeforeReload](../Source/Action/ShowNoiseBeforeReload.asm)
ставит элемент `#F2A5` в очередь текста, выбирает курсор AY `#EE4D`,
устанавливает I в `#3F` и IY в `#5C3A`. Затем копирует 3072 байта
из ROM 1 по адресу `#0500 + R` в линейный буфер `#8000`.

После `EI/HALT/DI` подключается CONTROL. Выполняются
[CopyViewportToScreen](../Source/Controls/CopyViewportToScreen.asm)
и [ConsumeTextQueue](../Source/Controls/ConsumeTextQueue.asm).
После возврата в ACTION обновляются эффекты AY.
Первые 99 опросов клавиатуры не меняют маршрут.
Начиная со 100-го кадра значение `#1F` в младших пяти битах
продолжает ожидание, любое другое ведёт по `#AAC4` к
[RelocateStationReload](../Source/Controls/RelocateStationReload.asm).

[Модель](../Tools/Disasm/Research/CheckActionNoiseExit.py) проверила
404 кадра в четырёх сценариях, включая удержанную клавишу во время
задержки и дополнительные кадры ожидания. Сверены все 3072 байта
копии ROM каждого кадра, ввод, переключения страниц и SP на `#AAC4`.
Пробуждение HALT задано явно. Аппаратный IRQ и дальнейшая загрузка
станции в этой проверке не исполнялись.
[Результаты](../Tools/Disasm/Reports/ActionNoiseExitVerification.json)
