                module Controls
                module UnknownE291
                ; Документация [координаты и значки](../../Docs/ControlsObjectProjection.md)
                ; Документация [частичный фон](../../Docs/ControlsRasterBackground.md)
                ; Документация [частичный выбор через RET](../../Docs/ControlsRasterReturns.md)
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #07B3..#0B7E
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
                ; Сохранение CPU-стека перед записью фона через PUSH в экранную память.
Entry:          LD IX, #A0C0
                LD (#E48F), SP
                ; Расчёт приращения из младшего байта знакового слова после сдвига вправо на два разряда.
                LD HL, (#A78F)
                SRA H
                RR L
                SRA H
                RR L
                ; Проверка знака именно младшего байта после сдвига, знак исходного слова здесь не проверяется.
                LD A, L
                BIT 7, L
                LD B, #01
                JR Z, @Controls.UnknownE291.PointE2AF                           ; переход, если младший байт сдвинутого слова неотрицателен


                LD B, #FF
                NEG
                ; Прибавление модуля приращения к дробному остатку предыдущего вызова.
PointE2AF:      LD L, #00
                ADD A, L
                LD (#E2B0), A
                LD C, #00
                JP NC, @Controls.UnknownE291.DispatchIndex                      ; переход, если сумма не переполнила байт, фаза остаётся прежней


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
                LD SP, @ControlsRasterReturns.Index00
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
PointE2DC:      EX AF, AF'
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
                JP NZ, @Controls.UnknownE291.PointE2F6                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE2F6                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 1, пять пар байтов 00, 00.
PointE2F6:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE30F                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE30F                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 2, пять пар байтов 80, 00.
PointE30F:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE328                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE328                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 3, пять пар байтов 00, 00.
PointE328:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE341                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE341                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 4, пять пар байтов 80, 00.
PointE341:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE35A                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE35A                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 5, пять пар байтов 00, 00.
PointE35A:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE373                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE373                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 6, пять пар байтов 80, 00.
PointE373:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE38C                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE38C                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 7, пять пар байтов 00, 00.
PointE38C:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3A5                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3A5                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 8, пять пар байтов 80, 00.
PointE3A5:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3BE                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3BE                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 9, пять пар байтов 00, 00.
PointE3BE:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3D7                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3D7                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 10, пять пар байтов 80, 00.
PointE3D7:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3F0                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3F0                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 11, пять пар байтов 00, 00.
PointE3F0:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE409                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE409                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 12, пять пар байтов 80, 00.
PointE409:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE422                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE422                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 13, пять пар байтов 00, 00.
PointE422:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE43B                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE43B                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 14, пять пар байтов 80, 00.
PointE43B:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE454                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE454                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Строка фазы 15, десять байтов 55 образуют горизонтальную разделительную полосу.
PointE454:      LD SP, HL
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE46B                          ; переход, если следующая строка остаётся внутри знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE46B                           ; переход, если перенос столбцового байта уже перевёл адрес в следующую треть экрана


                LD A, H
                SUB #08
                LD H, A
                ; Проверка оставшихся повторов периода, счётчик хранится в альтернативном A.
PointE46B:      EX AF, AF'
                DEC A
                JP NZ, @Controls.UnknownE291.PointE2DC                          ; переход, если остаются повторы полного периода из 16 строк


                ; Проверка длины нижнего дополнения, пять периодов с пропуском начальной фазы дают 80 минус фаза строк.
                LD A, #00
                AND A
                JR Z, @Controls.UnknownE291.PointE48E                           ; переход, если начальная фаза нулевая, все 80 строк уже записаны


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
                LD SP, @ControlsRasterReturns.Index00
                ADD HL, SP
                LD SP, HL
                LD A, #01
                LD HL, #5555
                EX DE, HL
                EX AF, AF'
                RET


                ; Восстановление CPU-стека и установка центрального квадрата 3 на 3 пикселя, X от 103, Y от 143.
PointE48E:      LD SP, #0000
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
                JP @Controls.UnknownE291.PointE4B7


                ; Проверка завершения списка, этот вход достижим только после маркера 80 в поле IX+1.
PointE4B1:      LD A, (IX + #00)
                CP #80
                RET Z                                                           ; выход, если поле IX+0 тоже равно 80, список завершён

                ; Продолжение объектного прохода, полный контракт и игровое назначение полей ещё не установлены.
PointE4B7:      LD DE, #0040
                ; Переход к следующей физической записи размером 64 байта.
PointE4BA:      ADD IX, DE
                LD A, (IX + #01)
                ; Проверка кода состояния, значение 80 направляет к маркеру окончания.
                CP #80
                JR Z, @Controls.UnknownE291.PointE4B1                           ; переход, если поле IX+1 равно 80, требуется проверить маркер окончания


                LD A, (IX + #12)
                ; Проверка двух типов, пропускаемых этим отображением, остальные коды здесь не ограничиваются.
                CP #14
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если код типа равен 14, запись не отображается


                CP #15
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если код типа равен 15, запись не отображается


                LD A, (IX + #1B)
                ; Проверка недопустимого знакового байта 80 в первой координате.
                CP #80
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если первая координата равна 80, запись пропускается


                LD C, A
                AND A
                JP P, @Controls.UnknownE291.PointE4DC                           ; переход, если первая координата неотрицательна, модуль уже находится в A


                NEG
PointE4DC:      CP #80
                JR NC, @Controls.UnknownE291.PointE4BA                          ; переход, если модуль первой координаты не меньше 80, запись пропускается


                LD A, (IX + #1D)
                LD B, A
                ; Проверка знака высоты перед проверкой её допустимого модуля.
                AND A
                JP P, @Controls.UnknownE291.PointE4EA                           ; переход, если высота неотрицательна, модуль уже находится в A


                NEG
PointE4EA:      CP #80
                JR NC, @Controls.UnknownE291.PointE4BA                          ; переход, если высота равна знаковому байту 80, запись пропускается


                LD A, (IX + #1F)
                LD E, A
                ; Проверка знака второй координаты, исходный байт уже сохранён в E.
                AND A
                JP P, @Controls.UnknownE291.PointE4F8                           ; переход, если вторая координата неотрицательна, модуль уже находится в A


                NEG
PointE4F8:      CP #80
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если вторая координата равна 80, шаг DE сначала восстанавливается


                ; Расчёт экранного Y из противоположного по знаку поля IX+1F и X из поля IX+1B.
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
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если экранный Y не меньше 181, объект вне нижней границы


                CP #6B
                JR C, @Controls.UnknownE291.PointE4B7                           ; переход, если экранный Y меньше 107, объект вне верхней границы


                LD C, A
                ; Проверка экранного X относительно центра 104 и диапазона от 64 до 140 включительно.
                LD A, #68
                ADD A, E
                CP #8D
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если экранный X не меньше 141, объект вне правой границы


                CP #40
                JR C, @Controls.UnknownE291.PointE4B7                           ; переход, если экранный X меньше 64, объект вне левой границы


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
                ; Расчёт знаковой высоты линии из поля IX+1D, два SRA делят её на четыре с округлением вниз.
                LD A, B
                EXX
                SRA A
                SRA A
                JP Z, @Controls.UnknownE291.PointE5E5                           ; переход, если высота после деления равна нулю, линия не требуется


                JP P, @Controls.UnknownE291.PointE5B5                           ; переход, если ненулевая высота положительна, линия направлена вниз


                NEG
                LD B, A
                EXX
                LD A, C
                EXX
                ; Проверка верхнего конца линии относительно строки 107.
                SUB B
                CP #6B
                CCF
                JR C, @Controls.UnknownE291.PointE576                           ; переход, если верхний конец не выше строки 107, длина не ограничивается


                ; Расчёт сокращённой длины до верхней границы, сброс Carry затем запрещает значок.
                SUB #6B
                ADD A, B
                JP M, @Controls.UnknownE291.PointE5E5                           ; переход, если пересчитанная длина отрицательна, линия не рисуется


                LD B, A
                AND A
                JP Z, @Controls.UnknownE291.PointE5E5                           ; переход, если пересчитанная длина нулевая, значок рисуется на исходной строке


                ; Сохранение решения о значке в альтернативном Carry перед линией вверх.
PointE576:      EX AF, AF'
                ; Установка пикселя линии и переход на предыдущую строку Spectrum.
PointE577:      LD A, (DE)
                OR C
                LD (DE), A
                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE58C                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE58C                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE58C:      DJNZ @Controls.UnknownE291.PointE577

                ; Отступ ещё на две строки вверх, трёхстрочный значок заканчивается на верхнем конце линии.
                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5A0                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE5A0                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE5A0:      LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5B1                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JR C, @Controls.UnknownE291.PointE5B1                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE5B1:      LD A, D
                JP @Controls.UnknownE291.PointE5E1


PointE5B5:      LD B, A
                EXX
                LD A, C
                EXX
                ; Проверка нижнего конца линии относительно исключающей границы 181.
                ADD A, B
                CP #B5
                JR C, @Controls.UnknownE291.PointE5CA                           ; переход, если нижний конец выше строки 181, значок будет допущен


                ; Расчёт числа пикселей до строки 180 включительно, значок при нижнем отсечении пропускается.
                SUB #B5
                SUB B
                NEG
                LD B, A
                AND A
                JR Z, @Controls.UnknownE291.PointE5E5                           ; переход, если пересчитанная длина нулевая, линия пропускается


                JP M, @Controls.UnknownE291.PointE5E5                           ; переход, если пересчитанная длина отрицательна, линия пропускается


                ; Сохранение решения о значке в альтернативном Carry перед линией вниз.
PointE5CA:      EX AF, AF'
                ; Установка пикселя линии и переход на следующую строку Spectrum.
PointE5CB:      LD A, (DE)
                OR C
                LD (DE), A
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5DF                          ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Controls.UnknownE291.PointE5DF                           ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
PointE5DF:      DJNZ @Controls.UnknownE291.PointE5CB

                ; Восстановление решения о значке, Carry сброшен после сокращения ненулевой линии.
PointE5E1:      EX AF, AF'
                JP NC, @Controls.UnknownE291.PointE4B7                          ; переход, если линия отсечена границей окна, значок пропускается


                ; Расчёт смещения шестибайтовой фазы значка по альтернативному E, содержащему экранный X.
PointE5E5:      EXX
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
                LD A, (IX + #12)
                JR NZ, @Controls.UnknownE291.PointE5FC                          ; переход, если управляющий байт не равен FF, используется тип из записи


                LD A, #01
                ; Поиск указателя формы, таблица содержит двадцать исходных записей по два байта.
PointE5FC:      SLA A
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
                JP NZ, @Controls.UnknownE291.PointE632                          ; переход, если средняя строка остаётся внутри знакоместа


                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE632                           ; переход, если перенос младшего байта уже выбрал следующую треть экрана


                LD A, D
                SUB #08
                LD D, A
                ; Обновление средней строки значка теми же двумя масками очистки.
PointE632:      LD A, (DE)
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
                JP NZ, @Controls.UnknownE291.PointE650                          ; переход, если нижняя строка остаётся внутри знакоместа


                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE650                           ; переход, если перенос младшего байта уже выбрал следующую треть экрана


                LD A, D
                SUB #08
                LD D, A
                ; Обновление нижней строки значка и продолжение обхода записей.
PointE650:      LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                JP @Controls.UnknownE291.PointE4B7


                endmodule
                endmodule
