                ifndef _AWAKEN_STRUCTS_
                define _AWAKEN_STRUCTS_

                ; -----------------------------------------
                ; запись каталога TR-DOS, исходный формат диска
                ; поле Parameter зависит от типа файла и фактического загрузчика
                ; -----------------------------------------
                struct FTrDosEntry
Name            ds 8, #00                                                       ; восемь исходных байтов имени
Extension       db #00                                                          ; байт типа файла
Parameter       dw #0000                                                        ; параметр записи, не универсальный адрес загрузки
Length          dw #0000                                                        ; логическая длина в байтах
SectorCount     db #00                                                          ; число выделенных физических секторов
FirstSector     db #00                                                          ; первый сектор, отсчёт от нуля
FirstTrack      db #00                                                          ; первая логическая дорожка
                ends
                assert FTrDosEntry == #10

                ; девять байтов ключа файлового запроса TR-DOS, без терминатора
                struct FTrDosFileKey
Name            text 8, { #00 }                                                 ; восемь символов имени с исходными пробелами
Extension       db #00                                                          ; байт типа файла
                ends
                assert FTrDosFileKey == #09

                ; -----------------------------------------
                ; шесть первых байтов заголовка упакованных ресурсов с сигнатурой HR
                ; длины подтверждены байтами файлов панелей и экранов stscr
                ; -----------------------------------------
                struct FPackedHeader
Signature       dw #5248                                                        ; исходная сигнатура HR, младший байт первым
UnpackedSize    dw #0000                                                        ; размер распакованного блока
PackedSize      dw #0000                                                        ; длина исходного упакованного файла
                ends
                assert FPackedHeader == #06

                ; -----------------------------------------
                ; запись эффекта файла VOXAL, шаг #12 установлен кодом AllocateEffect
                ; State, схема разрядов 7..0
                ;   7 6 5 4 3 2 1 0
                ;   T V V V V V V V
                ; T, установленный знак завершает поиск, запись не изменяется
                ; V, младшие семь бит вместе со знаком образуют байт состояния, не набор независимых флагов
                ; State = 0, запись свободна
                ; State = 1..127, запись занята
                ; State = 128..255, ограничитель списка
                ; -----------------------------------------
                struct FVisualEffect
SavedHL         dw #0000                                                        ; исходный HL из альтернативного набора
SavedDE         dw #0000                                                        ; исходный DE из альтернативного набора
SavedBC         dw #0000                                                        ; исходный BC из альтернативного набора
Mode            db #00                                                          ; параметр из изменяемого операнда AllocateEffect
State           db #00                                                          ; ноль означает свободную запись, знак завершает поиск
FramePointer    dw #0000                                                        ; адрес текущего кадра ресурса
FirstFrame      dw #0000                                                        ; адрес первого кадра ресурса
FrameCount      db #01                                                          ; оставшиеся шаги до возврата к первому кадру
FrameReload     db #00                                                          ; счётчик после возврата к первому кадру
FrameStride     dw #0000                                                        ; шаг между кадрами ресурса в байтах
FrameWidth      db #00                                                          ; ширина исходного кадра для проекции
FrameHeight     db #00                                                          ; высота исходного кадра для проекции
                ends
                assert FVisualEffect == #12

                ; -----------------------------------------
                ; элемент станционного интерфейса, исходная таблица начинается с #F0FD
                ; поле группы #E0 участвует в порядке обработки, остальные биты ещё не названы
                ; поля указателей подтверждены диспетчерами #9C77 и #9DBA
                ; Flags, схема разрядов 7..0
                ;   7 6 5 4 3 2 1 0
                ;   G G G ? ? ? ? ?
                ; G, трёхбитовое поле группы, код 010 переносит обработчик в начало списка рисования
                ; ?, назначение разряда пока не установлено
                ; нулевое значение не выбирает группу переноса, семантика остальных нулевых битов не доказана
                ; -----------------------------------------
                struct FInterfaceItem
X               db #00                                                          ; горизонтальная координата
Y               db #00                                                          ; вертикальная координата
Width           db #00                                                          ; ширина элемента
Height          db #00                                                          ; высота элемента
Flags           db #00                                                          ; флаги, исходные биты состояния элемента
TextIndex       db #00                                                          ; индекс текстовой записи в общих рисователях элемента
EventHandler    dw #0000                                                        ; указатель обработчика события с трёхбайтовой обёрткой
SavedX          db #00                                                          ; сохранённая горизонтальная координата
SavedY          db #00                                                          ; сохранённая вертикальная координата
SavedWidth      db #00                                                          ; сохранённая ширина элемента
SavedHeight     db #00                                                          ; сохранённая высота элемента
DrawHandler     dw #0000                                                        ; указатель, помещаемый в список вызовов перерисовки
Reserved        dw #0000                                                        ; резервное слово, в исходных записях равно нулю
                ends
                assert FInterfaceItem == #10
                assert FInterfaceItem.Reserved == #0E

                ; -----------------------------------------
                ; запись проецируемой вершины, читается диспетчером 3DPART из таблицы #8E00
                ; индекс из списка вершин является байтовым смещением в пределах этой страницы
                ; -----------------------------------------
                struct FProjectedPoint
X               dw #0000                                                        ; горизонтальная координата
Y               dw #0000                                                        ; вертикальная координата
ClipCodes       db #00                                                          ; составной байт кодов отсечения
                ends
                assert FProjectedPoint == #05

                ; -----------------------------------------
                ; физическая запись бинарного вызова на стеке выражений языка
                ; экземпляры создаются во время исполнения, статическая память не выделяется
                ; CallExpression читает запись от HL' минус её размер
                ; -----------------------------------------
                struct FExpressionCall
Left            dw #0000                                                        ; левый операнд, передаваемый в DE
Handler         dw #0000                                                        ; адрес обработчика, вызываемого через JP (HL)
Right           dw #0000                                                        ; правый операнд, передаваемый в BC
                ends
                assert FExpressionCall == #06

                ; -----------------------------------------
                ; физическая запись диспетчера торгового языка, шаг поиска равен трём байтам
                ; экземпляры находятся в ScriptTokens, один символ может встречаться в разных подтаблицах
                ; -----------------------------------------
                struct FScriptToken
Symbol          db #00                                                          ; ASCII-код символа команды, операции или суффикса
Handler         dw #0000                                                        ; исходный адрес обработчика в модуле языка
                ends
                assert FScriptToken == #03

                struct FScriptModeByte
Value           db #00                                                          ; полный байтовый режим, публичные операции записывают 0 или 1
                ends
                assert FScriptModeByte == 1

                struct FScriptGroupStart
Marker          db #FF                                                          ; разделитель первого поиска CPIR
                ends
                assert FScriptGroupStart == 1

                struct FScriptRecordStart
Marker          db #FE                                                          ; разделитель второго поиска CPIR и база смещения
                ends
                assert FScriptRecordStart == 1

                struct FScriptResourceSelection
GroupCount      db #00                                                          ; число поисков разделителя групп #FF, ноль задаёт 256 поисков
RecordCount     db #00                                                          ; число поисков разделителя записей #FE, ноль задаёт 256 поисков
                ends
                assert FScriptResourceSelection == 2

                ; -----------------------------------------
                ; состояние фазы вступления, три исходных слова обновляет AdvanceParameters
                ; знак Phase выбирает прибавление либо вычитание StepDelta из Step
                ; -----------------------------------------
                struct FTexturePhase
Phase           dw #0000                                                        ; накопленная фаза, старший байт используется как смещение
Step            dw #0000                                                        ; приращение фазы на следующем обновлении
StepDelta       dw #0000                                                        ; изменение приращения, знак действия выбирается по Phase
                ends
                assert FTexturePhase == #06

                ; -----------------------------------------
                ; исходная запись двух этапов рисования глифа
                ; -----------------------------------------
                struct FGlyphRoute
First           dw #0000                                                        ; цель первого участка, до границы знакоместа либо все восемь строк
AfterWrap       dw #0000                                                        ; цель оставшихся строк после перехода, ноль для Y кратного восьми
                ends
                assert FGlyphRoute == #04

                ; -----------------------------------------
                ; физический кадр CPU-стека DrawGlyph, создаётся последовательностью PUSH
                ; порядок полей соответствует POP общего выхода, адрес возврата находится последним
                ; -----------------------------------------
                struct FGlyphFrame
SavedAFAlt      dw #0000                                                        ; исходный альтернативный AF
SavedHLAlt      dw #0000                                                        ; исходный альтернативный HL
SavedBCAlt      dw #0000                                                        ; исходный альтернативный BC
SavedDEAlt      dw #0000                                                        ; исходный альтернативный DE
SavedHL         dw #0000                                                        ; исходный основной HL
SavedBC         dw #0000                                                        ; исходный основной BC
SavedDE         dw #0000                                                        ; исходный основной DE
ReturnAddress   dw #0000                                                        ; адрес возврата исходного вызова DrawGlyph
                ends
                assert FGlyphFrame == #10

                ; -----------------------------------------
                ; физический кадр DrawCenteredItem, создан существующими PUSH и EX (SP),HL
                ; -----------------------------------------
                struct FCenteredItemFrame
Workspace       dw #0000                                                        ; рабочее слово индекса, указателя Flags и затем адреса карты
SavedBC         dw #0000                                                        ; исходный BC
SavedDE         dw #0000                                                        ; исходный DE
SavedHL         dw #0000                                                        ; исходный индекс элемента в HL
ReturnAddress   dw #0000                                                        ; адрес возврата исходного вызова
                ends
                assert FCenteredItemFrame == #0A

                ; -----------------------------------------
                ; физический кадр CPU-стека, создаваемый исходными PUSH
                ; -----------------------------------------
                struct FCaptionItemFrame
Workspace       dw #0000                                                        ; рабочее слово индекса, указателя Height и адреса карты
SavedBC         dw #0000                                                        ; исходный BC
SavedDE         dw #0000                                                        ; исходный DE
SavedHL         dw #0000                                                        ; исходный индекс в HL
SavedBCAlt      dw #0000                                                        ; исходный альтернативный BC
ReturnAddress   dw #0000                                                        ; адрес возврата рисователя элемента
                ends
                assert FCaptionItemFrame == #0C

                ; -----------------------------------------
                ; физический кадр CPU-стека, создаваемый исходными PUSH
                ; -----------------------------------------
                struct FBandWaitFrame
SavedHLAlt      dw #0000                                                        ; альтернативный HL перед HALT
SavedDEAlt      dw #0000                                                        ; альтернативный DE перед HALT
SavedHL         dw #0000                                                        ; исходный основной HL
ReturnAddress   dw #0000                                                        ; адрес возврата обёртки полосовой рамки
                ends
                assert FBandWaitFrame == #08

                ; -----------------------------------------
                ; двухбайтовая запись списка рисования, создаётся и переставляется во время работы
                ; старший байт Handler равный единице обозначает ограничитель
                ; -----------------------------------------
                struct FDrawListEntry
Handler         dw #0000                                                        ; указатель обёртки рисования в младшем порядке
                ends
                assert FDrawListEntry == #02

                ; -----------------------------------------
                ; динамический кадр CPU-стека исходного переноса записи рисования
                ; -----------------------------------------
                struct FDrawMoveFrame
Candidate       dw #0000                                                        ; входной указатель новой обёртки
SavedBC         dw #0000                                                        ; исходный BC
SavedDE         dw #0000                                                        ; искомый индекс в DE
ReturnAddress   dw #0000                                                        ; адрес возврата MoveItemToTail
                ends
                assert FDrawMoveFrame == #08

                ; -----------------------------------------
                ; динамический кадр CPU-стека исходного переноса записи рисования
                ; -----------------------------------------
                struct FDrawShiftFrame
FoundHandler    dw #0000                                                        ; существующий обработчик с совпавшим индексом
SearchKey       dw #0000                                                        ; искомое слово индекса
NextEntry       dw #0000                                                        ; позиция списка после найденного указателя
                ends
                assert FDrawShiftFrame == #06

                ; -----------------------------------------
                ; динамический кадр восстановления геометрии, создан PUSH после переноса списка
                ; -----------------------------------------
                struct FRestoreBoundsFrame
SavedIX         dw #0000                                                        ; исходный IX
SavedBC         dw #0000                                                        ; исходный BC
SelectedHandler dw #0000                                                        ; выбранный обработчик списка
ReturnAddress   dw #0000                                                        ; адрес возврата RestoreItemBounds
                ends
                assert FRestoreBoundsFrame == #08

                ; -----------------------------------------
                ; динамический CPU-кадр SuspendPointer и ResumePointer, после пяти PUSH
                ; физический экземпляр возникает на текущем SP, отдельная память не выделяется
                ; -----------------------------------------
                struct FPointerGuardFrame
SavedBC         dw #0000                                                        ; исходный BC по смещению 0
SavedDE         dw #0000                                                        ; исходный DE по смещению 2
SavedHL         dw #0000                                                        ; исходный HL по смещению 4
SavedAF         dw #0000                                                        ; исходный AF по смещению 6
SavedIX         dw #0000                                                        ; исходный IX по смещению 8
ReturnAddress   dw #0000                                                        ; адрес возврата по смещению 10
                ends
                assert FPointerGuardFrame == #0C

                ; физическая строка одной фазы AND/XOR-указателя, исходный порядок байтов
                struct FPointerRasterRow
MaskLeft        db #00                                                          ; AND-маска левого экранного байта
XorLeft         db #00                                                          ; XOR левого экранного байта после AND
MaskRight       db #00                                                          ; AND-маска правого экранного байта
XorRight        db #00                                                          ; XOR правого экранного байта после AND
                ends
                assert FPointerRasterRow == #04

                ; физическая запись сохранённого фона, включая правый байт при отсечении рисунка
                struct FPointerSavedRow
Left            db #00                                                          ; исходный левый байт экранной строки
Right           db #00                                                          ; исходный правый байт экранной строки
                ends
                assert FPointerSavedRow == #02

                ; динамический кадр ToggleItemFrame, создаётся исходными PUSH
                struct FToggleItemFrame
SavedDE         dw #0000                                                        ; входной индекс элемента
SavedBC         dw #0000                                                        ; исходный BC
SavedHL         dw #0000                                                        ; исходный HL
ReturnAddress   dw #0000                                                        ; адрес возврата переключателя
                ends
                assert FToggleItemFrame == #08

                ; динамический кадр закрытия активного элемента, создан исходными PUSH
                struct FActiveCloseFrame
SavedHL         dw #0000                                                        ; входной HL, восстанавливается поверх результата callback
SavedDE         dw #0000                                                        ; входной DE, активный индекс загружается отдельно
ReturnAddress   dw #0000                                                        ; адрес возврата CloseActiveItem
                ends
                assert FActiveCloseFrame == #06

                ; динамический кадр ToggleItemBounds после двух PUSH DE
                struct FBoundsToggleFrame
WorkspaceIndex  dw #0000                                                        ; временный индекс, снимается в HL до расчёта смещения
SavedIndex      dw #0000                                                        ; исходный DE-индекс, возвращается при обоих выходах
ReturnAddress   dw #0000                                                        ; адрес возврата исходного действия
                ends
                assert FBoundsToggleFrame == #06

                ; динамический кадр XOR-контура, временные признаки отсечения находятся в DE'
                struct FOutlineFrame
SavedDEAlt      dw #0000                                                        ; исходный альтернативный DE перед использованием признаков отсечения
SavedDE         dw #0000                                                        ; исходные размеры в знакоместах
SavedBC         dw #0000                                                        ; исходные знаковые координаты в знакоместах
ReturnAddress   dw #0000                                                        ; адрес возврата XorRectOutline
                ends
                assert FOutlineFrame == #08

                ; Динамический кадр писателя XOR-полосы, создаётся исходным PUSH HL.
                struct FOutlineSpanFrame
SavedHL         dw #0000                                                        ; HL, восстанавливаемый после инверсии полосы
ReturnAddress   dw #0000                                                        ; адрес возврата после сохранённого HL
                ends
                assert FOutlineSpanFrame == #04
                assert FOutlineSpanFrame.SavedHL == 0
                assert FOutlineSpanFrame.ReturnAddress == 2

                ; динамический кадр удаления обработчика, создаётся исходными PUSH
                struct FRemoveDrawFrame
SavedBC         dw #0000                                                        ; исходный BC
SavedDE         dw #0000                                                        ; искомый индекс в DE
SavedHL         dw #0000                                                        ; исходный HL
SavedIX         dw #0000                                                        ; исходный IX
ReturnAddress   dw #0000                                                        ; адрес возврата RemoveItemDraw
                ends
                assert FRemoveDrawFrame == #0A

                ; динамические слова интерактивного действия, отдельная RAM не выделяется
                struct FGeometryHitFrame
ClickCell       dw #0000                                                        ; знакоместо попадания, B строка и C колонка
Record          dw #0000                                                        ; физическое начало FInterfaceItem
                ends
                assert FGeometryHitFrame == #04

                ; динамические слова интерактивного действия, отдельная RAM не выделяется
                struct FGeometryDragFrame
Anchor          dw #0000                                                        ; относительная точка перемещения либо абсолютная точка изменения размера
ClickCell       dw #0000                                                        ; исходное знакоместо попадания
Record          dw #0000                                                        ; физическое начало FInterfaceItem
                ends
                assert FGeometryDragFrame == #06

                ; динамические слова интерактивного действия, отдельная RAM не выделяется
                struct FGeometryWaitFrame
CenterXY        dw #0000                                                        ; центральная пиксельная точка измерения дельты
Size            dw #0000                                                        ; текущие размеры D,E
Origin          dw #0000                                                        ; текущие координаты B,C
                ends
                assert FGeometryWaitFrame == #06

                ; динамические слова интерактивного действия, отдельная RAM не выделяется
                struct FGeometryPreview
Size            dw #0000                                                        ; размеры либо временное слово сохраняемого DE
Origin          dw #0000                                                        ; позиция B,C после расчёта либо перед обратным XOR
                ends
                assert FGeometryPreview == #04

                ; динамический кадр начала скрытого обновления, создан исходными PUSH
                struct FScreenUpdateFrame
SavedBC         dw #0000                                                        ; исходный BC
SavedDE         dw #0000                                                        ; исходный DE
SavedHL         dw #0000                                                        ; исходный HL
ReturnAddress   dw #0000                                                        ; адрес возврата BeginScreenUpdate
                ends
                assert FScreenUpdateFrame == #08

                struct FRepaintFrame
SavedAF         dw #0000                                                        ; селектор и флаги после OR A
SavedDE         dw #0000                                                        ; исходный индекс выбранного элемента
SavedIX         dw #0000                                                        ; исходный IX вызывающей стороны
ReturnAddress   dw #0000                                                        ; возврат исходного вызова
                ends
                assert FRepaintFrame == #08

                struct FRepaintChain
DrawHandler     dw #0000                                                        ; первый возврат BeginScreenUpdate, вход рисователя
AfterDraw       dw #0000                                                        ; возврат рисователя, завершение экранного цикла
                ends
                assert FRepaintChain == #04

                struct FMouseInput
Action2         db #00                                                          ; действие с весом 2 в MergeActionInputs
Up              db #00                                                          ; направление уменьшения экранного Y
Down            db #00                                                          ; направление увеличения экранного Y
Right           db #00                                                          ; направление увеличения экранного X
Left            db #00                                                          ; направление уменьшения экранного X
Action1         db #00                                                          ; действие с весом 1 в MergeActionInputs
ExtraButton     db #00                                                          ; третий разряд кнопок
PreviousX       db #00                                                          ; прежнее значение аппаратного счётчика X
PreviousY       db #00                                                          ; прежнее значение аппаратного счётчика Y
                ends
                assert FMouseInput == #09

                struct FMousePollFrame
SavedIX         dw #0000                                                        ; исходный IX вызывающей стороны
ReturnAddress   dw #0000                                                        ; возврат полного PollMouse
                ends
                assert FMousePollFrame == #04

                struct FInputFlags
Right           db #00                                                          ; накопленное движение вправо
Left            db #00                                                          ; накопленное движение влево
Down            db #00                                                          ; накопленное движение вниз
Up              db #00                                                          ; накопленное движение вверх
Action2         db #00                                                          ; накопленное действие с весом 2
Action1         db #00                                                          ; накопленное действие с весом 1
                ends
                assert FInputFlags == #06

                struct FPointerDirection
Handler         dw #00                                                          ; адрес исходного обработчика одного сочетания направлений
                ends
                assert FPointerDirection == #02

                struct FKeyBinding
RowMask         db #00                                                          ; старший байт порта клавиатуры, младший равен FE
KeyMask         db #00                                                          ; проверяемые разряды строки, нажатие при нуле всех разрядов
                ends
                assert FKeyBinding == #02

                struct FStationBcdCounter
MidHigh         db #00                                                          ; третья пара цепочки, перенос от MidLow
High            db #00                                                          ; старшая четвёртая пара, конечный перенос теряется
MidLow          db #00                                                          ; вторая пара цепочки, перенос от Low
Low             db #00                                                          ; первая пара, увеличивается при достижении нуля делителя
                ends
                assert FStationBcdCounter == #04

                struct FStationIrqStorage
Scratch00       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch01       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch02       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch03       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch04       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch05       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch06       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch07       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch08       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch09       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch10       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch11       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
Scratch12       dw #00                                                          ; временное слово вложенных вызовов ISR, содержимое зависит от активного кадра
SavedPage       dw #00                                                          ; сохранённое слово Page исходного CPU-контекста
SavedBCAlt      dw #00                                                          ; сохранённое слово BCAlt исходного CPU-контекста
SavedDEAlt      dw #00                                                          ; сохранённое слово DEAlt исходного CPU-контекста
SavedHLAlt      dw #00                                                          ; сохранённое слово HLAlt исходного CPU-контекста
SavedAFAlt      dw #00                                                          ; сохранённое слово AFAlt исходного CPU-контекста
SavedBC         dw #00                                                          ; сохранённое слово BC исходного CPU-контекста
SavedDE         dw #00                                                          ; сохранённое слово DE исходного CPU-контекста
SavedHL         dw #00                                                          ; сохранённое слово HL исходного CPU-контекста
SavedAF         dw #00                                                          ; сохранённое слово AF исходного CPU-контекста
SavedIY         dw #00                                                          ; сохранённое слово IY исходного CPU-контекста
SavedIX         dw #00                                                          ; сохранённое слово IX исходного CPU-контекста
                ends
                assert FStationIrqStorage == #30

                struct FWindowReturnChain
InterruptPC     dw #00                                                          ; слово аппаратного PC при IRQ до первого RET
Row1            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row2            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row3            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row4            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row5            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row6            dw #00                                                          ; возврат к следующей пиксельной строке группы
Row7            dw #00                                                          ; возврат к следующей пиксельной строке группы
AfterGroup      dw #00                                                          ; возврат после восьмой строки к переходу знакоместа
TailWord        dw #00                                                          ; дополнительное исходное слово A0B6, цикл восьми RET не читает
                ends
                assert FWindowReturnChain == #14

                struct FMatrixKeyFrame
SavedDE         dw #0000                                                        ; исходный DE вызывающей стороны
SavedHL         dw #0000                                                        ; исходный HL вызывающей стороны
SavedBC         dw #0000                                                        ; исходный BC вызывающей стороны
ReturnAddress   dw #0000                                                        ; возврат исходного вызова ReadMatrixKey
                ends
                assert FMatrixKeyFrame == #08

                struct FSettingWord
ValueOrRow      db #00                                                          ; значение 0..126, маркер 80/81 либо строка матрицы
KeyMask         db #00                                                          ; маска только для строки матрицы, иначе не читается
                ends
                assert FSettingWord == #02

                struct FPopupScanFrame
SavedPosition   dw #0000                                                        ; адрес текущего указателя на время проверки группы
ReturnAddress   dw #0000                                                        ; исходный возврат RemoveOtherPopups
                ends
                assert FPopupScanFrame == #04

                struct FRebuildDrawFrame
AfterDraw       dw #0000                                                        ; возврат RET рисователя в локальный RebuildInterface.AfterDraw
NextPointer     dw #0000                                                        ; адрес следующей пары списка после возврата рисователя
                ends
                assert FRebuildDrawFrame == #04

                struct FDispatchSelectedFrame
ReturnCleanup   dw #0000                                                        ; аппаратный возврат RemoveOtherPopups в DispatchInterfaceEvent
SavedIndexDE    dw #0000                                                        ; выбранный индекс, восстанавливаемый в DE
SavedIndexHL    dw #0000                                                        ; та же исходная копия индекса для поиска записи
SavedAF         dw #0000                                                        ; кодированное событие и флаги до поиска владельца
ReturnAddress   dw #0000                                                        ; возврат вызывающей стороны диспетчера
                ends
                assert FDispatchSelectedFrame == #0A

                struct FRandomState
LowWord         dw #0000                                                        ; младшее слово, возвращаемое генератором после шага
HighByte        db #00                                                          ; отдельный старший байт накопления переносов и заёмов
                ends
                assert FRandomState == #03

                struct FSignatureKey
FirstWord       dw #0000                                                        ; первое слово шага, после обновления получает прежнее второе
SecondWord      dw #0000                                                        ; второе слово шага с байтовым смешиванием
                ends
                assert FSignatureKey == #04

                struct FSignatureInput
FirstWord       dw #0000                                                        ; первый числовой ключ и два байта геометрического классификатора
SecondWord      dw #0000                                                        ; второй числовой ключ, младшее слово начального состояния рынка
Variant         db #00                                                          ; число дополнительных шагов 0..255, всего выполняется 1..256
                ends
                assert FSignatureInput == #05


                struct FMarketRule
BasePrice       db #00                                                          ; исходная цена до случайного колебания и скидки
StockRule       db #00                                                          ; числовой код выбора маски случайного запаса, не независимые флаги
                ends
                assert FMarketRule == #02

                struct FMarketRow
StockAndSaleBan db #00                                                          ; bit7 запрет продажи со штрафом, bits6..0 количество
Price           db #00                                                          ; текущая цена после колебания, категорийной поправки и скидки
                ends
                assert FMarketRow == #02


                struct FFieldInvokeFrame
Operator        dw #0000                                                        ; адрес оператора, снимается POP DE
AfterStore      dw #0000                                                        ; возврат после сохранения целевого поля
                ends
                assert FFieldInvokeFrame == #04

                struct FFieldOperatorFrame
StoreReturn     dw #0000                                                        ; адрес Store, заменивший слово Operator
AfterStore      dw #0000                                                        ; тот же исходный возврат после записи
                ends
                assert FFieldOperatorFrame == #04


                struct FIndexedOperatorFrame
StoreReturn     dw #0000                                                        ; возврат оператора в Store
SavedTarget     dw #0000                                                        ; захваченный адрес целевого байта
AfterStore      dw #0000                                                        ; продолжение вызывающего после записи
                ends
                assert FIndexedOperatorFrame == #06

                struct FIndexedStoreFrame
SavedTarget     dw #0000                                                        ; адрес цели после RET оператора
AfterStore      dw #0000                                                        ; продолжение после сохранения
                ends
                assert FIndexedStoreFrame == #04


                ; физические десять слов после таблицы токенов, проверки переполнения стека нет
                struct FExpressionStackStorage
Word00          dw #0000
Word01          dw #0000
Word02          dw #0000
Word03          dw #0000
Word04          dw #0000
Word05          dw #0000
Word06          dw #0000
Word07          dw #0000
Word08          dw #0000
Word09          dw #0000
                ends
                assert FExpressionStackStorage == #14

                struct FAssignmentExpression
Writer          dw #0000                                                        ; статический Invoke выбранного писателя поля
Operator        dw #0000                                                        ; адрес бинарного оператора из таблицы
Right           dw #0000                                                        ; правое значение, передаваемое в BC
                ends
                assert FAssignmentExpression == #06

                struct FAssignmentNestedTail
Operator        dw #0000                                                        ; адрес оператора внутри скобок
Right           dw #0000                                                        ; правый операнд внутри скобок
                ends
                assert FAssignmentNestedTail == #04
                assert FAssignmentNestedTail.Operator == 0
                assert FAssignmentNestedTail.Right == 2

                ; физическая рамка четырёх сохраняемых пар и возврата вычислителя расстояния
                struct FMapDistanceFrame
SavedHLAlt      dw #0000                                                        ; сохранённый HL альтернативного набора на вершине кадра
SavedIY         dw #0000                                                        ; исходный IY
SavedIX         dw #0000                                                        ; исходный IX
SavedHL         dw #0000                                                        ; исходный основной HL
ReturnAddress   dw #0000                                                        ; возврат исходному вызывающему
                ends
                assert FMapDistanceFrame == #0A

                ; исходная двухбайтовая запись порога ранга со старшим байтом вперёд
                struct FRankThreshold
HighByte        db #00                                                          ; старшие восемь разрядов беззнакового порога
LowByte         db #00                                                          ; младшие восемь разрядов порога
                ends
                assert FRankThreshold == #02

                ; физическое состояние предложения, четыре промежуточных слова условно читаются CenterContractMap, исходное назначение не установлено
                struct FMissionOfferState
FirstWord       dw #0000                                                        ; первое слово предлагаемого ключа
SecondWord      dw #0000                                                        ; второе слово предлагаемого ключа
UnknownWord04   dw #0000                                                        ; при Cursor=99A4 первое слово ключа CenterContractMap, исходное назначение неизвестно
UnknownWord06   dw #0000                                                        ; при Cursor=99A4 второе слово ключа CenterContractMap, исходное назначение неизвестно
UnknownWord08   dw #0000                                                        ; при Cursor=99A5 первое слово ключа CenterContractMap, исходное назначение неизвестно
UnknownWord0A   dw #0000                                                        ; при Cursor=99A5 второе слово ключа CenterContractMap, исходное назначение неизвестно
Reward          dw #0000                                                        ; младшее слово произведения вознаграждения
RequiredTonnage db #00                                                          ; принятый требуемый тоннаж
MessageIndex   db #00                                                          ; числовой селектор сообщения расшифровки, генератор записывает 0
                ends
                assert FMissionOfferState == #10

                ; исходный сохранённый кадр нажатия миссии, ReturnAddress остаётся от исходного вызывающего
                struct FMissionActionFrame
SavedIY         dw #0000                                                        ; последняя сохранённая пара на вершине кадра
SavedIX         dw #0000                                                        ; исходный IX
SavedAF         dw #0000                                                        ; AF после проверки кода 1
SavedBC         dw #0000                                                        ; контекст BC перед действием
SavedHL         dw #0000                                                        ; контекст HL перед сравнением ключей
SavedDE         dw #0000                                                        ; контекст DE перед действием
ReturnAddress   dw #0000                                                        ; исходный возврат вызывающему диспетчер
                ends
                assert FMissionActionFrame == #0E

                ; физическая запись сохранённого ключа, Variant задаёт порядковый вариант ключа
                struct FStoredMapPoint
FirstWord       dw #0000
SecondWord      dw #0000
Variant         db #00
                ends
                assert FStoredMapPoint == #05

                ; кадр внешнего построителя секторных таблиц, PUSH DE, HL, BC
                struct FMapSectorTablesFrame
SavedBC         dw #0000
SavedHL         dw #0000
SavedDE         dw #0000
ReturnAddress   dw #0000
                ends
                assert FMapSectorTablesFrame == #08

                ; максимальный временный кадр рисователя точки, все слова снимаются до первого RET
                struct FMapPointMarkerFrame
SavedOriginY    dw #0000
SavedPointY     dw #0000
SavedSpriteBase dw #0000
ReturnAddress   dw #0000
                ends
                assert FMapPointMarkerFrame == #08

                ; физическое служебное поле и десять байтов плотных смещений второго списка
                ; Layout, схема разрядов 7..0
                ; Unknown Unknown Mode1 Mode0 N3 N2 N1 N0
                ; режим 00 Clear, 01 Set, 10 и 11 Xor, N=0 не рисует цепочку
                struct FStoredMapOrder
Layout          db #00
Order00         db #00
Order01         db #00
Order02         db #00
Order03         db #00
Order04         db #00
Order05         db #00
Order06         db #00
Order07         db #00
Order08         db #00
Order09         db #00
                ends
                assert FStoredMapOrder == #0B

                ; базовый кадр обычного поиска строки, сохранённый BC уже содержит C=исходный Y
                struct FBoundedRasterSeekFrame
SavedBC         dw #0000
SavedAF         dw #0000
ReturnAddress   dw #0000
                ends
                assert FBoundedRasterSeekFrame == #06


                ; физическое 32-битное произведение, слова следуют от младшего к старшему
                struct FClipProduct
LowWord         dw #0000
HighWord        dw #0000
                ends
                assert FClipProduct == #04

                ; двухбайтовая выходная точка после преобразования пересечения
                struct FClipOutputPoint
X               db #00
Y               db #00
                ends
                assert FClipOutputPoint == #02

                ; снимаемые слова специального выхода, не кадр обычного вызова помощника
                struct FClipUnwindFrame
FirstWord       dw #0000
SecondWord      dw #0000
ThirdWord       dw #0000
ReturnAddress   dw #0000
                ends
                assert FClipUnwindFrame == #08

                ; физическое состояние углов, старшая тетрада SeenFlags ещё не разобрана
                struct FClipCornerState
SeenFlags       db #00
BlockCode       db #00
                ends
                assert FClipCornerState == #02

                ; внешний кадр дуги, MapState.RasterStack указывает на сохранённый AF
                struct FArcReturnFrame
SavedAF         dw #0000
ReturnAddress   dw #0000
                ends
                assert FArcReturnFrame == #04

                ; байты команд, устанавливаемые вызывающим кодом перед рисованием линии
                struct FMapLineMode
PixelOpcode     db #00
ByteCrossOpcode db #00
                ends
                assert FMapLineMode == #02

                ; восемь значений маски для фазы относительного X от 0 до 7
                struct FMapLineMaskSet
Phase0          db #00
Phase1          db #00
Phase2          db #00
Phase3          db #00
Phase4          db #00
Phase5          db #00
Phase6          db #00
Phase7          db #00
                ends
                assert FMapLineMaskSet == #08

                ; физическое состояние DFAB..DFC2, значения экземпляра сохраняются отдельно
                struct FMapArcWorkspace
AbsY            db #00                                                          ; младший байт модуля оборачиваемого смещения Y
AbsX            db #00                                                          ; младший байт модуля оборачиваемого смещения X
QuadrantCode    db #00                                                          ; биты 0 и 1 знаков разностей, биты 7..2 ещё не установлены
Radius          db #00                                                          ; байтовый радиус, рассчитанный вызывающим кодом
OffsetY         db #00                                                          ; текущее смещение Y после подготовки диспетчером
OffsetX         db #00                                                          ; текущее смещение X после подготовки диспетчером
RowY            db #00                                                          ; относительная исходная строка растровой подготовки
CenterX         db #00                                                          ; относительный центр симметричной подготовки
StartY          db #00                                                          ; сохранённый результат корня для отсечённого начала
RasterStack     dw #0000                                                        ; SP внешнего кадра AF и адреса возврата
SqrtTarget      dw #0000                                                        ; оборачиваемая разность квадратов для пробных битов корня
LeftMask        db #00                                                          ; сохранённый B помощника правого края
RasterDown      db #00                                                          ; код направления, ноль вверх, ненулевое значение вниз
UpperRow        dw #0000                                                        ; адрес включённой верхней строки без колонки
LowerRow        dw #0000                                                        ; адрес исключённой нижней строки без колонки
MaxY            db #00                                                          ; параметр MaxY установщика для крайней строки
ReferenceX      db #00                                                          ; опорный X, установщик записывает HalfX
HalfY           db #00                                                          ; половина Y с исходным переносом от HalfX-2
HalfXLimit      db #00                                                          ; половина X для предела горизонтального счётчика
HalfXSquare     db #00                                                          ; половина X для аргументов квадратов и корней
                ends
                assert FMapArcWorkspace == #18

                ; семь пар экранных байтов фазы маркера и два исходных конечных байта
                struct FMapMarkerPhase
Row0Left        db #00                                                          ; первый байт строки 0 семистрочного маркера
Row0Right       db #00                                                          ; второй смежный байт строки 0 семистрочного маркера
Row1Left        db #00                                                          ; первый байт строки 1 семистрочного маркера
Row1Right       db #00                                                          ; второй смежный байт строки 1 семистрочного маркера
Row2Left        db #00                                                          ; первый байт строки 2 семистрочного маркера
Row2Right       db #00                                                          ; второй смежный байт строки 2 семистрочного маркера
Row3Left        db #00                                                          ; первый байт строки 3 семистрочного маркера
Row3Right       db #00                                                          ; второй смежный байт строки 3 семистрочного маркера
Row4Left        db #00                                                          ; первый байт строки 4 семистрочного маркера
Row4Right       db #00                                                          ; второй смежный байт строки 4 семистрочного маркера
Row5Left        db #00                                                          ; первый байт строки 5 семистрочного маркера
Row5Right       db #00                                                          ; второй смежный байт строки 5 семистрочного маркера
Row6Left        db #00                                                          ; первый байт строки 6 семистрочного маркера
Row6Right       db #00                                                          ; второй смежный байт строки 6 семистрочного маркера
UnknownTail0    db #00                                                          ; конечный байт фазы, этот рисователь не читает, глобальное назначение неизвестно
UnknownTail1    db #00                                                          ; конечный байт фазы, этот рисователь не читает, глобальное назначение неизвестно
                ends
                assert FMapMarkerPhase == #10

                ; общие управляющие коды по 99A3, отдельный отрицательный ограничитель сюда не входит
                struct FMapMarkerCodes
ActiveCode      db #00                                                          ; код состояния миссии, карта рисует при любом положительном значении
CompletionCode  db #00                                                          ; код повторной награды миссии, одновременно второй управляющий код карты
Unknown02       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown03       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown04       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown05       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown06       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown07       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown08       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown09       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
Unknown10       db #00                                                          ; карта читает как числовой код, остальные роли не установлены
                ends
                assert FMapMarkerCodes == #0B

                ; два слова координатного ключа без пятого байта варианта
                struct FMapCoordinateKey
FirstWord       dw #0000                                                        ; старшие байты мировых координат X и Y
SecondWord      dw #0000                                                        ; младшие байты мировых координат X и Y
                ends
                assert FMapCoordinateKey == #04

                ; пиксельные смещения циклической траектории, арифметика по модулю 256
                struct FMapPathPoint
OffsetX         db #00                                                          ; знаковое смещение X относительно общего начала вариантов
OffsetY         db #00                                                          ; знаковое смещение Y относительно общего начала вариантов
                ends
                assert FMapPathPoint == #02

                ; три строки двухбайтовой фазы спрайта варианта
                struct FMapVariantPhase
Row0Left        db #00                                                          ; первый байт строки 0 спрайта варианта
Row0Right       db #00                                                          ; второй смежный байт строки 0 спрайта варианта
Row1Left        db #00                                                          ; первый байт строки 1 спрайта варианта
Row1Right       db #00                                                          ; второй смежный байт строки 1 спрайта варианта
Row2Left        db #00                                                          ; первый байт строки 2 спрайта варианта
Row2Right       db #00                                                          ; второй смежный байт строки 2 спрайта варианта
                ends
                assert FMapVariantPhase == #06

                ; динамический кадр переключения двух контуров после PUSH DE
                struct FItemContourFrame
SavedNewIndex   dw #0000                                                        ; новый индекс, временно сохранённый до завершения первого рисунка
ReturnAddress   dw #0000                                                        ; исходный адрес возврата вызывающей процедуры
                ends
                assert FItemContourFrame == #04

                ; динамический кадр периодического обновления после сохранения начала панели
                struct FVariantUpdateFrame
SavedOriginXY   dw #0000                                                        ; символьные X,Y панели на время заливки внутреннего тела
SavedCountAF    dw #0000                                                        ; количество вариантов и точные флаги его вычисления
ReturnAddress   dw #0000                                                        ; исходный адрес возврата главного цикла
                ends
                assert FVariantUpdateFrame == #06

                ; динамический кадр проверки списка после PUSH DE и PUSH HL
                struct FListedItemMoveFrame
SavedHL         dw #0000                                                        ; кандидат новой обёртки до проверки существования DrawHandler
SavedDE         dw #0000                                                        ; исходный индекс выбранной записи FInterfaceItem
ReturnAddress   dw #0000                                                        ; исходный адрес возврата вызывающего кода
                ends
                assert FListedItemMoveFrame == #06

                ; Динамические кадры описывают уже существующие PUSH, постоянная память не выделяется.
                struct FSecondaryInsertFrame
SavedAddress    dw #0000                                                        ; адрес Insert до поиска, затем адрес Hole перед LDDR
ReturnAddress   dw #0000                                                        ; исходный адрес возврата вызывающего действия
                ends
                assert FSecondaryInsertFrame == #04

                struct FSecondaryDeleteFrame
NextRecord      dw #0000                                                        ; адрес следующей записи, источник физического сдвига
RemovedRecord   dw #0000                                                        ; начало удаляемой записи, приёмник физического сдвига
ReturnAddress   dw #0000                                                        ; исходный адрес возврата вызывающего действия
                ends
                assert FSecondaryDeleteFrame == #06


                struct FScrollExitFrame
SavedPointerXY  dw #0000                                                        ; сохранённые X в младшем байте и Y в старшем
ReturnAddress   dw #0000                                                        ; исходный возврат, расположенный после пары координат
                ends
                assert FScrollExitFrame == #04

                struct FScrollDrawFrame
SavedIndex      dw #0000                                                        ; принятый индекс перед очисткой и перед callback
SavedViewport   dw #0000                                                        ; BC, C содержит фиксированную высоту просмотра в строках
SavedPointerXY  dw #0000                                                        ; нижняя часть FScrollExitFrame с исходными X и Y
ReturnAddress   dw #0000                                                        ; исходный адрес возврата вызывающей процедуры
                ends
                assert FScrollDrawFrame == #08

                ; начальные индексы ценового рынка для одного числового уровня системы
                struct FModelAvailability
ShipBase        db #00                                                          ; начальный индекс кораблей 0..5, ноль открывает все шесть рыночных строк
SkimmerBase     db #00                                                          ; начальный индекс скимеров 0..3, ноль открывает все четыре строки
                ends
                assert FModelAvailability == #02

                ; физический узел очереди D3D, поля записываются от конца через рабочий SP
                struct FPreviewQueueNode
Next            db #00                                                          ; младший индекс следующей записи, 1 завершает активную цепочку
Flags           db #00                                                          ; бит 7 выбирает второй ключ сравнения, прочие разряды сохраняются
ModelOffset     db #00                                                          ; рабочее байтовое смещение указателя модели
AngleFirst      db #00                                                          ; первый исходный байтовый параметр ориентации
AngleSecond     db #00                                                          ; второй исходный байтовый параметр ориентации
AngleThird      db #00                                                          ; третий исходный байтовый параметр ориентации
FirstResult     dw #0000                                                        ; результат первой строки преобразования
SecondResult    dw #0000                                                        ; результат второй строки преобразования
ThirdResult     dw #0000                                                        ; результат третьей строки, первый ключ сравнения
SecondInput     dw #0000                                                        ; вторая исходная координата, второй ключ сравнения
                ends
                assert FPreviewQueueNode == #0E

                ; физические исходные данные PreviewSharedSeed
                struct FPreviewSharedSeed
InitialAngle0   db #00                                                          ; начальный первый угол Eye_a, копируется в AngleFirst до обхода записей
PlanarAngleBase db #00                                                          ; вычитаемый угловой отсчёт плоской модели, единица 1/256 оборота
InitialAngle2   db #00                                                          ; начальный третий угол Eye_g, копируется в AngleThird до обхода записей
                ends
                assert FPreviewSharedSeed == #03

                ; физические исходные данные PreviewSceneMatrix
                struct FPreviewSceneMatrix
Coeff11         dw #0000                                                        ; исходный коэффициент строки 1 при координате 1, проход использует старший байт
Coeff21         dw #0000                                                        ; исходный коэффициент строки 2 при координате 1, проход использует старший байт
Coeff31         dw #0000                                                        ; исходный коэффициент строки 3 при координате 1, проход использует старший байт
Coeff12         dw #0000                                                        ; исходный коэффициент строки 1 при координате 2, проход использует старший байт
Coeff22         dw #0000                                                        ; исходный коэффициент строки 2 при координате 2, проход использует старший байт
Coeff32         dw #0000                                                        ; исходный коэффициент строки 3 при координате 2, проход использует старший байт
Coeff13         dw #0000                                                        ; исходный коэффициент строки 1 при координате 3, проход использует старший байт
Coeff23         dw #0000                                                        ; исходный коэффициент строки 2 при координате 3, проход использует старший байт
Coeff33         dw #0000                                                        ; исходный коэффициент строки 3 при координате 3, проход использует старший байт
                ends
                assert FPreviewSceneMatrix == #12

                ; физические исходные данные PreviewModelPointers
                struct FPreviewModelPointers
BasePointer     dw #0000                                                        ; указатель модели при старшем байте третьего результата 31..127
AlternatePtr    dw #0000                                                        ; соседний указатель модели при старшем байте третьего результата 0..30
                ends
                assert FPreviewModelPointers == #04

                ; Документация [рабочий блок очереди](../../Docs/PreviewQueueBuild.md)
                struct FPreviewDrawState
Flags           db #00                                                          ; бит 0 одноосной ориентации, бит 7 второго ключа очереди, остальные биты в разобранном пути не используются
ModelOffset     db #00                                                          ; байтовое смещение выбранной пары либо соседнего указателя на странице D0
RawFirst        dw #0000                                                        ; последняя прочитанная первая координата записи, отдельные пути не обновляют последующие поля
RawSecond       dw #0000                                                        ; последняя прочитанная вторая координата записи
RawThird        dw #0000                                                        ; последняя прочитанная третья координата записи
Head            db #00                                                          ; индекс головы в странице C7, во время работы 1 означает конец, 0 является допустимым узлом
NextFree        db #00                                                          ; следующий свободный индекс в странице C7, шаг 14, заполненный пул имеет FC
                ends
                assert FPreviewDrawState == #0A

                ; Документация [заголовки и физические группы](../../Docs/PreviewModelGroups.md)
                struct FPreviewModelHeader
Size            db #00                                                          ; исходный размер модели, первый байт заголовка
ScaleFlags      db #00                                                          ; биты 6..0 показатель масштаба, бит 7 отдельный признак второго ключа
                ends
                assert FPreviewModelHeader == #02

                struct FPreviewVertexGroup
Mask            db #00                                                          ; маска комбинаций вершин 7..0, нуль является однобайтовым концом списка
ParamFirst      db #00                                                          ; первый байтовый параметр группы, вход B поставщика
ParamSecond     db #00                                                          ; второй байтовый параметр группы, вход C поставщика
ParamThird      db #00                                                          ; третий байтовый параметр группы, вход D поставщика
                ends
                assert FPreviewVertexGroup == #04

                ; Документация [пятибайтовая запись проекции](../../Docs/PreviewVertexClass.md)
                struct FPreviewProjectedVertex
SecondAxis      dw #0000                                                        ; слово второй координаты с центром HalfY
FirstAxis       dw #0000                                                        ; слово первой координаты с центром HalfX
Outcode         db #00                                                          ; код сторон, младшая тетрада прямая, старшая инверсная
                ends
                assert FPreviewProjectedVertex == #05

                ; Документация [физические параметры рёбер](../../Docs/PreviewEdgeRaster.md)
                struct FPreviewEdgeEndpoints
StartPoint      dw #0000                                                        ; начальное слово, младший байт колонка, старший строка
EndPoint        dw #0000                                                        ; конечное слово в том же формате
                ends
                assert FPreviewEdgeEndpoints == #04

                struct FPreviewEdgeMode
PixelOpcode     db #00                                                          ; байт пиксельной инструкции A1 для AND, A9 для XOR, B1 для OR
BoundaryOpcode  db #00                                                          ; байт перехода 30 для JR NC при AND, 38 для JR C при XOR и OR
                ends
                assert FPreviewEdgeMode == #02

                ; Документация [физические записи заливки](../../Docs/PreviewPolygonFill.md)
                struct FPreviewContourSize
ByteCount       db #00                                                          ; число байтов пар колонка и строка, рабочий профиль ненулевое чётное значение
                ends
                assert FPreviewContourSize == #01

                struct FPreviewFillMode
Index           db #00                                                          ; индекс пары внутренних шаблонов, крайние маски доказаны только для 0..4
                ends
                assert FPreviewFillMode == #01

                struct FPreviewFillPattern
Pattern         db #00                                                          ; первый шаблон внутренних байтов многоугольника
RowXor          db #00                                                          ; XOR шаблона при переходе к следующей строке контура
                ends
                assert FPreviewFillPattern == #02

                ; Документация [физические записи заливки](../../Docs/PreviewFaceStream.md)
                struct FPreviewFaceGateState
RejectCode      db #00                                                          ; нуль после принятой ориентации, один после отвергнутой, читатель проверяет весь байт
                ends
                assert FPreviewFaceGateState == #01

                ; Документация [физические записи](../../Docs/PreviewClipProducts.md)
                struct FPreviewClipProductWord
Word            dw #0000                                                        ; физическое слово разнесённого левого кэша, смысл младшего либо старшего задаётся именем экземпляра
                ends
                assert FPreviewClipProductWord == #02

                ; Документация [физические записи](../../Docs/PreviewClippedFaceStream.md)
                struct FPreviewLineCoordinates
PreviousColumn  dw #0000                                                        ; слово колонки предыдущего конца полилинии
PreviousRow     dw #0000                                                        ; слово строки предыдущего конца полилинии
CurrentColumn   dw #0000                                                        ; слово колонки очередного конца полилинии
                ends
                assert FPreviewLineCoordinates == #06

                struct FPreviewLineTail
CurrentRow      dw #0000                                                        ; слово строки очередного конца полилинии
PreviousCode    db #00                                                          ; полный код сторон предыдущего конца
CurrentCode     db #00                                                          ; полный код сторон очередного конца
                ends
                assert FPreviewLineTail == #04

                ; Документация [физические записи](../../Docs/PreviewQueueRender.md)
                struct FPreviewObjectAngles
First           db #00                                                          ; первый байтовый параметр ориентации объекта
Second          db #00                                                          ; второй байтовый параметр ориентации объекта
Third           db #00                                                          ; третий байтовый параметр ориентации объекта
                ends
                assert FPreviewObjectAngles == #03

                ; Документация [кэш строк HELP](../../Docs/HelpLineIndex.md)
                struct FHelpLinePointer
TextAddress     dw #0000                                                        ; начало строки в банке 7, ноль обозначает свободную запись
                ends
                assert FHelpLinePointer == #02

                ; Документация [обозначения клавиш](../../Docs/KeyLabels.md)
                struct FKeyAbbreviation
Glyph0          db #00                                                          ; код символа позиции 1 четырёхсимвольного обозначения
Glyph1          db #00                                                          ; код символа позиции 2 четырёхсимвольного обозначения
Glyph2          db #00                                                          ; код символа позиции 3 четырёхсимвольного обозначения
Glyph3          db #00                                                          ; код символа позиции 4 четырёхсимвольного обозначения
                ends
                assert FKeyAbbreviation == #04

                ; Документация [динамические кадры редактора настроек](../../Docs/SettingsPanelActions.md)
                struct FSettingsEditFrame
SavedIndex      dw #0000                                                        ; сохранённый индекс BC перед промежуточным рисунком
ValuePointer    dw #0000                                                        ; сохранённый HL изменяемого символа
ReturnAddress   dw #0000                                                        ; внешний обычный CPU-возврат действия
                ends
                assert FSettingsEditFrame == #06

                struct FSettingsWaitFrame
ValuePointer    dw #0000                                                        ; указатель символа, остающийся на стеке во время ввода
ReturnAddress   dw #0000                                                        ; внешний обычный CPU-возврат после снятия указателя
                ends
                assert FSettingsWaitFrame == #04

                ; Документация [кадры непрямого действия](../../Docs/PackedWordAndActionReturn.md)
                struct FActionDrawFrame
DrawReturn      dw #0000                                                        ; созданный адрес 7F30, снимается RET рисователя
SavedAF         dw #0000                                                        ; сохранённые F в младшем и A в старшем байте
ReturnAddress   dw #0000                                                        ; внешний обычный CPU-возврат действия
                ends
                assert FActionDrawFrame == #06

                struct FActionReturnFrame
SavedAF         dw #0000                                                        ; сохранённый AF после снятия созданного DrawReturn
ReturnAddress   dw #0000                                                        ; внешний обычный CPU-возврат после POP AF
                ends
                assert FActionReturnFrame == #04

                ; Документация [кадры дискового протокола слотов](../../Docs/SaveSlots.md)
                struct FSaveSlotFrame
SavedDE         dw #0000                                                        ; выбранный индекс панели записи
SavedAF         dw #0000                                                        ; A=3F и фактические флаги LD A,I
SavedHL         dw #0000                                                        ; HL в начале TransferState, обычно выбранный рисователь
SavedIY         dw #0000                                                        ; IY до замены на системный 5C3A
ReturnAddress   dw #0000                                                        ; внешний CPU-возврат действия
                ends
                ; проверка физического размера FSaveSlotFrame
                assert FSaveSlotFrame == #0A

                struct FLoadSlotFrame
SavedIY         dw #0000                                                        ; IY до замены на системный 5C3A
SavedAF         dw #0000                                                        ; A=3F и флаги LD A,I после арифметики цифры
SavedDE         dw #0000                                                        ; выбранный индекс панели чтения
SavedHL         dw #0000                                                        ; адрес цифры имени 7534, исходный HL уже заменён
ReturnAddress   dw #0000                                                        ; внешний CPU-возврат действия
                ends
                ; проверка физического размера FLoadSlotFrame
                assert FLoadSlotFrame == #0A

                ; Документация [физические кадры печати оснащения](../../Docs/EquipmentListPanels.md)
                struct FEquipmentRowsFrame
TopRow          dw #0000                                                        ; полное слово индекса, сохранённое последним PUSH DE
QuantityBase    dw #0000                                                        ; исходный адрес таблицы количеств 988E
ThresholdBase   dw #0000                                                        ; исходный адрес пар порог-вес 95F0
ShipSetsBase    dw #0000                                                        ; исходный адрес четырёхбайтовых наборов 9400
SavedShipAF     dw #0000                                                        ; F в младшем байте и текущий тип корабля в старшем
PricesBase      dw #0000                                                        ; исходный адрес слов цен 9592
ReturnAddress   dw #0000                                                        ; внешний CPU-возврат печатателя
                ends
                ; проверка физического размера FEquipmentRowsFrame
                assert FEquipmentRowsFrame == #0E

                struct FEquipmentMarkFrame
TablePointer    dw #0000                                                        ; начало текущего набора четырёх типов перед поиском
ReturnAddress   dw #0000                                                        ; внешний CPU-возврат, возможен до обратного EXX
                ends
                ; проверка физического размера FEquipmentMarkFrame
                assert FEquipmentMarkFrame == #04

                ; Документация [продолжения приветственного шаблона](../../Docs/WelcomePanel.md)
                struct FWelcomeTextFrame
Continuation    dw #0000                                                        ; фактический HL после печати части шаблона
ReturnAddress   dw #0000                                                        ; внешний обычный CPU-возврат рисователя
                ends
                assert FWelcomeTextFrame == #04

                ; Документация [двухсловный вход выхода из музыки](../../Docs/StopMusic.md)
                struct FStopMusicReturnFrame
HLWord          dw #0000                                                        ; выходное значение HL, первое слово входной рамки снимается POP без преобразования
ReturnAddress   dw #0000                                                        ; второе входное слово становится PC через RET
                ends
                ; проверка физического размера двухсловного входа
                assert FStopMusicReturnFrame == #04

                ; Документация [сохранённый конец HR-ресурса](../../Docs/UnpackResource.md)
                struct FUnpackTailFrame
FinalWord0      dw #0000                                                        ; пара исходных байтов 6..7, последние байты результата U-6 и U-5
FinalWord1      dw #0000                                                        ; пара исходных байтов 8..9, последние байты результата U-4 и U-3
FinalWord2      dw #0000                                                        ; пара исходных байтов 10..11, последние байты результата U-2 и U-1
ReturnAddress   dw #0000                                                        ; внешний CPU-возврат распаковщика под тремя сохранёнными словами
                ends
                ; проверка трёх сохранённых слов и внешнего возврата
                assert FUnpackTailFrame == #08

                ; Документация [физический префикс сжатых ресурсов](../../Docs/PackedResourcePrefix.md)
                struct FPackedFinalBytes
BytesMinus6     dw #0000                                                        ; два финальных байта результата по U-6 и U-5
BytesMinus4     dw #0000                                                        ; два финальных байта результата по U-4 и U-3
BytesMinus2     dw #0000                                                        ; два финальных байта результата по U-2 и U-1
                ends
                ; проверка трёх физических пар финальных байтов
                assert FPackedFinalBytes == #06


                ; Два физических байта адреса отложенного обработчика, код команды задан положением записи
                struct FMusicEffectTarget
Handler         dw #0000                                                        ; адрес обработчика в исходном банке MUZ1
                ends
                assert FMusicEffectTarget == 2

                ; Два отложенных эффекта и внешний возврат, физическая динамическая рамка CPU-стека
                struct FMusicDeferredPairFrame
LatestHandler   dw #0000                                                        ; последний помещённый адрес, его RET исполняет первым
EarlierHandler  dw #0000                                                        ; ранее помещённый адрес, его RET исполняет вторым
CallerReturn    dw #0000                                                        ; исходный внешний возврат после двух обработчиков
                ends
                assert FMusicDeferredPairFrame == 6

                ; Циклический заголовок исходных сэмплов и орнаментов, данные следуют сразу за ним
                struct FMusicLoopHeader
LoopPosition    db #00                                                          ; позиция возврата после достижения Length
Length          db #00                                                          ; предел следующей позиции, нулевой предел не нормализуется
                ends
                assert FMusicLoopHeader == 2

                ; Четыре физических байта шага сэмпла, сначала читаются как DE, затем как BC
                ; ShiftControl, схема разрядов 7..0:
                ;   7 6 5 4 3 2 1 0
                ;   A D S S S S S F
                ; A, обновить поправку уровня, D, единица увеличивает её, ноль уменьшает
                ; S, пятибитовый вклад огибающей, шумовой путь использует весь ShiftControl >> 1
                ; F, единица пропускает добавление маски огибающей к уровню
                ; LevelModes, схема разрядов 7..0:
                ;   7 6 5 4 3 2 1 0
                ;   E T S M V V V V
                ; E, вклад относится к огибающей, иначе к шуму, этот же бит попадает в старшую тройку микшера
                ; T, сохранять тональную поправку, S, сохранять шумовой либо огибающий вклад между кадрами
                ; M, бит младшей тройки микшера, V, базовый уровень 0..15
                ; нулевые управляющие байты задают базовый уровень 0 и режим шума без накопления
                struct FMusicSampleStep
ShiftControl    db #00                                                          ; совмещённое управление уровнем, сдвигом и маской огибающей
LevelModes      db #00                                                          ; базовый уровень, режим вклада и накопления, биты микшера
ToneDelta       dw #0000                                                        ; знаковое слово текущей тональной поправки
                ends
                assert FMusicSampleStep == 4


                ; Исходные физические данные проигрывателя, поля не выделяют новую память
                struct FMusicDataPointer
Address         dw #0000                                                        ; абсолютный указатель после InitializeModule, исходный ноль сохраняется
                ends
                assert FMusicDataPointer == 2

                struct FMusicAyRegisters
ToneA           dw #0000                                                        ; буфер периода тона A для регистров AY 0 и 1
ToneB           dw #0000                                                        ; буфер периода тона B для регистров AY 2 и 3
ToneC           dw #0000                                                        ; буфер периода тона C для регистров AY 4 и 5
Noise           db #00                                                          ; базовый буфер шума, при выводе добавляется текущий вклад IXH
Mixer           db #00                                                          ; буфер микшера, перед выводом заменяется IXL
LevelA          db #00                                                          ; сформированный уровень и маска огибающей A
LevelB          db #00                                                          ; сформированный уровень и маска огибающей B
LevelC          db #00                                                          ; сформированный уровень и маска огибающей C
EnvelopePeriod  dw #0000                                                        ; буфер периода общей огибающей
EnvelopeShape   db #00                                                          ; нулевой байт пропускает OUT регистра 13, ненулевой выводится и очищается
                ends
                assert FMusicAyRegisters == 14

                struct FMusicRowCounter
Remaining       db #00                                                          ; байтовая длительность строки, DEC исходного нуля даёт FF
                ends
                assert FMusicRowCounter == 1

                struct FMusicVolumeRow
Level00         db #00                                                          ; готовый уровень для входной амплитуды 0
Level01         db #00                                                          ; готовый уровень для входной амплитуды 1
Level02         db #00                                                          ; готовый уровень для входной амплитуды 2
Level03         db #00                                                          ; готовый уровень для входной амплитуды 3
Level04         db #00                                                          ; готовый уровень для входной амплитуды 4
Level05         db #00                                                          ; готовый уровень для входной амплитуды 5
Level06         db #00                                                          ; готовый уровень для входной амплитуды 6
Level07         db #00                                                          ; готовый уровень для входной амплитуды 7
Level08         db #00                                                          ; готовый уровень для входной амплитуды 8
Level09         db #00                                                          ; готовый уровень для входной амплитуды 9
Level0A         db #00                                                          ; готовый уровень для входной амплитуды 10
Level0B         db #00                                                          ; готовый уровень для входной амплитуды 11
Level0C         db #00                                                          ; готовый уровень для входной амплитуды 12
Level0D         db #00                                                          ; готовый уровень для входной амплитуды 13
Level0E         db #00                                                          ; готовый уровень для входной амплитуды 14
Level0F         db #00                                                          ; готовый уровень для входной амплитуды 15
                ends
                assert FMusicVolumeRow == 16

                struct FMusicNotePeriod
Period          dw #0000                                                        ; исходное little endian слово периода по индексу ноты
                ends
                assert FMusicNotePeriod == 2


                ; Физические поля исходной композиции, адреса и байты не меняются
                struct FMusicModuleHeader
Description     text 99, { #00 }                                                ; 99 исходных символов названия, автора и строки компилятора
ToneTableIndex  db #00                                                          ; номер частотной таблицы PT3, 2 соответствует ASM/PSC, InitializeModule его пропускает
RowTempo        db #00                                                          ; начальное количество тиков на строку, копируется в изменяемый операнд
PositionCount   db #00                                                          ; байт количества позиций, попадает в F при POP AF, границу списка задаёт FF
LoopIndex       db #00                                                          ; смещение позиции возврата от начала списка в байтах
PatternTable    dw #0000                                                        ; относительный адрес таблицы троек указателей
                ends
                assert FMusicModuleHeader == 105

                struct FMusicRelativePointer
Offset          dw #0000                                                        ; относительный адрес от начала композиции, ноль сохраняется буквально
                ends
                assert FMusicRelativePointer == 2

                struct FMusicPositionByte
Value           db #00                                                          ; смещение в единицах слова для тройки паттернов, FF завершает список
                ends
                assert FMusicPositionByte == 1

                struct FMusicPatternPointers
ChannelA        dw #0000                                                        ; относительный адрес потока A
ChannelB        dw #0000                                                        ; относительный адрес потока B
ChannelC        dw #0000                                                        ; относительный адрес потока C
                ends
                assert FMusicPatternPointers == 6

                struct FMusicOrnamentStep
NoteDelta       db #00                                                          ; байтовая поправка индекса ноты с оборачиванием при сложении
                ends
                assert FMusicOrnamentStep == 1


                ; Числовая запись либо указатель строки, старший байт хранится первым
                struct FTextQueueItem
HighKind        db #01                                                          ; 00 маркер конца, 01 свободно, 02 число, 03..FF старший байт указателя строки
LowValue        db #01                                                          ; числовое значение при HighKind=02, младший байт адреса при HighKind>=03
                ends
                assert FTextQueueItem == 2

                ; Динамический кадр производителя очереди, статической памяти нет
                struct FTextQueueInsertFrame
SavedAF         dw #0000                                                        ; входной AF, младший байт F
SavedBC         dw #0000                                                        ; сохранённый BC
SavedHL         dw #0000                                                        ; сохранённый HL
CallerReturn    dw #0000                                                        ; внешний адрес возврата
                ends
                assert FTextQueueInsertFrame == 8


                ; Собственная динамическая рамка QueueTextItemBank1, порядок отличается от рамки производителя
                struct FActionTextQueueFrame
SavedHL         dw #0000                                                        ; сохранённый HL
SavedBC         dw #0000                                                        ; сохранённый BC
SavedAF         dw #0000                                                        ; сохранённый AF
CallerReturn    dw #0000                                                        ; внешний адрес возврата Action
                ends
                assert FActionTextQueueFrame == 8


                ; Четыре исходные XOR-маски одной из восьми фаз маркера
                struct FMarkerPhaseMasks
Vertical        db #00                                                          ; маска четырёх верхних и четырёх нижних строк
CentralLeft     db #00                                                          ; маска левого байта центрального ряда
CentralMiddle   db #00                                                          ; маска среднего байта центрального ряда
CentralRight    db #00                                                          ; маска правого байта центрального ряда
                ends
                assert FMarkerPhaseMasks == 4


                ; Физическая запись координат линейного буфера, Y перед X
                struct FBufferPoint
Y               db #00                                                          ; вертикальная координата, первый физический байт
X               db #00                                                          ; горизонтальная координата, второй физический байт
                ends
                assert FBufferPoint == 2


                ; Физический знаковый отсчёт синусоиды ACTION
                struct FFixedSineValue
Value           db #00                                                          ; синус в дополнительном коде, масштаб 128
                ends
                assert FFixedSineValue == 1


                ; Физический байт одной из двух разрядных плоскостей квадрата
                struct FSquareTableByte
Value           db #00                                                          ; младший либо старший байт, часть указана именем экземпляра
                ends
                assert FSquareTableByte == 1


                ; Динамическая трёхбайтовая запись сравниваемого компонента
                struct FComponent24
Low             db #00                                                          ; биты 7..0 модуля проекции, вес 1, CompareComponents их не читает
Middle          db #00                                                          ; биты 15..8 модуля проекции, вес байта 256
High            db #00                                                          ; бит 7 задаёт знак, биты 6..0 задают 22..16 модуля в фазе проекции
                ends
                assert FComponent24 == 3


                ; Физическая упакованная затравка масок малых тел
                struct FSmallMaskSeed
Packed          db #00                                                          ; начальная маска в разрядах 7..3, число сдвигов в 2..0
                ends
                assert FSmallMaskSeed == 1

                ; Физическая строковая маска, изменяемая исходным подготовителем
                struct FSmallMaskRow
Mask            db #00                                                          ; исходный ноль до подготовки малой фигуры
                ends
                assert FSmallMaskRow == 1


                ; Физические входные байты проекции объекта в банке 1
                struct FBodyProjection
OffsetY         db #00                                                          ; вертикальное числовое смещение до выбора знака
OffsetX         db #00                                                          ; горизонтальное числовое смещение до выбора знака
Flags           db #00                                                          ; биты 0 и 1 задают направления, 2 и 3 задают N<=Q по X и Y, верхние биты требуют контекста писателя
Radius          db #00                                                          ; радиус, малый рисователь принимает только 2..8
                ends
                assert FBodyProjection == 4


                ; Физическая рабочая запись большого контура, исходное размещение сохранено
                struct FCircleRasterWork
WorkY           db #00                                                          ; рабочее Y, исходно OffsetY, отсечённые ветви могут его менять
WorkX           db #00                                                          ; рабочее X, исходно OffsetX, отсечённые ветви могут его менять
CenterY         db #00                                                          ; байтовая строка центра сечения
CenterX         db #00                                                          ; байтовая горизонтальная координата центра сечения
SectionRadius   db #00                                                          ; результат SqrtSquareDiff для отсечённого сечения
SavedSP         dw #0000                                                        ; сохранённый CPU-стек, указывает SavedAF перед внешним возвратом
SquareDiff      dw #0000                                                        ; рабочее слово D*D-A*A-Carry по модулю 65536
SavedB          db #00                                                          ; сохранённый B помощника правой маски
Direction       db #00                                                          ; код направления строк, 0 вверх, 1 вниз, проверка различает ноль и ненулевое
Mode            db #00                                                          ; авторский SEDETECT, прямые писатели задают 0/1, три чтения сохраняют или возвращают F от AND Mode, общий графический замысел не установлен
                ends
                assert FCircleRasterWork == 12


                ; Физическое двухсловное состояние генератора ACTION
                struct FWordRandomState
First           dw #0000                                                        ; получает прежнее Second
Second          dw #0000                                                        ; результат смешивающей рекурсии
                ends
                assert FWordRandomState == 4


                ; Физическое правило формирования одного байта параметра
                struct FParameterCoefficient
Base            db #00                                                          ; аддитивная база перед байтом выбранного шаблона
SlopeCode       db #00                                                          ; числовой код наклона, 01 ноль, 02 плюс C, FE минус C
ShiftMask       db #00                                                          ; ненулевая степень двойки, число SRA равно позиции установленного разряда
                ends
                assert FParameterCoefficient == 3


                ; Физическая фаза трёхстрочного знака, шесть последовательных масок
                struct FThreeRowGlyphPhase
Row0Left        db #00                                                          ; левая байтовая маска верхней строки
Row0Right       db #00                                                          ; правая байтовая маска верхней строки
Row1Left        db #00                                                          ; левая байтовая маска средней строки
Row1Right       db #00                                                          ; правая байтовая маска средней строки
Row2Left        db #00                                                          ; левая байтовая маска нижней строки
Row2Right       db #00                                                          ; правая байтовая маска нижней строки
                ends
                assert FThreeRowGlyphPhase == 6


                ; Физические входы трёх знаков, локальные роли установлены в E021
                struct FGlyphIndicatorControl
FirstMode       db #00                                                          ; код 01 пропускает первый знак, остальные значения допускают его
ThirdGate       db #00                                                          ; ноль допускает третий знак после проверки второго, ненулевое значение запрещает
TemplateMode    db #00                                                          ; вход в шаблонную ветвь, сбрасывается при активации параметров и очистке класса 12
                ends
                assert FGlyphIndicatorControl == 3

                struct FGlyphIndicatorYX
Y               db #00                                                          ; байт вертикального смещения в формуле экрана
X               db #00                                                          ; байт горизонтального смещения в формуле экрана
SignSource      db #00                                                          ; старший байт третьей компоненты компаса станции, знак выбирает заполненный или полый квадрат
                ends
                assert FGlyphIndicatorYX == 3

                struct FGlyphIndicatorXY
X               db #00                                                          ; байт горизонтального смещения в формуле экрана
Y               db #00                                                          ; байт вертикального смещения в формуле экрана
SignSource      db #00                                                          ; знаковый байт выбора формы, у Second весь байт также входит в OR-маркер отсутствия
                ends
                assert FGlyphIndicatorXY == 3


                ; Физический адрес для RET с временно выбранным табличным SP
                struct FReturnDispatchEntry
Target          dw #0000                                                        ; адрес кодового хвоста в том же банке
                ends
                assert FReturnDispatchEntry == 2


                ; Физическая запись ресурса ControlsObjectGlyphPointers
                struct FObjectGlyphPointer
Target          dw #0000                                                        ; адрес восьми фаз значка класса, порядок MOTAB и определения T_* подтверждены
                ends
                assert FObjectGlyphPointer == 2

                ; Физическая запись ресурса ControlsObjectPixelMasks
                struct FObjectPixelMask
Mask            db #00                                                          ; одиночный бит X внутри экранного байта
                ends
                assert FObjectPixelMask == 1

                ; Физическая запись ресурса ControlsObjectClearMasks
                struct FObjectGlyphClearPhase
LeftMask        db #00                                                          ; сохраняемые биты левой части строки
RightMask       db #00                                                          ; сохраняемые биты правой части строки
Unknown02       db #00                                                          ; исходный нулевой байт, этот потребитель его не читает
Unknown03       db #00                                                          ; исходный нулевой байт, этот потребитель его не читает
Unknown04       db #00                                                          ; исходный нулевой байт, этот потребитель его не читает
Unknown05       db #00                                                          ; исходный нулевой байт, этот потребитель его не читает
                ends
                assert FObjectGlyphClearPhase == 6


                ; Физическая маска частичного столбца шестистрочной шкалы
                struct FGaugePartialMask
Pattern         db #00                                                          ; исходный байт для шести строк частичного столбца
                ends
                assert FGaugePartialMask == 1


                ; Физическая пара ACTION для выбора значения и его изменяемого адреса
                struct FPreferredBytePair
Preferred       db #00                                                          ; выбирается вместе со своим адресом, если байт ненулевой
Fallback        db #00                                                          ; выбирается вместе со своим адресом, если Preferred равен нулю
                ends
                assert FPreferredBytePair == 2


                ; Физическая запись частично разобранного клавиатурного диспетчера
                struct FKeyHandlerPointer
Target          dw #0000                                                        ; адрес обработчика в общей RAM, его алгоритм требует отдельного разбора
                ends
                assert FKeyHandlerPointer == 2

                ; Физическая запись частично разобранного клавиатурного диспетчера
                struct FKeyScanInput
RowSelect       db #00                                                          ; старший байт порта IN A,(C), младший байт FE
InputMask       db #00                                                          ; маска входного байта, нулевой результат AND допускает обработчик
                ends
                assert FKeyScanInput == 2
                assert @ActionKeyScanConst.PrevMaskBack == FKeyScanInput - FKeyScanInput.InputMask


                ; Два исходных счётчика ракет в обратном порядке приоритета
                struct FMissileStock
Fallback        db #00                                                          ; запас ракет рп1 из строки 2 станции, выбирается при нулевом Preferred
Preferred       db #00                                                          ; запас ракет рп2 из строки 3 станции, выбирается первым при ненулевом значении
                ends
                assert FMissileStock == 2


                ; Три физических кода захваченных целей ракет
                struct FMissileTargets
Target0         db #00                                                          ; код записи цели в слоте 0, FF означает отсутствие захвата
Target1         db #00                                                          ; код записи цели в слоте 1, FF означает отсутствие захвата
Target2         db #00                                                          ; код записи цели в слоте 2, FF означает отсутствие захвата
                ends
                assert FMissileTargets == 3


                ; Физическая знаковая поправка исходной таблицы
                struct FIndexedDelta
Delta           db #00                                                          ; signed8, отрицательные значения не получают добавку режима
                ends
                assert FIndexedDelta == 1


                ; Исходная физическая раскладка, неизвестные поля не переименованы по предположению
                struct FActionWord
Low             db #00                                                          ; младший байт компоненты, формат little-endian
High            db #00                                                          ; старший байт слова, специальные коды зависят от владельца поля
                ends
                assert FActionWord == #02

                ; Исходная физическая раскладка, неизвестные поля не переименованы по предположению
                ; Контексты слов [объект и снимок очереди](../../Docs/ActionComponentContexts.md)
                struct FActionComponents
Component0      FActionWord                                                     ; в записи смещение XW из EQUS, в узле Output0, единицы расстояния не установлены
Component1      FActionWord                                                     ; в записи смещение YW из EQUS, в узле Output1, единицы расстояния не установлены
Component2      FActionWord                                                     ; в записи смещение ZW из EQUS, в узле Output2, единицы расстояния не установлены
                ends
                assert FActionComponents == #06
                assert FActionComponents.Component0 == #00
                assert FActionComponents.Component1 == #02
                assert FActionComponents.Component2 == #04

                ; Исходная физическая раскладка, неизвестные поля не переименованы по предположению
                struct FActionViewPosition
X               FActionWord                                                     ; знаковая координата после преобразования
Y               FActionWord                                                     ; знаковая координата после преобразования
Depth           FActionWord                                                     ; знаковая координата после преобразования
                ends
                assert FActionViewPosition == #06

                struct FActionRecord
Components      FActionComponents                                               ; три исходных слова записи, 60AE записывает результаты TransformVectorTransposed
ModelOffset     db #00                                                          ; байтовое смещение таблицы указателей 9E00, ReadObjectHeaderWord читает заголовок выбранной модели
OffsetPhase0    db #00                                                          ; байтовый индекс первой фазовой пары вычислителя смещения
OffsetPhase1    db #00                                                          ; байтовый индекс второй фазовой пары, подготовитель добавляет 128
OffsetPhase2    db #00                                                          ; байтовый индекс третьей фазовой пары вычислителя смещения
StateCode       db #00                                                          ; байтовый код выбора обработчика ObjectStateHandlers, 60AE записывает 08
LinkedIndex     db #00                                                          ; индекс связанной записи, 60AE записывает сюда индекс новой ракеты у цели
                ; Разряды 7..0, ? ? ? ? P H R B, маски B=01, R=02, H=04, P=08
                ; B задаёт обратную ссылку E804, R ракетную атаку, H ракетное поражение в State08, P выбор противоракетного порога
                ; Ноль сбрасывает четыре известных признака и неизвестные биты, отсутствие живой связи этим не доказывается
                ; 17 исследованных писателей обнуляют байт либо устанавливают биты 0..3 через SET
                ; иные косвенные писатели и происхождение старших битов этим локальным доказательством не исключены
                ; Писатели и ограничения [исходные байты и все значения флагов](../../Docs/ActionLinkFlagWrites.md)
LinkFlags       db #00                                                          ; бит 0 задаёт обратную связь E804, бит 1 ракетную атаку, бит 2 ракетное поражение в State08, бит 3 противоракетный выбор порога PS1/PS2, биты 7..4 влияют на ненулевость, отдельные роли неизвестны
Phase0OrLink    db #00                                                          ; первая локальная фаза либо байтовый индекс опоры, обработчик выбирает трактовку, создатель ракеты пишет #1A
LocalPhase1     db #00                                                          ; вторая локальная фаза, ApplyRecordLocalOffsets добавляет #80 по модулю байта
Phase2OrTarget  db #00                                                          ; третья локальная фаза, индекс цели или порог счётчика, назначение выбирает обработчик
OffsetScaleLow  db #00                                                          ; младший байт масштаба смещения, локальный расчёт использует его отдельно как беззнаковый масштаб
Unknown11       db #00                                                          ; таймер State07, порог State02/10, происхождение ракеты и уведомления State08, количество подбора класса 13
ClassCode       db #00                                                          ; полный код класса, используется FindRecordByCode, создаваемая ракета получает 11
EffectReserve   db #00                                                          ; текущий запас для проверки эффекта и связанных состояний, 60AE записывает 0A либо 32
MissileRepeatDelay    db #00                                                          ; счётчик повторного пуска ракеты, знаковая ветвь DEC может оставить прежнее значение
LinkOverride    db #00                                                          ; числовой индекс подстановки LinkedIndex, FF запрещает подстановку, ноль разрешён и возвращает Z
SavedStateCode  db #00                                                          ; код состояния для восстановления в обработчиках хода и ожидания
PhaseMoveTimer  db #00                                                          ; байтовый таймер вызовов обработчиков хода первой фазы
ReuseByte       db #00                                                          ; FF задаёт однократный пропуск поиска, в отдельных состояниях биты 1..0 задают счётчик, бит 2 запрос детей, бит 4 допуск эффекта
TimedResumeCode db #00                                                          ; прежний полный StateCode, восстанавливаемый при истечении таймера состояния #10
ViewPosition    FActionViewPosition                                             ; X, Y и глубина после ComputePatchedVector, старший байт X равен 80 до успешного преобразования
ProximityIndex  db #00                                                          ; байтовый индекс записи для проверки близости, резервный поиск класса 8 может заменить индекс
ProximityClass  db #00                                                          ; требуемый полный класс записи для проверки близости, резервный поиск его не меняет
ReserveCeiling  db #00                                                          ; предел восстановления запаса, при обходе сравнивается с ним минус один по модулю байта
PickupKind      db #00                                                          ; для класса #13 код подбора, используется как байтовый индекс груза и правила, границы не проверяются
OffsetScaleHigh db #00                                                          ; старший байт масштаба смещения, в состоянии ожидания используется как фазовый счётчик
TargetCodeStep  db #00                                                          ; числовой предельный шаг подвода второго и третьего фазовых кодов
WideTargetIndex db #00                                                          ; индекс строки из трёх 32-разрядных компонент широкой цели, шаг строки 12 байтов
Unknown27       db #00                                                          ; игровой смысл ещё неизвестен
Unknown28       db #00                                                          ; игровой смысл ещё неизвестен
Unknown29       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2A       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2B       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2C       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2D       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2E       db #00                                                          ; игровой смысл ещё неизвестен
Unknown2F       db #00                                                          ; игровой смысл ещё неизвестен
Unknown30       db #00                                                          ; игровой смысл ещё неизвестен
Unknown31       db #00                                                          ; игровой смысл ещё неизвестен
Unknown32       db #00                                                          ; игровой смысл ещё неизвестен
Unknown33       db #00                                                          ; игровой смысл ещё неизвестен
Unknown34       db #00                                                          ; игровой смысл ещё неизвестен
Unknown35       db #00                                                          ; игровой смысл ещё неизвестен
Unknown36       db #00                                                          ; игровой смысл ещё неизвестен
Unknown37       db #00                                                          ; игровой смысл ещё неизвестен
Unknown38       db #00                                                          ; игровой смысл ещё неизвестен
Unknown39       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3A       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3B       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3C       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3D       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3E       db #00                                                          ; игровой смысл ещё неизвестен
Unknown3F       db #00                                                          ; игровой смысл ещё неизвестен
                ends
                assert FActionRecord == #40
                assert FActionRecord.ViewPosition == #1A
                assert FActionRecord.ViewPosition.Depth.High == #1F


                ; Физическая четырёхбайтовая строка потоков эффектов ACTION
                struct FActionAyFrame
ToneLow         db 0                                                            ; младший байт периода
ToneHigh        db 0                                                            ; старший байт периода, полный исходный байт
MixerBits       db 0                                                            ; байт для OR со смесителем, B предварительно выполняет RLCA
Volume          db 0                                                            ; байт записи уровня, полный исходный байт
                ends


                ; Физический байт исходной таблицы граничных поправок
                struct FSymmetricSquareValue
Value           db 0                                                            ; нормированный квадрат min(i,255-i)^2 DIV 127
                ends


                ; Три физических байтовых фазы исходной синусоиды, оборот равен 256
                struct FRenderPhases
Phase0          db #00                                                          ; фаза 0, индекс страницы синусоиды
Phase1          db #00                                                          ; фаза 1, индекс страницы синусоиды
Phase2          db #00                                                          ; фаза 2, индекс страницы синусоиды
                ends
                assert FRenderPhases == #03
                assert FRenderPhases.Phase0 == #00
                assert FRenderPhases.Phase1 == #01
                assert FRenderPhases.Phase2 == #02

                ; Физическая раскладка создаваемого runtime-узла, дисковые экземпляры не подменяются
                struct FActionRenderNode
Next            db #00                                                          ; младший байт следующего узла в странице 8F, 01 конец
Unknown01       db #00                                                          ; позиция младшего байта SETS архивного узла, текущая вставка сохраняет
Unknown02       db #00                                                          ; позиция старшего байта SETS архивного узла, текущая вставка сохраняет
HeaderWord0     dw #0000                                                        ; снимок ModeBits и ModelByteOffset по 9B8D, порядок байтов сохранён
Phases          FRenderPhases                                                   ; Phase0, Phase1 и Phase2, снимок 9B12..9B14
Components      FActionComponents                                               ; снимок Output0, Output1 и Output2, глубина по +0C
                ends
                assert FActionRenderNode == #0E
                assert FActionRenderNode.HeaderWord0 == #03
                assert FActionRenderNode.Phases == #05
                assert FActionRenderNode.Phases.Phase2 == #07
                assert FActionRenderNode.Components == #08
                assert FActionRenderNode.Components.Component2 == #0C


                ; Физическая экранная точка, X перед Y
                struct FActionAimPoint
X               db #00                                                          ; горизонтальный экранный байт
Y               db #00                                                          ; вертикальный экранный байт
                ends
                assert FActionAimPoint == #02
                assert FActionAimPoint.X == #00
                assert FActionAimPoint.Y == #01


                ; Исходный little-endian указатель потока OBJECT3D банка 4
                struct FObjectDataPointer
Target          dw #0000                                                        ; адрес данных банка 4, не адрес кода
                ends
                assert FObjectDataPointer == #02
                assert FObjectDataPointer.Target == #00


                ; Создаваемая перспективой runtime-запись, пятый байт сохраняется
                struct FRenderProjectedPoint
Second          dw #0000                                                        ; второе экранное слово, при отказе high=80 и low=LOW(depth)
First           dw #0000                                                        ; первое экранное слово либо глубина при раннем отказе
ClipCode        db #00                                                          ; парные признаки границ заполняет ClassifyProjectedVertices, перспектива байт сохраняет
                ends
                assert FRenderProjectedPoint == #05
                assert FRenderProjectedPoint.Second == #00
                assert FRenderProjectedPoint.First == #02
                assert FRenderProjectedPoint.ClipCode == #04


                struct FLinePixelMask
Mask            db #00                                                          ; физическая маска одной пиксельной фазы
                ends
                assert FLinePixelMask == #01
                assert FLinePixelMask.Mask == #00


                ; Физическая запись трёхбайтового состояния генератора ACTION
                struct FFoldedRandomState
LowWord         dw #0000                                                        ; слово смешивания и возвращаемого 16-битного результата
FoldByte        db #00                                                          ; байт свёртки переносов, числовая величина modulo 256
                ends
                assert FFoldedRandomState == 3


                ; Физический байт одной из трёх плоскостей табличного корня
                struct FRootCacheByte
Value           db #00                                                          ; значение исходного байта, плоскость и индекс заданы именем экземпляра
                ends
                assert FRootCacheByte == 1


                ; Физический указатель косвенного диспетчера класса ACTION
                struct FClassHandler
Handler         dw #0000                                                        ; исходный адрес обработчика, младший байт записан первым
                ends
                assert FClassHandler == #02


                ; Физический исходный код одного индекса знакового отношения
                struct FSignedRatioCode
Code            db #00                                                          ; исходный код, смещения четырёх знаковых ветвей добавляет EncodeSignedRatio
                ends
                assert FSignedRatioCode == #01


                ; Динамические физические рамки EncodeHalfCoordinateDeltas, статическая RAM не выделяется
                struct FDeltaCodeRootFrame
SavedPortBC     dw #0000                                                        ; BC текущего SelectMemoryPage, второй раз содержит BC кэша корня
ReturnSelect    dw #0000                                                        ; возврат выбора банка AD4E либо AD57
SavedSquareBC   dw #0000                                                        ; половина Right1 при малом втором квадрате либо ноль при полном ядре
ReturnRoot      dw #0000                                                        ; возврат банкового корня AD8C
Delta1          dw #0000                                                        ; сохранённый d1
Delta0          dw #0000                                                        ; сохранённый d0
SavedIX         dw #0000                                                        ; входной IX
CallerReturn    dw #0000                                                        ; внешний возврат исходного вызывающего
                ends
                assert FDeltaCodeRootFrame == #10

                struct FDeltaCodeFirstFrame
ReturnRatio     dw #0000                                                        ; возврат логарифмического делителя AE36
SavedDen        dw #0000                                                        ; исходный знаменатель d2 первого кодировщика
SignAF          dw #0000                                                        ; совместный признак исходных знаков и XOR-флаги
ReturnCode      dw #0000                                                        ; возврат первого кодировщика ADA4
Delta1          dw #0000                                                        ; сохранённый d1
Delta0          dw #0000                                                        ; сохранённый d0
SavedIX         dw #0000                                                        ; входной IX
CallerReturn    dw #0000                                                        ; внешний возврат
                ends
                assert FDeltaCodeFirstFrame == #10

                struct FDeltaCodeSecondFrame
ReturnRatio     dw #0000                                                        ; возврат логарифмического делителя AE36
SavedDen        dw #0000                                                        ; исходный знаменатель d0 второго кодировщика
SignAF          dw #0000                                                        ; совместный признак исходных знаков и XOR-флаги
ReturnCode      dw #0000                                                        ; возврат второго кодировщика ADB2
FirstCodeAF     dw #0000                                                        ; будущий B в старшем байте и флаги его сложения в младшем
SavedIX         dw #0000                                                        ; входной IX
CallerReturn    dw #0000                                                        ; внешний возврат
                ends
                assert FDeltaCodeSecondFrame == #0E



                ; Динамические вложенные рамки основного StepRecordTargetCodes, память не выделяется
                struct FRecordStepRootFrame
ChildFrame      FDeltaCodeRootFrame                                             ; реальная рамка дочерней геометрии, её внешний возврат равен 6268
CallerReturn    dw #0000                                                        ; внешний возврат вызывающего StepRecordTargetCodes
                ends
                assert FRecordStepRootFrame == #12

                struct FRecordStepFirstFrame
ChildFrame      FDeltaCodeFirstFrame                                            ; реальная рамка дочерней геометрии, её внешний возврат равен 6268
CallerReturn    dw #0000                                                        ; внешний возврат вызывающего StepRecordTargetCodes
                ends
                assert FRecordStepFirstFrame == #12

                struct FRecordStepSecondFrame
ChildFrame      FDeltaCodeSecondFrame                                           ; реальная рамка дочерней геометрии, её внешний возврат равен 6268
CallerReturn    dw #0000                                                        ; внешний возврат вызывающего StepRecordTargetCodes
                ends
                assert FRecordStepSecondFrame == #10



                ; Динамическая рамка в третьем AbsSigned32, память не выделяется
                struct FClampVectorFrame
ReturnAbs       dw #7F3F                                                        ; возврат третьего вызова AbsSigned32
SecondMagnitude dw #0000                                                        ; сохранённый насыщенный модуль второй компоненты
FirstMagnitude  dw #0000                                                        ; сохранённый насыщенный модуль первой компоненты
CallerReturn    dw #0000                                                        ; внешний возврат ClampPatchedVectorWords
                ends
                assert FClampVectorFrame == #08



                ; Три исходных signed32, формат доказан чтениями 7EB7 и вычитаниями 68CD
                struct FActionWideComponent
Byte0           db #00                                                          ; разряды 7..0 исходной компоненты
Byte1           db #00                                                          ; разряды 15..8 исходной компоненты
Byte2           db #00                                                          ; разряды 23..16, бит 7 используется 7F0E как знак выходного слова
Byte3           db #00                                                          ; разряды 31..24, бит 7 задаёт знак полного signed32
                ends
                assert FActionWideComponent == #04

                struct FActionWideVector
Component0      FActionWideComponent                                            ; исходная широкая компонента 0
Component1      FActionWideComponent                                            ; исходная широкая компонента 1
Component2      FActionWideComponent                                            ; исходная широкая компонента 2
                ends
                assert FActionWideVector == #0C



                ; Динамическая рамка во вложенной проверке близости, память не выделяется
                struct FNearVectorSearchFrame
ReturnPredicate dw #69D2                                                        ; возврат настоящего CheckThreeUpperWordsNear
SavedIY         dw #0000                                                        ; сохранённый указатель внешнего вызывающего
CallerReturn    dw #0000                                                        ; внешний адрес возврата поиска
                ends
                assert FNearVectorSearchFrame == #06



                ; Динамическая рамка внутри NextActiveRecord при падающем фронте Request
                struct FControlDecayFrame
ReturnIterator  dw #E997                                                        ; возврат итератора в FindRecordByCode
ReturnFindCode  dw #6177                                                        ; возврат поиска в ReleaseBoostDebrisRecords
ReturnRelease   dw #6F65                                                        ; возврат освобождения в обработку падающего фронта
CallerReturn    dw #0000                                                        ; внешний возврат LatchControlsAndDecay
                ends
                assert FControlDecayFrame == #08



                ; Динамические рамки межбанкового диспетчера, новая память не выделяется
                struct FBankCallbackFrame
Continuation    dw #6D00                                                        ; адрес возвратного хвоста, снимается RET обработчика
CallerReturn    dw #0000                                                        ; внешний возврат, снимается RestoreRuntimePage
                ends
                assert FBankCallbackFrame == #04

                struct FBankCallbackSelectFrame
SavedBC         dw #0000                                                        ; сохранённый BC внутри SelectMemoryPage
ReturnSelect    dw #0000                                                        ; 6CF6 при входе в обработчик либо 6D05 при возврате
CallerReturn    dw #0000                                                        ; внешний возврат исходного диспетчера либо хвоста
                ends
                assert FBankCallbackSelectFrame == #06



                ; Рамка внутренних строк после трёх PUSH, динамический экземпляр на CPU-стеке
                ; Документация [сохранённые слова и роль Mode](../../Docs/ControlsInteriorRows.md#физическая-рамка-строк)
                struct FInteriorRowsFrame
SavedBC         dw #0000                                                        ; B исходное число строк, C номер первой строки после обёртки
SavedAF         dw #0000                                                        ; A номер первой строки, F вызывающего либо AND Mode после обёртки
SavedDE         dw #0000                                                        ; исходный DE, восстанавливается после сохранённого AF
CallerReturn    dw #0000                                                        ; внешний возврат, снимается после трёх сохранённых слов
                ends
                assert FInteriorRowsFrame == #08
                assert FInteriorRowsFrame.SavedBC == #00
                assert FInteriorRowsFrame.SavedAF == #02
                assert FInteriorRowsFrame.SavedDE == #04
                assert FInteriorRowsFrame.CallerReturn == #06

                ; Динамические рамки двух половин внутреннего контура, память не выделяется
                struct FInteriorCircleUpFrame
Temporary0      dw #0000                                                        ; правый HL внутри FillEvenSpan либо два байта рисунка в быстрой фазе
Temporary1      dw #0000                                                        ; возврат помощника либо сохранённый DE быстрой подготовки
SavedAF         dw #0000                                                        ; левая включающая маска и F=42, восстанавливаются при выходе половины
ReturnHalf      dw #D31A                                                        ; возврат верхней половины к повторному построению сечения
CallerReturn    dw #0000                                                        ; исходный внешний возврат внутреннего контура
                ends
                assert FInteriorCircleUpFrame == #0A

                struct FInteriorCircleDownFrame
Temporary0      dw #0000                                                        ; правый HL внутри FillEvenSpan либо два байта рисунка в быстрой фазе
Temporary1      dw #0000                                                        ; возврат помощника либо сохранённый DE быстрой подготовки
SavedAF         dw #0000                                                        ; левая включающая маска и F=42, восстанавливаются при выходе половины
CallerReturn    dw #0000                                                        ; исходный внешний возврат внутреннего контура
                ends
                assert FInteriorCircleDownFrame == #08



                ; Динамическая рамка отдельной половины контура, память не выделяется
                struct FSingleCircleHalfFrame
Temporary0      dw #0000                                                        ; правый HL либо два байта рисунка быстрой фазы
Temporary1      dw #0000                                                        ; возврат помощника либо временный DE быстрой фазы
SavedAF         dw #0000                                                        ; произвольный исходный AF вызывающего, полностью восстанавливается
CallerReturn    dw #0000                                                        ; исходный внешний возврат отдельной половины
                ends
                assert FSingleCircleHalfFrame == #08



                ; Единственное слово нового CPU-стека перед переходом загрузчика
                struct FStationReloadFrame
NextEntry       dw #4200                                                        ; реальное слово по 5FFD, снимается RET и оставляет SP=5FFF
                ends
                assert FStationReloadFrame == #02



                ; Знаковая 24-битная компонента в дополнительном коде, не формат модуля проекции
                struct FActionWorkComponent24
LowWord         dw #0000                                                        ; разряды 15..0, записываются до проверки переполнения старшего байта
High            db #00                                                          ; разряды 23..16, бит 7 задаёт знак всей 24-битной компоненты
                ends
                assert FActionWorkComponent24 == 3

                ; Физический рабочий вектор вычитателя 66D2
                struct FActionWorkVector24
Component0      FActionWorkComponent24                                          ; первая компонента в дополнительном коде
Component1      FActionWorkComponent24                                          ; вторая компонента в дополнительном коде
Component2      FActionWorkComponent24                                          ; третья компонента в дополнительном коде
                ends
                assert FActionWorkVector24 == 9


                ; Самая глубокая динамическая рамка обновления шкалы, память не выделяется
                struct FPanelRefreshGaugeFrame
SavedBC         dw #0000                                                        ; сохранённые BC при выборе банка внутри DrawBankedGauge
SelectorRet     dw #0000                                                        ; возврат селектора к банковой обёртке шкалы
GaugeRet        dw #0000                                                        ; возврат DrawBankedGauge к обработчику одной из шести шкал
PanelRet        dw #6161                                                        ; возврат UpdatePanelGauges к выбору банка CONTROL
CallerRet       dw #0000                                                        ; исходный возврат, используется после хвостового вывода BCD
                ends
                assert FPanelRefreshGaugeFrame == #0A



                ; Физический указатель обработчика состояния объекта
                struct FObjectStateHandler
Handler         dw #0000                                                        ; адрес в банке ACTION
                ends
                assert FObjectStateHandler == 2

                struct FActionModelHeader
BoundMantissa   db #00                                                          ; мантисса границы близости и проекции
ScaleExponent   db #00                                                          ; показатель масштаба преобразования
                ends
                assert FActionModelHeader == #02

                struct FActionModelGroup
Mask            db #00                                                          ; код создаваемых комбинаций компонент
Component0      db #00                                                          ; компонента поставщика произведений
Component1      db #00                                                          ; компонента поставщика произведений
Component2      db #00                                                          ; компонента поставщика произведений
                ends
                assert FActionModelGroup == #04

                struct FActionModelPrimitive2
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive2 == #03

                struct FActionModelPrimitive3
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive3 == #04

                struct FActionModelPrimitive4
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive4 == #05

                struct FActionModelPrimitive5
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive5 == #06

                struct FActionModelPrimitive6
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive6 == #07

                struct FActionModelPrimitive7
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive7 == #08

                struct FActionModelPrimitive8
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive8 == #09

                struct FActionModelPrimitive9
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive9 == #0A

                struct FActionModelPrimitive10
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive10 == #0B

                struct FActionModelPrimitive11
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex10        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive11 == #0C

                struct FActionModelPrimitive12
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex10        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex11        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive12 == #0D

                struct FActionModelPrimitive13
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex10        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex11        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex12        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive13 == #0E

                struct FActionModelPrimitive14
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex10        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex11        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex12        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex13        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive14 == #0F

                struct FActionModelPrimitive15
Header          db #00                                                          ; тип, материал либо режим и число индексов
Vertex0         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex1         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex2         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex3         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex4         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex5         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex6         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex7         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex8         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex9         db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex10        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex11        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex12        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex13        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
Vertex14        db #00                                                          ; байтовое смещение проецированной вершины, кратное пяти
                ends
                assert FActionModelPrimitive15 == #10

                struct FEffectByteRow16
Pair00          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair01          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair02          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair03          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair04          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair05          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair06          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair07          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair08          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair09          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair10          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair11          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair12          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair13          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair14          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair15          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
                ends
                assert FEffectByteRow16 == #10

                struct FEffectByteRow32
Pair00          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair01          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair02          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair03          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair04          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair05          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair06          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair07          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair08          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair09          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair10          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair11          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair12          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair13          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair14          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair15          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair16          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair17          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair18          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair19          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair20          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair21          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair22          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair23          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair24          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair25          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair26          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair27          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair28          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair29          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair30          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
Pair31          db #00                                                          ; исходная пара четырёхбитных кодов либо результат табличной выборки
                ends
                assert FEffectByteRow32 == #20

                struct FChooseScreenAttributes
Column00        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column01        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column02        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column03        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column04        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column05        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column06        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column07        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column08        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column09        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column10        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column11        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column12        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column13        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column14        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column15        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column16        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column17        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column18        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column19        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column20        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column21        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column22        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column23        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column24        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column25        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column26        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column27        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column28        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column29        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column30        db #00                                                          ; flash, bright, paper и ink одного знакоместа
Column31        db #00                                                          ; flash, bright, paper и ink одного знакоместа
                ends
                assert FChooseScreenAttributes == #20

                ; Динамический кадр ADC5 во время дочернего CALL, память не выделяется
                struct FOverlayProjectionFrame
DivideReturn    dw #0000                                                        ; ADD5 либо ADFB, возврат из настоящего делителя
SavedDepth      dw #0000                                                        ; исходная знаковая глубина обеих осей
SavedAxis       dw #0000                                                        ; исходная горизонталь на первом вызове, экранный Y на втором
                ends
                assert FOverlayProjectionFrame == #06

                ; Физические записи BAR, значения полей подтверждены архивным потребителем
                struct FFighterPosePointer
FileOffset      dw #0000                                                        ; файловое смещение группы BAR, адрес RAM не назначается
                ends
                assert FFighterPosePointer == #02

                struct FFighterPoseHeader
FrameCount      db #00                                                          ; число кадров группы
RepeatFlags     db #00                                                          ; флаг, бит 6 задаёт повтор с RepeatIndex, ноль выбирает NextAction
RepeatIndex     db #00                                                          ; индекс кадра после окончания группы при повторе
NextAction      db #00                                                          ; следующий код действия при отключённом повторе
                ends
                assert FFighterPoseHeader == #04

                struct FFighterPoseStep
Ticks           db #00                                                          ; задержка до продвижения кадра
MoveX           dw #0000                                                        ; приращение горизонтальной позиции с учётом стороны
MoveY           dw #0000                                                        ; приращение вертикальной позиции по модулю 256
DrawX           dw #0000                                                        ; смещение рисунка по горизонтали относительно новой позиции
DrawY           dw #0000                                                        ; смещение рисунка по вертикали относительно новой позиции
BankIndex       db #00                                                          ; индекс файла BD0..BD3
SpriteAddress   dw #0000                                                        ; адрес пары маски и пикселей в окне C000
WidthBytes      db #00                                                          ; число пар в строке
Height          db #00                                                          ; число строк
                ends
                assert FFighterPoseStep == #0E

                struct FPlayerSaveHeader
ShipIndex       db #00                                                          ; индекс текущей модели корабля, его игровые значения здесь не перечисляются
SkimmerIndex    db #00                                                          ; индекс скимера, FF пропускает дополнительное слагаемое взвешенной загрузки
StatusCode      db #00                                                          ; числовой полицейский статус, все 8 бит участвуют в расчётах, подпись по старшим трём
RankScore       dw #0000                                                        ; беззнаковое слово выбора ранга
Money           dw #0000                                                        ; денежное слово, печатается и изменяется торговлей и наградой
UsedTonnage     db #00                                                          ; байт используемого тоннажа статусной панели
Capacity        db #00                                                          ; байт вместимости статусной панели
                ends
                assert FPlayerSaveHeader == #09

                struct FOwnedCargoRow
QuantityAndMark db #00                                                          ; рисователь читает 6..0 как количество и 7 как FE, сборщик и LANG читают весь байт, смысл пометки неизвестен
Price           db #00                                                          ; полный байт цены колонки Наличие
                ends
                assert FOwnedCargoRow == #02

                struct FEquipmentQuantityCode
Code            db #00                                                          ; код количества оборудования, 81..FF инвертируются, 80 останавливает печать
                ends
                assert FEquipmentQuantityCode == #01

                struct FSpawnDataPointer
Address         dw #0000                                                        ; доказанный адрес исходной строки в перенесённом ядре
                ends
                assert FSpawnDataPointer == #02

                struct FSpawnTemplateRow
Delta0          dw #0000                                                        ; знаковая поправка к первой компоненте
Delta1          dw #0000                                                        ; знаковая поправка ко второй компоненте
Delta2          dw #0000                                                        ; знаковая поправка к третьей компоненте
ModelOffset     db #00                                                          ; байтовое смещение, записываемое в FActionRecord.ModelOffset
OffsetPhase1    db #00                                                          ; байт, записываемый в FActionRecord.OffsetPhase1
                ends
                assert FSpawnTemplateRow == #08

                struct FSpawnTemplateEnd
Unknown00       db #00                                                          ; Unknown, младший FF авторского слова 80FF, отдельная роль не установлена
EndCode         db #00                                                          ; код 80 завершает обход, проверяется отдельно от предыдущих восьми байтов
                ends
                assert FSpawnTemplateEnd == #02

                struct FSpawnModelPair
ModelOffset     db #00                                                          ; байтовое смещение, записываемое в FActionRecord.ModelOffset
RecordByte0F    db #00                                                          ; байт, записываемый в FActionRecord.Phase2OrTarget, смысл зависит от класса
                ends
                assert FSpawnModelPair == #02

                struct FOverlayGlyphPhase
Row0Left        db #00                                                          ; пиксели левой колонки строки 0, объединяются с буфером через XOR
Row0Right       db #00                                                          ; пиксели правой колонки строки 0, объединяются с буфером через XOR
Row1Left        db #00                                                          ; пиксели левой колонки строки 1, объединяются с буфером через XOR
Row1Right       db #00                                                          ; пиксели правой колонки строки 1, объединяются с буфером через XOR
Row2Left        db #00                                                          ; пиксели левой колонки строки 2, объединяются с буфером через XOR
Row2Right       db #00                                                          ; пиксели правой колонки строки 2, объединяются с буфером через XOR
Row3Left        db #00                                                          ; пиксели левой колонки строки 3, объединяются с буфером через XOR
Row3Right       db #00                                                          ; пиксели правой колонки строки 3, объединяются с буфером через XOR
Row4Left        db #00                                                          ; пиксели левой колонки строки 4, объединяются с буфером через XOR
Row4Right       db #00                                                          ; пиксели правой колонки строки 4, объединяются с буфером через XOR
Row5Left        db #00                                                          ; пиксели левой колонки строки 5, объединяются с буфером через XOR
Row5Right       db #00                                                          ; пиксели правой колонки строки 5, объединяются с буфером через XOR
Row6Left        db #00                                                          ; пиксели левой колонки строки 6, объединяются с буфером через XOR
Row6Right       db #00                                                          ; пиксели правой колонки строки 6, объединяются с буфером через XOR
Row7Left        db #00                                                          ; пиксели левой колонки строки 7, объединяются с буфером через XOR
Row7Right       db #00                                                          ; пиксели правой колонки строки 7, объединяются с буфером через XOR
                ends
                assert FOverlayGlyphPhase == #10

                struct FBasicLineHeader
LineHigh        db #00                                                          ; старший байт номера строки, номер хранится big-endian
LineLow         db #00                                                          ; младший байт номера строки
BodyLength      dw #0000                                                        ; длина тела little-endian, включает завершающий CR
                ends
                assert FBasicLineHeader == #04

                struct FBasicSmallInteger
Exponent        db #00                                                          ; нулевой байт выбирает компактное целое вместо плавающей точки
Sign            db #00                                                          ; ноль для исходного положительного целого
Low             db #00                                                          ; младший байт абсолютного значения
High            db #00                                                          ; старший байт абсолютного значения
Unused          db #00                                                          ; пятый байт исходного компактного целого, сохранён как ноль
                ends
                assert FBasicSmallInteger == #05

                struct FIntroCoordinateSample
Value           db #00                                                          ; беззнаковый исходный отсчёт координатной таблицы, не готовый адрес и не флаги
                ends
                assert FIntroCoordinateSample == #01

                struct FTrDosBasicAutostart
Marker80        db #80                                                          ; первый байт сигнатуры автозапуска, не самостоятельный флаг
MarkerAA        db #AA                                                          ; второй байт сигнатуры автозапуска
LineNumber      dw #0000                                                        ; номер первой выполняемой строки BASIC, little-endian
                ends
                assert FTrDosBasicAutostart == #04

                struct FIntroLookupParameter
InitialIYL      db #00                                                          ; исходный IYL для одной из 63 последовательностей построителя
                ends
                assert FIntroLookupParameter == #01

                struct FIntroAttributeSeed
Nibbles         db #00                                                          ; старший полубайт столбца и младший полубайт строки матрицы атрибутов
                ends
                assert FIntroAttributeSeed == #01

                struct FIntroColumnTailSample
LookupCode      db #00                                                          ; код выборки хвоста, затем прибавляются фазы косвенной адресации
                ends
                assert FIntroColumnTailSample == #01

                struct FIntroScaleSample
Offset          db #00                                                          ; добавка 0..15 к базовому индексу строки масштаба 56
                ends
                assert FIntroScaleSample == #01


                ; Исходная физическая запись связанного состояния
                struct FOverlayLine
Header          db #00                                                          ; B2, открытый XOR-сегмент из двух вершин
FirstIndex      db #00                                                          ; байтовое смещение первой FRenderProjectedPoint
SecondIndex     db #00                                                          ; байтовое смещение второй FRenderProjectedPoint
Terminator      db #00                                                          ; полный нулевой конец потока
                ends
                assert FOverlayLine == #04
                assert FOverlayLine.Header == #00
                assert FOverlayLine.FirstIndex == #01
                assert FOverlayLine.SecondIndex == #02
                assert FOverlayLine.Terminator == #03

                ; Исходная физическая запись связанного состояния
                struct FMissileRepeatDelay
Counter         db #00                                                          ; начальное значение MissileRepeatDelay после попытки пуска, авторский счётчик RCO
                ends
                assert FMissileRepeatDelay == #01
                assert FMissileRepeatDelay.Counter == #00


                ; Полный числовой код элемента списка, отдельные битовые флаги не задаются
                struct FCandidateCode
Code            db #00                                                          ; 00..FD индекс записи, FF пропуск, FE конец списка
                ends
                assert FCandidateCode == 1
                assert FCandidateCode.Code == 0


                ; Двухбайтовое слово базиса, не код доступности FActionRecord
                struct FBasisWord
Low             db #00                                                          ; младший байт слова базиса
High            db #00                                                          ; старший байт, RenderSceneFrame передаёт его с заменой 80 на 81
                ends
                assert FBasisWord == 2
                assert FBasisWord.Low == 0
                assert FBasisWord.High == 1


                ; Байтовый код либо счётчик оборудования по физической раскладке авторского описания
                struct FEquipmentCode
Value           db #00                                                          ; полный байт, трактовка счётчика, наличия и маркера зависит от записи
                ends
                assert FEquipmentCode == 1
                assert FEquipmentCode.Value == 0


                ; Физические знаковые управления, это числовые байты, не наборы флагов
                struct FFlightControls
YControl        db #00                                                          ; управление проходом Y
XControl        db #00                                                          ; управление проходом X
TurnControl     db #00                                                          ; отрицание по модулю 256 задаёт индекс синусоиды
                ends
                assert FFlightControls == 3
                assert FFlightControls.YControl == 0
                assert FFlightControls.XControl == 1
                assert FFlightControls.TurnControl == 2

                ; Физическое зерно BuildParameterTables, размещено в общем ядре ACTION
                struct FParameterSeeds
SeedFirst       dw #0000                                                        ; первое слово зерна
SeedSecond      dw #0000                                                        ; второе слово зерна
StepControl     db #00                                                          ; управляющий байт количества повторов
                ends
                assert FParameterSeeds == 5
                assert FParameterSeeds.SeedFirst == 0
                assert FParameterSeeds.SeedSecond == 2
                assert FParameterSeeds.StepControl == 4


                ; Упакованная пиксельная точка линии, порядок отличается от FBufferPoint
                struct FLineRasterPoint
Second          db #00                                                          ; горизонтальная пиксельная координата, младший байт слова
First           db #00                                                          ; вертикальная пиксельная координата, старший байт слова
                ends
                assert FLineRasterPoint == 2
                assert FLineRasterPoint.Second == 0
                assert FLineRasterPoint.First == 1

                ; Полные коды команд для выбранного режима линии, не независимые флаги
                struct FLineRasterMode
PixelOpcode     db #00                                                          ; A1 для AND C, B1 для OR C либо A9 для XOR C
BranchOpcode    db #00                                                          ; 30 для JR NC либо 38 для JR C
                ends
                assert FLineRasterMode == 2
                assert FLineRasterMode.PixelOpcode == 0
                assert FLineRasterMode.BranchOpcode == 1

                ; Префикс разделённой таблицы CF00/D000, индексы 03 и 07 используются как состояние
                struct FClipDispatchPrefix
AppendPointLow  db #00                                                          ; младший байт адреса AppendSecondClipPoint.Entry
ToRightLow      db #00                                                          ; младший байт адреса ClipInsideToRight.Entry
ToLeftLow       db #00                                                          ; младший байт адреса ClipInsideToLeft.Entry
CornerBlock     db #00                                                          ; нулевой байт разрешает запись углов, любой ненулевой запрещает
ToBottomLow     db #00                                                          ; младший байт адреса ClipInsideToBottom.Entry
ToBottomRLow    db #00                                                          ; младший байт адреса ClipInsideToBottomRight.Entry
ToBottomLLow    db #00                                                          ; младший байт адреса ClipInsideToBottomLeft.Entry
SeenFlags       db #00                                                          ; отметки TL, TR, BL, BR в битах 3..0, обработчики углов сохраняют 7..4
                ends
                assert FClipDispatchPrefix == 8
                assert FClipDispatchPrefix.AppendPointLow == 0
                assert FClipDispatchPrefix.ToRightLow == 1
                assert FClipDispatchPrefix.ToLeftLow == 2
                assert FClipDispatchPrefix.CornerBlock == 3
                assert FClipDispatchPrefix.ToBottomLow == 4
                assert FClipDispatchPrefix.ToBottomRLow == 5
                assert FClipDispatchPrefix.ToBottomLLow == 6
                assert FClipDispatchPrefix.SeenFlags == 7

                ; Строка старших байтов разделённого диспетчера, младшая тетрада выбирает поле
                struct FClipTargetHighRow
SecondSides0    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 0
SecondSides1    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 1
SecondSides2    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 2
SecondSides3    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 3
SecondSides4    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 4
SecondSides5    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 5
SecondSides6    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 6
SecondSides7    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 7
SecondSides8    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 8
SecondSides9    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 9
SecondSidesA    db #00                                                          ; старший байт адреса при младшей тетраде второго кода A
SecondSidesB    db #00                                                          ; старший байт адреса при младшей тетраде второго кода B
SecondSidesC    db #00                                                          ; старший байт адреса при младшей тетраде второго кода C
SecondSidesD    db #00                                                          ; старший байт адреса при младшей тетраде второго кода D
SecondSidesE    db #00                                                          ; старший байт адреса при младшей тетраде второго кода E
SecondSidesF    db #00                                                          ; старший байт адреса при младшей тетраде второго кода F
                ends
                assert FClipTargetHighRow == 16
                assert FClipTargetHighRow.SecondSides0 == 0
                assert FClipTargetHighRow.SecondSides1 == 1
                assert FClipTargetHighRow.SecondSides2 == 2
                assert FClipTargetHighRow.SecondSides3 == 3
                assert FClipTargetHighRow.SecondSides4 == 4
                assert FClipTargetHighRow.SecondSides5 == 5
                assert FClipTargetHighRow.SecondSides6 == 6
                assert FClipTargetHighRow.SecondSides7 == 7
                assert FClipTargetHighRow.SecondSides8 == 8
                assert FClipTargetHighRow.SecondSides9 == 9
                assert FClipTargetHighRow.SecondSidesA == 10
                assert FClipTargetHighRow.SecondSidesB == 11
                assert FClipTargetHighRow.SecondSidesC == 12
                assert FClipTargetHighRow.SecondSidesD == 13
                assert FClipTargetHighRow.SecondSidesE == 14
                assert FClipTargetHighRow.SecondSidesF == 15

                ; Сохранение и установка крайних пикселей по формуле (старый AND Preserve) OR Apply
                struct FPolygonEdgeMask
Preserve        db #00                                                          ; единичные биты сохраняют прежние пиксели вне заполняемой части
Apply           db #00                                                          ; единичные биты устанавливают пиксели выбранного шаблона
                ends
                assert FPolygonEdgeMask == 2
                assert FPolygonEdgeMask.Preserve == 0
                assert FPolygonEdgeMask.Apply == 1

                ; Физическая часть строки младших адресов, пропущенные части заняты отдельными структурами
                struct FClipTargetLowRow
SecondSides0    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 0
SecondSides1    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 1
SecondSides2    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 2
SecondSides3    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 3
SecondSides4    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 4
SecondSides5    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 5
SecondSides6    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 6
SecondSides7    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 7
SecondSides8    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 8
SecondSides9    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 9
SecondSidesA    db #00                                                          ; младший байт адреса при младшей тетраде второго кода A
SecondSidesB    db #00                                                          ; младший байт адреса при младшей тетраде второго кода B
SecondSidesC    db #00                                                          ; младший байт адреса при младшей тетраде второго кода C
SecondSidesD    db #00                                                          ; младший байт адреса при младшей тетраде второго кода D
SecondSidesE    db #00                                                          ; младший байт адреса при младшей тетраде второго кода E
SecondSidesF    db #00                                                          ; младший байт адреса при младшей тетраде второго кода F
                ends
                assert FClipTargetLowRow == 16
                assert FClipTargetLowRow.SecondSides0 == 0
                assert FClipTargetLowRow.SecondSides1 == 1
                assert FClipTargetLowRow.SecondSides2 == 2
                assert FClipTargetLowRow.SecondSides3 == 3
                assert FClipTargetLowRow.SecondSides4 == 4
                assert FClipTargetLowRow.SecondSides5 == 5
                assert FClipTargetLowRow.SecondSides6 == 6
                assert FClipTargetLowRow.SecondSides7 == 7
                assert FClipTargetLowRow.SecondSides8 == 8
                assert FClipTargetLowRow.SecondSides9 == 9
                assert FClipTargetLowRow.SecondSidesA == 10
                assert FClipTargetLowRow.SecondSidesB == 11
                assert FClipTargetLowRow.SecondSidesC == 12
                assert FClipTargetLowRow.SecondSidesD == 13
                assert FClipTargetLowRow.SecondSidesE == 14
                assert FClipTargetLowRow.SecondSidesF == 15

                ; Физическая часть строки младших адресов, пропущенные части заняты отдельными структурами
                struct FClipTargetLowHead
SecondSides0    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 0
SecondSides1    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 1
SecondSides2    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 2
SecondSides3    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 3
SecondSides4    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 4
SecondSides5    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 5
SecondSides6    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 6
SecondSides7    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 7
SecondSides8    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 8
SecondSides9    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 9
SecondSidesA    db #00                                                          ; младший байт адреса при младшей тетраде второго кода A
                ends
                assert FClipTargetLowHead == 11
                assert FClipTargetLowHead.SecondSides0 == 0
                assert FClipTargetLowHead.SecondSides1 == 1
                assert FClipTargetLowHead.SecondSides2 == 2
                assert FClipTargetLowHead.SecondSides3 == 3
                assert FClipTargetLowHead.SecondSides4 == 4
                assert FClipTargetLowHead.SecondSides5 == 5
                assert FClipTargetLowHead.SecondSides6 == 6
                assert FClipTargetLowHead.SecondSides7 == 7
                assert FClipTargetLowHead.SecondSides8 == 8
                assert FClipTargetLowHead.SecondSides9 == 9
                assert FClipTargetLowHead.SecondSidesA == 10

                ; Физическая часть строки младших адресов, пропущенные части заняты отдельными структурами
                struct FClipTargetLowTail
SecondSidesB    db #00                                                          ; младший байт адреса при младшей тетраде второго кода B
SecondSidesC    db #00                                                          ; младший байт адреса при младшей тетраде второго кода C
SecondSidesD    db #00                                                          ; младший байт адреса при младшей тетраде второго кода D
SecondSidesE    db #00                                                          ; младший байт адреса при младшей тетраде второго кода E
SecondSidesF    db #00                                                          ; младший байт адреса при младшей тетраде второго кода F
                ends
                assert FClipTargetLowTail == 5
                assert FClipTargetLowTail.SecondSidesB == 0
                assert FClipTargetLowTail.SecondSidesC == 1
                assert FClipTargetLowTail.SecondSidesD == 2
                assert FClipTargetLowTail.SecondSidesE == 3
                assert FClipTargetLowTail.SecondSidesF == 4

                ; Физическая часть строки младших адресов, пропущенные части заняты отдельными структурами
                struct FClipTargetLowAlias
SecondSides8    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 8
SecondSides9    db #00                                                          ; младший байт адреса при младшей тетраде второго кода 9
SecondSidesA    db #00                                                          ; младший байт адреса при младшей тетраде второго кода A
                ends
                assert FClipTargetLowAlias == 3
                assert FClipTargetLowAlias.SecondSides8 == 0
                assert FClipTargetLowAlias.SecondSides9 == 1
                assert FClipTargetLowAlias.SecondSidesA == 2


                ; Физические байты существующего рабочего состояния ACTION
                struct FRenderQueueCursor
Head            db #00                                                          ; младшее смещение головы в странице 8F, рабочий конец цепочки 01
FreeOffset      db #00                                                          ; смещение следующего узла, рабочий шаг 0E и признак исчерпания FC
                ends
                assert FRenderQueueCursor == 2
                assert FRenderQueueCursor.Head == 0
                assert FRenderQueueCursor.FreeOffset == 1

                ; Физические байты существующего рабочего состояния ACTION
                struct FClipOutputState
OutputSize      db #00                                                          ; байтовая длина выходных пар Second, First в странице 90
                ends
                assert FClipOutputState == 1
                assert FClipOutputState.OutputSize == 0

                ; Физические байты существующего рабочего состояния ACTION
                struct FActionParameterSet
Link1ABaseLimit db #00                                                          ; поле 00, базовый порог связи 1A при сброшенном бите 3 LinkFlags, адрес изменяемого операнда F79C
LegacyHitPower  db #00                                                          ; архивная мощность лазера по игроку PMLPI, текущий ApplyParameterSet читает без применения
OtherLinkLimit  db #00                                                          ; поле 02, порог для LinkedIndex, отличного от 1A, адрес изменяемого операнда F798
RegenPhaseStep  db #00                                                          ; поле 03, шаг фазы восстановления первой шкалы, адрес изменяемого операнда A968
PairedLineStep  db #00                                                          ; поле 04, шаг фазового допуска RequestPairedAimLines, адрес изменяемого операнда 63B9
ThirdGaugeStep  db #00                                                          ; поле 05, шаг фазы повышения третьей шкалы, адрес изменяемого операнда A8B5
SpawnLowAndBias db #00                                                          ; общий начальный SpawnLowLimit и база пересчёта SpawnBiasBase
Class0RLimit    db #00                                                          ; поле 07, изменяемый операнд CP аппаратного R в ConfigureClass0Link, адрес изменяемого операнда 6615
RandomLowLimit  db #00                                                          ; поле 08, изменяемый операнд CP младшего байта Stream10 в FindFilteredRecordOr26, адрес изменяемого операнда E6E7
LinkedRLimit    db #00                                                          ; поле 09, порог R обратной связи в CheckAndToggleLinkedOverlay, адрес изменяемого операнда E823
Class3RLimit    db #00                                                          ; поле 0A, изменяемый операнд CP аппаратного R в ConfigureClass3Link, адрес изменяемого операнда 65E5
SavedLowLimit   db #00                                                          ; поле 0B, нижний предел младшего байта сохранённого слова с верхним байтом 23
SpawnValueMask  db #00                                                          ; поле 0C, маска OR кандидата Unknown13 в обоих создателях, адрес изменяемого операнда 7E07
SpawnValueCap   db #00                                                          ; поле 0D, исключённый верхний предел Unknown13, ноль даёт FF, адрес изменяемого операнда 7E09
SpawnField11    db #00                                                          ; поле 0E, значение Unknown11 после непересекающихся случайных масок, адрес изменяемого операнда 7DE4
                ends
                assert FActionParameterSet == 15
                assert FActionParameterSet.Link1ABaseLimit == 0
                assert FActionParameterSet.LegacyHitPower == 1
                assert FActionParameterSet.OtherLinkLimit == 2
                assert FActionParameterSet.RegenPhaseStep == 3
                assert FActionParameterSet.PairedLineStep == 4
                assert FActionParameterSet.ThirdGaugeStep == 5
                assert FActionParameterSet.SpawnLowAndBias == 6
                assert FActionParameterSet.Class0RLimit == 7
                assert FActionParameterSet.RandomLowLimit == 8
                assert FActionParameterSet.LinkedRLimit == 9
                assert FActionParameterSet.Class3RLimit == 10
                assert FActionParameterSet.SavedLowLimit == 11
                assert FActionParameterSet.SpawnValueMask == 12
                assert FActionParameterSet.SpawnValueCap == 13
                assert FActionParameterSet.SpawnField11 == 14

                struct FArchivedEyeState
EyeX            dw #0000                                                        ; исходное слово EYE_X
EyeY            dw #0000                                                        ; исходное слово EYE_Y
EyeZ            dw #0000                                                        ; исходное слово EYE_Z
StpA            db #00                                                          ; авторский STPA, потребитель не установлен
StpB            db #00                                                          ; авторский STPB, потребитель не установлен
StpG            db #00                                                          ; авторский STPG, потребитель не установлен
                ends
                assert FArchivedEyeState == #09

                struct FArchivedSpawnChances
Pirates         db #00                                                          ; пираты
Civilians       db #00                                                          ; мирные корабли
Police          db #00                                                          ; полиция
Military        db #00                                                          ; военные
Legion          db #00                                                          ; легионеры
SecondPirates   db #00                                                          ; вторая группа пиратов
Ufo             db #00                                                          ; НЛО
SecondUfo       db #00                                                          ; вторая группа НЛО
Hermit          db #00                                                          ; отшельник
                ends
                assert FArchivedSpawnChances == #09


                ; Существующее физическое состояние панели, новая память не выделяется
                struct FFlightBcdCounter
MidHigh         db #00                                                          ; BCD-пара разрядов 10^4 и 10^5, регистр E
High            db #00                                                          ; BCD-пара разрядов 10^6 и 10^7, регистр D
Low             db #00                                                          ; BCD-пара разрядов 10^0 и 10^1, регистр L
MidLow          db #00                                                          ; BCD-пара разрядов 10^2 и 10^3, регистр H
                ends
                assert FFlightBcdCounter == 4
                assert FFlightBcdCounter.MidHigh == 0
                assert FFlightBcdCounter.High == 1
                assert FFlightBcdCounter.Low == 2
                assert FFlightBcdCounter.MidLow == 3

                ; Существующее физическое состояние панели, новая память не выделяется
                struct FPanelEventFlags
                ; Разряды 7..0, ? ? ? ? ? F B C, маски C=#01, B=#02, F=#04
                ; Нулевое значение не запрашивает списание, мигание и связанный звук
Flags           db #00                                                          ; UpdateFrame использует биты 0, 1 и 2, остальные биты не интерпретируются
                ends
                assert FPanelEventFlags == 1
                assert FPanelEventFlags.Flags == 0

                ; Существующее физическое состояние панели, новая память не выделяется
                struct FPanelSignedWord
Value           dw #0000                                                        ; знаковая скорость движения игрока и источник шестой шкалы, физическая единица неизвестна
                ends
                assert FPanelSignedWord == 2
                assert FPanelSignedWord.Value == 0

                ; Существующее физическое состояние панели, новая память не выделяется
                struct FPanelGaugeValue
Value           db #00                                                          ; уровень защиты игрока SHILD, источник первой шкалы
                ends
                assert FPanelGaugeValue == 1
                assert FPanelGaugeValue.Value == 0


                ; Физические поля существующего контекста ACTION
                struct FContextWordPair
OtherFirst      dw #0000                                                        ; первое слово для сравнения с SeedFirst
OtherSecond     dw #0000                                                        ; второе слово для сравнения с SeedSecond
                ends
                assert FContextWordPair == 4
                assert FContextWordPair.OtherFirst == 0
                assert FContextWordPair.OtherSecond == 2

                ; Физические поля существующего контекста ACTION
                struct FContextPublishIndex
SelectedIndex   db #00                                                          ; байт публикации при совпадении обеих пар контекста
                ends
                assert FContextPublishIndex == 1
                assert FContextPublishIndex.SelectedIndex == 0

                ; Физические поля существующего контекста ACTION
                struct FFlightStatus
Code            db #00                                                          ; статус игрока, переносится на станцию для сценария штрафов
                ends
                assert FFlightStatus == 1
                assert FFlightStatus.Code == 0

                ; Физические поля существующего контекста ACTION
                struct FActionRankScore
Value           dw #0000                                                        ; очки ранга за уничтожение целей учитываемых классов, исходное значение ACTION
                ends
                assert FActionRankScore == 2
                assert FActionRankScore.Value == 0

                ; Физические поля существующего контекста ACTION
                struct FFlightTonnage
Used            db #00                                                          ; учтённый тоннаж, изменяется в полёте по модулю 256
Capacity        db #00                                                          ; беззнаковый предел при пополнении топлива и подборе
                ends
                assert FFlightTonnage == 2
                assert FFlightTonnage.Used == 0
                assert FFlightTonnage.Capacity == 1


                ; Заголовок текущей модели, слово снимка HeaderWord0
                struct FRenderHeaderState
ModeBits        db #00                                                          ; бит 0 задаёт одноосный расчёт, RenderSceneFrame пишет 00 либо 01
ModelByteOffset db #00                                                          ; байтовое смещение слова указателя модели в таблице OBJECT3D
                ends
                assert FRenderHeaderState == 2
                assert FRenderHeaderState.ModeBits == 0
                assert FRenderHeaderState.ModelByteOffset == 1



                ; Физический заголовок растровой полосы BANK, метаданные не задают банк загрузки
                struct FScreenBitmapStrip
ScreenAddress   dw #0000                                                        ; слово координат в раскладке ULA-экрана
Height          db #00                                                          ; количество следующих строк по шесть байтов
                ends
                assert FScreenBitmapStrip == 3
                assert FScreenBitmapStrip.ScreenAddress == 0
                assert FScreenBitmapStrip.Height == 2

                ; Исходный байт правила счётчика при сборе, младшие шесть битов не переименовываются в придуманные флаги
                struct FTractorCargoRule
Control         db #00                                                          ; поле 7..6, нуль учитывает количество в Current, ненулевое значение исключает
                ends
                assert FTractorCargoRule == 1
                assert FTractorCargoRule.Control == 0


                ; Физическая часть существующего рабочего состояния, адреса и промежуточные маски сохранены
                struct FClipLineHead
CurrentSecond   dw #0000                                                        ; полная горизонтальная компонента первой точки текущего сегмента
CurrentFirst    dw #0000                                                        ; полная вертикальная компонента первой точки текущего сегмента
NextSecond      dw #0000                                                        ; полная горизонтальная компонента следующей точки ломаной
                ends
                assert FClipLineHead == 6
                assert FClipLineHead.CurrentSecond == 0
                assert FClipLineHead.CurrentFirst == 2
                assert FClipLineHead.NextSecond == 4

                ; Физическая часть существующего рабочего состояния, адреса и промежуточные маски сохранены
                struct FClipLineTail
NextFirst       dw #0000                                                        ; полная вертикальная компонента следующей точки ломаной
CurrentCode     db #00                                                          ; полный ClipCode первой точки, ноль означает локальный отказ подготовки
NextCode        db #00                                                          ; полный ClipCode следующей точки, ноль означает локальный отказ подготовки
                ends
                assert FClipLineTail == 4
                assert FClipLineTail.NextFirst == 0
                assert FClipLineTail.CurrentCode == 2
                assert FClipLineTail.NextCode == 3

                ; Физическая часть существующего рабочего состояния, адреса и промежуточные маски сохранены
                struct FFaceGateCode
Code            db #00                                                          ; полный код ориентации, ноль допускает связанную ломаную, любой ненулевой байт запрещает
                ends
                assert FFaceGateCode == 1
                assert FFaceGateCode.Code == 0


                struct FActionNewsState
State           db #00                                                          ; исходное состояние NEWS по авторской заметке, игровые коды не проверены
Byte01          db #00                                                          ; второй исходный байт строки 1, 0, назначение неизвестно
Word02          dw #0000                                                        ; первое слово нулевой пары, назначение неизвестно
Word04          dw #0000                                                        ; второе слово нулевой пары, назначение неизвестно
Byte06          db #00                                                          ; последний исходный ноль NEWS, назначение неизвестно
                ends
                assert FActionNewsState == 7
                assert FActionNewsState.State == 0
                assert FActionNewsState.Byte01 == 1
                assert FActionNewsState.Word02 == 2
                assert FActionNewsState.Word04 == 4
                assert FActionNewsState.Byte06 == 6

                struct FArchivedStationJob
DestKeyFirst    dw #0000                                                        ; первое слово ключа доставки
DestKeySecond   dw #0000                                                        ; второе слово ключа доставки
DeadlineDay     dw #0000                                                        ; день окончания срока
DeadlineTime    dw #0000                                                        ; вторая пара байтов срока
CreatedDay      dw #0000                                                        ; день создания
CreatedTime     dw #0000                                                        ; вторая пара байтов времени создания
Payment         dw #0000                                                        ; сумма оплаты
WeightFlags     db #00                                                          ; биты 6..0, вес, бит 7, миссия принята
Planet          db #00                                                          ; номер планеты назначения
                ends
                assert FArchivedStationJob == #10

                struct FActionOrderRecord
Marker          db #00                                                          ; исходное значение FF из записи ORDER, проверка маркера не найдена
Byte01          db #00                                                          ; байт тела по смещению 1, игровое назначение не доказано
Byte02          db #00                                                          ; байт тела по смещению 2, игровое назначение не доказано
Byte03          db #00                                                          ; байт тела по смещению 3, игровое назначение не доказано
Byte04          db #00                                                          ; байт тела по смещению 4, игровое назначение не доказано
Byte05          db #00                                                          ; байт тела по смещению 5, игровое назначение не доказано
Byte06          db #00                                                          ; байт тела по смещению 6, игровое назначение не доказано
Byte07          db #00                                                          ; байт тела по смещению 7, игровое назначение не доказано
Byte08          db #00                                                          ; байт тела по смещению 8, игровое назначение не доказано
Byte09          db #00                                                          ; байт тела по смещению 9, игровое назначение не доказано
Byte10          db #00                                                          ; байт тела по смещению 10, игровое назначение не доказано
Byte11          db #00                                                          ; байт тела по смещению 11, игровое назначение не доказано
Byte12          db #00                                                          ; байт тела по смещению 12, игровое назначение не доказано
Byte13          db #00                                                          ; байт тела по смещению 13, игровое назначение не доказано
Byte14          db #00                                                          ; байт тела по смещению 14, игровое назначение не доказано
Byte15          db #00                                                          ; байт тела по смещению 15, игровое назначение не доказано
                ends
                assert FActionOrderRecord == 16
                assert FActionOrderRecord.Marker == 0
                assert FActionOrderRecord.Byte01 == 1
                assert FActionOrderRecord.Byte02 == 2
                assert FActionOrderRecord.Byte03 == 3
                assert FActionOrderRecord.Byte04 == 4
                assert FActionOrderRecord.Byte05 == 5
                assert FActionOrderRecord.Byte06 == 6
                assert FActionOrderRecord.Byte07 == 7
                assert FActionOrderRecord.Byte08 == 8
                assert FActionOrderRecord.Byte09 == 9
                assert FActionOrderRecord.Byte10 == 10
                assert FActionOrderRecord.Byte11 == 11
                assert FActionOrderRecord.Byte12 == 12
                assert FActionOrderRecord.Byte13 == 13
                assert FActionOrderRecord.Byte14 == 14
                assert FActionOrderRecord.Byte15 == 15

                struct FHyperJumpCost
Cost            db #00                                                          ; базовая стоимость гиперперехода, маршрут Preferred удваивает её в слове
                ends
                assert FHyperJumpCost == 1
                assert FHyperJumpCost.Cost == 0


                struct FFinalSyncPointers
AfterRow18      dw #0000                                                        ; указатель вставки после восемнадцатого знакоместного ряда, установлен построителем
AfterRow10      dw #0000                                                        ; указатель вставки после десятого знакоместного ряда, установлен построителем
                ends
                assert FFinalSyncPointers == 4
                assert FFinalSyncPointers.AfterRow18 == 0
                assert FFinalSyncPointers.AfterRow10 == 2

                struct FPreviewObjectHeader
First           dw #0000                                                        ; первая координата исходной записи, прочитана первым POP
Second          dw #0000                                                        ; вторая координата исходной записи, прочитана вторым POP
Third           dw #0000                                                        ; третья координата исходной записи, управление принимает значения 512..4095
ModelOffset     db #00                                                          ; байтовое смещение пары указателей модели, устанавливается SetupPreviewModel
                ends
                assert FPreviewObjectHeader == 7
                assert FPreviewObjectHeader.First == 0
                assert FPreviewObjectHeader.Second == 2
                assert FPreviewObjectHeader.Third == 4
                assert FPreviewObjectHeader.ModelOffset == 6


                struct FStationEventCodes
InterfaceCode   db #00                                                          ; код интерфейсного события, используется при передаче действия и выборе меню
ScriptCode      db #00                                                          ; код события для LANG, ReadEventCode переносит его в стек выражений
                ends
                assert FStationEventCodes == 2
                assert FStationEventCodes.InterfaceCode == 0
                assert FStationEventCodes.ScriptCode == 1

                struct FSpecialRecordPrefix
Component0      dw #0000                                                        ; первое слово родителя для SpawnPrepared, UpdateFrame очищает старший байт
Component1      dw #0000                                                        ; второе слово родителя, его старший байт совпадает с позицией до списка эффектов
Component2      dw #0000                                                        ; третье слово родителя для SpawnPrepared
ModelOffset     db #00                                                          ; байтовое смещение модели игрока, PrepareLargeEffect читает заголовок OBJECT3D
OffsetPhase0    db #00                                                          ; первый фазовый байт, копируется из родителя в создаваемую запись
OffsetPhase1    db #00                                                          ; второй фазовый байт, копируется из родителя в создаваемую запись
OffsetPhase2    db #00                                                          ; третий фазовый байт, копируется из родителя в создаваемую запись
PlayerMarker    db #00                                                          ; маркер игрока FF, на ближнем пути State08 запрещает освобождение текущей ракеты
LinkedIndex     db #00                                                          ; индекс связанной записи, при создании ракеты с целью 1A получает её индекс
                ends
                assert FSpecialRecordPrefix == 12
                assert FSpecialRecordPrefix.Component0 == 0
                assert FSpecialRecordPrefix.Component1 == 2
                assert FSpecialRecordPrefix.Component2 == 4
                assert FSpecialRecordPrefix.ModelOffset == 6
                assert FSpecialRecordPrefix.OffsetPhase0 == 7
                assert FSpecialRecordPrefix.OffsetPhase1 == 8
                assert FSpecialRecordPrefix.OffsetPhase2 == 9
                assert FSpecialRecordPrefix.PlayerMarker == 10
                assert FSpecialRecordPrefix.LinkedIndex == 11


                struct FMeasuredDistance
Value           db #00                                                          ; результат MeasureCoordinateDistance, FF при переполнении
                ends
                assert FMeasuredDistance == 1
                assert FMeasuredDistance.Value == 0

                struct FTransitionCounter
Count           db #00                                                          ; байтовый счётчик, станционный переход условно прибавляет 30
                ends
                assert FTransitionCounter == 1
                assert FTransitionCounter.Count == 0

                struct FRenderInputSnapshot
InputX          dw #0000                                                        ; первое исходное слово текущего объекта до допуска по старшему байту
InputY          dw #0000                                                        ; второе исходное слово после допуска X, до допуска Y
InputDepth      dw #0000                                                        ; третье исходное слово после допуска Y, до допуска глубины
                ends
                assert FRenderInputSnapshot == 6
                assert FRenderInputSnapshot.InputX == 0
                assert FRenderInputSnapshot.InputY == 2
                assert FRenderInputSnapshot.InputDepth == 4

                struct FBodyDrawMode
Mode            db #00                                                          ; режим малого рисователя, поддерживаются полные коды 0..3
                ends
                assert FBodyDrawMode == 1
                assert FBodyDrawMode.Mode == 0


                struct FBackdropSectorCount
Sectors         db #00                                                          ; число физических секторов упакованного фона
                ends
                assert FBackdropSectorCount == 1
                assert FBackdropSectorCount.Sectors == 0

                struct FStationItemIndexPair
Low             db #00                                                          ; младший байт ключа, проверяется первым при поиске
High            db #00                                                          ; старший байт ключа, FF означает свободную пару
                ends
                assert FStationItemIndexPair == 2
                assert FStationItemIndexPair.Low == 0
                assert FStationItemIndexPair.High == 1

                struct FEquipmentPrice
Price           dw #0000                                                        ; слово для колонки «Цена» и стекового запроса LANG
                ends
                assert FEquipmentPrice == 2
                assert FEquipmentPrice.Price == 0

                struct FEquipmentWeight
Threshold       db #00                                                          ; нижний допустимый признак L для вывода веса и прямой проверки
Weight          db #00                                                          ; выводимый вес и множитель взвешенной суммы
                ends
                assert FEquipmentWeight == 2
                assert FEquipmentWeight.Threshold == 0
                assert FEquipmentWeight.Weight == 1

                struct FSecondWeightFactor
Threshold       db #00                                                          ; нижний допустимый признак L в прямой проверке второго набора
Factor          db #00                                                          ; множитель третьего слагаемого и байт запроса ReadSecondaryEquipmentWeight
                ends
                assert FSecondWeightFactor == 2
                assert FSecondWeightFactor.Threshold == 0
                assert FSecondWeightFactor.Factor == 1

                struct FNeighborBounds
Left            db #00                                                          ; число шагов влево кодируется отрицанием по модулю 256
Right           db #00                                                          ; число шагов вправо без преобразования
                ends
                assert FNeighborBounds == 2
                assert FNeighborBounds.Left == 0
                assert FNeighborBounds.Right == 1

                struct FParameterRowGroup
First           db #00                                                          ; первая строка получает этот байт без добавки индекса
Row01           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row02           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row03           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row04           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row05           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row06           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row07           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row08           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Spacing0        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing1        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing2        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing3        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing4        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing5        db #00                                                          ; исходный байт между группами, DE10 его не читает
Spacing6        db #00                                                          ; исходный байт между группами, DE10 его не читает
                ends
                assert FParameterRowGroup == 16
                assert FParameterRowGroup.First == 0
                assert FParameterRowGroup.Row01 == 1
                assert FParameterRowGroup.Row02 == 2
                assert FParameterRowGroup.Row03 == 3
                assert FParameterRowGroup.Row04 == 4
                assert FParameterRowGroup.Row05 == 5
                assert FParameterRowGroup.Row06 == 6
                assert FParameterRowGroup.Row07 == 7
                assert FParameterRowGroup.Row08 == 8
                assert FParameterRowGroup.Spacing0 == 9
                assert FParameterRowGroup.Spacing1 == 10
                assert FParameterRowGroup.Spacing2 == 11
                assert FParameterRowGroup.Spacing3 == 12
                assert FParameterRowGroup.Spacing4 == 13
                assert FParameterRowGroup.Spacing5 == 14
                assert FParameterRowGroup.Spacing6 == 15

                struct FParameterRowValues
First           db #00                                                          ; первая строка получает этот байт без добавки индекса
Row01           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row02           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row03           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row04           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row05           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row06           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row07           db #00                                                          ; база строки, к ней прибавляется средний индекс C
Row08           db #00                                                          ; база строки, к ней прибавляется средний индекс C
                ends
                assert FParameterRowValues == 9
                assert FParameterRowValues.First == 0
                assert FParameterRowValues.Row01 == 1
                assert FParameterRowValues.Row02 == 2
                assert FParameterRowValues.Row03 == 3
                assert FParameterRowValues.Row04 == 4
                assert FParameterRowValues.Row05 == 5
                assert FParameterRowValues.Row06 == 6
                assert FParameterRowValues.Row07 == 7
                assert FParameterRowValues.Row08 == 8

                struct FParameterValueGroup
Value00         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value01         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value02         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value03         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value04         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value05         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value06         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value07         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value08         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value09         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value10         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value11         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value12         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value13         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value14         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Spacing         db #00                                                          ; исходный байт между группами, DE10 его не читает
                ends
                assert FParameterValueGroup == 16
                assert FParameterValueGroup.Value00 == 0
                assert FParameterValueGroup.Value01 == 1
                assert FParameterValueGroup.Value02 == 2
                assert FParameterValueGroup.Value03 == 3
                assert FParameterValueGroup.Value04 == 4
                assert FParameterValueGroup.Value05 == 5
                assert FParameterValueGroup.Value06 == 6
                assert FParameterValueGroup.Value07 == 7
                assert FParameterValueGroup.Value08 == 8
                assert FParameterValueGroup.Value09 == 9
                assert FParameterValueGroup.Value10 == 10
                assert FParameterValueGroup.Value11 == 11
                assert FParameterValueGroup.Value12 == 12
                assert FParameterValueGroup.Value13 == 13
                assert FParameterValueGroup.Value14 == 14
                assert FParameterValueGroup.Spacing == 15

                struct FParameterValueBytes
Value00         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value01         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value02         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value03         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value04         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value05         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value06         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value07         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value08         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value09         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value10         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value11         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value12         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value13         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
Value14         db #00                                                          ; групповая прибавка к соответствующему полю Parameters
                ends
                assert FParameterValueBytes == 15
                assert FParameterValueBytes.Value00 == 0
                assert FParameterValueBytes.Value01 == 1
                assert FParameterValueBytes.Value02 == 2
                assert FParameterValueBytes.Value03 == 3
                assert FParameterValueBytes.Value04 == 4
                assert FParameterValueBytes.Value05 == 5
                assert FParameterValueBytes.Value06 == 6
                assert FParameterValueBytes.Value07 == 7
                assert FParameterValueBytes.Value08 == 8
                assert FParameterValueBytes.Value09 == 9
                assert FParameterValueBytes.Value10 == 10
                assert FParameterValueBytes.Value11 == 11
                assert FParameterValueBytes.Value12 == 12
                assert FParameterValueBytes.Value13 == 13
                assert FParameterValueBytes.Value14 == 14

                struct FPreviewEdgeMaskPhase
LeftAnd0        db #00                                                          ; AND краевого байта
LeftOr0         db #00                                                          ; OR шаблона внутри края
LeftAnd1        db #00                                                          ; AND краевого байта
LeftOr1         db #00                                                          ; OR шаблона внутри края
LeftAnd2        db #00                                                          ; AND краевого байта
LeftOr2         db #00                                                          ; OR шаблона внутри края
LeftAnd3        db #00                                                          ; AND краевого байта
LeftOr3         db #00                                                          ; OR шаблона внутри края
LeftAnd4        db #00                                                          ; AND краевого байта
LeftOr4         db #00                                                          ; OR шаблона внутри края
LeftAnd5        db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
LeftOr5         db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
LeftAnd6        db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
LeftOr6         db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
LeftAnd7        db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
LeftOr7         db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
RightAnd0       db #00                                                          ; AND краевого байта
RightOr0        db #00                                                          ; OR шаблона внутри края
RightAnd1       db #00                                                          ; AND краевого байта
RightOr1        db #00                                                          ; OR шаблона внутри края
RightAnd2       db #00                                                          ; AND краевого байта
RightOr2        db #00                                                          ; OR шаблона внутри края
RightAnd3       db #00                                                          ; AND краевого байта
RightOr3        db #00                                                          ; OR шаблона внутри края
RightAnd4       db #00                                                          ; AND краевого байта
RightOr4        db #00                                                          ; OR шаблона внутри края
RightAnd5       db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
RightOr5        db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
RightAnd6       db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
RightOr6        db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
RightAnd7       db #00                                                          ; исходный операнд AND, геометрическая маска не подтверждена
RightOr7        db #00                                                          ; исходный операнд OR, игровое применение не подтверждено
                ends
                assert FPreviewEdgeMaskPhase == 32
                assert FPreviewEdgeMaskPhase.LeftAnd0 == 0
                assert FPreviewEdgeMaskPhase.LeftOr0 == 1
                assert FPreviewEdgeMaskPhase.LeftAnd1 == 2
                assert FPreviewEdgeMaskPhase.LeftOr1 == 3
                assert FPreviewEdgeMaskPhase.LeftAnd2 == 4
                assert FPreviewEdgeMaskPhase.LeftOr2 == 5
                assert FPreviewEdgeMaskPhase.LeftAnd3 == 6
                assert FPreviewEdgeMaskPhase.LeftOr3 == 7
                assert FPreviewEdgeMaskPhase.LeftAnd4 == 8
                assert FPreviewEdgeMaskPhase.LeftOr4 == 9
                assert FPreviewEdgeMaskPhase.LeftAnd5 == 10
                assert FPreviewEdgeMaskPhase.LeftOr5 == 11
                assert FPreviewEdgeMaskPhase.LeftAnd6 == 12
                assert FPreviewEdgeMaskPhase.LeftOr6 == 13
                assert FPreviewEdgeMaskPhase.LeftAnd7 == 14
                assert FPreviewEdgeMaskPhase.LeftOr7 == 15
                assert FPreviewEdgeMaskPhase.RightAnd0 == 16
                assert FPreviewEdgeMaskPhase.RightOr0 == 17
                assert FPreviewEdgeMaskPhase.RightAnd1 == 18
                assert FPreviewEdgeMaskPhase.RightOr1 == 19
                assert FPreviewEdgeMaskPhase.RightAnd2 == 20
                assert FPreviewEdgeMaskPhase.RightOr2 == 21
                assert FPreviewEdgeMaskPhase.RightAnd3 == 22
                assert FPreviewEdgeMaskPhase.RightOr3 == 23
                assert FPreviewEdgeMaskPhase.RightAnd4 == 24
                assert FPreviewEdgeMaskPhase.RightOr4 == 25
                assert FPreviewEdgeMaskPhase.RightAnd5 == 26
                assert FPreviewEdgeMaskPhase.RightOr5 == 27
                assert FPreviewEdgeMaskPhase.RightAnd6 == 28
                assert FPreviewEdgeMaskPhase.RightOr6 == 29
                assert FPreviewEdgeMaskPhase.RightAnd7 == 30
                assert FPreviewEdgeMaskPhase.RightOr7 == 31

                struct FPreviewClipTargetRow
End0            db #00                                                          ; байт адреса по прямому коду второго конца
End1            db #00                                                          ; байт адреса по прямому коду второго конца
End2            db #00                                                          ; байт адреса по прямому коду второго конца
End3            db #00                                                          ; байт адреса по прямому коду второго конца
End4            db #00                                                          ; байт адреса по прямому коду второго конца
End5            db #00                                                          ; байт адреса по прямому коду второго конца
End6            db #00                                                          ; байт адреса по прямому коду второго конца
End7            db #00                                                          ; байт адреса по прямому коду второго конца
End8            db #00                                                          ; байт адреса по прямому коду второго конца
End9            db #00                                                          ; байт адреса по прямому коду второго конца
EndA            db #00                                                          ; байт адреса по прямому коду второго конца
EndB            db #00                                                          ; байт адреса по прямому коду второго конца
EndC            db #00                                                          ; байт адреса по прямому коду второго конца
EndD            db #00                                                          ; байт адреса по прямому коду второго конца
EndE            db #00                                                          ; байт адреса по прямому коду второго конца
EndF            db #00                                                          ; байт адреса по прямому коду второго конца
                ends
                assert FPreviewClipTargetRow == 16
                assert FPreviewClipTargetRow.End0 == 0
                assert FPreviewClipTargetRow.End1 == 1
                assert FPreviewClipTargetRow.End2 == 2
                assert FPreviewClipTargetRow.End3 == 3
                assert FPreviewClipTargetRow.End4 == 4
                assert FPreviewClipTargetRow.End5 == 5
                assert FPreviewClipTargetRow.End6 == 6
                assert FPreviewClipTargetRow.End7 == 7
                assert FPreviewClipTargetRow.End8 == 8
                assert FPreviewClipTargetRow.End9 == 9
                assert FPreviewClipTargetRow.EndA == 10
                assert FPreviewClipTargetRow.EndB == 11
                assert FPreviewClipTargetRow.EndC == 12
                assert FPreviewClipTargetRow.EndD == 13
                assert FPreviewClipTargetRow.EndE == 14
                assert FPreviewClipTargetRow.EndF == 15

                struct FEquipmentTypeSet
Type0           db #FF                                                          ; код для сравнения с текущим типом транспорта
Type1           db #FF                                                          ; код для сравнения с текущим типом транспорта
Type2           db #FF                                                          ; код для сравнения с текущим типом транспорта
Type3           db #FF                                                          ; код для сравнения с текущим типом транспорта
                ends
                assert FEquipmentTypeSet == 4
                assert FEquipmentTypeSet.Type0 == 0
                assert FEquipmentTypeSet.Type1 == 1
                assert FEquipmentTypeSet.Type2 == 2
                assert FEquipmentTypeSet.Type3 == 3

                struct FPreviewRootSample
Value           db #00                                                          ; исходное байтовое приближение
                ends
                assert FPreviewRootSample == 1
                assert FPreviewRootSample.Value == 0

                struct FStationShipTradeRow
Capacity        db #00                                                          ; поле K.t, переносится в вместимость при покупке
Price           dw #0000                                                        ; цена K.c, младший байт первым
Unknown03       db #00                                                          ; скорость из CNKR, текущий потребитель и единицы не установлены
SaleField       db #00                                                          ; авторский код легальности, нуль выбирает особую ветвь продажи
                ends
                assert FStationShipTradeRow == 5
                assert FStationShipTradeRow.Capacity == 0
                assert FStationShipTradeRow.Price == 1
                assert FStationShipTradeRow.Unknown03 == 3
                assert FStationShipTradeRow.SaleField == 4

                struct FStationSkimmerTradeRow
Unknown00       db #00                                                          ; тоннаж из CNSK, Entry читателя Capacity при индексах 7..10 читает это поле, штатная роль не установлена
PriceField      dw #0000                                                        ; слово свойства c второго набора, сценарий покупки отсутствует
Unknown03       db #00                                                          ; скорость из CNSK, текущий потребитель и единицы не установлены
LoadAddend      db #00                                                          ; свойство v и добавка в ComputeWeightedLoad
                ends
                assert FStationSkimmerTradeRow == 5
                assert FStationSkimmerTradeRow.Unknown00 == 0
                assert FStationSkimmerTradeRow.PriceField == 1
                assert FStationSkimmerTradeRow.Unknown03 == 3
                assert FStationSkimmerTradeRow.LoadAddend == 4

                struct FPolygonEdgeScratch
Row             db #00                                                          ; младший байт PUSH HL, текущая строка из D
MaskPage        db #00                                                          ; старший байт PUSH HL, текущая страница масок из H
                ends
                assert FPolygonEdgeScratch == 2
                assert FPolygonEdgeScratch.Row == 0
                assert FPolygonEdgeScratch.MaskPage == 1

                struct FIntroStackSnapshot
Stack           dw #0000                                                        ; сохранённое слово CPU-SP
                ends
                assert FIntroStackSnapshot == 2
                assert FIntroStackSnapshot.Stack == 0

                struct FVoxelCosineByte
Value           db #00                                                          ; исходный байт коэффициента
                ends
                assert FVoxelCosineByte == 1
                assert FVoxelCosineByte.Value == 0

                struct FCargoLoadScale
Code            db #00                                                          ; код вклада строки груза
                ends
                assert FCargoLoadScale == 1
                assert FCargoLoadScale.Code == 0

                struct FPreviewObjectEnd
Low             db #80                                                          ; бит 7 означает конец списка при High=80
High            db #80                                                          ; старший байт специальной записи
                ends
                assert FPreviewObjectEnd == 2
                assert FPreviewObjectEnd.Low == 0
                assert FPreviewObjectEnd.High == 1

                struct FMapClipLowTail3
SecondSidesE    db #00                                                          ; младший байт адреса при младшей тетраде второго кода E
SecondSidesF    db #00                                                          ; младший байт адреса при младшей тетраде второго кода F
                ends
                assert FMapClipLowTail3 == 2
                assert FMapClipLowTail3.SecondSidesE == 0
                assert FMapClipLowTail3.SecondSidesF == 1

                struct FMapClipHighHead
SecondSides0    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 0
SecondSides1    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 1
SecondSides2    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 2
SecondSides3    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 3
SecondSides4    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 4
SecondSides5    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 5
SecondSides6    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 6
SecondSides7    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 7
SecondSides8    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 8
SecondSides9    db #00                                                          ; старший байт адреса при младшей тетраде второго кода 9
SecondSidesA    db #00                                                          ; старший байт адреса при младшей тетраде второго кода A
                ends
                assert FMapClipHighHead == 11
                assert FMapClipHighHead.SecondSides0 == 0
                assert FMapClipHighHead.SecondSides1 == 1
                assert FMapClipHighHead.SecondSides2 == 2
                assert FMapClipHighHead.SecondSides3 == 3
                assert FMapClipHighHead.SecondSides4 == 4
                assert FMapClipHighHead.SecondSides5 == 5
                assert FMapClipHighHead.SecondSides6 == 6
                assert FMapClipHighHead.SecondSides7 == 7
                assert FMapClipHighHead.SecondSides8 == 8
                assert FMapClipHighHead.SecondSides9 == 9
                assert FMapClipHighHead.SecondSidesA == 10

                struct FArchiveBankStripRoute
BankIndex       db #00                                                          ; индекс файла BANK, которому принадлежит маршрут
FrameCount      db #00                                                          ; число используемых кадров в каждом списке
Staged00        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged01        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged02        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged03        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged04        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged05        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged06        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged07        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged08        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged09        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged10        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Staged11        dw #0000                                                        ; указатель полосы через буфер для страницы 7
Direct00        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct01        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct02        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct03        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct04        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct05        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct06        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct07        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct08        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct09        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct10        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
Direct11        dw #0000                                                        ; указатель полосы прямого вывода в экран 4000
                ends
                assert FArchiveBankStripRoute == 50
                assert FArchiveBankStripRoute.BankIndex == 0
                assert FArchiveBankStripRoute.FrameCount == 1
                assert FArchiveBankStripRoute.Staged00 == 2
                assert FArchiveBankStripRoute.Staged01 == 4
                assert FArchiveBankStripRoute.Staged02 == 6
                assert FArchiveBankStripRoute.Staged03 == 8
                assert FArchiveBankStripRoute.Staged04 == 10
                assert FArchiveBankStripRoute.Staged05 == 12
                assert FArchiveBankStripRoute.Staged06 == 14
                assert FArchiveBankStripRoute.Staged07 == 16
                assert FArchiveBankStripRoute.Staged08 == 18
                assert FArchiveBankStripRoute.Staged09 == 20
                assert FArchiveBankStripRoute.Staged10 == 22
                assert FArchiveBankStripRoute.Staged11 == 24
                assert FArchiveBankStripRoute.Direct00 == 26
                assert FArchiveBankStripRoute.Direct01 == 28
                assert FArchiveBankStripRoute.Direct02 == 30
                assert FArchiveBankStripRoute.Direct03 == 32
                assert FArchiveBankStripRoute.Direct04 == 34
                assert FArchiveBankStripRoute.Direct05 == 36
                assert FArchiveBankStripRoute.Direct06 == 38
                assert FArchiveBankStripRoute.Direct07 == 40
                assert FArchiveBankStripRoute.Direct08 == 42
                assert FArchiveBankStripRoute.Direct09 == 44
                assert FArchiveBankStripRoute.Direct10 == 46
                assert FArchiveBankStripRoute.Direct11 == 48

                struct FPolygonLiteralEdgeMask
AndMask         db #00                                                          ; буквальный операнд AND краевого байта в исходном состоянии
OrMask          db #00                                                          ; буквальный операнд OR краевого байта в исходном состоянии
                ends
                assert FPolygonLiteralEdgeMask == 2
                assert FPolygonLiteralEdgeMask.AndMask == 0
                assert FPolygonLiteralEdgeMask.OrMask == 1

                struct FActionPlayerIndices
ShipIndex       db #00                                                          ; копия индекса корабля из состояния станции
SkimmerIndex    db #00                                                          ; копия индекса глайдера из состояния станции
                ends
                assert FActionPlayerIndices == 2
                assert FActionPlayerIndices.ShipIndex == 0
                assert FActionPlayerIndices.SkimmerIndex == 1

                struct FActionPlayerMoney
Money           dw #0000                                                        ; копия суммы игрока из состояния станции
                ends
                assert FActionPlayerMoney == 2
                assert FActionPlayerMoney.Money == 0


                struct FFinalIrqFrame
SavedAF         dw #0000                                                        ; альтернативный AF на время записи в порт
ResumeAddress   dw #0000                                                        ; адрес возврата из IM 2 в генерируемую цепочку
                ends
                assert FFinalIrqFrame == 4
                assert FFinalIrqFrame.SavedAF == 0
                assert FFinalIrqFrame.ResumeAddress == 2

                struct FStationNewsTransfer
EndHour         db #00                                                          ; при переносе занимает байт часа окончания из авторского NEWS
SystemWord0     dw #0000                                                        ; при переносе занимает первое слово системы в NEWS
SystemWord1     dw #0000                                                        ; при переносе занимает второе слово системы в NEWS
PlanetIndex     db #00                                                          ; при переносе занимает номер планеты в NEWS
                ends
                assert FStationNewsTransfer == 6
                assert FStationNewsTransfer.EndHour == 0
                assert FStationNewsTransfer.SystemWord0 == 1
                assert FStationNewsTransfer.SystemWord1 == 3
                assert FStationNewsTransfer.PlanetIndex == 5

                struct FArchivedPlayerPanelWord
Value           dw #0000                                                        ; исходное слово после ACTION, текущий потребитель неизвестен
                ends
                assert FArchivedPlayerPanelWord == 2
                assert FArchivedPlayerPanelWord.Value == 0

                struct FArchivedPlayerPanelType
Byte0           db #00                                                          ; исходный ноль после скорости, назначение неизвестно
TypeCode        db #00                                                          ; полный класс игрока, большой эффект выбирает маску и допуск дочерних записей
Byte2           db #00                                                          ; исходный ноль перед SHILD, назначение неизвестно
                ends
                assert FArchivedPlayerPanelType == 3
                assert FArchivedPlayerPanelType.Byte0 == 0
                assert FArchivedPlayerPanelType.TypeCode == 1
                assert FArchivedPlayerPanelType.Byte2 == 2

                struct FIntroStackSampleByte
Value           db #00                                                          ; исходный байт рядом со снимком SP, копируется при выборке текстуры
                ends
                assert FIntroStackSampleByte == 1
                assert FIntroStackSampleByte.Value == 0

                struct FArchiveEngineIrqStack
AtmOutputEntry  dw #0000                                                        ; адрес команды OUT, снимаемый RET по #3D30
AtmAFOrReturn   dw #0000                                                        ; AF до CPL, затем адрес возврата из ПЗУ TR-DOS
PagingHLOrAF    dw #0000                                                        ; HL для селектора ATM-2 или AF для Scorpion
PagingSavedBC   dw #0000                                                        ; BC, сохраняемый переходником выбора страницы
NestedReturn    dw #0000                                                        ; адрес возврата вложенного вызова
ServiceReturn   dw #0000                                                        ; адрес возврата в основной обработчик IRQ
AltAF           dw #0000                                                        ; сохранённое альтернативное AF
AltBC           dw #0000                                                        ; сохранённое альтернативное BC
AltDE           dw #0000                                                        ; сохранённое альтернативное DE
AltHL           dw #0000                                                        ; сохранённое альтернативное HL
SavedAF         dw #0000                                                        ; сохранённое основное AF
SavedBC         dw #0000                                                        ; сохранённое основное BC
SavedDE         dw #0000                                                        ; сохранённое основное DE
SavedHL         dw #0000                                                        ; сохранённое основное HL
SavedIX         dw #0000                                                        ; сохранённый указатель IX
                ends
                assert FArchiveEngineIrqStack == #1E
                assert FArchiveEngineIrqStack.AtmAFOrReturn == #02
                assert FArchiveEngineIrqStack.PagingSavedBC == #06
                assert FArchiveEngineIrqStack.ServiceReturn == #0A
                assert FArchiveEngineIrqStack.SavedIX == #1C

                struct FArchiveEngineTimer
Seconds         db #00                                                          ; оставшееся время, две десятичные цифры BCD
Ticks           db #00                                                          ; остаток кадров до уменьшения времени
                ends
                assert FArchiveEngineTimer == 2
                assert FArchiveEngineTimer.Ticks == 1

                struct FArchiveEnginePagingState
CurrentCode     db #00                                                          ; последний логический код страницы, без преобразования для порта
IrqSavedCode    db #00                                                          ; код страницы до вывода экранных индикаторов в IRQ
                ends
                assert FArchiveEnginePagingState == 2
                assert FArchiveEnginePagingState.IrqSavedCode == 1

                struct FArchiveEngineSpritePages
Bd0             db #00                                                          ; код страницы масок BD0
Bd1             db #00                                                          ; код страницы масок BD1
Bd2             db #00                                                          ; код страницы масок BD2
Bd3             db #00                                                          ; код страницы масок BD3
                ends
                assert FArchiveEngineSpritePages == 4

                struct FArchiveEngineModeTargets
Pentagon        dw #0000                                                        ; адрес селектора для режима меню 0
Scorpion        dw #0000                                                        ; адрес селектора для режима меню 1
Atm             dw #0000                                                        ; адрес селектора для режима меню 2
                ends
                assert FArchiveEngineModeTargets == 6

                struct FArchiveEngineMeters
LeftTarget      db #00                                                          ; заданная ширина левого заполнения в пикселях
RightTarget     db #00                                                          ; заданная ширина правого заполнения в пикселях
LeftShown       db #00                                                          ; число уже добавленных левых столбцов
RightShown      db #00                                                          ; число уже добавленных правых столбцов
LeftCursor      dw #0000                                                        ; адрес верхнего пикселя левого столбца
RightCursor     dw #0000                                                        ; адрес верхнего пикселя правого столбца
LeftMask        db #00                                                          ; однобитовая маска текущего столбца слева
RightMask       db #00                                                          ; однобитовая маска текущего столбца справа
                ends
                assert FArchiveEngineMeters == #0A
                assert FArchiveEngineMeters.LeftCursor == 4
                assert FArchiveEngineMeters.RightCursor == 6

                struct FArchiveEngineScene
RowBytes        dw #0000                                                        ; полный шаг между строками рабочего растра
SourceWidth     dw #0000                                                        ; ширина в байтах для расчёта начального положения окна
MaxHorizontal   dw #0000                                                        ; правый предел, потребитель читает младший байт
SourceRows      dw #0000                                                        ; значение совпадает с высотой файла, читатель пока неизвестен
MaxVertical     dw #0000                                                        ; верхний предел вертикального смещения, читается младший байт
VerticalOffset  db #00                                                          ; текущее смещение начала окна в строках
Unknown0B       db #00                                                          ; исходный ноль, читатель не установлен
ViewColumn      dw #0000                                                        ; адрес первого столбца окна в нулевой строке
SpriteYBias     db #00                                                          ; прибавка к Y записи бойца при адресации рабочего растра
MeterGapSource  dw #0000                                                        ; начало первой строки области индикаторов в текущем кадре
                ends
                assert FArchiveEngineScene == #11
                assert FArchiveEngineScene.VerticalOffset == #0A
                assert FArchiveEngineScene.ViewColumn == #0C
                assert FArchiveEngineScene.MeterGapSource == #0F

                struct FArchiveTimerAddress
Background      dw #0000                                                        ; адрес левой цифры и её сохранённого фона в сцене
                ends
                assert FArchiveTimerAddress == 2

                struct FArchiveFighterWord
Low             db #00                                                          ; младший байт слова
High            db #00                                                          ; старший байт слова
                ends
                assert FArchiveFighterWord == 2

                struct FArchiveFighterKey
Port            dw #0000                                                        ; полный адрес порта клавиатуры
Mask            db #00                                                          ; нажатие даёт нулевой результат AND
                ends
                assert FArchiveFighterKey == 3

                struct FArchiveEngineFighter
Side            db #00                                                          ; ноль для прямого кадра, ненулевой для зеркального
FrameSource     FArchiveFighterWord                                             ; адрес масок и рисунка в окне страницы BD
FrameDest       FArchiveFighterWord                                             ; адрес первого байта рисования в рабочей сцене
Request         db #00                                                          ; запрошенный номер действия
LoadedAction    db #FF                                                          ; загруженное действие, FF заставляет загрузить первое
PreviousWidth   db #00                                                          ; ширина предыдущего кадра в байтах
Unknown08       db #00                                                          ; исходный ноль, назначение не установлено
PreviousHeight  db #00                                                          ; высота предыдущего кадра в строках
Unknown0A       db #00                                                          ; исходный ноль, назначение не установлено
PreviousAddress FArchiveFighterWord                                             ; адрес предыдущего кадра, сохранённый при рисовании
BarBase         FArchiveFighterWord                                             ; начало таблицы указателей BAR этого бойца
StepIndex       db #00                                                          ; индекс шага в текущем действии
StepTicks       db #00                                                          ; оставшиеся кадры текущего шага
FrameWidth      db #00                                                          ; ширина текущего кадра в байтах
FrameHeight     db #00                                                          ; высота текущего кадра в строках
PreviousMirror  db #00                                                          ; сторона, с которой был нарисован предыдущий кадр
PositionX       db #00                                                          ; базовый горизонтальный столбец бойца
PositionY       db #00                                                          ; базовая вертикальная строка бойца
PreviousY       db #00                                                          ; DrawY предыдущего кадра до прибавки SpriteYBias
SpriteBank      db #00                                                          ; индекс файла BD, 0..3
StepCount       db #00                                                          ; число шагов текущего действия
Steps           FArchiveFighterWord                                             ; адрес первой записи шага
DrawX           db #00                                                          ; горизонтальный столбец с учётом поправки кадра
DrawY           db #00                                                          ; вертикальная строка с учётом поправки кадра
ActionFlags     db #00                                                          ; флаг, бит 6 включает повтор с RepeatStep
Primary0        FArchiveFighterKey                                              ; прямая сторона, бит 0
Primary1        FArchiveFighterKey                                              ; прямая сторона, бит 1
Primary2        FArchiveFighterKey                                              ; прямая сторона, бит 2
Primary3        FArchiveFighterKey                                              ; прямая сторона, бит 3
Primary4        FArchiveFighterKey                                              ; прямая сторона, бит 4
Mirror0         FArchiveFighterKey                                              ; зеркальная сторона, бит 0
Mirror1         FArchiveFighterKey                                              ; зеркальная сторона, бит 1
Mirror2         FArchiveFighterKey                                              ; зеркальная сторона, бит 2
Mirror3         FArchiveFighterKey                                              ; зеркальная сторона, бит 3
Mirror4         FArchiveFighterKey                                              ; зеркальная сторона, бит 4
Extra0          FArchiveFighterKey                                              ; дополнительная группа, бит 0
Extra1          FArchiveFighterKey                                              ; дополнительная группа, бит 1
Extra2          FArchiveFighterKey                                              ; дополнительная группа, бит 2
Extra3          FArchiveFighterKey                                              ; дополнительная группа, бит 3
RepeatStep      db #00                                                          ; шаг повторения при установленном бите 6
PrimaryBits     db #00                                                          ; накопленные нажатия основной группы
ExtraBits       db #00                                                          ; накопленные нажатия дополнительной группы
Rules           FArchiveFighterWord                                             ; таблица правил перехода, индексируется действием
FramePending    db #00                                                          ; ненулевое значение требует применить шаг по текущему индексу
PreviousExtra   db #00                                                          ; последний обработанный набор дополнительных клавиш
NextAction      db #00                                                          ; действие после завершения неповторяющейся группы
MoveX           FArchiveFighterWord                                             ; знаковое горизонтальное смещение текущего шага
TurnPending     db #00                                                          ; отложенное переключение стороны при смене действия
                ends
                assert FArchiveEngineFighter == #53
                assert FArchiveEngineFighter.Primary0 == #1E
                assert FArchiveEngineFighter.Mirror0 == #2D
                assert FArchiveEngineFighter.Extra0 == #3C
                assert FArchiveEngineFighter.MoveX == #50

                struct FArchiveInputRulePointer
Target          dw #0000                                                        ; адрес блока правил для данного запроса
                ends
                assert FArchiveInputRulePointer == 2

                struct FArchiveInputRuleCount
Count           db #00                                                          ; число пятибайтовых записей в блоке
                ends
                assert FArchiveInputRuleCount == 1

                struct FArchiveInputRule
PrimaryMask     db #00                                                          ; маска основной группы
PrimaryValue    db #00                                                          ; ожидаемый результат AND основной группы
ExtraMask       db #00                                                          ; маска дополнительной группы
ExtraValue      db #00                                                          ; ожидаемый результат AND дополнительной группы
Action          db #00                                                          ; новый запрос при двух совпадениях
                ends
                assert FArchiveInputRule == 5

                struct FArchiveRunMenuState
Cursor          dw #0000                                                        ; текущий адрес рисования подписи
Selected        db #00                                                          ; индекс выбранной записи, заголовок имеет индекс 0
LastItem        db #00                                                          ; максимальный индекс текущего списка
Records         dw #0000                                                        ; адрес первой четырёхбайтовой записи списка
                ends
                assert FArchiveRunMenuState == 6

                struct FArchiveRunModeState
Current         db #00                                                          ; выбранный режим, 0..2
Count           db #00                                                          ; число режимов для замыкания цикла
                ends
                assert FArchiveRunModeState == 2

                struct FArchiveRunCaption
Target          dw #0000                                                        ; адрес нуль-терминированной подписи
                ends
                assert FArchiveRunCaption == 2

                struct FArchiveRunMenuItem
Caption         dw #0000                                                        ; адрес нуль-терминированной строки пункта
Handler         dw #0000                                                        ; процедура подтверждения пункта
                ends
                assert FArchiveRunMenuItem == 4
                assert FArchiveRunMenuItem.Handler == 2

                struct FArchiveStartPaging
CurrentCode     db #00                                                          ; последний полный код страницы
Visible         db #00                                                          ; индекс видимого экрана 0 или 1
IrqSavedCode    db #00                                                          ; код страницы до кадровой работы
NextVisible     db #00                                                          ; индекс показа на следующем IRQ
Bank0           db #00                                                          ; код страницы BANK0
Bank1           db #00                                                          ; код страницы BANK1
Bank2           db #00                                                          ; код страницы BANK2
Bank3           db #00                                                          ; код страницы BANK3
Bank4           db #00                                                          ; код страницы BANK4
Bank5           db #00                                                          ; код страницы BANK5
DefaultCode     db #00                                                          ; рабочая страница меню после временного переключения
                ends
                assert FArchiveStartPaging == #0B
                assert FArchiveStartPaging.Bank0 == 4

                struct FArchiveStartFrame
LeftMinor       db #00                                                          ; младший индекс левого набора
LeftMajor       db #00                                                          ; старший индекс левого набора
RightMinor      db #00                                                          ; младший индекс правого набора
RightMajor      db #00                                                          ; старший индекс правого набора
LeftKeyLatch    db #00                                                          ; защёлка повторного нажатия для левой стороны
RightKeyLatch   db #00                                                          ; защёлка повторного нажатия для правой стороны
StripPhase      db #00                                                          ; фаза вывода полос 0..3
LayerPhase      db #00                                                          ; фаза динамического слоя 0..2
                ends
                assert FArchiveStartFrame == 8

                struct FArchiveStartKey
LatchCode       db #00                                                          ; код удерживаемой клавиши, 1..4
Limit           db #00                                                          ; значение селектора, блокирующее шаг
Latch           dw #0000                                                        ; адрес фиксатора нажатия стороны
Selector        dw #0000                                                        ; адрес изменяемого селектора
Step            db #00                                                          ; знаковый шаг, +1 или −1
Commit          dw #0000                                                        ; подключение полосы для нового значения
Redraw          dw #0000                                                        ; перерисовка слоёв со старым значением
Side            db #00                                                          ; 0 для левой стороны, 1 для правой
                ends
                assert FArchiveStartKey == #0C

                struct FArchiveTileOffset
X               db #00                                                          ; горизонтальное смещение плитки в знакоместах
Y               db #00                                                          ; вертикальное смещение плитки в знакоместах
                ends
                assert FArchiveTileOffset == 2

                struct FArchiveTileRaster
Row0            db #00                                                          ; верхняя строка плитки
Row1            db #00
Row2            db #00
Row3            db #00
Row4            db #00
Row5            db #00
Row6            db #00
Row7            db #00                                                          ; нижняя строка плитки
                ends
                assert FArchiveTileRaster == 8

                struct FArchiveStartLoadState
NextKey         dw #0000                                                        ; адрес следующего файлового ключа
                ends
                assert FArchiveStartLoadState == 2

                endif
