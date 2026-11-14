                module ArchiveEngineConst
FirstSprite     equ #00                                                         ; начальный индекс файла и страницы масок бойцов
SpriteBankCount equ #04                                                         ; число файлов BD0..BD3 в первой таблице ключей
SpriteData      equ #C000                                                       ; начало файла масок в окне выбранной страницы
BarPage         equ #00                                                         ; общая страница двух экземпляров BAR
FirstBar        equ #C000                                                       ; начало первой копии таблицы шагов
SecondBar       equ #D000                                                       ; начало второй копии таблицы шагов
MirrorTable     equ #7600                                                       ; 256 значений с обращённым порядком битов
LoadByName      equ #FF                                                         ; режим поиска ключа перед чтением через TR-DOS
ScenePixels     equ #7700                                                       ; рабочий растр сцены, начало файла scene1po
ScreenPage      equ #07                                                         ; страница теневого экрана
ScreenBitmap    equ #C000                                                       ; растр в банковом окне теневого экрана
BitmapSize      equ #1800                                                       ; размер растра ZX Spectrum без атрибутов
AttributeTail   equ #02FF                                                       ; число атрибутов после первого байта заполнителя
EmptyAttribute  equ #07                                                         ; белые чернила на чёрном фоне без яркости и мигания
SceneStackTop   equ #6000                                                       ; верхняя граница обычного стека сцены
VectorPage      equ #5E                                                         ; старший байт таблицы векторов IM2
VectorAddress   equ #5E00                                                       ; начало таблицы из 257 байтов
VectorTail      equ #0100                                                       ; число байтов для размножения первого значения
VectorValue     equ #5F                                                         ; одинаковые старший и младший байты адреса переходника
JumpOpcode      equ #C3                                                         ; код JP nn, записываемый перед адресом IRQ
StartSeconds    equ #99                                                         ; начальное число секунд в упакованном BCD
TicksPerSecond  equ #32                                                         ; число прерываний на одну секунду таймера
SecondsOnes     equ #0F                                                         ; маска младшей цифры BCD
SecondsTens     equ #F0                                                         ; маска старшей цифры BCD
SecondsBorrow   equ #10                                                         ; вычитаемая десятка при заёме из старшей цифры
LastDigit       equ #09                                                         ; младшая цифра после заёма
LowPageMask     equ #07                                                         ; три младших разряда кода страницы
ExtendedPage    equ #08                                                         ; четвёртый разряд кода страницы
ScreenRomBits   equ #18                                                         ; выбор теневого экрана и ROM 48K в значении #7FFD
ScorpionPort    equ #1FFD                                                       ; порт дополнительного разряда страницы Scorpion
AtmWindowPort   equ #FFF7                                                       ; порт управления отображением верхнего окна ATM-2
AtmPortBit6     equ #06                                                         ; шестой разряд значения ATM-2 всегда установлен
AtmPortBit7     equ #07                                                         ; седьмой разряд значения ATM-2 всегда установлен
RomOutput       equ #2A53                                                       ; OUT (C), A и RET в ROM TR-DOS
MeterFull       equ #78                                                         ; 15 знакомест по 8 столбцов для заполнения
MeterWidth      equ #0F                                                         ; ширина полосы в байтах
MeterTail       equ #0E                                                         ; ширина без первого атрибута
MeterRows       equ #0A                                                         ; верхняя рамка, восемь строк и нижняя рамка
MeterHeight     equ #08                                                         ; число вертикальных пикселей столбца
MeterAttribute  equ #14                                                         ; исходный атрибут полосы
MeterAttrLeft   equ #D840                                                       ; первый атрибут левой полосы
MeterAttrRight  equ #D851                                                       ; первый атрибут правой полосы
MeterLeftTop    equ #C720                                                       ; верхняя строка левой полосы
MeterRightTop   equ #C731                                                       ; верхняя строка правой полосы
CharRowBytes    equ #20                                                         ; шаг знакоместного ряда экрана
SceneHeadPage   equ #0D                                                         ; первая страница резервной копии фона
SceneTailPage   equ #0E                                                         ; вторая страница резервной копии фона
SceneSplitRow   equ #B2                                                         ; первая строка второй страницы
SceneHeadBytes  equ #3FF8                                                       ; 178 строк по 92 байта
SceneTailBytes  equ #0958                                                       ; 26 строк, включая 92 байта после конца файла
WindowNegWidth  equ #FFE0                                                       ; вычитание 32 байтов окна из шага или ширины
ScenePageDelta  equ #49                                                         ; разность старших байтов #C000 и #7700
ScreenBottom    equ #D7E0                                                       ; адрес строки 191 теневого экрана
ScreenGroups    equ #14                                                         ; число полных групп по 8 строк ниже индикаторов
BelowMeters     equ #07                                                         ; оставшиеся полные строки до области индикаторов
AboveMeters     equ #C620                                                       ; адрес строки 14 над индикаторами
ScreenTopGroup  equ #C700                                                       ; адрес строки 7 теневого экрана
MeterGapColumn  equ #0F                                                         ; первый из двух видимых столбцов между полосами
MeterGapBottom  equ #C06F                                                       ; два байта строки 24 между полосами
MeterGapMiddle  equ #C74F                                                       ; два байта строки 23 между полосами
MeterGapTop     equ #C72F                                                       ; два байта строки 15 между полосами
TimerDigitRows  equ #10                                                         ; высота цифры, на строку приходится пара маска и рисунок
TimerFirstRow   equ #BD                                                         ; смещение исходной строки первой строки таймера от начала окна
InitialKeyPort  equ #7FFE                                                       ; порт первого чтения перед опросом бойцов
PrimaryKeyCount equ #05                                                         ; число битов основной группы клавиш
ExtraKeyCount   equ #04                                                         ; число битов дополнительной группы клавиш
ActionRepeatBit equ #06                                                         ; номер бита повтора группы
FacingMask      equ #01                                                         ; маска младшего бита стороны
                endmodule

