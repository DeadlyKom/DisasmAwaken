                module ArchiveStartConst
StackTop        equ #6000                                                       ; обычный стек меню выбора BANK
MemoryMode      equ #5F5E                                                       ; режим памяти, переданный меню RUN
Window          equ #C000                                                       ; банковое окно для экрана и файлов BANK
LoadByName      equ #FF                                                         ; выбор поиска ключа перед чтением файла
EngineAddress   equ #4000                                                       ; действительный адрес загрузки ENGINE
PrimaryPage     equ #00                                                         ; логический код страницы перед загрузкой ENGINE
FirstScreenPage equ #05                                                         ; начало пары экранных страниц 5 и 7
BaseRomBit      equ #10                                                         ; выбор основной ROM в порту #7FFD
BankCount       equ #06                                                         ; число загружаемых файлов BANK
StripBufferSize equ #0258                                                       ; фиксированный перенос 600 байтов
LayerAttrRight  equ #D87A                                                       ; адрес за правым краем первого ряда атрибутов
LayerAttrRows   equ #15                                                         ; 21 ряд прямоугольника атрибутов
ScreenRowBytes  equ #0020                                                       ; число байтов в ряду атрибутов
RightEdge       equ #1F                                                         ; прибавка к младшему байту адреса правой полосы
CommonTileCount equ #14                                                         ; двадцать общих плиток варианта
CommonTileBytes equ #00A0                                                       ; байты двадцати общих плиток по восемь строк
RightTileSkip   equ #0010                                                       ; пропуск двух восьмибайтовых плиток левого набора
RightCoordSkip  equ #0004                                                       ; пропуск двух пар координат левого набора
MaskVariantSize equ #0060                                                       ; смещение второй группы растров масок
TileHeight      equ #08                                                         ; строк в плитке
LayerCellStride equ #0153                                                       ; байтов команд на восемь строк знакоместа
LayerLineStride equ #002A                                                       ; байтов команд между соседними строками
OpComplement    equ #2F                                                         ; код CPL, инверсия маски перед AND
OpAndAtHL       equ #A6                                                         ; код AND (HL), стирание битов под маской
OpOrAtHL        equ #B6                                                         ; код OR (HL), наложение плитки
FirstAttributes equ #D800                                                       ; первый атрибут экрана в банковом окне
NextAttribute   equ #D801                                                       ; второй атрибут для перекрывающегося переноса
AttributeTail   equ #02FF                                                       ; число атрибутов после первого
BlankAttribute  equ #07                                                         ; белые чернила на чёрном фоне
VectorBase      equ #5E00                                                       ; начало таблицы IM2
VectorTail      equ #0100                                                       ; число байтов после первого элемента
VectorFill      equ #5F                                                         ; одинаковые байты адреса переходника
VectorJump      equ #5F5F                                                       ; код JP к обработчику меню BANK
VectorOperand   equ #5F60                                                       ; изменяемое слово адреса IRQ
VectorPage      equ #5E                                                         ; старший байт таблицы IM2
                endmodule

