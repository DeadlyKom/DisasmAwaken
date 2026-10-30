                module Station
                module DrawCaptionItem
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [элемент с верхней полосой и ожиданием HALT](../../Docs/CaptionItem.md)
; -----------------------------------------
; Регистрация элемента, полосовая рамка, заголовок и установка курсора содержимого
; исходная запись 4, файловые смещения #6287..#62CA
; In:
;   HL - индекс FInterfaceItem с неотрицательными X,Y, Width=2..32, Height=3..24 и полным размещением на экране
;   Flags выбирает вид верхней полосы битом 0, TextIndex выбирает запись в CaptionTextBase
;   после удаления прежнего ключа в индексной таблице есть свободная пара, таблицы адресации и шрифта готовы
;   действует договор пробуждения HALT из DrawBandSync, исходный LineEndCode содержит JP
;   шесть изменяемых слов рамки задают обычный либо заполненный режим из StationSpans.md
; Out:
;   HL, DE, BC и HL', DE', BC' восстановлены, AF - A=8 при установленном бите 0 Flags, иначе A=0
;   при A=8 F=#08, при A=0 F имеет S от последней колонки регистрации и биты 5,3 от Flags SHR 1, остальные биты сброшены
;   для допустимой геометрии S=1 тогда, когда (Y+Height-1) modulo 8 не меньше 4
;   Style=0, после заголовка CursorX=0, CursorY=8 при бите 0 Flags, иначе CursorY=0
;   bitmap рамки и заголовка записан без изменения атрибутов, прямоугольник зарегистрирован
; Corrupt:
;   AF, AF'
; Note:
;   IX и IY сохраняются при договоре IRQ, код обработчика сам не меняет I и IFF, SP восстанавливается
;   FCaptionItemFrame содержит отдельное сохранение BC', FBandWaitFrame сохраняет HL' и DE' вокруг рамки
;   F текстового вывода не возвращается, после заголовка POP AF восстанавливает Flags и состояние регистрации
;   заголовок начинается с CursorX=1 и отступов начала 3,3, размеры уменьшены на 4,11
;   TextIndex выбирается пропуском TextIndex+1 LF, затем вызывается PrintText без автоматического переноса
;   Carry и Z результата всегда сброшены в допустимой области, они не сообщают об отказе заголовка
;   настоящий IRQ, отсечённая геометрия и реальные игровые заголовки этим полным тестом не подтверждены
;   шесть изменяемых операндов имеют обычный набор ResetBandMode либо заполненный набор SetBandFillMode
;   в заполненном режиме строки 3..10 всегда SetCutoutPattern, строки 12 и 13..15 и середина также заполнены
;   нижнее знакоместо заполненного режима содержит пять строк SetCutoutPattern, одну фиксированную SetOutlinePattern, SetSixBitPattern и ClearSpanPattern
;   строки 2,11 и третья снизу сохраняют обычный боковой узор, их фиксированные вызовы не подменяются
; -----------------------------------------
Entry:          EXX
                ; создание FCaptionItemFrame.SavedBCAlt из альтернативного BC
                PUSH BC
                EXX
                ; сохранение исходных HL, DE и BC в FCaptionItemFrame
                PUSH HL
                PUSH DE
                PUSH BC
                ; создание Workspace, первоначально содержащего индекс элемента
                PUSH HL
                ; выбор начала FInterfaceItem по нулевому смещению
                XOR A
                CALL @Station.GetItemField.Entry
                ; чтение физических X, Y, Width и Height в C, B, E, D
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                ; настройка окна заголовка с CursorX=1 и отступами начала 3,3
                CALL @Station.SetupInsetTextWindow.Entry
                ; получение индекса из Workspace для регистрации, указатель Height временно сохраняется в кадре
                EX (SP), HL
                CALL @Station.RegisterItemCells.Entry
                ; возврат указателя Height из кадра, Workspace получает рабочий адрес карты
                EX (SP), HL
                ; переход к Flags перед выбором полосы рамки
                INC HL
                LD A, (HL)
                ; сохранение Flags и F регистрации для последующей установки Y содержимого
                PUSH AF
                ; ожидание HALT и рисование рамки с сохранением указателя Flags
                CALL @Station.DrawBandSync.Entry
                ; переход к TextIndex после возврата рамки
                INC HL
                LD A, (HL)
                ; поиск заголовка за TextIndex+1 ограничителями LF в CaptionTextBase
                LD HL, @InterfaceText.CaptionTextBase
                CALL @Station.SkipLfRecords.Entry
                ; выбор отбрасывания остатка строки при отказе ширины заголовка
                XOR A
                LD (@TextWindow.Style), A
                CALL @Station.PrintText.Entry
                ; возврат Flags и флагов регистрации, статус текста здесь не передаётся
                POP AF
                ; проверка бита 0 Flags для выбора Y содержимого
                RRA
                LD A, #00
                LD L, A
                JR NC, @Station.DrawCaptionItem.ContentY                        ; переход, если бит 0 Flags сброшен, содержимое начинается при Y=0

                ; выбор Y=8 и итогового AF=#0808 для варианта с установленным битом 0
                ADD A, @ScreenConst.PixelsPerChar
                ; обновление обеих координат курсора содержимого, X всегда равен нулю
ContentY:       LD H, A
                LD (@TextWindow.CursorX), HL
                ; удаление Workspace и восстановление SavedBC, SavedDE и SavedHL
                POP HL
                POP BC
                POP DE
                POP HL
                EXX
                ; восстановление FCaptionItemFrame.SavedBCAlt перед возвратом
                POP BC
                EXX
                RET

                endmodule
                endmodule
