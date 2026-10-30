# StationExit

## LoadAction

[StationExit.LoadAction](../../Source/StationExit/LoadAction.asm)

Вход #4200, физическая запись 4, смещения #216C..#21B3. Адрес исполнения получен из исходного LDIR станции. Инициализация MUZ1, копирование имени ACTION, запрос TR-DOS и условное продолжение с передачей контекста разобраны в [StationExit](../StationExit.md). Внутренний вход AfterLoad находится по #4236, на стеке TR-DOS адрес этого входа. Полный договор находится в исходнике.

[Ключ файла](../../Source/StationExit/Data/ActionFileName.asm) физически следует за кодом, но не исполняется, поскольку фрагмент заканчивается JP 6000.
