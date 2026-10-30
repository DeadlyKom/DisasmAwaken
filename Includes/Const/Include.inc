                ifndef _AWAKEN_CONSTANTS_
                define _AWAKEN_CONSTANTS_

                module TrDos
Dispatch        equ #3D13                                                       ; интерфейс системных функций TR-DOS
ReadSectors     equ #05                                                         ; чтение физических секторов
ReadCatalog     equ #08                                                         ; получение записи каталога
FindFile        equ #0A                                                         ; поиск имени из системного буфера
LoadFile        equ #0E                                                         ; загрузка файла через интерфейс TR-DOS
                endmodule

                module Hardware
PagingPort      equ #7FFD                                                       ; порт выбора страницы памяти и экранного банка
PageUpperMask   equ #F8                                                         ; старшие пять битов теневого байта при объединении с входным A
BorderPort      equ #FE                                                         ; младший байт порта ULA
AySelect        equ #FFFD                                                       ; выбор регистра AY
AyWrite         equ #BFFD                                                       ; запись регистра AY
                endmodule

                module ScriptConst
ReaderCount     equ #24                                                         ; число физических записей чтения, включая повтор y
WriterCount     equ #07                                                         ; число записей выбора писателя присваивания
UnaryCount      equ #07                                                         ; число записей унарного изменения поля
OperatorCount   equ #0B                                                         ; число записей таблицы бинарных операторов
DecimalZero     equ #30                                                         ; код первой десятичной цифры ASCII
DecimalLimit    equ #3A                                                         ; код сразу после последней десятичной цифры
Cursor          equ #00                                                         ; символ в текущей позиции текстового курсора IX
NextChar        equ #01                                                         ; символ сразу после текущего CR при проверке открывающей скобки
SuffixBack      equ #01                                                         ; прочитанный суффикс перед уже продвинутым IX
UnitsBack       equ #01                                                         ; единицы перед курсором конца числа
TensBack        equ #02                                                         ; десятки перед курсором конца числа
HundredsBack    equ #03                                                         ; сотни перед курсором конца числа
ThousandsBack   equ #04                                                         ; тысячи перед курсором конца числа
TenThousands    equ #05                                                         ; десятки тысяч перед курсором конца числа
                endmodule

                module MapConst
SquareLowPage   equ #E9                                                         ; страница младших байтов квадратов 0..255
                endmodule

                module InterfaceFlags
CloseTopMask    equ #C0                                                         ; старшая пара разрядов, ноль разрешает CloseAllItems
ClosePairMask   equ #60                                                         ; совместно установленные биты 6 и 5 также разрешают CloseAllItems
FrameBitMask    equ #01                                                         ; бит 0 выбирает вид контура, ToggleItemFrame его инвертирует
ToggleLockBit   equ #04                                                         ; номер бита запрета перерисовки в ToggleItemFrame
FrameMask       equ #1F                                                         ; младшие биты типа рамки, общий рисователь проверяет из них только бит 0
GroupMask       equ #E0                                                         ; поле группы элемента в старших трёх разрядах
FrontGroup      equ #40                                                         ; группа, переносимая в начало списка рисования
FrameBit        equ #00                                                         ; номер бита выбора формы контура, соответствующая маска FrameBitMask
                endmodule

                module LoaderConst
StackTop        equ #5FFF                                                       ; исходная вершина стека первого загрузчика
SystemIY        equ #5C3A                                                       ; исходное значение IY перед обращением к TR-DOS
IntroSectors    equ #2C                                                         ; число физических секторов вступления
                endmodule

                module IntroConst
PhaseSignBit    equ #07                                                         ; бит знака старшего байта фазы, выбирающий направление изменения шага
                endmodule

                module ScreenConst
PixelOffsetMask equ #07                                                         ; младшие три бита пиксельной координаты внутри знакоместа
ColumnMask      equ #1F                                                         ; младшие пять битов колонки в экранном адресе
ColumnEndLimit  equ #21                                                         ; граница сравнения исключённой правой колонки, 32 включительно
RowEndLimit     equ #19                                                         ; граница сравнения исключённой нижней строки, 24 включительно
CharRows        equ #18                                                         ; число строк знакомест экрана Spectrum
ByteColumns     equ #20                                                         ; число байтов в строке пикселей
LastColumn      equ #1F                                                         ; индекс последней байтовой колонки
PixelsPerChar   equ #08                                                         ; число пиксельных строк знакоместа
                endmodule

                module SpanPattern
DeepLeft        equ #1F                                                         ; заполненный край без трёх внешних левых пикселей
DeepRight       equ #F8                                                         ; заполненный край без трёх внешних правых пикселей
InnerLeft       equ #20                                                         ; боковой пиксель внутреннего левого контура
InnerRight      equ #04                                                         ; боковой пиксель внутреннего правого контура
Empty           equ #00                                                         ; нулевой байт фона полосы
Solid           equ #FF                                                         ; полностью заполненный байт полосы
EmptyPair       equ #0000                                                       ; нулевые левый край и середина
SolidPair       equ #FFFF                                                       ; заполненные левый край и середина
OutlineLeft     equ #40                                                         ; одиночный пиксель левого края
OutlineRight    equ #02                                                         ; одиночный пиксель правого края
CutoutLeft      equ #5F                                                         ; левый заполненный край с двумя раздельными пропусками
CutoutRight     equ #FA                                                         ; правый заполненный край с двумя раздельными пропусками
SixBitEdge      equ #7E                                                         ; шесть средних пикселей крайнего байта
InsetLeft       equ #3F                                                         ; заполнение без двух внешних левых пикселей
InsetRight      equ #FC                                                         ; заполнение без двух внешних правых пикселей
                endmodule

                module SpanOpcode
LeftPair        equ #2C72                                                       ; байты LD (HL),D и INC L в младшем порядке
WriteRight      equ #71                                                         ; байт команды LD (HL),C
                endmodule

                module StationTables
RowHighPage     equ #82                                                         ; первая из трёх страниц табличного вычисления адреса рамки
CellMapPage     equ #86                                                         ; первая страница карты владельцев экранных знакомест
WorkspaceTail   equ #02FF                                                       ; число байтов после первого в карте из 768 знакомест
IndexInitTail   equ #007F                                                       ; число байтов после первого в исходной инициализации таблицы индексов
                endmodule

                module ItemIndexConst
FreeHigh        equ #FF                                                         ; старший байт свободной или снятой индексной пары
                endmodule

                module TextWindowConst
CenterYInset    equ #04                                                         ; вертикальный отступ окна центрируемого текста
OriginInset     equ #03                                                         ; добавка к младшим байтам начала внутреннего текстового окна
WidthInset      equ #04                                                         ; уменьшение пиксельной ширины внутреннего окна
HeightInset     equ #0B                                                         ; уменьшение пиксельной высоты внутреннего окна
                endmodule

                module FontConst
RouteHalfPage   equ #49                                                         ; старшая часть половинного адреса таблицы #9200 перед ADD HL,HL
GlyphTopLimit   equ #B9                                                         ; первая недопустимая верхняя строка восьмипиксельного глифа
WidthPage       equ #89                                                         ; страница 256 исходных байтов ширины символов
GlyphBase       equ #8A00                                                       ; начало исходных восьмибайтовых изображений символов
                endmodule

                module TextConst
Space           equ #20                                                         ; граница слова, выводимая вызывающим выравнивателем
FirstGlyph      equ #07                                                         ; первый код глифа, LF и CR обрабатываются отдельно
CarriageReturn  equ #0D                                                         ; безусловный ограничитель измеряемого текста
LineFeed        equ #0A                                                         ; второй безусловный ограничитель измеряемого текста
                endmodule

                module GlyphStatus
Vertical        equ #01                                                         ; ошибка физического Y либо нижней границы экрана
Height          equ #02                                                         ; относительный курсор достиг высоты текстового окна
Width           equ #03                                                         ; следующая позиция курсора достигла ширины окна или переполнила байт
                endmodule

                module GlyphOpcode
SkipJump        equ #C3                                                         ; JP общего успешного выхода вместо пиксельной части
ResumeFirst     equ #68                                                         ; исходный первый байт префикса, LD L,B
ResumePair      equ #2648                                                       ; исходные второй и третий байты, LD C,B и начало LD H,nn
                endmodule

                module NumberConst
DigitZero       equ #0030                                                       ; код десятичного нуля
Max1Digit       equ #0009                                                       ; последнее однозначное число
Max2Digits      equ #0063                                                       ; последнее двузначное число
Max3Digits      equ #03E7                                                       ; последнее трёхзначное число
Max4Digits      equ #270F                                                       ; последнее четырёхзначное число
Ten             equ #000A                                                       ; делитель разряда десятков
Hundred         equ #0064                                                       ; делитель разряда сотен
Thousand        equ #03E8                                                       ; делитель разряда тысяч
TenThousand     equ #2710                                                       ; делитель старшего разряда слова
TwentyThousand  equ #4E20                                                       ; первое пробное вычитание пятизначной ветви
                endmodule

                module JustifyConst
MinHeight       equ #000E                                                       ; минимальная высота окна выравнивателя
MinGap          equ #0002                                                       ; минимальный интервал слов в пикселях
                endmodule

                module TextFlowOpcode
Continue        equ #C3                                                         ; JP продолжения текстового потока после явного CR
Return          equ #C9                                                         ; RET после принятого явного CR для центрирования
                endmodule

                module InterfaceText
CaptionTextBase equ #E399                                                       ; исходная таблица заголовков полосовых элементов
CenterTextBase  equ #E4AA                                                       ; исходная таблица текстов центрируемых элементов
                endmodule

                module ItemRectLimit
EndColumn       equ #21                                                         ; первая недопустимая байтовая правая граница
EndRow          equ #19                                                         ; первая недопустимая байтовая нижняя граница
MinSize         equ #04                                                         ; минимальные ширина и высота проверяемого элемента
                endmodule

                module DrawOpcode
Disabled        equ #C9                                                         ; RET немедленно завершает обёртку рисования
Enabled         equ #21                                                         ; LD HL,nn разрешает загрузку индекса и переход в рисователь
                endmodule

                module DrawListLimit
ShiftBytes      equ #0080                                                       ; фиксированная длина исходного LDIR при переносе записи
EndByte         equ #01                                                         ; оба байта создаваемого ограничителя #0101
                endmodule

                module InterfaceTable
EndX            equ #80                                                         ; маркер конца таблицы в поле текущего X
                endmodule

                module PointerConst
PlainShapeMask  equ #C0                                                         ; ненулевая группа запрещает краевые формы и callback наведения
TopBlockMask    equ #04                                                         ; бит запрета верхней формы в этом потребителе Flags
BottomBlockMask equ #02                                                         ; бит запрета нижней формы в этом потребителе Flags
Low3Mask        equ #07                                                         ; младшие три разряда фазы X либо пиксельной строки внутри знакоместа
PairLimit       equ #F8                                                         ; порог X для однобайтового отсечения правой половины
FullTailRows    equ #07                                                         ; число строк ниже верхней для полного восьмистрочного указателя
LastScreenY     equ #BF                                                         ; последняя допустимая пиксельная строка основного экрана
CellHeight      equ #08                                                         ; высота знакоместа и полного указателя в пикселях
NormalShape     equ #6000                                                       ; обычная форма, восемь фаз сдвига по восемь строк
TopShape        equ #6100                                                       ; форма для верхней строки элемента при сброшенном бите 2
BottomShape     equ #6200                                                       ; форма для нижней строки элемента при сброшенном бите 1
BackgroundBase  equ #6575                                                       ; исходный физический буфер двух байтов каждой из восьми строк
                endmodule

                module BoundsToggleConst
WidthLimit      equ #10                                                         ; порог ширины, от которого возвращается сохранённый прямоугольник
HeightLimit     equ #08                                                         ; порог высоты при ширине меньше WidthLimit
ExpandedX       equ #06                                                         ; исходная символьная колонка большого прямоугольника
ExpandedY       equ #04                                                         ; исходная символьная строка большого прямоугольника
ExpandedWidth   equ #14                                                         ; исходная ширина большого прямоугольника в знакоместах
ExpandedHeight  equ #0A                                                         ; исходная высота большого прямоугольника в знакоместах
                endmodule

                module TrackConst
CenterXY        equ #6080                                                       ; исходный программный центр, X=128,Y=96 в пикселях
Class00Min      equ #0003                                                       ; минимум обеих осей при нулевых старших разрядах Flags
Class40Min      equ #0002                                                       ; минимум для класса #40
CellBitsMask    equ #00F8                                                       ; старшие пять битов пиксельной координаты, без позиции внутри знакоместа
                endmodule

                module ScreenUpdateConst
CopyPage        equ #0017                                                       ; окно банка 7, показ банка 5, ROM 1
HiddenPage      equ #0018                                                       ; окно банка 0, показ снимка банка 7, ROM 1
VisiblePage     equ #0010                                                       ; окно банка 0, показ обновлённого банка 5, ROM 1
BaseScreen      equ #4000                                                       ; исходный адрес базовых пикселей и атрибутов банка 5
BankWindow      equ #C000                                                       ; начало существующего переключаемого окна RAM
ScreenBytes     equ #1B00                                                       ; 6912 байтов пикселей и атрибутов одного экрана
                endmodule

                module RepaintConst
AndA            equ #A7                                                         ; код AND A для очистки Carry в общем выходе
SetCarry        equ #37                                                         ; код SCF для обязательного Carry после перерисовки
                endmodule

                module MouseConst
ButtonPort      equ #FADF                                                       ; полный порт трёх активных низких разрядов кнопок
XPort           equ #FBDF                                                       ; порт байтового аппаратного счётчика X
YPort           equ #FFDF                                                       ; порт байтового аппаратного счётчика Y
MaxX            equ #FE                                                         ; верхний предел положительного шага X, 254
MaxY            equ #BF                                                         ; верхний предел положительного шага Y, 191
                endmodule

                module StationIrqConst
StationPage     equ #10                                                         ; банк станции 0 с установкой ROM 1
MusicPage       equ #13                                                         ; банк музыки 3 с установкой ROM 1
MusicMode       equ #81                                                         ; полный код режима исполнения музыкального тика
ReloadFrames    equ #32                                                         ; исходная перезагрузка делителя на 50 вызовов
                endmodule

                module WindowFillConst
TailWordValue   equ #A0B6                                                       ; значение дополнительного слова цепочки, не отдельный вход кода
                endmodule

                module KeyboardConst
DelayTicks      equ #0A                                                         ; десять пробуждений HALT перед ожиданием нажатия
FirstPort       equ #7FFE                                                       ; первая проверяемая строка матрицы
MaskSeed        equ #80                                                         ; исходная маска, первый RLC даёт разряд 0
TableBias       equ #6954                                                       ; отрицательный адрес Code1D по модулю 65536
FirstCode       equ #1D                                                         ; возвращаемый код первой позиции таблицы
                endmodule

                module SettingsLabelConst
FirstRow        equ #7F                                                         ; порог отделения числовых байтов от маркеров и строк
DigitZero       equ #30                                                         ; прибавляемый код нуля для числового байта
NoTag           equ #80                                                         ; маркер преобразования в N
YesTag          equ #81                                                         ; маркер преобразования в Y
NoChar          equ #4E                                                         ; код символа N
YesChar         equ #59                                                         ; код символа Y
                endmodule

                module PopupConst
NoSelection     equ #FFF0                                                       ; исходное исключение при отсутствии выбранного элемента
GroupCode       equ #20                                                         ; код группы удаляемых временных элементов в маске E0
MaxX            equ #17                                                         ; последняя колонка начала исходного меню шириной 9
MaxY            equ #0F                                                         ; последняя строка начала исходного меню высотой 9
                endmodule

                module RowSelectConst
CellMask        equ #F8                                                         ; округление байтовой величины вниз к восьми пикселям
RowMask         equ #1F                                                         ; пять разрядов частного после деления разности на восемь
BottomInset     equ #05                                                         ; нижний вычет из доступной высоты до округления
                endmodule

                module SelectionBandConst
Low5Mask        equ #1F                                                         ; пять младших пикселей края, также максимум 31 полного байта
High5Mask       equ #F8                                                         ; пять старших пикселей правого края
                endmodule

                module InterfaceEventConst
HeldMask        equ #80                                                         ; бит 7 повторного кода перед DEC, при новом коде исходные биты сохраняются
                endmodule


                module AssignmentConst
BackFromHigh    equ #FFFB                                                       ; минус пять, от старшего Right к началу FAssignmentExpression
                endmodule

                module CounterDrawConst
HighNibble      equ #F0                                                         ; маска старшего разряда BCD-пары
LowNibble       equ #0F                                                         ; маска младшего разряда BCD-пары
Separator       equ #3A                                                         ; двоеточие между старшей группой, MidLow и Low
                endmodule

                module MapRootConst
SeedPage        equ #EB                                                         ; страница байтов дополнения начального приближения
OffsetLowPage   equ #EC                                                         ; младшие байты исходного начального смещения
OffsetHighPage  equ #ED                                                         ; старшие байты исходного начального смещения
                endmodule

                module MapDistanceConst
ScaleSquared    equ #0009                                                       ; делитель суммы квадратов до извлечения корня
OverflowCode    equ #FF                                                         ; результат при переполнении квадрата или суммы
                endmodule

                module RankConst
ThresholdCount  equ #06                                                         ; шесть убывающих порогов до низшего ранга
                endmodule

                module MissionOfferConst
RewardScale     equ #0014                                                       ; коэффициент 20 в произведении расстояния и тоннажа
                endmodule

                module SystemNameConst
MapPage         equ #11                                                         ; банк KARTA 1 с установкой ROM 1
LowNibble       equ #0F                                                         ; младший полубайт поля имени
HighNibble      equ #F0                                                         ; старший полубайт поля имени
Dash            equ #2D                                                         ; дефис между префиксом, числами и буквой
Slash           equ #2F                                                         ; косая черта между числовыми полями
FirstLetter     equ #80                                                         ; код первой из шестнадцати завершающих букв
                endmodule

                module CompactDecimalConst
BeforeFirst     equ #FF                                                         ; значение счётчика перед первым INC B
Hundred         equ #64                                                         ; величина сотни в последовательных вычитаниях
Ten             equ #0A                                                         ; величина десятка в последовательных вычитаниях
                endmodule

                module MissionHoverConst
NoRow           equ #FF                                                         ; отсутствует прежняя XOR-строка после перерисовки
LimitAndOffset  equ #0203                                                       ; D две строки для ClampRowHeight, E отступ 3 пикселя
                endmodule


                module MapSectorConst
InitialMix      equ #8237                                                       ; начальное третье рабочее слово генератора секторной таблицы
HighXor         equ #0A                                                         ; маска старшего байта суммы U+V
                endmodule


                module MapMarkerConst
RowHighPage     equ #EE                                                         ; страница старших байтов адреса строки карты
RightInset      equ #08                                                         ; исключённый правый запас в проверке DX
BottomInset     equ #07                                                         ; исключённый нижний запас в проверке DY
                endmodule


                module MapClipConst
InsideCode      equ #F0                                                         ; полный дополненный код внутренней точки
SideMask        equ #0F                                                         ; четыре младших признака внешних сторон
DispatchLowPage equ #DE                                                         ; страница младших байтов таблицы обработчиков
OutputPage      equ #F9                                                         ; страница байтовых выходных точек пересечений
VisibleYEnd     equ #C0                                                         ; исключённая граница проверки младшего выходного Y
MinCoordinate   equ #0000                                                       ; нормированная верхняя и левая координата границы
CountMask       equ #0F                                                         ; младшая тетрада исходного количества точек
ExcludedEnd     equ #FF                                                         ; исключённая правая и нижняя граница координаты
Complement      equ #F0                                                         ; дополнение четырёх признаков в старшей тетраде
                endmodule


                module MapClipBit
Right           equ #00                                                         ; X не меньше 255
Left            equ #01                                                         ; отрицательный X
Bottom          equ #02                                                         ; Y не меньше 255
Top             equ #03                                                         ; отрицательный Y
                endmodule

                module MapClipCornerBit
BottomRight     equ #00                                                         ; уже отмечен нормированный нижний правый угол
BottomLeft      equ #01                                                         ; уже отмечен нормированный нижний левый угол
TopRight        equ #02                                                         ; уже отмечен нормированный верхний правый угол
TopLeft         equ #03                                                         ; уже отмечен нормированный верхний левый угол
                endmodule

                module MapLineConst
MaskPage        equ #D4                                                         ; страница исходных восьмифазных масок
SetMaskLow      equ #20                                                         ; младший адрес одноразрядных масок D420
ClearMaskLow    equ #28                                                         ; младший адрес инверсных масок D428
AndPixel        equ #A1                                                         ; код AND C для очистки пикселя инверсной маской
OrPixel         equ #B1                                                         ; код OR C для установки пикселя одноразрядной маской
XorPixel        equ #A9                                                         ; код XOR C для инверсии пикселя одноразрядной маской
CrossClear      equ #30                                                         ; код JR NC при вращении инверсной маски
CrossSet        equ #38                                                         ; код JR C при вращении одноразрядной маски
ClearMode       equ #30A1                                                       ; PixelOpcode=AND C, ByteCrossOpcode=JR NC
SetMode         equ #38B1                                                       ; PixelOpcode=OR C, ByteCrossOpcode=JR C
XorMode         equ #38A9                                                       ; PixelOpcode=XOR C, ByteCrossOpcode=JR C
                endmodule

                module MapChainConst
PointPage       equ #F8                                                         ; старший байт существующего рабочего массива FProjectedPoint
StyleMask       equ #30                                                         ; двухбитовый код режима в Layout, это поле, а не независимые флаги
SetStyle        equ #10                                                         ; код 01 в поле режима выбирает OR C
                endmodule

                module MapMathConst
InitialMinimum  equ #FFFF                                                       ; исходный минимум, превышающий любой квадрат байтового расстояния
ByteBits        equ #08                                                         ; число разрядов каждого множителя байтового квадрата
                endmodule

                module MapVariantConst
OriginBias      equ #0404                                                       ; исходное смещение упакованного Origin перед словным масштабированием
TargetBias      equ #0603                                                       ; исходное смещение после умножения полного слова на восемь
TileBias        equ #04                                                         ; прибавление к каждому байту начала до общего масштаба восемь
EndPath         equ #80                                                         ; отдельный однобайтовый ограничитель циклического потока смещений
PhaseMask       equ #07                                                         ; маска восьми горизонтальных фаз трёхстрочного спрайта
CountMask       equ #07                                                         ; младшие три бита XOR четырёх байтов ключа до декремента количества
                endmodule

                module MapArcConst
MinRadius       equ #09                                                         ; минимальный Radius, передаваемый диспетчером растровым проходам
TestSetBit      equ #38                                                         ; код JR C в четырёх поисках установленного граничного бита
TestClearBit    equ #30                                                         ; код JR NC в четырёх поисках сброшенного граничного бита
InitialBias     equ #00                                                         ; исходный байт SUB, установщик заменяет его на HalfX-2 modulo 256
                endmodule

                module MapArcBit
NonnegativeX    equ #00                                                         ; бит неотрицательного WorldX-OriginX-HalfX
NonnegativeY    equ #01                                                         ; бит неотрицательного OriginY-WorldY+HalfY
                endmodule

                module StationScreenPage
RowHigh         equ #82                                                         ; старший адресный байт станционной таблицы RowHigh по 8200
                endmodule

                module MapPanelConst
ClipWidthTrim   equ #0D                                                         ; пиксели, вычитаемые из ширины текста для включённого MaxX карты
ClipHeightTrim  equ #0E                                                         ; пиксели, вычитаемые из высоты текста для включённого MaxY карты
                endmodule

                module MapPanConst
Step            equ #08                                                         ; положительный шаг начала карты в мировых единицах
NegativeStep    equ #F8                                                         ; отрицательный шаг -8 в байтовом дополнительном коде
                endmodule

                module StoredPointConst
PreviousRecord  equ #FFFB                                                       ; отрицательный размер пятибайтовой записи
Empty           equ #FF                                                         ; первый байт физически пустой записи
EndMarker       equ #80                                                         ; точный исходный ограничитель прохода очистки B
                endmodule

                endif
