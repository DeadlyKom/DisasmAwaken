                module Controls
                module DrawRadar
                ; Документация [алгоритм и проверка](../../Docs/ControlsRasterBackground.md)
                ; -----------------------------------------
                ; Фазовый фон радара, центральная метка и вывод объектов со знаковыми линиями
                ; исходная запись 23, банк 1, смещения #07B3..#0B7E
                ; In:
                ;   банк 1 выбран, SignedWord задаёт приращение фона, доступен список FActionRecord с конечным маркером
                ;   на входном стеке внешний возврат, прерывания не вмешиваются в временный SP
                ; Out:
                ;   пересчитаны остаток и фаза, записаны 80 строк фона и центральная метка
                ;   допущенные объекты получают линии и маскированные значки, SP восстанавливается до объектного прохода
                ;   внешний RET происходит после маркера #8080, IX указывает на маркер
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, R, экран, изменяемые операнды и временные слова стека
                ; Note:
                ;   допустимые индексы форм от 0 до 19, принудительный выбор задаёт байт #9C2B
                ;   сквозная модель сверяет весь экран на всех фазах с одной проверяемой записью и маркером
                ;   отдельные модели сверяют регистры и записи фона, линий и значков, общий IRQ не моделируется
                ; -----------------------------------------
                ; Сохранение CPU-стека перед записью фона через PUSH в экранную память.
Entry:          LD IX, #A0C0
                LD (#E48F), SP
                ; Расчёт приращения из младшего байта знакового слова после сдвига вправо на два разряда.
                LD HL, (@ActionPanelGaugesState.SignedWord)
                SRA H
                RR L
                SRA H
                RR L
                ; Проверка знака именно младшего байта после сдвига, знак исходного слова здесь не проверяется.
                LD A, L
                BIT 7, L
                LD B, #01
                JR Z, @Controls.DrawRadar.Accumulate                            ; переход, если младший байт сдвинутого слова неотрицателен

                LD B, #FF
                NEG
                ; Прибавление модуля приращения к дробному остатку предыдущего вызова.
Accumulate:     LD L, #00
                ADD A, L
                LD (#E2B0), A
                LD C, #00
                JP NC, @Controls.DrawRadar.DispatchIndex                        ; переход, если сумма не переполнила байт, фаза остаётся прежней

                LD C, B
                ; Расчёт фазы по модулю 16, перенос меняет её на один шаг согласно знаку приращения.
DispatchIndex:  LD A, #00
                SUB C
                EXX
                AND #0F
                LD (@ControlsRasterReturnsState.EntryIndex), A
                LD (@ControlsRasterReturnsState.RepeatIndex), A
                RLCA
                LD L, A
                LD H, #00
                LD B, H
                LD SP, #E271
                ADD HL, SP
                LD SP, HL
                ; Подготовка правой границы десяти байтов фона, начальная строка экрана 104.
                LD HL, #48B2
                LD DE, #5555
                LD A, #05
                EX AF, AF'
                RET

                ; Начальный вход фазы 0 содержит два обмена AF, повтор периода входит со второго обмена.
                EX AF, AF'
RepeatPhase:    EX AF, AF'
                ; Строка фазы 0, пять пар байтов 80, 00.
                LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase01                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase01                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 1, пять пар байтов 00, 00.
DrawPhase01:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase02                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase02                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 2, пять пар байтов 80, 00.
DrawPhase02:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase03                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase03                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 3, пять пар байтов 00, 00.
DrawPhase03:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase04                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase04                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 4, пять пар байтов 80, 00.
DrawPhase04:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase05                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase05                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 5, пять пар байтов 00, 00.
DrawPhase05:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase06                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase06                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 6, пять пар байтов 80, 00.
DrawPhase06:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase07                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase07                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 7, пять пар байтов 00, 00.
DrawPhase07:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase08                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase08                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 8, пять пар байтов 80, 00.
DrawPhase08:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase09                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase09                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 9, пять пар байтов 00, 00.
DrawPhase09:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase10                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase10                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 10, пять пар байтов 80, 00.
DrawPhase10:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase11                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase11                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 11, пять пар байтов 00, 00.
DrawPhase11:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase12                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase12                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 12, пять пар байтов 80, 00.
DrawPhase12:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase13                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase13                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 13, пять пар байтов 00, 00.
DrawPhase13:    LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase14                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase14                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 14, пять пар байтов 80, 00.
DrawPhase14:    LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.DrawPhase15                          ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.DrawPhase15                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 15, десять байтов 55 образуют горизонтальную разделительную полосу.
DrawPhase15:    LD SP, HL
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.DrawRadar.FinishPeriod                         ; переход, если следующая строка остаётся внутри знакоместа

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.DrawRadar.FinishPeriod                          ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана

                LD A, H
                SUB #08
                LD H, A
                ; Проверка оставшихся повторов периода, счётчик хранится в альтернативном A.
FinishPeriod:   EX AF, AF'
                DEC A
                JP NZ, @Controls.DrawRadar.RepeatPhase                          ; переход, если остаются повторы полного периода из 16 строк

                ; Проверка длины нижнего дополнения, пять периодов с пропуском начальной фазы дают 80 минус фаза строк.
                LD A, #00
                AND A
                JR Z, @Controls.DrawRadar.RestoreStack                          ; переход, если начальная фаза нулевая, все 80 строк уже записаны

                ; Расчёт входа 16 минус фаза, нижнее дополнение повторяет хвост периода, не его начало.
                EX DE, HL
                LD L, A
                LD A, #10
                SUB L
                RLCA
                LD L, A
                XOR A
                LD H, A
                LD (@ControlsRasterReturnsState.RepeatIndex), A
                LD SP, #E271
                ADD HL, SP
                LD SP, HL
                LD A, #01
                LD HL, #5555
                EX DE, HL
                EX AF, AF'
                RET

                ; Восстановление CPU-стека и установка центрального квадрата 3 на 3 пикселя, X от 103, Y от 143.
RestoreStack:   LD SP, #0000
                LD HL, #572C
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                LD HL, #504C
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                INC H
                DEC L
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                JP @Controls.DrawRadar.ResetStride

                ; Проверка завершения списка, этот вход достижим только после маркера 80 в поле IX+1.
CheckEnd:       LD A, (IX + @FActionRecord.Components.Component0.Low)
                CP #80
                RET Z                                                           ; выход, если поле IX+0 тоже равно 80, список завершён

                ; Восстановление шага после обработки экранных координат или значка.
ResetStride:    LD DE, #0040
                ; Переход к следующей физической записи размером 64 байта.
NextRecord:     ADD IX, DE
                LD A, (IX + @FActionRecord.Components.Component0.High)
                ; Проверка кода состояния, значение 80 направляет к маркеру окончания.
                CP #80
                JR Z, @Controls.DrawRadar.CheckEnd                              ; переход, если поле IX+1 равно 80, требуется проверить маркер окончания

                LD A, (IX + @FActionRecord.ClassCode)
                ; Проверка двух типов, пропускаемых этим отображением, остальные коды здесь не ограничиваются.
                CP #14
                JR Z, @Controls.DrawRadar.NextRecord                            ; переход, если код типа равен 14, запись не отображается

                CP #15
                JR Z, @Controls.DrawRadar.NextRecord                            ; переход, если код типа равен 15, запись не отображается

                LD A, (IX + @FActionRecord.ViewPosition.X.High)
                ; Проверка недопустимого знакового байта 80 в первой координате.
                CP #80
                JR Z, @Controls.DrawRadar.NextRecord                            ; переход, если первая координата равна 80, запись пропускается

                LD C, A
                AND A
                JP P, @Controls.DrawRadar.CheckX                                ; переход, если первая координата неотрицательна, модуль уже находится в A

                NEG
CheckX:         CP #80
                JR NC, @Controls.DrawRadar.NextRecord                           ; переход, если модуль первой координаты не меньше 80, запись пропускается

                LD A, (IX + @FActionRecord.ViewPosition.Y.High)
                LD B, A
                ; Проверка знака высоты перед проверкой её допустимого модуля.
                AND A
                JP P, @Controls.DrawRadar.CheckHeight                           ; переход, если высота неотрицательна, модуль уже находится в A

                NEG
CheckHeight:    CP #80
                JR NC, @Controls.DrawRadar.NextRecord                           ; переход, если высота равна знаковому байту 80, запись пропускается

                LD A, (IX + @FActionRecord.ViewPosition.Depth.High)
                LD E, A
                ; Проверка знака второй координаты, исходный байт уже сохранён в E.
                AND A
                JP P, @Controls.DrawRadar.CheckDepth                            ; переход, если вторая координата неотрицательна, модуль уже находится в A

                NEG
CheckDepth:     CP #80
                JR NC, @Controls.DrawRadar.ResetStride                          ; переход, если вторая координата равна 80, шаг DE сначала восстанавливается

                ; Расчёт экранного Y из противоположного по знаку ViewPosition.Depth.High и X из ViewPosition.X.High.
                LD A, E
                LD E, C
                NEG
                LD C, A
                ; Масштабирование знакового байта, четверть плюс округлённая вверх половина этой четверти.
                SRA C
                SRA C
                LD A, C
                SRA C
                ADC A, C
                LD C, A
                ; Такое же масштабирование второй координаты, младшие два бита теряются до сложения.
                SRA E
                SRA E
                LD A, E
                SRA E
                ADC A, E
                LD E, A
                ; Проверка экранного Y относительно центра 144 и диапазона от 107 до 180 включительно.
                LD A, #90
                ADD A, C
                CP #B5
                JR NC, @Controls.DrawRadar.ResetStride                          ; переход, если экранный Y не меньше 181, объект вне нижней границы

                CP #6B
                JR C, @Controls.DrawRadar.ResetStride                           ; переход, если экранный Y меньше 107, объект вне верхней границы

                LD C, A
                ; Проверка экранного X относительно центра 104 и диапазона от 64 до 140 включительно.
                LD A, #68
                ADD A, E
                CP #8D
                JR NC, @Controls.DrawRadar.ResetStride                          ; переход, если экранный X не меньше 141, объект вне правой границы

                CP #40
                JR C, @Controls.DrawRadar.ResetStride                           ; переход, если экранный X меньше 64, объект вне левой границы

                LD E, A
                ; Преобразование принятого Y в старший байт адреса пикселя Spectrum.
                LD A, C
                AND A
                RRA
                SCF
                RRA
                AND A
                RRA
                XOR C
                AND #F8
                XOR C
                EXX
                LD D, A
                EXX
                ; Преобразование младших разрядов X и старших разрядов Y в младший байт адреса.
                LD A, E
                RLCA
                RLCA
                RLCA
                XOR C
                AND #C7
                XOR C
                RLCA
                RLCA
                EXX
                LD E, A
                EXX
                LD A, E
                EXX
                ; Выбор одиночной пиксельной маски по фазе X внутри экранного байта.
                AND #07
                LD C, A
                LD B, #00
                LD HL, @ControlsObjectPixelMasks.Phase00
                ADD HL, BC
                LD C, (HL)
                EXX
                ; Расчёт знаковой высоты линии из ViewPosition.Y.High, два SRA делят её на четыре с округлением вниз.
                LD A, B
                EXX
                SRA A
                SRA A
                JP Z, @Controls.DrawRadar.PrepareIcon                           ; переход, если высота после деления равна нулю, линия не требуется

                JP P, @Controls.DrawRadar.CheckBottom                           ; переход, если ненулевая высота положительна, линия направлена вниз

                NEG
                LD B, A
                EXX
                LD A, C
                EXX
                ; Проверка верхнего конца линии относительно строки 107.
                SUB B
                CP #6B
                CCF
                JR C, @Controls.DrawRadar.BeginUp                               ; переход, если верхний конец не выше строки 107, длина не ограничивается

                ; Расчёт сокращённой длины до верхней границы, сброс Carry затем запрещает значок.
                SUB #6B
                ADD A, B
                JP M, @Controls.DrawRadar.PrepareIcon                           ; переход, если пересчитанная длина отрицательна, линия не рисуется

                LD B, A
                AND A
                JP Z, @Controls.DrawRadar.PrepareIcon                           ; переход, если пересчитанная длина нулевая, значок рисуется на исходной строке

                ; Сохранение решения о значке в альтернативном Carry перед линией вверх.
BeginUp:        EX AF, AF'
                ; Установка пикселя линии и переход на предыдущую строку Spectrum.
DrawUp:         LD A, (DE)
                OR C
                LD (DE), A
                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.DrawRadar.RepeatUp                             ; переход, если исходная строка не первая в знакоместе, адрес предыдущей строки готов

                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.DrawRadar.RepeatUp                              ; переход, если исходный E меньше #20, переход в предыдущую треть уже учтён

                LD A, D
                ADD A, #08
                LD D, A
RepeatUp:       DJNZ @Controls.DrawRadar.DrawUp

                ; Отступ ещё на две строки вверх, трёхстрочный значок заканчивается на верхнем конце линии.
                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.DrawRadar.CheckIconTop                         ; переход, если исходная строка не первая в знакоместе, первая строка отступа найдена

                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.DrawRadar.CheckIconTop                          ; переход, если исходный E меньше #20, первая строка отступа лежит в предыдущей трети

                LD A, D
                ADD A, #08
                LD D, A
CheckIconTop:   LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.DrawRadar.CheckIconBase                        ; переход, если исходная строка не первая в знакоместе, вторая строка отступа найдена

                LD A, E
                SUB #20
                LD E, A
                JR C, @Controls.DrawRadar.CheckIconBase                         ; переход, если исходный E меньше #20, вторая строка отступа лежит в предыдущей трети

                LD A, D
                ADD A, #08
                LD D, A
CheckIconBase:  LD A, D
                JP @Controls.DrawRadar.CheckIcon

CheckBottom:    LD B, A
                EXX
                LD A, C
                EXX
                ; Проверка нижнего конца линии относительно исключающей границы 181.
                ADD A, B
                CP #B5
                JR C, @Controls.DrawRadar.BeginDown                             ; переход, если нижний конец выше строки 181, значок будет допущен

                ; Расчёт числа пикселей до строки 180 включительно, значок при нижнем отсечении пропускается.
                SUB #B5
                SUB B
                NEG
                LD B, A
                AND A
                JR Z, @Controls.DrawRadar.PrepareIcon                           ; переход, если пересчитанная длина нулевая, линия пропускается

                JP M, @Controls.DrawRadar.PrepareIcon                           ; переход, если пересчитанная длина отрицательна, линия пропускается

                ; Сохранение решения о значке в альтернативном Carry перед линией вниз.
BeginDown:      EX AF, AF'
                ; Установка пикселя линии и переход на следующую строку Spectrum.
DrawDown:       LD A, (DE)
                OR C
                LD (DE), A
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.DrawRadar.RepeatDown                           ; переход, если новая строка не первая в знакоместе, адрес следующей строки готов

                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Controls.DrawRadar.RepeatDown                            ; переход, если сложение E с #20 дало перенос, следующая треть уже выбрана

                LD A, D
                SUB #08
                LD D, A
RepeatDown:     DJNZ @Controls.DrawRadar.DrawDown

                ; Восстановление решения о значке, Carry сброшен после сокращения ненулевой линии.
CheckIcon:      EX AF, AF'
                JP NC, @Controls.DrawRadar.ResetStride                          ; переход, если линия отсечена границей окна, значок пропускается

                ; Расчёт смещения шестибайтовой фазы значка по альтернативному E, содержащему экранный X.
PrepareIcon:    EXX
                LD A, E
                AND #07
                ADD A, A
                LD E, A
                ADD A, A
                ADD A, E
                EXX
                LD C, A
                LD B, #00
                ; Проверка управляющего байта, FF принудительно выбирает второй указатель формы.
                LD A, (#9C2B)
                INC A
                LD A, (IX + @FActionRecord.ClassCode)
                JR NZ, @Controls.DrawRadar.FindIcon                             ; переход, если управляющий байт не равен FF, используется тип из записи

                LD A, #01
                ; Поиск указателя формы, таблица содержит двадцать исходных записей по два байта.
FindIcon:       SLA A
                ADD A, #5D
                LD L, A
                LD A, #E6
                ADC A, #00
                LD H, A
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                ADD HL, BC
                ; Сохранение указателя пиксельной фазы при чтении двух масок очистки.
                PUSH HL
                LD HL, @ControlsObjectClearMasks.Phase00
                ADD HL, BC
                LD B, (HL)
                INC HL
                LD C, (HL)
                POP HL
                ; Обновление верхней строки значка, биты за пределами трёх пикселей сохраняются.
                LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                INC HL
                DEC E
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.DrawRadar.DrawIconMiddle                       ; переход, если средняя строка остаётся внутри знакоместа

                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.DrawRadar.DrawIconMiddle                        ; переход, если перенос младшего байта уже выбрал следующую треть экрана

                LD A, D
                SUB #08
                LD D, A
                ; Обновление средней строки значка теми же двумя масками очистки.
DrawIconMiddle: LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                INC HL
                DEC E
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.DrawRadar.DrawIconBottom                       ; переход, если нижняя строка остаётся внутри знакоместа

                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.DrawRadar.DrawIconBottom                        ; переход, если перенос младшего байта уже выбрал следующую треть экрана

                LD A, D
                SUB #08
                LD D, A
                ; Обновление нижней строки значка и продолжение обхода записей.
DrawIconBottom: LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                JP @Controls.DrawRadar.ResetStride

                endmodule
                endmodule
