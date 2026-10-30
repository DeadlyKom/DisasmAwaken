                module Station
                module DrawPointer
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [указатель и сохранение фона](../../Docs/Pointer.md)
; -----------------------------------------
; Выбор формы и обработчика наведения, сохранение фона и рисование AND/XOR-указателя
; исходная запись 4, файловые смещения #06BF..#07F2
; In:
;   X=#6307 в пределах 0..255, Y=#6308 в пределах 0..191, адресные таблицы #8200..#84FF построены
;   активен станционный код и его таблицы, экран #4000..#5FFF и собственные операнды доступны для записи
;   ненулевой код владельца ячейки обязан иметь допустимый индекс FInterfaceItem в таблице #8500
;   при RestoredFlag=0 BackgroundAddr, VisibleRows=1..8 и фон соответствуют последнему рисованию
; Out:
;   HL, DE, BC, AF - рабочие значения выбора формы либо рисования, пути раннего выхода различаются
;   AF', IX - рабочие значения выбора записи, прочие альтернативные регистры и IY сохранены
;   SpriteBase выбран, при новом рисовании фон сохранён, RestoredFlag=0, VisibleRows и BackgroundAddr обновлены
; Corrupt:
;   HL, DE, BC, AF, AF', IX
; Note:
;   rows=min(8,192-Y), сохраняются два байта строки даже при X>=248, где рисуется только один
;   при новом рисовании HL=SpriteBase OR ((32*(X AND 7)+4*rows) AND #FF), DE следующий экранный адрес
;   B=0,C=191-2*rows, AF результат последнего перехода на следующую строку, точная формула приведена в Pointer.md
;   при RestoredFlag=0 возвращается AF=#0044 без сохранения и рисования, выбор формы и callback уже выполнен
;   при ненулевом владельце IX становится адресом FInterfaceItem, при нулевом сохраняется
;   AF' используется выбором верхней либо нижней формы, HL', DE', BC', IY, I и IFF сохраняются
;   нулевой RestoredFlag означает активный рисунок, ненулевой уже восстановленный фон, это целый байт состояния
;   невалидная индексная пара со старшим байтом #FF приводит к POP IX без парного PUSH, потребляется адрес возврата
;   форма зависит от Flags AND #C0 и битов 2,1 только в проверках верхней и нижней строки
;   наведение устанавливается лишь для последнего обработчика рисования и Flags AND #C0=0
;   SP восстанавливается только при выполнении предусловия допустимого владельца
; -----------------------------------------
                ; поиск владельца символьной ячейки под текущей пиксельной позицией
Entry:          CALL @Station.GetPointerOwner.Entry
                ; проверка кода владельца, ноль выбирает обычную форму без чтения записи
                AND A
                LD DE, @PointerConst.NormalShape
                JP Z, @Station.DrawPointer.CheckSaved                           ; переход, если ячейка не имеет владельца, проверить состояние фона

                ; расчёт адреса пары индекса по коду владельца, два байта на пару в странице #85
                DEC A
                RLCA
                LD L, A
                LD H, #85
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                ; проверка старшего байта индекса на #FF, этот путь нарушает симметрию стека
                INC H
                JR Z, @Station.DrawPointer.NormalShape                          ; переход, если индекс недействителен, исходный POP IX далее снимет адрес возврата

                DEC H
                LD D, H
                LD E, L
                ; получение адреса Flags физической FInterfaceItem по найденному индексу
                CALL @Station.GetItemFlags.Entry
                ; сохранение адреса Flags для последующей установки IX на начало записи
                PUSH HL
                ; проверка старших двух разрядов Flags для разрешения краевых форм
                LD A, (HL)
                AND @PointerConst.PlainShapeMask
                JR NZ, @Station.DrawPointer.NormalShape                         ; переход, если Flags AND #C0 ненулевой, выбрать обычную форму

                ; сохранение Flags в AF' и переход от Flags к полю Y
                LD A, (HL)
                EX AF, AF'
                DEC HL
                DEC HL
                DEC HL
                ; расчёт символьной строки указателя как Y в пикселях, делённое на восемь
                LD A, (@StationState.PointerXY + 1)
                SRL A
                SRL A
                SRL A
                ; сравнение строки указателя с верхней строкой элемента
                CP (HL)
                LD DE, @PointerConst.TopShape
                JR NZ, @Station.DrawPointer.CheckBottom                         ; переход, если указатель вне верхней строки, проверить нижнюю

                EX AF, AF'
                ; проверка запрета верхней формы в бите 2 Flags
                AND @PointerConst.TopBlockMask
                JR NZ, @Station.DrawPointer.NormalShape                         ; переход, если бит 2 установлен, выбрать обычную форму

                JR @Station.DrawPointer.SelectShape

CheckBottom:    EX AF, AF'
                ; проверка запрета нижней формы в бите 1 Flags
                AND @PointerConst.BottomBlockMask
                JR NZ, @Station.DrawPointer.NormalShape                         ; переход, если бит 1 установлен, выбрать обычную форму

                EX AF, AF'
                LD B, A
                ; расчёт нижней строки как Y+Height-1 с исходным восьмибитным переполнением
                LD A, (HL)
                INC HL
                INC HL
                ADD A, (HL)
                DEC A
                ; сравнение нижней строки элемента со строкой указателя
                CP B
                LD DE, @PointerConst.BottomShape
                JR Z, @Station.DrawPointer.SelectShape                          ; переход, если указатель на нижней строке, принять нижнюю форму

NormalShape:    LD DE, @PointerConst.NormalShape
                ; сохранение выбранной страницы масок в изменяемом операнде SpriteBase
SelectShape:    LD (@PointerState.SpriteBase), DE
                ; извлечение сохранённого адреса Flags, недействительный индекс попадает сюда без PUSH
                POP IX
                ; расчёт начала записи из адреса её поля Flags
                LD DE, 0 - FInterfaceItem.Flags
                ADD IX, DE
                ; чтение последнего указателя списка для проверки верхнего элемента
                CALL @Station.GetLastDraw.Entry
                LD E, (IX + FInterfaceItem.DrawHandler)
                LD D, (IX + FInterfaceItem.DrawHandler + 1)
                ; сравнение DrawHandler записи с последним обработчиком списка
                OR A
                SBC HL, DE
                JR NZ, @Station.DrawPointer.LoadShape                           ; переход, если обработчик не последний, не обновлять callback наведения

                ; проверка разрешения callback по старшим двум разрядам Flags
                LD A, (IX + FInterfaceItem.Flags)
                AND @PointerConst.PlainShapeMask
                JR NZ, @Station.DrawPointer.LoadShape                           ; переход, если Flags AND #C0 ненулевой, не устанавливать callback

                ; установка пары текущая запись и EventHandler в операнды основного цикла
                LD L, (IX + FInterfaceItem.EventHandler)
                LD H, (IX + FInterfaceItem.EventHandler + 1)
                LD (@InterfaceState.HoverItem), IX
                LD (@InterfaceState.HoverCallback), HL
LoadShape:      LD DE, (@PointerState.SpriteBase)
                ; обновление SpriteBase выполняется даже при уже нарисованном указателе
CheckSaved:     LD (@PointerState.SpriteBase), DE
                LD A, (@PointerState.RestoredFlag)
                ; проверка целого байта состояния фона, ноль означает активный рисунок
                OR A
                RET Z                                                           ; выход, если фон ещё не восстановлен, повторно указатель не накладывать

                ; чтение Y в B и X в C для адреса экрана и сдвига маски
                LD BC, (@StationState.PointerXY)
                LD A, C
                ; расчёт смещения фазы масок как 32*(X AND 7)
                AND @PointerConst.Low3Mask
                LD L, #00
                RRA
                RR L
                RRA
                RR L
                RRA
                RR L
                LD H, A
                LD DE, #0000
                ADD HL, DE
                EX DE, HL
                ; получение адреса пиксельной строки из таблиц #82, #83 и #84
                LD H, #82
                LD L, B
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, C
                OR (HL)
                LD L, A
                LD H, B
                ; сохранение экранного адреса в операнде RestorePointer
                LD (@PointerState.BackgroundAddr), HL
                ; сохранение указателя маски на стеке на время копирования фона
                PUSH DE
                LD DE, @PointerConst.BackgroundBase
                ; расчёт числа видимых строк как min(8,192-Y)
                LD A, (@StationState.PointerXY + 1)
                LD B, A
                LD A, @PointerConst.LastScreenY
                LD C, A
                SUB B
                LD B, A
                ; проверка остатка высоты экрана для полного восьмистрочного указателя
                CP @PointerConst.FullTailRows
                LD A, @PointerConst.CellHeight
                JR NC, @Station.DrawPointer.SetRows                             ; переход, если ниже текущей строки остаётся не менее семи строк, сохранить восемь

                LD A, B
                INC A
                ; самоподмена счётчика LD B, используемого рисованием и последующим восстановлением
SetRows:        LD (@PointerState.VisibleRows), A
                LD B, A
                ; сохранение обоих байтов фона строки, в том числе при правом отсечении
SaveRow:        LDI
                LDI
                DEC HL
                DEC HL
                ; расчёт адреса следующей пиксельной строки с чередованием строк Spectrum
                INC H
                LD A, H
                ; проверка границы восьми пиксельных строк внутри знакоместа
                AND @PointerConst.Low3Mask
                JP NZ, @Station.DrawPointer.SaveNext                            ; переход, если граница знакоместа ещё не достигнута, продолжить сохранение

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Station.DrawPointer.SaveNext                             ; переход, если сложение младшего адреса дало перенос, старшая треть уже выбрана

                LD A, H
                SUB @PointerConst.CellHeight
                LD H, A
SaveNext:       DJNZ @Station.DrawPointer.SaveRow

                ; возврат к экранному началу и маскам для наложения указателя
                LD DE, (@PointerState.BackgroundAddr)
                POP HL
                ; установка состояния активного рисунка, его фон уже сохранён
                XOR A
                LD (@PointerState.RestoredFlag), A
                ; операнд VisibleRows ранее заменён числом видимых строк, исходное значение восемь
                LD B, @PointerConst.CellHeight
                LD A, (@StationState.PointerXY)
                ; проверка правого края для выбора одного либо двух экранных байтов
                CP @PointerConst.PairLimit
                JR C, @Station.DrawPointer.DrawPair                             ; переход, если X меньше 248, наложить обе половины строки

                ; наложение левой пары AND/XOR и пропуск правой пары масок при отсечении
DrawSingle:     LD A, (DE)
                AND (HL)
                INC L
                XOR (HL)
                INC L
                INC L
                INC L
                LD (DE), A
                ; расчёт следующей экранной строки для однобайтового ядра
                INC D
                LD A, D
                ; проверка границы знакоместа после увеличения старшего адреса
                AND @PointerConst.Low3Mask
                JP NZ, @Station.DrawPointer.SingleNext                          ; переход, если внутри знакоместа остаются строки, завершить итерацию

                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Station.DrawPointer.SingleNext                           ; переход, если перенос младшего адреса уже перевёл в следующую треть

                LD A, D
                SUB @PointerConst.CellHeight
                LD D, A
SingleNext:     DJNZ @Station.DrawPointer.DrawSingle

                RET

                ; наложение двух пар AND/XOR, правый байт на единицу правее левого
DrawPair:       LD A, (DE)
                AND (HL)
                INC L
                XOR (HL)
                INC L
                LD (DE), A
                INC E
                LD A, (DE)
                AND (HL)
                INC L
                XOR (HL)
                INC L
                LD (DE), A
                DEC E
                ; расчёт следующей экранной строки для двухбайтового ядра
                INC D
                LD A, D
                ; проверка границы знакоместа после увеличения старшего адреса
                AND @PointerConst.Low3Mask
                JP NZ, @Station.DrawPointer.PairNext                            ; переход, если внутри знакоместа остаются строки, завершить итерацию

                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Station.DrawPointer.PairNext                             ; переход, если перенос младшего адреса уже перевёл в следующую треть

                LD A, D
                SUB @PointerConst.CellHeight
                LD D, A
PairNext:       DJNZ @Station.DrawPointer.DrawPair

                RET

                endmodule
                endmodule
