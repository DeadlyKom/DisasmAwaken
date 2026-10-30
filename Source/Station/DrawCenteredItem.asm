                module Station
                module DrawCenteredItem
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [рамка и центрирование текста элемента](../../Docs/CenteredItem.md)
; -----------------------------------------
; Регистрация и рисование рамки элемента с центрированием CR-строк и выравниванием последнего абзаца
; исходная запись 4, файловые смещения #62DF..#6324
; In:
;   HL - индекс существующей FInterfaceItem с непустой допустимой геометрией
;   X и Y неотрицательны, Width=2..32, Height=2..24, прямоугольник помещается на экран
;   Flags выбирает контур битом 0, TextIndex задаёт A для SkipLfRecords в таблице CenterTextBase
;   таблицы адресации и шрифта готовы, в индексной таблице есть свободная пара после удаления прежнего ключа
;   исходные инструкции глифа и текстового потока доступны для записи, стек не перекрывает исполняемые части
; Out:
;   HL, DE и BC восстановлены, AF - A=#C3, F от последнего текстового прохода
;   рамка и глифы записаны в bitmap, атрибуты не меняются, элемент зарегистрирован в карте владельцев
;   TextWindow имеет начало X*8+3,Y*8+4 и размеры Width*8-4,Height*8-11 для допустимых экранных координат
;   Style=1, LineEndCode восстановлен в исходный JP, курсор соответствует последнему текстовому выходу
; Corrupt:
;   AF, HL', AF'
; Note:
;   H', DE', BC', IX, IY, I и IFF сохраняются, SP восстанавливается
;   физический FCenteredItemFrame создаётся четырьмя PUSH, Workspace меняется через EX (SP),HL
;   CR-строки имеют X=floor(max(0,ширина окна-измеренная ширина)/2), затем печатаются до принятого CR либо отказа
;   остаток до первого LF без предварительного CR выводится через PrintJustified с X=0
;   не сохраняется произвольный прежний LineEndCode, временный RET всегда заменяется исходным JP
;   регистрация, рамка и уже выведенный текст не отменяются при последующем отказе вывода
;   контракт модели ограничен размещением на экране, полное отсечение и вмешательство IRQ здесь не подтверждены
; -----------------------------------------
                ; создание FCenteredItemFrame.SavedHL из исходного индекса элемента
Entry:          PUSH HL
                ; сохранение FCenteredItemFrame.SavedDE
                PUSH DE
                ; сохранение FCenteredItemFrame.SavedBC
                PUSH BC
                ; создание рабочего слова FCenteredItemFrame.Workspace, сначала в нём исходный индекс
                PUSH HL
                ; выбор автоматического переноса текста при отказе ширины
                LD A, #01
                LD (@TextWindow.Style), A
                ; выбор начала физической записи FInterfaceItem по нулевому смещению
                XOR A
                CALL @Station.GetItemField.Entry
                ; чтение X,Y,Width,Height в C,B,E,D в физическом порядке полей
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                ; настройка центрируемого окна, HL остаётся указателем FInterfaceItem.Flags
                CALL @Station.SetupCenterText.Entry
                ; получение исходного индекса из Workspace для регистрации, указатель Flags временно сохраняется в кадре
                EX (SP), HL
                CALL @Station.RegisterItemCells.Entry
                ; возврат указателя Flags, Workspace получает рабочий адрес карты от RegisterItemCells
                EX (SP), HL
                ; выбор типа контура из младших пяти битов Flags, рисователь затем использует только бит 0
                LD A, (HL)
                AND @InterfaceFlags.FrameMask
                ; переход к FInterfaceItem.TextIndex, рисователь рамки сохраняет этот HL
                INC HL
                CALL @Station.DrawFrameKeepHL.Entry
                ; чтение индекса текстовой записи из поля TextIndex
                LD A, (HL)
                ; поиск начала выбранного текста за TextIndex+1 ограничителями LF
                LD HL, @InterfaceText.CenterTextBase
                CALL @Station.SkipLfRecords.Entry
                ; временная замена JP на RET после явного CR для поочерёдного центрирования строк
                LD A, @TextFlowOpcode.Return
                LD (@TextStreamState.LineEndCode), A
                ; сохранение начала текущего участка перед поиском ближайшего CR либо LF
NextLine:       PUSH HL
                ; поиск ограничителя строки без печати просмотренных символов
ScanLine:       LD A, (HL)
                INC HL
                ; проверка LF, который выбирает последний абзац без центрирования
                CP @TextConst.LineFeed
                JP Z, @Station.CenterItemLine.FinalWords                        ; переход, если до CR найден LF, остаток выводится через PrintJustified

                ; проверка CR для измерения и центрирования отдельной строки
                CP @TextConst.CarriageReturn
                JP NZ, @Station.DrawCenteredItem.ScanLine                       ; переход, если текущий байт не CR, поиск ограничителя продолжается

                ; восстановление начала строки с удалением временного слова над FCenteredItemFrame
                POP DE
                DEC HL
                EX DE, HL
                ; выбор нулевого дополнительного ограничителя измерителя ширины
                LD B, #00
                CALL @Station.MeasureTextRunSaved.Entry
                LD C, A

                ; JP @Station.CenterItemLine.Entry, продолжение в CenterItemLine.asm

                endmodule
                endmodule
