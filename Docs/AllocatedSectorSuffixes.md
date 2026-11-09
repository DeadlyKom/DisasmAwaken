# Физические суффиксы выделенных секторов

[Проверка происхождения](../Tools/Disasm/Research/InspectAllocatedSectorSuffixes.py), [первичный реестр](../Tools/Disasm/Reports/AllocatedSectorSuffixInspection.json), [текущие диапазоны](../Tools/Disasm/Research/AllocatedSectorSuffixResources.py).

16 диапазонов, 2558 байтов, находятся после объявленной длины соответствующих небейсиковых файлов и внутри выделенных им секторов. Это положительно установленная физическая роль. Содержимое всех байтов, включая повторяющийся текст и нули, сохраняется буквально. Термины «неиспользуемый», «мусор», «свободная память» к ним не применяются. Чтение TR-DOS полными секторами, прямое секторное чтение и последующие обращения игры этой классификацией не исключаются.

BASIC-файл AWAKEN исключён. За его объявленной длиной находятся подтверждённые машинные модули вступления, поэтому общий вывод о роли всех байтов после поля Length был бы ошибкой. Длина каталога и доказанный исполняемый состав не смешиваются.

У OBJECT3D и FINALF прежний неизвестный диапазон пересекал логическую границу. Неизвестная часть внутри длины остаётся отдельной и не классифицируется по роли последующего суффикса. Все физические смещения и порядок включений сохранены.

| Слот | Начало суффикса | Байтов | Исходный ресурс |
| --- | --- | --- | --- |
| 5 | 0F18 | 232 | [LANG](../Source/Resources/05_LANG/AfterMarketScript.bin) |
| 6 | 3E6A | 150 | [D3D](../Source/Resources/06_D3D/AfterDescriptionText.bin) |
| 8 | 1721 | 223 | [HELP](../Source/Resources/08_HELP/SectorTail.bin) |
| 18 | 1C2D | 211 | [DATAS](../Source/Resources/18_DATAS/SectorTail.bin) |
| 19 | 2020 | 224 | [3DPART](../Source/Resources/19_3DPART/SectorTail.bin) |
| 21 | 0EC8 | 56 | [VOXAL](../Source/Resources/21_VOXAL/SectorTail.bin) |
| 22 | 1ADE | 34 | [CONTROL0](../Source/Resources/22_CONTROL0/SectorTail.bin) |
| 23 | 194A | 182 | [CONTROL](../Source/Resources/23_CONTROL/SectorTail.bin) |
| 24 | 2954 | 172 | [OBJECT3D](../Source/Resources/24_OBJECT3D/SectorTail.bin) |
| 29 | 4AAA | 86 | [FINALF](../Source/Resources/29_FINALF/SectorTail.bin) |
| 30 | 48F4 | 12 | [scene1po](../Source/Resources/30_scene1po/SectorTail.bin) |
| 39 | 0C04 | 252 | [BAR](../Source/Resources/39_BAR/SectorTail.bin) |
| 40 | 3F8C | 116 | [BD0](../Source/Resources/40_BD0/SectorTail.bin) |
| 41 | 3F18 | 232 | [BD1](../Source/Resources/41_BD1/SectorTail.bin) |
| 42 | 3F78 | 136 | [BD2](../Source/Resources/42_BD2/SectorTail.bin) |
| 43 | 2F10 | 240 | [BD3](../Source/Resources/43_BD3/SectorTail.bin) |

VerifySources проверяет каждый текущий ресурс по извлечённым физическим секторам, его SourceMap, начало после объявленной длины и полный набор байтов. Публикация предварительно сверяет оригинальный TRD, длины и SHA256. Сборка и нативный запуск не выполнялись. Эта физическая классификация не является полным смысловым разбором возможных игровых потребителей.
