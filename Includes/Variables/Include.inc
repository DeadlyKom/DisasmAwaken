                ifndef _AWAKEN_VARIABLES_
                define _AWAKEN_VARIABLES_

; -----------------------------------------
; исходные адреса из машинного кода станции, новые области памяти не выделяются
; -----------------------------------------
                module StationState
CurrentPage     equ #6306                                                       ; теневая копия полного байта #7FFD
PointerXY       equ #6307                                                       ; байты пиксельных координат указателя, сначала X, затем Y
ItemIndex       equ #8500                                                       ; таблица индексов элементов интерфейса
DirtyCells      equ #8600                                                       ; карта 768 знакомест для восстановления фона
Items           equ #F0FD                                                       ; исходные записи FInterfaceItem
DrawList        equ #F3DE                                                       ; список обработчиков с ограничителем #0101
CellSpanSkip    equ #BF08                                                       ; смещение JR развёрнутой записи прямоугольника владельца
                endmodule

; -----------------------------------------
; изменяемые операнды проигрывателя в его исходном банке, память не выделяется
; -----------------------------------------
                module MusicState
SlideCounterC   equ #E29D                                                       ; число тиков до добавления шага к тону C
SlideReloadC    equ #E2CC                                                       ; перезагрузка счётчика после добавления шага
SlideStepC      equ #E2A6                                                       ; слово шага, прибавляемое к накопленному смещению
SlideBranchC    equ #E2AD                                                       ; байт смещения JR после обновления тона C
GateCounterC    equ #E2D5                                                       ; счётчик чередования включённого и выключенного C
                endmodule

                module ScriptTables
ReadAnchor      equ #C980                                                       ; адрес за одной FScriptToken до 36 читателей
WriteAnchor     equ #CA3A                                                       ; адрес за одной FScriptToken до семи писателей
UnaryAnchor     equ #CA4F                                                       ; адрес за одной FScriptToken до семи унарных обработчиков
OperatorAnchor  equ #C95F                                                       ; адрес за одной FScriptToken до бинарных операторов
                endmodule

                module ScriptSelection
EquipmentRow    equ #7217                                                       ; байт выбранной строки списка оснащения
EquipmentBase   equ #71B9                                                       ; слово прокрутки оснащения, сценарий читает только младший байт
CargoRow        equ #7068                                                       ; байт выбранной строки списка товаров
CargoBase       equ #7026                                                       ; слово индекса прокрутки, сценарий читает только младший байт
                endmodule

                module MapState
LeftMask        equ #DFB8                                                       ; временно сохранённая маска левого края в PrepareRightRasterPoint
LastDistance    equ #9908                                                       ; байт результата MeasureCoordinateDistance, включая FF переполнения
RasterStack     equ #DFB4                                                       ; указатель на существующий стековый FArcReturnFrame внешнего вызова
SqrtTarget      equ #DFB6                                                       ; временная разность квадратов для двоичного поиска корня
RasterDown      equ #DFB9                                                       ; ноль выбирает движение вверх, ненулевой байт движение вниз
UpperRow        equ #DFBA                                                       ; включённая верхняя граница растрового прохода
LowerRow        equ #DFBC                                                       ; исключённая нижняя граница растрового прохода
                endmodule

                module LoaderState
NextIntroBlock  equ #5CF4                                                       ; слово дорожки и сектора, читаемое первым загрузчиком
                endmodule

                module IntroState
LookupHL        equ #6BA2                                                       ; младший байт указателя HL табличного преобразования
LookupBCAlt     equ #6BA6                                                       ; младший байт указателя BC альтернативного набора
LookupHLAlt     equ #6BA9                                                       ; младший байт указателя HL альтернативного набора
LookupDEAlt     equ #6BAC                                                       ; младший байт указателя DE альтернативного набора
SampleCursor    equ #6C12                                                       ; слово текущего указателя выборки, младший байт изменяется с шагом три
                endmodule

                module IntroTables
PhaseSamples    equ #6400                                                       ; страница байтов четвёртого параметра текстурной выборки
                endmodule

                module StationRaster
BandDefault     equ #C095                                                       ; слово исходного установщика верхней полосы в LD HL
BandLine11      equ #C0F2                                                       ; слово CALL узора строки 11
BandLine12      equ #C0F8                                                       ; слово CALL разделителя строки 12
BandSides       equ #C0FF                                                       ; слово CALL боковых строк и середины
BandBottom0     equ #C13E                                                       ; слово CALL первой строки нижнего знакоместа
BandBottom1     equ #C144                                                       ; слово CALL следующих четырёх нижних строк
FillMode        equ #99B4                                                       ; бит 0 выбирает нулевое заполнение, остальные биты здесь не используются
RectangleByte   equ #C656                                                       ; байт заполнения в операнде LD A развёрнутого прямоугольника
RectangleSkip   equ #C658                                                       ; смещение JR для пропуска лишних пар записи прямоугольника
BandPattern     equ #C0CA                                                       ; слово адреса установщика узора верхней полосы рамки
LeftCode        equ #C17C                                                       ; пара записи левого края и шага L, либо два NOP
SpanSkip        equ #C17F                                                       ; смещение JR, пропускающее ненужные средние байты полосы
RightCode       equ #C1BC                                                       ; запись правого края, либо NOP
                endmodule

                module TextWindow
CursorX         equ #6320                                                       ; горизонтальная позиция текста относительно окна в пикселях
CursorY         equ #6321                                                       ; вертикальная позиция текста относительно окна в пикселях
OriginXLow      equ #AEBB                                                       ; младший байт горизонтального начала в операнде LD A
OriginXHigh     equ #AEBF                                                       ; байт знакового расширения горизонтального начала
OriginYLow      equ #AEC7                                                       ; младший байт вертикального начала в операнде LD A
OriginYHigh     equ #AECB                                                       ; байт знакового расширения вертикального начала
Width           equ #AEB3                                                       ; ширина текстового окна в операнде сравнения
Height          equ #AEAB                                                       ; высота текстового окна в операнде сравнения
Style           equ #BD26                                                       ; целый байт политики отказа, ноль пропускает строку, ненулевой разрешает перенос
SavedXLow       equ #A437                                                       ; операнд восстановления младшего байта начала X
SavedYLow       equ #A43C                                                       ; операнд восстановления младшего байта начала Y
SavedXHigh      equ #A441                                                       ; операнд восстановления знакового расширения X
SavedYHigh      equ #A446                                                       ; операнд восстановления знакового расширения Y
SavedWidth      equ #A44B                                                       ; операнд восстановления ширины
SavedHeight     equ #A450                                                       ; операнд восстановления высоты
SavedStyle      equ #A455                                                       ; операнд восстановления режима
SavedCursorX    equ #A45A                                                       ; операнд восстановления позиции текста по X
SavedCursorY    equ #A45F                                                       ; операнд восстановления позиции текста по Y
                endmodule

                module GlyphState
DispatchTarget  equ #AF0A                                                       ; слово цели изменяемого JP первого и второго участка глифа
KernelPrefix    equ #AED5                                                       ; три изменяемых байта начала пиксельной части, либо JP успешного выхода
                endmodule

                module TextStreamState
LineEndCode     equ #BD4F                                                       ; код JP продолжения после CR, временно RET для центрирования
Column2X        equ #BD73                                                       ; изменяемый операнд X управляющего кода 2
Column3X        equ #BD7E                                                       ; изменяемый операнд X управляющего кода 3
Column4X        equ #BD89                                                       ; изменяемый операнд X управляющего кода 4
Column5X        equ #BD94                                                       ; изменяемый операнд X управляющего кода 5
Column6X        equ #BD9F                                                       ; изменяемый операнд X управляющего кода 6
                endmodule

                module JustifyState
SkipWidth       equ #AD4E                                                       ; операнд ширины сухого прохода
PrintWidth      equ #ADDA                                                       ; операнд ширины печатающего прохода
                endmodule

                module TextSelectState
Separator       equ #A397                                                       ; изменяемый ограничитель CPIR, обычно LF, временно CR
                endmodule

                module DrawItemState
Index00         equ #7F36                                                       ; изменяемый индекс элемента статуса
Opcode00        equ #7F35                                                       ; первый байт рисователя статуса, LD HL либо временный RET
Index32         equ #AA86                                                       ; изменяемый индекс условий миссии
Opcode32        equ #AA85                                                       ; первый байт рисователя условий миссии, LD HL либо временный RET
Opcode31        equ #6FC5                                                       ; первый байт рамки цели миссии, LD HL либо временный RET
Index31         equ #6FC6                                                       ; изменяемый индекс элемента цели миссии
Opcode01        equ #A6EE                                                       ; первый байт рисователя счётчика, LD HL либо временный RET
Index01         equ #A6EF                                                       ; изменяемый индекс записи счётчика, исходный загрузчик записывает 1
Opcode30        equ #7A15                                                       ; первый байт DrawItem30, LD HL либо временный RET
Opcode28        equ #7A55                                                       ; первый байт DrawItem28, LD HL либо временный RET
Opcode29        equ #7A82                                                       ; первый байт DrawItem29, LD HL либо временный RET
Opcode09        equ #7A9E                                                       ; первый байт DrawItem09, LD HL либо временный RET
Opcode02        equ #7AB4                                                       ; первый байт DrawItem02, LD HL либо временный RET
Opcode03        equ #7B0B                                                       ; первый байт DrawItem03, LD HL либо временный RET
Opcode37        equ #7B25                                                       ; первый байт DrawItem37, LD HL либо временный RET
Opcode36        equ #7B40                                                       ; первый байт DrawItem36, LD HL либо временный RET
Opcode21        equ #7B51                                                       ; первый байт DrawItem21, LD HL либо временный RET
Opcode14        equ #7C7E                                                       ; первый байт DrawItem14, LD HL либо временный RET
Opcode15        equ #7CB6                                                       ; первый байт DrawItem15, LD HL либо временный RET
Opcode18        equ #7CF8                                                       ; первый байт DrawItem18, LD HL либо временный RET
Opcode17        equ #7D24                                                       ; первый байт DrawItem17, LD HL либо временный RET
Opcode16        equ #7D53                                                       ; первый байт DrawItem16, LD HL либо временный RET
Opcode35        equ #7D77                                                       ; первый байт DrawItem35, LD HL либо временный RET
Opcode04        equ #7D99                                                       ; первый байт DrawItem04, LD HL либо временный RET
Opcode05        equ #7DB5                                                       ; первый байт DrawItem05, LD HL либо временный RET
Opcode06        equ #7DE1                                                       ; первый байт DrawItem06, LD HL либо временный RET
Opcode07        equ #7E19                                                       ; первый байт DrawItem07, LD HL либо временный RET
Opcode08        equ #7F11                                                       ; первый байт DrawItem08, LD HL либо временный RET
Opcode33        equ #AA4F                                                       ; первый байт DrawItem33, LD HL либо временный RET
Index30         equ #7A16                                                       ; изменяемое слово индекса обёртки DrawItem30
Index28         equ #7A56                                                       ; изменяемое слово индекса DrawSaleModeButton
Index29         equ #7A83                                                       ; изменяемое слово индекса DrawPurchaseModeButton
Index09         equ #7A9F                                                       ; изменяемое слово индекса обёртки DrawItem09
Index02         equ #7AB5                                                       ; изменяемое слово индекса обёртки DrawItem02
Index03         equ #7B0C                                                       ; изменяемое слово индекса обёртки DrawItem03
Index37         equ #7B26                                                       ; изменяемое слово индекса DrawEquipmentPurchase
Index36         equ #7B41                                                       ; изменяемое слово индекса DrawEquipmentSale
Index21         equ #7B52                                                       ; изменяемое слово индекса обёртки DrawItem21
Index12         equ #7BA9                                                       ; изменяемое слово индекса обёртки DrawItem12
Index13         equ #7C1F                                                       ; изменяемое слово индекса обёртки DrawItem13
Index14         equ #7C7F                                                       ; изменяемое слово индекса обёртки DrawItem14
Index15         equ #7CB7                                                       ; изменяемое слово индекса обёртки DrawItem15
Index18         equ #7CF9                                                       ; изменяемое слово индекса обёртки DrawItem18
Index17         equ #7D25                                                       ; изменяемое слово индекса обёртки DrawItem17
Index16         equ #7D54                                                       ; изменяемое слово индекса обёртки DrawItem16
Index35         equ #7D78                                                       ; изменяемое слово индекса обёртки DrawItem35
Index04         equ #7D9A                                                       ; изменяемое слово индекса обёртки DrawItem04
Index05         equ #7DB6                                                       ; изменяемое слово индекса обёртки DrawItem05
Index06         equ #7DE2                                                       ; изменяемое слово индекса обёртки DrawItem06
Index07         equ #7E1A                                                       ; изменяемое слово индекса обёртки DrawItem07
Index08         equ #7F12                                                       ; изменяемое слово индекса обёртки DrawItem08
Index33         equ #AA50                                                       ; изменяемое слово индекса обёртки DrawItem33
                endmodule

                module DrawListState
HeadOperand     equ #9CA6                                                       ; изменяемая база списка в слове LD HL функции RebuildInterface
                endmodule

                module InterfaceState
EventCode       equ #9839                                                       ; код DispatchInterfaceEvent после DEC A, Rotate в ActivateItem возвращает бит 7 в Carry
HoverItem       equ #9A8D                                                       ; операнд LD IX основного цикла, физическая запись наведённого элемента
HoverCallback   equ #9A90                                                       ; слово CALL основного цикла, EventHandler наведённого элемента
EventEnabled    equ #9A82                                                       ; операнд MainLoop, ноль запрашивает перестроение и запрещает события
                endmodule

                module PointerState
UpdateBlocked   equ #9B16                                                       ; операнд периодического кода, ненулевой байт запрещает вызов UpdatePointer
SpriteBase      equ #64B3                                                       ; слово LD DE в DrawPointer, выбранная страница AND/XOR-масок
VisibleRows     equ #6501                                                       ; операнд LD B в DrawPointer, число строк также читает RestorePointer
RestoredFlag    equ #6548                                                       ; операнд LD A в RestorePointer, ноль означает активный рисунок
BackgroundAddr  equ #6550                                                       ; слово LD DE в RestorePointer, начало сохранённого участка экрана
                endmodule

                module ActiveItemState
Active          equ #9E78                                                       ; операнд LD A закрытия, ноль означает отсутствие активного элемента
Index           equ #9E7E                                                       ; операнд LD DE закрытия, индекс активного элемента
Callback        equ #9E8B                                                       ; операнд CALL закрытия, сбрасывается в EmptyCallback после вызова
NextCallback    equ #CCA4                                                       ; операнд LD HL активации, ранее сохранённый входной callback
                endmodule

                module XorOutlineState
HorizontalSkip  equ #C570                                                       ; смещение JR, выбирающего число байтов горизонтальной XOR-грани
VerticalMask    equ #C5F5                                                       ; операнд LD B вертикальной грани, штатно #80 либо #01
                endmodule

                module TrackState
HoldMove        equ #C9BF                                                       ; операнд CP удержания перемещения, задаётся по входному Z
HoldResize      equ #CADF                                                       ; операнд CP удержания изменения размера
RestoreOrigin   equ #C9B1                                                       ; операнд LD BC с геометрией удаляемого XOR-контура
RestoreSize     equ #C9B4                                                       ; операнд LD DE с размерами удаляемого XOR-контура
FlagsCache      equ #CA20                                                       ; операнд LD A, кэш Flags от DispatchInterfaceEvent
MinWidthTest    equ #CA77                                                       ; операнд CP минимальной ширины
MinWidthValue   equ #CA7C                                                       ; операнд LD L минимальной ширины
MinHeightTest   equ #CAAC                                                       ; операнд CP минимальной высоты
MinHeightValue  equ #CAB1                                                       ; операнд LD H минимальной высоты
                endmodule

                module RepaintState
ExitInstruction equ #CC17                                                       ; изменяемый байт SCF либо AND A в RepaintItemCore
                endmodule

                module MousePollState
Disabled        equ #65A8                                                       ; ненулевой операнд LD A запрещает опрос мыши
SetupJump       equ #65C7                                                       ; исходный двухбайтовый JR настройки либо два NOP
FirstOffset     equ #65CC                                                       ; смещение первого RL (IX+d), 0 либо 5
SecondOffset    equ #65D1                                                       ; смещение второго RL (IX+d), 5 либо 0
                endmodule

                module PointerInputState
JoyDisabled     equ #6639                                                       ; ненулевой операнд LD A запрещает опрос #001F
Step            equ #66CD                                                       ; операнд LD E, StartStation записывает шаг 2 пикселя
MaxY            equ #66CF                                                       ; операнд LD D, предел 191 для положительного Y
MaxX            equ #66D1                                                       ; операнд LD A, предел 255 для положительного X
                endmodule

                module StationIrqState
SavedSP         equ #9C0D                                                       ; операнд LD SP, сначала адрес аппаратного PC, затем SP до IRQ
ReturnPC        equ #9C11                                                       ; операнд финального JP, адрес аппаратного продолжения
ModeOperand     equ #9B62                                                       ; операнд CP музыкальной ветви, немузыкальная ветвь не обновляет текущим режимом
SavedMixer      equ #9B72                                                       ; операнд LD A, сохранённое при глушении значение AY 7
Divider         equ #9B7E                                                       ; операнд LD A, байтовый делитель с перезагрузкой 50
Pulse           equ #9A99                                                       ; операнд MainLoop, перенос низшей BCD-пары на последнем обновлении
MusicMode       equ #99B2                                                       ; целый код режима, значение 81 выбирает музыкальный тик
                endmodule

                module WindowFillState
FillByte        equ #A0A3                                                       ; операнд LD A, байт заполнения тела окна
SavedSP         equ #A0C1                                                       ; операнд LD SP, обычный стек до цепочки возвратов
                endmodule

                module PopupState
PreviousRow     equ #757A                                                       ; операнд HoverContextMenu, #FF нет выделения, иначе возвращённый номер
SkippedIndex    equ #9E31                                                       ; операнд LD HL исключения, Dispatcher пишет выбранный индекс
MenuDrawIndex   equ #7584                                                       ; операнд DrawItem40, загрузчик задаёт индекс 40
                endmodule

                module MapHighlightState
WidthSkip       equ #C91D                                                       ; банк 1, операнд JR пропуска 4*(31-B) байтов XOR-ядра
                endmodule

                module MenuCommandState
PeriodicCall    equ #9A89                                                       ; операнд периодического CALL MainLoop, команда скрытия ставит EmptyCallback
Hidden          equ #9CAA                                                       ; операнд LD A в RebuildInterface, 1 запрещает EnableDrawList
                endmodule

                module BackgroundState
ItemAttribute   equ #9D48                                                       ; операнд LD C атрибута действительного владельца, задаётся RebuildInterface
                endmodule

                module SignatureState
WorkKey         equ #631C                                                       ; динамическое представление FSignatureKey в уже существующей памяти загрузчика
                endmodule


                module MarketState
MinorCode       equ #A967                                                       ; операнд LD A категорийной поправки, записывается генератором
MajorCode       equ #A999                                                       ; операнд LD A выбора принудительного маркера
MarkMode        equ #A9A9                                                       ; операнд AND, #80 новый маркер, 0 сохранение прежнего bit7
                endmodule


                module FieldSuffixState
DefaultTarget   equ #C804                                                       ; банк LANG, операнд JP без точки, задаётся входным HL
                endmodule


                module WeightedLoadState
SelectedRow     equ #C884                                                       ; банк LANG, операнд LD HL адреса выбранной строки
FirstWeight     equ #C8BF                                                       ; операнд ADD A веса второго набора
SecondWeight    equ #C8E1                                                       ; операнд ADD A веса третьего набора
                endmodule


                module DelimitedRecordState
GroupCount      equ #C856                                                       ; банк LANG, операнд LD B числа FF, 0 означает 256
RecordCount     equ #C862                                                       ; операнд LD B числа FE, 0 означает 256
                endmodule


                module ThresholdSetState
Limit           equ #C509                                                       ; банк LANG, операнд LD A числового предела текущего ключа
                endmodule


                module PackedWriterState
Target          equ #C697                                                       ; банк LANG, операнд LD HL захваченного адреса
InitialValue    equ #C69A                                                       ; операнд LD A захваченного левого значения
                endmodule

                module EncodedWriterState
Target          equ #C6CD                                                       ; банк LANG, операнд LD HL захваченного адреса
InitialValue    equ #C6D0                                                       ; операнд LD A захваченного левого значения
                endmodule


                module ScriptRuntimeState
SavedSP         equ #C01C                                                       ; операнд LD SP в SkipLine, читается NextCommand и FinishScript
StopAtLine      equ #C028                                                       ; операнд LD A завершения после CR, 0 продолжение, ненулевой байт возврат
                endmodule

                module TextRowState
Row             equ #6E91                                                       ; операнд LD A индекса текста в DrawQueuedMessagePanel
                endmodule

                module MainLoopState
TransitionCode  equ #9AB7                                                       ; операнд LD A, коды 2..128 выбирают BeginTransition после DEC
PreviousAction  equ #9AD0                                                       ; операнд LD D, прошлый объединённый код до записи нового
                endmodule

                module RankState
Score           equ #984C                                                       ; слово счётчика, определяющего печатаемый ранг
                endmodule

                module SystemNameState
Buffer          equ #630B                                                       ; имя поверх отработавшего начального bootstrap, до 18 байтов с LF
                endmodule

                module MissionHoverState
Row             equ #6F54                                                       ; операнд LD A в UpdateMissionRowHover, FF без прежнего выделения
                endmodule


                module MissionState
ActiveCode      equ #99A3                                                       ; код 1 разрешает расторжение и проверку завершения миссии
CompletionCode  equ #99A4                                                       ; код 1 запрещает повторную награду, принятие пишет 0
                endmodule


                module PlayerStatusState
Status984B      equ #984B                                                       ; разряды 7..5 выбирают полицейский статус, младшие здесь не установлены
                endmodule


                module MapSelection
FirstWord       equ #9844                                                       ; выбранное первое слово ключа карты
SecondWord      equ #9846                                                       ; выбранное второе слово ключа карты
Variant         equ #9848                                                       ; порядковый вариант выбранного ключа, также пятое поле сохранённой точки
                endmodule


                module MapViewState
OriginLow       equ #6300                                                       ; младшие байты X и Y начала области карты поверх отработавшего bootstrap
OriginHigh      equ #6302                                                       ; старшие байты X и Y начала области карты
Width           equ #6304                                                       ; ширина области в координатных единицах карты
Height          equ #6305                                                       ; высота области в координатных единицах карты
                endmodule


                module MapSectorTables
Cell00          equ #F200                                                       ; таблица сектора X,Y банка KARTA
Cell10          equ #F300                                                       ; таблица сектора X+1,Y банка KARTA
Cell01          equ #F400                                                       ; таблица сектора X,Y+1 банка KARTA
Cell11          equ #F500                                                       ; таблица сектора X+1,Y+1 банка KARTA
                endmodule


                module MapScreenTables
RowHigh         equ #EE00                                                       ; старшие адресные байты 256 строк карты банка KARTA
RowLow          equ #EF00                                                       ; младшие адресные байты строк без горизонтальной колонки
ColumnByte      equ #F000                                                       ; байтовые горизонтальные колонки для 256 пиксельных X
PixelMask       equ #F100                                                       ; одноразрядные маски пиксельных X
                endmodule


                module MapVariantState
Cursor0         equ #C6CA                                                       ; текущий курсор пары координат варианта 0
Cursor1         equ #C6E7                                                       ; текущий курсор пары координат варианта 1
Cursor2         equ #C704                                                       ; текущий курсор пары координат варианта 2
Cursor3         equ #C721                                                       ; текущий курсор пары координат варианта 3
Cursor4         equ #C73E                                                       ; текущий курсор пары координат варианта 4
Cursor5         equ #C75B                                                       ; текущий курсор пары координат варианта 5
Count           equ #C7B6                                                       ; операнд исходного количества вариантов
Wanted          equ #C817                                                       ; операнд сравнения искомого варианта
Resource0       equ #C6C1                                                       ; операнд указателя ресурса варианта 0
Resource1       equ #C6DE                                                       ; операнд указателя ресурса варианта 1
Resource2       equ #C6FB                                                       ; операнд указателя ресурса варианта 2
Resource3       equ #C718                                                       ; операнд указателя ресурса варианта 3
Resource4       equ #C735                                                       ; операнд указателя ресурса варианта 4
Resource5       equ #C752                                                       ; операнд указателя ресурса варианта 5
SpriteSource    equ #C845                                                       ; операнд начала восьми трёхстрочных фаз рисуемого варианта
BlinkMask       equ #C777                                                       ; циклическая временная маска мигания Selected, исходно CC
                endmodule


                module MapVariantResources
Default         equ #CD03                                                       ; обычный ресурс варианта KARTA, формат потребителя ещё разбирается
Current         equ #CD33                                                       ; ресурс текущего варианта
Stored          equ #CD63                                                       ; ресурс варианта второго списка
Selected        equ #CD93                                                       ; ресурс выбранного варианта
                endmodule


                module SecondaryPointState
Cursor          equ #6309                                                       ; существующий указатель текущей пятибайтовой записи второго списка
                endmodule


                module MapClipState
CornerBlock     equ #DE3A                                                       ; ноль разрешает добавлять угол, любое ненулевое значение блокирует его
Output          equ #F900                                                       ; исходная runtime-страница выходных FClipOutputPoint
Points          equ #F800                                                       ; исходный рабочий массив FProjectedPoint банка KARTA
                endmodule

                module MapArcState
AbsY            equ #DFAB                                                       ; младший байт полного модуля Y до коррекции диспетчера
AbsX            equ #DFAC                                                       ; младший байт полного модуля X до коррекции диспетчера
MaxY            equ #DFBE                                                       ; байтовая нижняя координата окна из установщика
HalfY           equ #DFC0                                                       ; оборачиваемая половина Y с переносом от HalfX-2
HalfXLimit      equ #DFC1                                                       ; половина X для предела горизонтального счётчика
HalfXSquare     equ #DFC2                                                       ; половина X для аргументов квадратов и корней
QuadrantCode    equ #DFAD                                                       ; исходный код относительного положения, копируемый в E
Radius          equ #DFAE                                                       ; байтовый радиус растровой рекурсии
OffsetY         equ #DFAF                                                       ; рабочее вертикальное смещение, младший байт загружаемого BC
OffsetX         equ #DFB0                                                       ; рабочее горизонтальное смещение, старший байт загружаемого BC
RowY            equ #DFB1                                                       ; исходная строка подготовки табличного края
CenterX         equ #DFB2                                                       ; центр X симметричной подготовки двух краёв
StartY          equ #DFB3                                                       ; начальный альтернативный E для усечённой растровой рекурсии
ReferenceX      equ #DFBF                                                       ; базовый X в формулах двух подготовок края дуги
                endmodule

                module MapLinePatch
MaskOffset      equ #D306                                                       ; изменяемый операнд ADD A,n при выборе восьмифазной маски
LeftXPixel      equ #D338                                                       ; NOP заменяется командой изменения пикселя, X основной шаг влево
LeftXCross      equ #D33B                                                       ; код условного JR при переходе в левый байт
LeftYPixel      equ #D377                                                       ; NOP заменяется командой изменения пикселя, Y основной шаг влево
LeftYCross      equ #D391                                                       ; код условного JR при переходе в левый байт
RightXPixel     equ #D3B4                                                       ; NOP заменяется командой изменения пикселя, X основной шаг вправо
RightXCross     equ #D3B7                                                       ; код условного JR при переходе в правый байт
RightYPixel     equ #D3F3                                                       ; NOP заменяется командой изменения пикселя, Y основной шаг вправо
RightYCross     equ #D40D                                                       ; код условного JR при переходе в правый байт
                endmodule

                module MapDistanceState
Minimum         equ #C668                                                       ; слово минимума в исходном операнде LD DE,nn помощника расстояния
                endmodule

                module MapVisibleState
Points          equ #F600                                                       ; циклическая страница принятых относительных пар X,Y
Pointers        equ #F700                                                       ; параллельная страница адресов исходных секторных слов
                endmodule

                module MapVisiblePatch
Minimum         equ #C3D0                                                       ; минимальный квадрат расстояния в операнде LD DE,nn видимого поиска
SelectedPoint   equ #C3E8                                                       ; выбранный адрес пары F6 в операнде LD HL,nn, не сбрасывается при пустом списке
SavedStack      equ #C5B6                                                       ; слово исходного SP в операнде заключительного LD SP,nn
WidthFirst      equ #C52B                                                       ; порог ширины при прямом X в Cell00
WidthSecond     equ #C590                                                       ; порог ширины при прямом X в Cell01
InverseWidthA   equ #C55C                                                       ; обратный порог (1-w)&FF для Cell10
InverseWidthB   equ #C5CA                                                       ; обратный порог (1-w)&FF для Cell11
HeightPositive  equ #C511                                                       ; прямой порог h в младшем байте LD BC,nn
HeightNegative  equ #C579                                                       ; обратный порог (1-h)&FF в младшем байте LD BC,nn
                endmodule

                module MapArcPatch
ModeControl     equ #DFC4                                                       ; параметр первого LD A, бит 0 выбирает JR C либо JR NC хвостов
LowTailJump     equ #E426                                                       ; код условия поиска младшего бита одиночного хвоста
HighTailJump    equ #E438                                                       ; код условия поиска старшего бита одиночного хвоста
RightLowJump    equ #E44F                                                       ; код условия младшего хвоста правого адреса
LeftHighJump    equ #E460                                                       ; код условия старшего хвоста левого адреса
LimitBias       equ #E22A                                                       ; байт SUB в DrawClippedArcPair, получает HalfX-2
                endmodule

                module MapScenePatch
SavedStack      equ #C22E                                                       ; исходный SP перед стековым чтением секторных таблиц
WidthFirst      equ #C18B                                                       ; прямой порог X страницы Cell00
WidthSecond     equ #C1E4                                                       ; прямой порог X страницы Cell01
InverseWidthA   equ #C1B6                                                       ; обратный порог X страницы Cell10
InverseWidthB   equ #C211                                                       ; обратный порог X страницы Cell11
HeightPositive  equ #C174                                                       ; прямой порог Y первых двух страниц
HeightNegative  equ #C1D1                                                       ; обратный порог Y последних двух страниц
                endmodule

                module VariantPanelState
ItemIndex       equ #788D                                                       ; слово изменяемого индекса в первом LD HL рисователя панели
RefreshPending  equ #78D7                                                       ; полный код запроса отложенной перерисовки, ноль означает отсутствие запроса
CadenceMask     equ #78DC                                                       ; циклическая временная маска, исходное 80 разрешает один такт из восьми
ResumeRequired  equ #7942                                                       ; полный код возобновления указателя, этот путь пишет 0 либо 1
                endmodule

                module MapPanelState
ItemIndex       equ #6DA9                                                       ; изменяемый индекс записи основной панели карты
ScreenRequest   equ #6D75                                                       ; полный запрос построения экранных таблиц, сбрасывается после рисунка
SectorRequest   equ #6D7B                                                       ; полный запрос построения секторов, хвост рисунка его сохраняет
ClipRequest     equ #6D90                                                       ; полный запрос настройки локального отсечения, сбрасывается после рисунка
                endmodule

                module SystemTraitsText
GovernmentList  equ #EB8D                                                       ; LF перед исходными строками пяти кодов строя
EconomyList     equ #EBC2                                                       ; LF перед исходными строками четырёх типов экономики
                endmodule

                module SystemInfoState
ItemIndex       equ #7690                                                       ; изменяемый индекс FInterfaceItem панели систем
RangeSource     equ #988E                                                       ; исходное слово показанной дальности топлива и геометрии дуги
                endmodule

                module SystemInfoText
Template        equ #EA9B                                                       ; исходные подписи полей панели систем
NoPlanets       equ #EB82                                                       ; исходная фраза Планет нет. до LF
PoliticalAreas  equ #F0B2                                                       ; LF-список четырёх политических областей
                endmodule

                module StoredPointCycle
Cursor          equ #7C99                                                       ; изменяемый операнд LD HL циклического выбора первого списка
                endmodule

                module DecodedMessageText
Entry           equ #E262                                                       ; начальный LF перед сообщениями о системе и иносигнале
                endmodule

                module DecodedPanelState
ItemIndex       equ #6DD5                                                       ; изменяемый индекс FInterfaceItem панели расшифровки
Unknown98A0     equ #98A0                                                       ; Unknown, только FE допускает финал при заданном ключе
                endmodule

                module QueuedMessageState
ItemIndex       equ #6E8B                                                       ; изменяемый индекс FInterfaceItem уведомления
                endmodule

                module QueuedMessageText
Entry           equ #CE19                                                       ; начальный LF таблицы уведомлений
                endmodule

                module PanelHoverState
ShipsRow        equ #67D7                                                       ; сохранённая строка списка Корабли, FF при отсутствии
IndexRow        equ #6A52                                                       ; сохранённая строка списка Индекс, FF при отсутствии
EnvironmentRow  equ #6B95                                                       ; сохранённая строка установок среды, FF при отсутствии
ToPositionRow   equ #7489                                                       ; сохранённая строка списка В позицию, FF при отсутствии
FromPositionRow equ #7512                                                       ; сохранённая строка списка С позиции, FF при отсутствии
GameSettingsRow equ #7627                                                       ; сохранённая строка установок игры, FF при отсутствии
                endmodule

                module TradeTableText
Header          equ #EBF3                                                       ; исходный заголовок колонок Продажа и Наличие
Names           equ #EC4C                                                       ; исходный CR-список товаров с единицами измерения
                endmodule

                module TradeColumnState
OwnedRows       equ #9852                                                       ; читаемая пара количества и цены для колонки Наличие
                endmodule

                module ClearBodyState
TopOffset       equ #C6E3                                                       ; изменяемая байтовая добавка к младшему OriginY
WholeSkip       equ #C754                                                       ; смещение JR перед записями с обоими боковыми полями
LeftSkip        equ #C7AE                                                       ; смещение JR после отсечения слева
RightSkip       equ #C80B                                                       ; смещение JR после отсечения справа
                endmodule

                module ScrollState
EndLimit        equ #A235                                                       ; изменяемая граница проверки индекса и высоты просмотра
ClearHeight     equ #A25E                                                       ; доступная высота, записанная при входе перед вызовом очистки
RenderCall      equ #A265                                                       ; изменяемое слово CALL рисователя принятого индекса
                endmodule

                module TradePanelState
Opcode          equ #7071                                                       ; первый 21 активного Entry либо C9 отключённого рисователя
ItemIndex       equ #7072                                                       ; изменяемый индекс FInterfaceItem товарной панели
HoverArea       equ #7062                                                       ; слово LD DE, младший отступ и старший запрос строк
HoverRows       equ #7063                                                       ; число начатых строк от рисователя, старший байт HoverArea
                endmodule

                module ScriptCallState
EventCode       equ #983A                                                       ; код события, читаемый торговым ReadEventCode
                endmodule

                module EquipmentInfoState
ItemIndex       equ #6AB7                                                       ; слово индекса FInterfaceItem внутри LD HL рисователя документации
SourcePointer   equ #6AE0                                                       ; слово начала выбранной LF-записи внутри LD HL печатателя
LineCount       equ #6A9C                                                       ; полное число сухих визуальных строк внутри LD HL действия
TopRow          equ #6AA4                                                       ; полный индекс прокрутки, печататель использует младший байт
TextIndex       equ #6ACC                                                       ; изменяемый индекс LF-текста описания оснащения
                endmodule

                module SaveSlotState
Buffer          equ #983B                                                       ; существующий блок состояния длиной 512 байтов
FileDigit       equ #7534                                                       ; пятый символ физического FTrDosFileKey по 7530
SaveI           equ #7471                                                       ; операнд восстановления I обработчика записи
LoadI           equ #74FF                                                       ; операнд восстановления I обработчика чтения
SaveIndex       equ #7493                                                       ; изменяемый индекс рисователя пяти позиций записи
LoadIndex       equ #751C                                                       ; изменяемый индекс рисователя пяти позиций чтения
                endmodule

                module SaveSlotText
SaveOptions     equ #DE53                                                       ; пять CR-строк В позицию 1..5, конец LF
LoadOptions     equ #DE8F                                                       ; пять CR-строк С позиции 1..5, конец LF
                endmodule

                module TrDosState
Descriptor      equ #5CDD                                                       ; системный FTrDosEntry, начало имени и каталожного дескриптора
                endmodule

                module EquipmentTradeState
OwnedMode       equ #71EC                                                       ; полный режим, 0 покупка, любое ненулевое значение продажа
                endmodule

                module EquipmentListState
HoverArea       equ #7211                                                       ; слово операнда наведения, младший отступ и старший счётчик строк
KeySize         equ #72DD                                                       ; числовая характеристика L текущего ключа, 1..16
ItemIndex       equ #7228                                                       ; изменяемое слово индекса панели оснащения, штатно 38
RowCount        equ #7212                                                       ; старший байт LD DE наведения, число попыток с маркером 80
ShipOperand     equ #7306                                                       ; текущий тип корабля внутри LD A проверки четырёхбайтового набора
                endmodule

                module EquipmentListData
Prices          equ #9592                                                       ; слова цен, шаг два байта по полному индексу
ShipSets        equ #9400                                                       ; четыре байта типов корабля на каждую строку
Weights         equ #95F0                                                       ; пары минимальной модели станции и байтового веса
Quantities      equ #988E                                                       ; количества с инверсным кодированием и отдельным маркером 80
                endmodule

                module EquipmentListText
Headings        equ #EE19                                                       ; заголовки Наименование, Кол, Цена, Вес и Уст
Names           equ #EE57                                                       ; CR перед первым наименованием оснащения, имена разделены CR
                endmodule

                module WelcomePanelState
ItemIndex       equ #7956                                                       ; изменяемое слово индекса приветственного окна, штатно 45
                endmodule

                module WelcomeText
ModelLabels     equ #CCF3                                                       ; LF перед шестнадцатью подписями моделей станции
Template        equ #CD82                                                       ; четыре части приветствия с тремя разделителями вставок 01
                endmodule

                module ShipPanelState
PreviewIndex    equ #6878                                                       ; изменяемое слово индекса FInterfaceItem в LD HL рисователя просмотра
Selector        equ #6906                                                       ; полный селектор корабельных панелей, назначение всех категорий ещё неизвестно
PendingRedraw   equ #68EB                                                       ; ненулевой операнд периодического входа запрашивает обновление списка и панелей
OwnedMode       equ #79DD                                                       ; полный режим, 0 покупка, любое ненулевое значение продажа
                endmodule

                module D3DClipState
HalfXLow        equ #DAE7                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
HalfYLow        equ #DBA5                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxCorner       equ #E7DB                                                       ; существующее слово угла, старший X и младший Y
MinCorner       equ #E7BA                                                       ; существующее слово угла, старший X и младший Y
MaxXMinY        equ #E7D0                                                       ; существующее слово угла, старший X и младший Y
MinXMaxY        equ #E7C5                                                       ; существующее слово угла, старший X и младший Y
AfterMaxX       equ #DF7F                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
AfterMaxY       equ #DF64                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxX0           equ #E613                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxX1           equ #E6E0                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxX2           equ #E6F3                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxX3           equ #E72E                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxX4           equ #E78B                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinX0           equ #E5F4                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinX1           equ #E695                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinX2           equ #E6A8                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinX3           equ #E73F                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinX4           equ #E79C                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY0           equ #E646                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY1           equ #E69D                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY2           equ #E6E8                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY3           equ #E788                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY4           equ #E799                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MaxY5           equ #E7AB                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY0           equ #E627                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY1           equ #E692                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY2           equ #E6DD                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY3           equ #E72B                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY4           equ #E73C                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
MinY5           equ #E74E                                                       ; существующий байтовый операнд границы, соседний байт сохраняется
                endmodule

                module D3DPreviewState
ThirdCoordinate equ #CDC4                                                       ; третье слово позиции записи, единицы ещё не установлены
ModelOffset     equ #CDC6                                                       ; байтовое смещение модели в исходной записи просмотра
RowOperand      equ #E146                                                       ; изменяемый операнд LD A с компонентом строки
BaseOperand     equ #E148                                                       ; изменяемый операнд ADD A со смещением списка
                endmodule

                module PreviewLineTable
RowHigh         equ #C900                                                       ; страница старших байтов 256 адресов строк в текущем банке
RowLow          equ #CA00                                                       ; страница младших байтов адресов строк без начальной колонки
Column          equ #CB00                                                       ; страница 256 байтовых колонок с повтором по восемь
                endmodule

                module PreviewFaceHeaders
Quad0           equ #F0F0                                                       ; существующий байт заголовка грани в банке D3D 4
Quad1           equ #F382                                                       ; существующий байт заголовка грани в банке D3D 4
Quad2           equ #F434                                                       ; существующий байт заголовка грани в банке D3D 4
Quad3           equ #F4C4                                                       ; существующий байт заголовка грани в банке D3D 4
Quad4           equ #F144                                                       ; существующий байт заголовка грани в банке D3D 4
Quad5           equ #F266                                                       ; существующий байт заголовка грани в банке D3D 4
Quad6           equ #F31A                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle0       equ #F2B7                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle1       equ #F544                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle2       equ #F548                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle3       equ #F2BB                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle4       equ #F1BE                                                       ; существующий байт заголовка грани в банке D3D 4
Triangle5       equ #F1DB                                                       ; существующий байт заголовка грани в банке D3D 4
                endmodule

                module ModelListState
Opcode          equ #67E0                                                       ; первый байт рисователя, 21 либо отключающий C9
ItemIndex       equ #67E1                                                       ; изменяемый индекс FInterfaceItem панели моделей
HoverRows       equ #67D2                                                       ; вычисленный старший байт LD DE наведения, исходно 30
                endmodule

                module CurrentModels
ShipIndex       equ #9849                                                       ; текущий индекс корабля для собственного ценового просмотра
SkimmerIndex    equ #984A                                                       ; текущий индекс скимера для собственного ценового просмотра
                endmodule

                module ModelDescriptionState
RowCount        equ #692B                                                       ; существующий операнд слова общей границы прокрутки описания
TopRow          equ #6933                                                       ; существующий операнд текущего 16-битного начала прокрутки
Opcode          equ #6945                                                       ; первый байт рисователя описания, 21 либо отключающий C9
ItemIndex       equ #6946                                                       ; изменяемый индекс FInterfaceItem панели описания
                endmodule

                module PreviewMultiplyState
ReturnTarget    equ #EB7C                                                       ; два байта изменяемого JP умножителя, адрес продолжения из входного DE
                endmodule

                module PreviewTransformState
InputFirst      equ #EB7F                                                       ; операнд первой исходной координаты, знаковое слово
InputSecond     equ #EB8D                                                       ; операнд второй исходной координаты, знаковое слово
InputThird      equ #EBA0                                                       ; операнд третьей исходной координаты, знаковое слово
ResultFirst     equ #DAF6                                                       ; рабочее слово принятого результата первой строки
ResultSecond    equ #DA38                                                       ; рабочее слово принятого результата второй строки
ResultThird     equ #DA16                                                       ; рабочее слово принятого результата третьей строки
Coeff11         equ #D567                                                       ; знаковый коэффициент строки 1 при координате 1
Coeff12         equ #D574                                                       ; знаковый коэффициент строки 1 при координате 2
Coeff13         equ #D586                                                       ; знаковый коэффициент строки 1 при координате 3
Coeff21         equ #D599                                                       ; знаковый коэффициент строки 2 при координате 1
Coeff22         equ #D5A6                                                       ; знаковый коэффициент строки 2 при координате 2
Coeff23         equ #D5B8                                                       ; знаковый коэффициент строки 2 при координате 3
Coeff31         equ #D5CB                                                       ; знаковый коэффициент строки 3 при координате 1
Coeff32         equ #D5D8                                                       ; знаковый коэффициент строки 3 при координате 2
Coeff33         equ #D5EA                                                       ; знаковый коэффициент строки 3 при координате 3
                endmodule

                module PreviewQueueState
Head            equ #CF02                                                       ; младший индекс головы активной очереди, 1 обозначает пустую
NextFree        equ #CF03                                                       ; свободный индекс с шагом 14, FC завершает обход объектов
Flags           equ #CEFA                                                       ; флаги подготавливаемого узла, бит 7 участвует в выборе ключа
ModelOffset     equ #CEFB                                                       ; рабочее смещение указателя модели подготавливаемого узла
AngleFirst      equ #C21E                                                       ; первый параметр ориентации подготавливаемого узла
AngleSecond     equ #C21F                                                       ; второй параметр ориентации подготавливаемого узла
AngleThird      equ #C220                                                       ; третий параметр ориентации подготавливаемого узла
                endmodule

                module PreviewBoundsState
FirstSkip       equ #EDC4                                                       ; операнд первого JR масштаба, заранее получает 6-b
SecondSkip      equ #EDFD                                                       ; операнд второго JR масштаба, заранее получает 6-b
                endmodule

                module PreviewQueueBuildState
RawFirst        equ #CEFC                                                       ; последняя прочитанная первая координата записи
RawSecond       equ #CEFE                                                       ; последняя прочитанная вторая координата
RawThird        equ #CF00                                                       ; последняя прочитанная третья координата
SavedSP         equ #EEEF                                                       ; операнд LD SP восстановления настоящего CPU-стека
SizeSkip        equ #ED5C                                                       ; операнд первого JR масштаба, получает 6-b
                endmodule

                module PreviewModelMatrixState
Coeff11         equ #D561                                                       ; изменяемый байтовый операнд матрицы модели 11
Coeff21         equ #D563                                                       ; изменяемый байтовый операнд матрицы модели 21
Coeff31         equ #D565                                                       ; изменяемый байтовый операнд матрицы модели 31
Coeff12         equ #D5FD                                                       ; изменяемый байтовый операнд матрицы модели 12
Coeff22         equ #D5FF                                                       ; изменяемый байтовый операнд матрицы модели 22
Coeff32         equ #D601                                                       ; изменяемый байтовый операнд матрицы модели 32
Coeff13         equ #D6A9                                                       ; изменяемый байтовый операнд матрицы модели 13
Coeff23         equ #D6AB                                                       ; изменяемый байтовый операнд матрицы модели 23
Coeff33         equ #D6AD                                                       ; изменяемый байтовый операнд матрицы модели 33
                endmodule

                module PreviewMatrixComposeState
Scene11         equ #D567                                                       ; байтовый операнд сцены или итоговой матрицы 11
Scene12         equ #D574                                                       ; байтовый операнд сцены или итоговой матрицы 12
Scene13         equ #D586                                                       ; байтовый операнд сцены или итоговой матрицы 13
Scene21         equ #D599                                                       ; байтовый операнд сцены или итоговой матрицы 21
Scene22         equ #D5A6                                                       ; байтовый операнд сцены или итоговой матрицы 22
Scene23         equ #D5B8                                                       ; байтовый операнд сцены или итоговой матрицы 23
Scene31         equ #D5CB                                                       ; байтовый операнд сцены или итоговой матрицы 31
Scene32         equ #D5D8                                                       ; байтовый операнд сцены или итоговой матрицы 32
Scene33         equ #D5EA                                                       ; байтовый операнд сцены или итоговой матрицы 33
Coeff11         equ #D8C1                                                       ; байтовый операнд сцены или итоговой матрицы 11
Coeff12         equ #D8D1                                                       ; байтовый операнд сцены или итоговой матрицы 12
Coeff13         equ #D8C9                                                       ; байтовый операнд сцены или итоговой матрицы 13
Coeff21         equ #D8D9                                                       ; байтовый операнд сцены или итоговой матрицы 21
Coeff22         equ #D8E9                                                       ; байтовый операнд сцены или итоговой матрицы 22
Coeff23         equ #D8E1                                                       ; байтовый операнд сцены или итоговой матрицы 23
Coeff31         equ #D8F1                                                       ; байтовый операнд сцены или итоговой матрицы 31
Coeff32         equ #D901                                                       ; байтовый операнд сцены или итоговой матрицы 32
Coeff33         equ #D8F9                                                       ; байтовый операнд сцены или итоговой матрицы 33
                endmodule

                module PreviewProjectionScaleState
DepthSkip       equ #DA20                                                       ; операнд JR масштаба глубины
FirstAxisSkip   equ #DA3B                                                       ; операнд JR масштаба первой проектируемой координаты
SecondAxisSkip  equ #DAF9                                                       ; операнд JR масштаба второй проектируемой координаты
                endmodule

                module PreviewPerspectiveState
SecondOutput    equ #DBB6                                                       ; операнд второго результата перед PUSH HL
PreserveTarget  equ #DBC0                                                       ; операнд адреса повторной записи прежнего слова по входному SP-6
                endmodule

                module PreviewVertexGroupState
PackedFirst     equ #D910                                                       ; операнд первой упакованной пары произведений
PackedSecond    equ #D913                                                       ; операнд второй упакованной пары произведений
PackedThird     equ #D916                                                       ; операнд третьей упакованной пары произведений
DepthFirst      equ #D956                                                       ; операнд первого произведения третьей компоненты
DepthSecond     equ #D955                                                       ; операнд второго произведения третьей компоненты
DepthThird      equ #D953                                                       ; операнд третьего произведения третьей компоненты
NextOffset      equ #D90D                                                       ; младший байт LD SP страницы C6, следующий свободный индекс
SavedSP         equ #DA11                                                       ; операнд восстановления CPU-SP после генерации группы
PackedVertex0   equ #D97A                                                       ; операнд двух упакованных осей комбинации 0
PackedVertex1   equ #D9AE                                                       ; операнд двух упакованных осей комбинации 1
PackedVertex3   equ #D9BB                                                       ; операнд двух упакованных осей комбинации 3
PackedVertex2   equ #D9CA                                                       ; операнд двух упакованных осей комбинации 2
PackedVertex5   equ #D9EF                                                       ; операнд двух упакованных осей комбинации 5
PackedVertex4   equ #D9FC                                                       ; операнд двух упакованных осей комбинации 4
PackedVertex6   equ #D9D5                                                       ; операнд двух упакованных осей комбинации 6
PackedVertex7   equ #D9E2                                                       ; операнд двух упакованных осей комбинации 7
DepthVertex5    equ #D9F2                                                       ; операнд третьей компоненты комбинации 5
DepthVertex4    equ #D9FF                                                       ; операнд третьей компоненты комбинации 4
DepthVertex6    equ #D9D8                                                       ; операнд третьей компоненты комбинации 6
DepthVertex7    equ #D9E5                                                       ; операнд третьей компоненты комбинации 7
                endmodule

                module PreviewPlanarProductsState
CosFirst        equ #D861                                                       ; операнд косинуса для первого входного параметра
SinFirst        equ #D869                                                       ; операнд синуса для третьего входного параметра
SinSecond       equ #D871                                                       ; операнд синуса, отрицаемого перед умножением первого параметра
CosSecond       equ #D87B                                                       ; операнд косинуса для третьей компоненты третьего параметра
                endmodule

                module PreviewEdgeRasterState
MaskOffset      equ #DE34                                                       ; операнд младшего адреса таблицы масок, B0 либо B8
LeftFlatOp      equ #DE66                                                       ; изменяемый opcode пиксельной операции ветви LeftFlat
LeftFlatJump    equ #DE69                                                       ; изменяемый opcode границы байта ветви LeftFlat
LeftSteepOp     equ #DEA5                                                       ; изменяемый opcode пиксельной операции ветви LeftSteep
LeftSteepJump   equ #DEBF                                                       ; изменяемый opcode границы байта ветви LeftSteep
RightFlatOp     equ #DEE2                                                       ; изменяемый opcode пиксельной операции ветви RightFlat
RightFlatJump   equ #DEE5                                                       ; изменяемый opcode границы байта ветви RightFlat
RightSteepOp    equ #DF21                                                       ; изменяемый opcode пиксельной операции ветви RightSteep
RightSteepJump  equ #DF3B                                                       ; изменяемый opcode границы байта ветви RightSteep
                endmodule

                module PreviewPolygonState
PatternDelta    equ #D20C                                                       ; операнд XOR для смены шаблона строки
LeftSubtract    equ #D223                                                       ; вычитаемая дробная часть левого шага
LeftHeight      equ #D227                                                       ; восстанавливаемый период левой ошибки
RightSubtract   equ #D22F                                                       ; вычитаемая дробная часть правого шага
RightHeight     equ #D233                                                       ; восстанавливаемый период правой ошибки
CurrentRow      equ #D239                                                       ; операнд загрузки текущей строки контура
LastRow         equ #D23B                                                       ; исключённая нижняя строка всего контура
LeftEndRow      equ #D23F                                                       ; строка смены левого ребра
RightEndRow     equ #D243                                                       ; строка смены правого ребра
ColumnBase      equ #D257                                                       ; операнд начальной байтовой колонки экрана
SavedStack      equ #D27E                                                       ; операнд восстановления CPU-SP перед POP HL и RET
UpdateLeft      equ #D28C                                                       ; существующий вход обновления левой цепочки
SelectRight     equ #D282                                                       ; существующий JP к обновлению правой цепочки
                endmodule

                module PreviewPolygonEdgeState
LeftVertex      equ #D290                                                       ; операнд указателя строкового байта начала левого ребра
RightVertex     equ #D358                                                       ; операнд указателя строкового байта начала правого ребра
LastIndex       equ #D35F                                                       ; операнд последнего нечётного индекса строки контура в странице C8
                endmodule

                module PreviewPolygonPrepState
FirstRowLow     equ #D4C7                                                       ; операнд OR младшего адреса начальной экранной строки
                endmodule

                module HelpTextState
RecordOperand   equ #DB01                                                       ; банк 7, байт номера LF-записи внутри LD A индексатора HELP
                endmodule

                module HelpPanelState
HoverRows       equ #6A4C                                                       ; слово DE обработчика наведения, E отступ, D текущее число видимых строк
TextIndex       equ #69A9                                                       ; слово индекса FInterfaceItem внутри LD HL рисователя текста справки
ContentsIndex   equ #6A5C                                                       ; слово индекса FInterfaceItem внутри LD HL рисователя разделов
TopLine         equ #699D                                                       ; слово верхней визуальной строки внутри LD HL действия панели
ContentsTop     equ #6A15                                                       ; слово верхнего CR-заголовка внутри LD HL действия списка
VisibleTitles   equ #6A4D                                                       ; байт D операнда LD DE обработчика наведения списка разделов
LineCount       equ #6995                                                       ; слово числа строк HELP внутри LD HL действия панели справки
                endmodule

                module EnvironmentPanelState
ItemIndex       equ #6BA6                                                       ; слово индекса FInterfaceItem в LD HL рисователя среды
TopRow          equ #6B23                                                       ; полный индекс начальной подписи и значения в действии среды
RowCount        equ #6B90                                                       ; байт D обработчика наведения, число обработанных значений
HoverRows       equ #6B8F                                                       ; слово DE обработчика наведения, E отступ, D число строк
                endmodule

                module GameSettingsPanelState
ItemIndex       equ #7638                                                       ; слово индекса FInterfaceItem в LD HL рисователя игры
TopRow          equ #75D3                                                       ; полный индекс начальной подписи и значения в действии игры
RowCount        equ #7622                                                       ; байт D обработчика наведения, число обработанных значений
HoverRows       equ #7621                                                       ; слово DE обработчика наведения, E отступ, D число строк
                endmodule


                module ContractMapState
Cursor          equ #7CCC                                                       ; изменяемое слово LD HL выбора контракта, исходно MapAuxiliaryCodes.State
                endmodule


                ; Изменяемые операнды огибающей MUZ1 и исходный буфер AY, память не выделяется
                module MusicEnvelopeState
RowTempo        equ #DF62                                                       ; изменяемый темп строки из заголовка модуля либо команды 09
AyShape         equ #DC0D                                                       ; однократный буфер формы AY13, ноль пропускает аппаратную запись
AyNoise         equ #DC06                                                       ; базовый шум в буфере AY6 до добавления вклада сэмплов
EnvelopeBase    equ #E2F1                                                       ; базовый период огибающей в изменяемом операнде
Shape           equ #DF48                                                       ; ожидающая форма, ненулевой байт перезапускает период и скольжение
SlideOffset     equ #E2EE                                                       ; накопленное слово скольжения огибающей
SlideCounter    equ #E2FA                                                       ; текущий байтовый счётчик задержки скольжения
Phase           equ #E37D                                                       ; числовая стадия распределённого разбора каналов B и C
SlideStep       equ #E302                                                       ; слово шага для прибавления к смещению огибающей
SlideReload     equ #E309                                                       ; задержка перезагрузки после применения шага
SlideGate       equ #DF6B                                                       ; код команды, 18 пропускает отложенную установку, 06 включает её
Base            equ #DF50                                                       ; ожидающий базовый период для новой формы огибающей
Noise           equ #DF67                                                       ; ожидающий базовый шум текущей строки паттерна
Step            equ #DF6E                                                       ; ожидающий шаг отложенной команды скольжения
Delay           equ #DF74                                                       ; ожидающая задержка отложенной команды скольжения
                endmodule


                ; Исходные изменяемые операнды MusicChannelAState, память не выделяется
                module MusicChannelAState
GateCommand     equ #DE90                                                       ; код команды длительностей, 18 пропускает тело, 06 включает его
EnabledTicks    equ #DE97                                                       ; ожидающая длительность включённого состояния
DisabledTicks   equ #DE9F                                                       ; ожидающая длительность выключенного состояния
SampleCommand   equ #DEA3                                                       ; код отложенной установки позиции сэмпла
SamplePosition  equ #DEA6                                                       ; ожидающая байтовая позиция сэмпла
OrnamentCommand equ #DEAE                                                       ; код отложенной установки позиции орнамента
OrnamentPos     equ #DEB1                                                       ; ожидающая байтовая позиция орнамента
GateEnabled     equ #E0E9                                                       ; длительность после перехода в включённое состояние
GateDisabled    equ #E0E5                                                       ; длительность после перехода в выключенное состояние
GateCounter     equ #E0D7                                                       ; текущий счётчик до переключения разрешения канала A
SampleCursor    equ #DFFA                                                       ; позиция шага сэмпла, используемая синтезом A
OrnamentCursor  equ #E07C                                                       ; позиция байта орнамента, используемая синтезом A
                endmodule


                ; Исходные изменяемые операнды MusicChannelBState, память не выделяется
                module MusicChannelBState
GateCommand     equ #DF1E                                                       ; код команды длительностей, 18 пропускает тело, 06 включает его
EnabledTicks    equ #DF25                                                       ; ожидающая длительность включённого состояния
DisabledTicks   equ #DF2D                                                       ; ожидающая длительность выключенного состояния
SampleCommand   equ #DF31                                                       ; код отложенной установки позиции сэмпла
SamplePosition  equ #DF34                                                       ; ожидающая байтовая позиция сэмпла
OrnamentCommand equ #DF3C                                                       ; код отложенной установки позиции орнамента
OrnamentPos     equ #DF3F                                                       ; ожидающая байтовая позиция орнамента
GateEnabled     equ #E1E9                                                       ; длительность после перехода в включённое состояние
GateDisabled    equ #E1E5                                                       ; длительность после перехода в выключенное состояние
GateCounter     equ #E1D7                                                       ; текущий счётчик до переключения разрешения канала B
SampleCursor    equ #E0F9                                                       ; позиция шага сэмпла, используемая синтезом A
OrnamentCursor  equ #E17C                                                       ; позиция байта орнамента, используемая синтезом A
                endmodule


                ; Исходные изменяемые операнды MusicChannelBRow, память не выделяется
                module MusicChannelBRow
ResetOpcode     equ #DEBC                                                       ; 22 сбрасывает SlideOffset, 01 загружает BC адресом без записи
NoteBlock       equ #DEBF                                                       ; код пропуска сброса ноты, 18 пропускает тело, 06 включает его
EnableCode      equ #DED6                                                       ; NOP 00 включает канал, CPL 2F задаёт выключенное состояние FF
PendingNote     equ #DEDB                                                       ; ожидающий индекс ноты канала B
PendingSample   equ #DEE0                                                       ; ожидающий указатель сэмпла для новой ноты
VolumeRow       equ #DEEB                                                       ; смещение строки таблицы громкости, копируется без нормализации
OrnamentBlock   equ #DEEF                                                       ; код пропуска настройки орнамента, сохраняется самим блоком
PendingOrnament equ #DEF6                                                       ; ожидающий указатель орнамента
PendingEnvelope equ #DEFC                                                       ; ожидающая маска огибающей для амплитуды канала B
SlideBlock      equ #DF00                                                       ; код пропуска настройки скольжения, сохраняется самим блоком
PendingTarget   equ #DF03                                                       ; ожидающая целевая нота для ограниченного скольжения
PendingDelay    equ #DF08                                                       ; ожидающая задержка шага скольжения
PendingStep     equ #DF10                                                       ; ожидающий знаковый шаг скольжения
PendingBranch   equ #DF16                                                       ; ожидаемое смещение JR после прибавления шага
SlideOffset     equ #E198                                                       ; накопленное слово скольжения, обнуляется только при ResetOpcode=22
SampleCursor    equ #E0F9                                                       ; позиция сэмпла канала B
NoiseAccum      equ #E13D                                                       ; накопленный вклад сэмпла B в шум
EnvelopeAccum   equ #E154                                                       ; накопленный вклад сэмпла B в период огибающей
OrnamentCursor  equ #E17C                                                       ; позиция орнамента канала B
SlideCounter    equ #E19F                                                       ; текущий счётчик задержки скольжения B
GateCounter     equ #E1D7                                                       ; текущий счётчик чередования разрешения B
ToneAccum       equ #E16C                                                       ; накопленная тональная поправка сэмпла B
Disabled        equ #E0EE                                                       ; 00 разрешает синтез B, FF пропускает его, это числовое состояние
CurrentNote     equ #E1BB                                                       ; текущий индекс ноты канала B
SamplePointer   equ #E0F5                                                       ; указатель сэмпла канала B
AmplitudeAdjust equ #E110                                                       ; исходное 10 отключает направленное изменение амплитуды
VolumeOffset    equ #E12C                                                       ; смещение в таблице громкости после вычисления амплитуды
OrnamentPointer equ #E178                                                       ; указатель орнамента канала B
EnvelopeMask    equ #E136                                                       ; маска огибающей, добавляемая к амплитуде B
TargetNote      equ #E1B3                                                       ; индекс ноты для сравнения при ограниченном скольжении
SlideReload     equ #E1CE                                                       ; перезагрузка счётчика после добавления шага
SlideStep       equ #E1A8                                                       ; слово шага скольжения B
SlideBranch     equ #E1AF                                                       ; смещение JR после обновления накопленного тона
                endmodule


                ; Исходные операнды счётчиков и байты буфера AY, память не выделяется
                module MusicGateState
AmplitudeA      equ #DC08                                                       ; буфер амплитуды AY канала A
CounterA        equ #E0D7                                                       ; текущий счётчик чередования канала A
StateA          equ #DFEF                                                       ; полный байт состояния, 00 разрешает синтез, FF пропускает его канала A
DisabledTicksA  equ #E0E5                                                       ; перезагрузка после получения ненулевого состояния канала A
EnabledTicksA   equ #E0E9                                                       ; перезагрузка после получения нулевого состояния канала A
AmplitudeB      equ #DC09                                                       ; буфер амплитуды AY канала B
CounterB        equ #E1D7                                                       ; текущий счётчик чередования канала B
StateB          equ #E0EE                                                       ; полный байт состояния, 00 разрешает синтез, FF пропускает его канала B
DisabledTicksB  equ #E1E5                                                       ; перезагрузка после получения ненулевого состояния канала B
EnabledTicksB   equ #E1E9                                                       ; перезагрузка после получения нулевого состояния канала B
AmplitudeC      equ #DC0A                                                       ; буфер амплитуды AY канала C
CounterC        equ #E2D5                                                       ; текущий счётчик чередования канала C
StateC          equ #E1EE                                                       ; полный байт состояния, 00 разрешает синтез, FF пропускает его канала C
DisabledTicksC  equ #E2E3                                                       ; перезагрузка после получения ненулевого состояния канала C
EnabledTicksC   equ #E2E7                                                       ; перезагрузка после получения нулевого состояния канала C
                endmodule


                ; Исходные операнды и буфер аппаратного вывода AY, память не выделяется
                module MusicAyState
Registers       equ #DC00                                                       ; начало исходного буфера четырнадцати регистров AY
EnvelopePeriod  equ #DC0B                                                       ; слово периода огибающей в буфере AY11 и AY12
SavedSP         equ #E30E                                                       ; изменяемое слово восстановления настоящего стека
NoiseSeed       equ #DFE9                                                       ; старший байт начального IX для следующего кадра
                endmodule


                ; Исходные изменяемые операнды музыкальных команд, память не выделяется
                module MusicEffectState
PendingDelayA   equ #DE7A                                                       ; ожидающая задержка тонального скольжения A
PendingStepA    equ #DE82                                                       ; ожидающее слово шага тонального скольжения A
PendingBranchA  equ #DE88                                                       ; ожидаемое смещение JR после обновления тона A
PendingTargetA  equ #DE75                                                       ; ожидающая целевая нота ограниченного скольжения A
PendingNoteA    equ #DE4D                                                       ; ожидающая нота строки A
CurrentNoteA    equ #E0BB                                                       ; текущая нота в сравнении ограниченного скольжения A
TargetNoteC     equ #E2B1                                                       ; целевая нота ограниченного скольжения C
CurrentNoteC    equ #E2B9                                                       ; текущий индекс ноты C
PreviousNoteC   equ #E6EC                                                       ; сохранённая декодером прежняя нота C, изменяемый операнд LD (HL),n
SampleCursorC   equ #E1F9                                                       ; текущая позиция сэмпла C
OrnamentCursorC equ #E27A                                                       ; текущая позиция орнамента C
                endmodule


                ; Исходные операнды синтеза A, память не выделяется
                module MusicSynthesisA
SamplePointer   equ #DFF6                                                       ; указатель заголовка и четырёхбайтовых шагов сэмпла
AmplitudeAdjust equ #E011                                                       ; накопленная поправка базового уровня, нейтральное значение 10
VolumeOffset    equ #E02D                                                       ; байтовое смещение строки таблицы громкости
EnvelopeMask    equ #E037                                                       ; маска огибающей, применяемая при нулевом FixedLevelBit
NoiseAccum      equ #E03E                                                       ; накопленный вклад сэмпла в шум
EnvelopeAccum   equ #E055                                                       ; накопленный вклад сэмпла в общий период огибающей
ToneAccum       equ #E06C                                                       ; накопленная тональная поправка сэмпла
OrnamentPointer equ #E078                                                       ; указатель заголовка и байтов орнамента
SlideOffset     equ #E098                                                       ; накопленное слово тонального скольжения
SlideCounter    equ #E09F                                                       ; число тиков до следующего шага скольжения
SlideStep       equ #E0A8                                                       ; знаковое слово шага тонального скольжения
SlideReload     equ #E0CE                                                       ; перезагрузка счётчика после добавления шага
SlideBranch     equ #E0AF                                                       ; смещение JR, 1D пропускает ограничение, 00 выполняет его
TargetNote      equ #E0B3                                                       ; целевая нота ограниченного скольжения
                endmodule

                ; Исходные операнды синтеза C, память не выделяется
                module MusicSynthesisC
SamplePointer   equ #E1F5                                                       ; указатель заголовка и четырёхбайтовых шагов сэмпла
AmplitudeAdjust equ #E20F                                                       ; накопленная поправка базового уровня, нейтральное значение 10
VolumeOffset    equ #E22B                                                       ; байтовое смещение строки таблицы громкости
EnvelopeMask    equ #E235                                                       ; маска огибающей, применяемая при нулевом FixedLevelBit
NoiseAccum      equ #E23C                                                       ; накопленный вклад сэмпла в шум
EnvelopeAccum   equ #E253                                                       ; накопленный вклад сэмпла в общий период огибающей
ToneAccum       equ #E26A                                                       ; накопленная тональная поправка сэмпла
OrnamentPointer equ #E276                                                       ; указатель заголовка и байтов орнамента
SlideOffset     equ #E296                                                       ; накопленное слово тонального скольжения
                endmodule

                module MusicSynthesisState
EnvelopeSeed    equ #DFE4                                                       ; исходный операнд младшего байта общего вклада огибающей
                endmodule

                module MusicSynthesisState
MixerSeed       equ #DFE8                                                       ; исходный младший байт IX, сохраняется при пропуске A
                endmodule


                ; Исходные изменяемые операнды MusicChannelARow, память не выделяется
                module MusicChannelARow
EntryOpcode     equ #DE1F                                                       ; C3 выбирает JP к синтезу, 01 исполняет LD BC и продолжает подготовку строки
ResetOpcode     equ #DE2E                                                       ; 22 сбрасывает SlideOffset через LD (nn),HL, 01 сохраняет его через LD BC,nn
NoteBlock       equ #DE31                                                       ; код пропуска сброса ноты, 18 пропускает тело, 06 включает его
EnableCode      equ #DE48                                                       ; NOP 00 включает канал, CPL 2F задаёт выключенное состояние FF
PendingNote     equ #DE4D                                                       ; ожидающий индекс ноты канала A
PendingSample   equ #DE52                                                       ; ожидающий указатель сэмпла для новой ноты
VolumeRow       equ #DE5D                                                       ; смещение строки таблицы громкости, копируется без нормализации
OrnamentBlock   equ #DE61                                                       ; код пропуска настройки орнамента, сохраняется самим блоком
PendingOrnament equ #DE68                                                       ; ожидающий указатель орнамента
PendingEnvelope equ #DE6E                                                       ; ожидающая маска огибающей для амплитуды канала A
SlideBlock      equ #DE72                                                       ; код пропуска настройки скольжения, сохраняется самим блоком
PendingTarget   equ #DE75                                                       ; ожидающая целевая нота для ограниченного скольжения
PendingDelay    equ #DE7A                                                       ; ожидающая задержка шага скольжения
PendingStep     equ #DE82                                                       ; ожидающий знаковый шаг скольжения
PendingBranch   equ #DE88                                                       ; ожидаемое смещение JR после прибавления шага
                endmodule


                ; Существующие счётчики и операнды паттернов, память не выделяется
                module MusicPatternState
RowCounterA     equ #DE1E                                                       ; текущий байтовый счётчик длительности строки A
RowCounterB     equ #DC0E                                                       ; текущий байтовый счётчик длительности строки B
RowCounterC     equ #DC0F                                                       ; текущий байтовый счётчик длительности строки C
PatternB        equ #E393                                                       ; изменяемый указатель следующей команды B
PatternC        equ #E3C4                                                       ; изменяемый указатель следующей команды C
RowDelayA       equ #DFC9                                                       ; перезагрузка счётчика длительности A, команда B1 копирует байт без нормализации
RowDelayB       equ #E39F                                                       ; перезагрузка счётчика длительности B
RowDelayC       equ #E3D0                                                       ; перезагрузка счётчика длительности C
                endmodule


                ; Исходные изменяемые операнды MusicAdvanceAState, память не выделяется
                module MusicAdvanceAState
PatternA        equ #DF89                                                       ; изменяемый указатель следующей команды A, нулевой командный байт выбирает новую позицию
PositionCursor  equ #DF98                                                       ; указатель следующего байта списка позиций
LoopPosition    equ #DF9F                                                       ; указатель позиции возврата при маркере FF
PatternTable    equ #DFA7                                                       ; база таблицы относительных указателей, к ней дважды прибавляется байт позиции
ModuleBase      equ #DFAE                                                       ; база модуля, прибавляемая к каждому из трёх относительных указателей
SavedStack      equ #DFBD                                                       ; исходный SP, сохраняемый перед тремя POP из таблицы и восстанавливаемый перед CALL
                endmodule


                ; Существующий изменяемый операнд восстановления SP, память не выделяется
                module MusicInitializeState
SavedStack      equ #DB4D                                                       ; слово SP в исходной команде LD SP, nn
                endmodule

                endif
