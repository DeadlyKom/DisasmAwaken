# Внутренние входы арифметики VOXAL и финала

Имена относятся к исходным операциям и сохраняют фактические адреса.
Изменений инструкций и новых областей памяти нет.

| Процедура | Адрес | Имя | Назначение входа |
| --- | --- | --- | --- |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F939 | NextBit5 | сдвиг накопителя перед разрядом 5 |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F93E | NextBit4 | сдвиг накопителя перед разрядом 4 |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F943 | NextBit3 | сдвиг накопителя перед разрядом 3 |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F948 | NextBit2 | сдвиг накопителя перед разрядом 2 |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F94D | NextBit1 | сдвиг накопителя перед разрядом 1 |
| [Multiply7BitWord](../Source/Voxel/Multiply7BitWord.asm) | #F952 | NextBit0 | сдвиг накопителя перед разрядом 0 |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8AF | CheckBCSign | проверка знака второго множителя |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8BA | SplitMagnitude | разделение разрядов модуля второго множителя |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8CF | UpperShift1 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8D7 | UpperShift2 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8DF | UpperShift3 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8E7 | UpperShift4 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8EF | UpperShift5 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8F7 | UpperShift6 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E8FF | UpperShift7 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E907 | UpperShift8 | сдвиг первой стадии после условного сложения |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E91B | LowerShift1 | сдвиг второй стадии с входным накопителем IY |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E926 | LowerShift2 | сдвиг второй стадии с входным накопителем IY |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E931 | LowerShift3 | сдвиг второй стадии с входным накопителем IY |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E93C | LowerShift4 | сдвиг второй стадии с входным накопителем IY |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E947 | LowerShift5 | сдвиг второй стадии с входным накопителем IY |
| [SignedSeededProduct](../Source/Voxel/SignedSeededProduct.asm) | #E952 | LowerShift6 | сдвиг второй стадии с входным накопителем IY |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F978 | IntegerBit6 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F97D | StoreInt6 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F97F | IntegerBit5 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F984 | StoreInt5 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F986 | IntegerBit4 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F98B | StoreInt4 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F98D | IntegerBit3 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F992 | StoreInt3 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F994 | IntegerBit2 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F999 | StoreInt2 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F99B | IntegerBit1 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9A0 | StoreInt1 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9A2 | IntegerBit0 | пробное вычитание для целого разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9A7 | StoreInt0 | запись инвертированного разряда целого частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9AF | StoreFrac7 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9B6 | StoreFrac6 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9BD | StoreFrac5 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9C4 | StoreFrac4 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9CB | StoreFrac3 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9D2 | StoreFrac2 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9D9 | StoreFrac1 | запись инвертированного дробного разряда частного |
| [Divide7BitFixed](../Source/Voxel/Divide7BitFixed.asm) | #F9E0 | StoreFrac0 | запись инвертированного дробного разряда частного |
| [InitializeFinal](../Source/Final/InitializeFinal.asm) | #607A | BeginFramePair | ожидание IRQ перед парой экранов |
| [InitializeFinal](../Source/Final/InitializeFinal.asm) | #60D5 | DelaySecond | задержка перед выводом второго экрана |
| [ReadSpeedKeys](../Source/Final/ReadSpeedKeys.asm) | #6134 | DecreaseDelay | уменьшение задержки по Q |
| [ReadSpeedKeys](../Source/Final/ReadSpeedKeys.asm) | #613D | IncreaseDelay | увеличение задержки по A |
| [ReadSpeedKeys](../Source/Final/ReadSpeedKeys.asm) | #6144 | StoreDelay | запись нового значения в операнд цикла |
| [BuildDisplayChain](../Source/Final/BuildDisplayChain.asm) | #61E2 | CharacterRow | начало знакоместного ряда |
| [BuildDisplayChain](../Source/Final/BuildDisplayChain.asm) | #61E5 | BitmapLine | генерация очередной пиксельной строки |
| [BuildDisplayChain](../Source/Final/BuildDisplayChain.asm) | #61FE | CheckFirstSync | проверка места синхронизации после десятого ряда |
| [BuildDisplayChain](../Source/Final/BuildDisplayChain.asm) | #620B | CountRows | счётчик оставшихся знакоместных рядов |
| [InitializeRandomStates](../Source/ActionBoot/InitializeRandomStates.asm) | #4316 | WarmRandom | начальное число шагов генератора от одного до четырёх |

Положение меток сверяет [CheckSourceLabels](../Tools/Disasm/Research/CheckSourceLabels.py).
Инструкции сверяет [VerifySources](../Tools/Disasm/VerifySources.py), без запуска сборки.
