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
; имена Unknown сохраняют неустановленное назначение полей
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
Source          dw #0000                                                        ; исходный адрес ресурса из HL
Cursor          dw #0000                                                        ; начальная копия адреса ресурса
Unknown0C       db #01                                                          ; начальное значение единица
Unknown0D       db #00                                                          ; параметр выбранного варианта эффекта
Unknown0E       dw #0000                                                        ; исходный DE выбранного варианта эффекта
Unknown10       db #00                                                          ; параметр варианта, малый эффект #0C, большой #14
Unknown11       db #00                                                          ; параметр выбранного варианта эффекта
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
Unknown0E       dw #0000                                                        ; исходные дополнительные байты записи
                ends
                assert FInterfaceItem == #10

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

; физическое состояние предложения, смысл промежуточных слов и последнего статуса не установлен
                struct FMissionOfferState
FirstWord       dw #0000                                                        ; первое слово предлагаемого ключа
SecondWord      dw #0000                                                        ; второе слово предлагаемого ключа
UnknownWord04   dw #0000                                                        ; Unknown, слово по смещению 4
UnknownWord06   dw #0000                                                        ; Unknown, слово по смещению 6
UnknownWord08   dw #0000                                                        ; Unknown, слово по смещению 8
UnknownWord0A   dw #0000                                                        ; Unknown, слово по смещению 10
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

                endif
