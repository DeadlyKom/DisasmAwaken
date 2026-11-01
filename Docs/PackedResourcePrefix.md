# Физический префикс ресурсов HR

После FPackedHeader размером шесть байтов каждый ресурс хранит три слова FPackedFinalBytes. Они являются последними шестью байтами распакованного результата. Физический именованный экземпляр FinalBytes начинается по смещению 6, Bitstream по смещению 12, Tail остаётся по PackedSize. Полный секторный размер сохраняется.

Поля BytesMinus6, BytesMinus4 и BytesMinus2 содержат пары little-endian, соответствующие результату U-6..U-1. Поля не являются счётчиками либо адресами. [Объявление структуры](../Includes/Structs/Include.inc), [алгоритм распаковки](UnpackResource.md), [исходная процедура](../Source/Station/UnpackResource.asm).

| Запись и экран | Физический исходник | BytesMinus6 | BytesMinus4 | BytesMinus2 |
|---|---|---|---|---|
| 9, 0 | [Screen00.asm](../Source/Screens/Station/Screen00.asm) | `#7878` | `#7878` | `#7878` |
| 9, 1 | [Screen01.asm](../Source/Screens/Station/Screen01.asm) | `#6868` | `#6868` | `#6868` |
| 9, 2 | [Screen02.asm](../Source/Screens/Station/Screen02.asm) | `#7878` | `#7878` | `#7878` |
| 9, 3 | [Screen03.asm](../Source/Screens/Station/Screen03.asm) | `#7878` | `#7878` | `#7878` |
| 9, 4 | [Screen04.asm](../Source/Screens/Station/Screen04.asm) | `#6969` | `#6969` | `#6969` |
| 9, 5 | [Screen05.asm](../Source/Screens/Station/Screen05.asm) | `#2828` | `#2828` | `#2828` |
| 9, 6 | [Screen06.asm](../Source/Screens/Station/Screen06.asm) | `#7878` | `#7878` | `#7878` |
| 9, 7 | [Screen07.asm](../Source/Screens/Station/Screen07.asm) | `#7878` | `#7878` | `#6878` |
| 9, 8 | [Screen08.asm](../Source/Screens/Station/Screen08.asm) | `#6868` | `#6868` | `#7868` |
| 9, 9 | [Screen09.asm](../Source/Screens/Station/Screen09.asm) | `#7878` | `#7878` | `#7878` |
| 9, 10 | [Screen10.asm](../Source/Screens/Station/Screen10.asm) | `#7878` | `#7878` | `#7868` |
| 9, 11 | [Screen11.asm](../Source/Screens/Station/Screen11.asm) | `#5858` | `#5858` | `#5858` |
| 9, 12 | [Screen12.asm](../Source/Screens/Station/Screen12.asm) | `#6868` | `#7868` | `#6868` |
| 9, 13 | [Screen13.asm](../Source/Screens/Station/Screen13.asm) | `#6868` | `#6868` | `#6868` |
| 9, 14 | [Screen14.asm](../Source/Screens/Station/Screen14.asm) | `#7070` | `#7070` | `#7070` |
| 9, 15 | [Screen15.asm](../Source/Screens/Station/Screen15.asm) | `#7179` | `#7171` | `#7171` |
| 25, 0 | [Screen00.asm](../Source/Screens/Panel25/Screen00.asm) | `#0707` | `#0707` | `#0707` |
| 26, 0 | [Screen00.asm](../Source/Screens/Panel26/Screen00.asm) | `#0E0E` | `#0E0E` | `#0E0E` |
| 27, 0 | [Screen00.asm](../Source/Screens/Panel27/Screen00.asm) | `#B9B9` | `#B9B9` | `#B9B9` |
| 28, 0 | [Screen00.asm](../Source/Screens/Panel28/Screen00.asm) | `#FDFD` | `#FDFD` | `#FDFD` |

Общий поток вынесен в файл ScreenNN.Bitstream.bin, который содержит исходные байты от 12 до PackedSize-1. Прежний Payload.bin заменён после проверки отдельного кандидата, сохранения предыдущей версии и побайтовой сверки всего выделенного диапазона с образом. Секторные Tail.bin не менялись. Python для обычной сборки не требуется.

[CheckPackedResourcePrefix.py](../Tools/Disasm/Research/CheckPackedResourcePrefix.py) проверяет все 20 структур, 120 именованных байтов, положение меток и полные выделенные диапазоны вместе с хвостами. [Отчёт](../Tools/Disasm/Reports/PackedResourcePrefixVerification.json). Это типизация существующих ресурсных байтов, новых адресов памяти и новых байтов образа нет. В Inventory эти экземпляры остаются внутри соответствующих resource-диапазонов.
