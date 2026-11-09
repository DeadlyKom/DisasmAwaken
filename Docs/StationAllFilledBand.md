# Заполнение одиннадцатой строки полосовой рамки

[SetAllFilledBandMode](../Source/Station/SetAllFilledBandMode.asm) по CCAA
выбирает SetCutoutPattern и переходит по CCB2. Этот вход пропускает начальную
загрузку SetOutlinePattern обычного настройщика. Проверка бита 0 FillMode
и ветвь восстановления обычного режима выполняются по тому же коду.
[Общий настройщик](../Source/Station/SetBandFillMode.asm),
[операнды рамки](StationSpans.md).

При нулевом бите слово BandLine11 получает SetCutoutPattern вместо
SetOutlinePattern. Пять остальных изменяемых слов тоже получают
SetCutoutPattern. Фиксированные вызовы рисователя остаются прежними.
При единичном бите восстанавливается обычный набор из шести слов.

В 65 536 сценариях CCAA сопоставлены все пары исходного FillMode и F,
результат A, полный F, DE, стек, сохраняемые регистры и шесть слов.
В 5 172 профилях с настоящим рисователем дополнительно сравнены пиксели
рамки, глифы, карта владельцев и индексная таблица. Штатный вызывающий
путь CCAA ещё не установлен. [Настройка](../Tools/Disasm/Reports/BandModeVerification.json),
[рисование](../Tools/Disasm/Reports/AllFilledCaptionItemVerification.json).
