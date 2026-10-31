                module Station
                module ClearScrollWindowBody
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [пределы отсечения, три изменяемых JR и нулевой счётчик на Y=191](../../Docs/ScrollBodyClear.md)
                ; -----------------------------------------
                ; Очистка тела окна с трёхпиксельными боковыми полями и тремя путями горизонтального отсечения
                ; исходная запись 4, файловые смещения #66B0..#685D
                ; In:
                ;   AF - A исходная высота перед добавлением пяти пикселей, F не является параметром
                ;   TextWindow содержит OriginX=8*X+3, OriginY=8*Y+3 и Width=8*W-4 для штатной геометрии окна
                ;   ClearBodyState.TopOffset задаёт исходный байтовый сдвиг верха, таблицы адресации подготовлены
                ;   код и три операнда JR доступны для записи, стек вне очищаемой области, повторного входа нет
                ;   для нормального прямоугольника модели W=2..32, H=3..24, A=8*H-11-TopOffset, TopOffset не больше 8*H-11
                ;   верх ровно 191 и переполнение счётчика A+5 имеют отдельное исходное поведение, они не являются безопасным пустым прямоугольником
                ; Out:
                ;   в обычном пути очищена область от OriginX до 8*(X+W)-4, от OriginY+TopOffset на (A+5) AND FF строк с исходным отсечением
                ;   при штатном A=8*H-11-TopOffset нижняя граница до отсечения равна 8*(Y+H)-4
                ;   левое и правое поля сохраняют маски E0 и 07, внутренние целые байты обнуляются
                ;   левое отсечение выбирает путь без левой маски, правое путь без правой, в обычном пути используются обе
                ;   нижняя коррекция при достижении границы C0 считает высоту до BF, поэтому при отсечении строка 191 остаётся
                ;   при старте ровно на Y=191 коррекция даёт D=0, цикл DEC D выполняет 256 строк, записывая за bitmap, это поведение сохранено
                ;   на выполненном цикле D=0, E=7, HL адрес следующей экранной строки, C младший адрес начала последней строки
                ;   B=E0 для обычного и правого путей, B=07 для левого, F от последнего DEC D с сохранённым Carry шага адреса
                ;   три смещения JR получают одинаковые 2*(30-число_целых_байтов), исходные байты развёрнутых записей не заменяются
                ;   HL, DE, BC и AF рабочие, C' хранит классификацию отсечения, B', HL', DE', AF', IX, IY сохранены
                ;   I, IFF, IM и страницы собственный код не меняет, SP обычного возврата равен входному SP+2
                ;   ранние отказы не рисуют, AF принадлежит соответствующей проверке вертикального края либо ширины, рабочие основные регистры не восстанавливаются
                ; Corrupt:
                ;   HL, DE, BC, AF, BC', очищаемые байты и три операнда JR, в граничном пути также байты за bitmap
                ; Note:
                ;   отрицательное начало и правый перенос обрабатываются исходной байтовой арифметикой, произвольный положительный старший X не валидируется как координата
                ;   A+5 и прибавление TopOffset к младшему Y байтовые, старший Y не получает перенос этой суммы
                ;   в каждом развёрнутом блоке 30 пар LD (HL),A и INC L, смещение пропуска вычисляется в байтах кода
                ;   цикл со счётчиком ноль не пропускается, он выполняет 256 строк
                ;   модель прошла 14319 геометрий и три отдельных случая Y=191, все записи за bitmap в этих трёх случаях сопоставлены с независимым расчётом
                ;   нативная достижимость опасной геометрии из игрового ввода и аппаратные IRQ не проверены, алгоритм очищающего ядра от этого не изменён
                ; -----------------------------------------
                ; -----------------------------------------
                ; Горизонтальное отсечение и выбор сохранённых боковых полей
                ; -----------------------------------------
                ; сохранение высоты перед расчётом горизонтальной области
Entry:          PUSH AF
                ; чтение внутренней ширины окна в пикселях
                LD A, (@TextWindow.Width)
                LD E, A
                ; чтение младшего X, старший X сохраняется в C' как классификатор отсечения
                LD A, (@TextWindow.OriginXLow)
                LD C, A
                EXX
                LD A, (@TextWindow.OriginXHigh)
                LD C, A
                EXX
                ; проверка знака старшего X без изменения самого байта
                AND A
                LD A, C
                JP P, @Station.ClearScrollWindowBody.RightExtent                ; переход, если старший X неотрицателен, проверить правый перенос

                ; расчёт видимой ширины при отрицательном X с исходным байтовым прибавлением восьми
                ADD A, E
                ADD A, @ScreenConst.PixelsPerChar
                LD E, A
                ; выбор нулевой экранной колонки для отсечения слева
                LD C, #00
                JP @Station.ClearScrollWindowBody.Height

                ; расчёт правого конца от младшего X-1 и ширины
RightExtent:    DEC A
                ADD A, E
                JP NC, @Station.ClearScrollWindowBody.Height                    ; переход, если правый конец не дал переноса, сохранить обычную ширину

                ; выбор классификатора 1 в C' для правого отсечения
                EXX
                LD C, #01
                EXX
                ; расчёт сокращённой ширины после правого переноса, без изменения исходного X
                CPL
                ADD A, E
                ADD A, @ScreenConst.PixelsPerChar
                LD E, A
                ; -----------------------------------------
                ; Вертикальное отсечение с исходной границей BF
                ; -----------------------------------------
                ; возврат высоты и расчёт байтового числа строк A+5
Height:         POP AF
                ADD A, @ClearBodyConst.HeightExtra
                LD D, A
                ; расчёт младшего Y от начала окна и изменяемого TopOffset без переноса в старший байт
                LD A, (@TextWindow.OriginYLow)
                ADD A, #00
                LD B, A
                ; проверка знака старшего Y для верхнего отсечения
                LD A, (@TextWindow.OriginYHigh)
                AND A
                LD A, B
                JP P, @Station.ClearScrollWindowBody.Bottom                     ; переход, если старший Y неотрицателен, проверить нижнюю границу

                ; расчёт конца области при отрицательном начале Y
                ADD A, D
                RET Z                                                           ; выход, если байтовый конец области равен нулю

                ; проверка конца отрицательной области по исходному пределу 192
                CP @ClearBodyConst.YEnd
                RET NC                                                          ; выход, если конец области не меньше 192, исходный верхний путь отвергает её

                ; проверка знака младшего начала после прибавления TopOffset
                BIT 7, B
                JR Z, @Station.ClearScrollWindowBody.Address                    ; переход, если младший Y неотрицателен, не сдвигать начало к нулю

                ; обрезка отрицательного верха к строке 0 с высотой оставшегося конца
                LD B, #00
                LD D, A
                JP @Station.ClearScrollWindowBody.Address

                ; проверка неотрицательного начала относительно 192
Bottom:         CP @ClearBodyConst.YEnd
                RET NC                                                          ; выход, если начальный Y не меньше 192

                ; расчёт конца области с исходным байтовым переполнением
                ADD A, D
                JR C, @Station.ClearScrollWindowBody.ClipBottom                 ; переход, если сумма начала и высоты переполнила байт, сократить низ

                ; проверка конца без переполнения относительно 192
                CP @ClearBodyConst.YEnd
                JR C, @Station.ClearScrollWindowBody.Address                    ; переход, если конец меньше 192, оставить исходную высоту

                ; расчёт высоты до BF, строка 191 исключается, при начале 191 получится нулевой D
ClipBottom:     SUB @PointerConst.LastScreenY
                NEG
                ADD A, D
                LD D, A
                ; -----------------------------------------
                ; Экранный адрес и длина развёрнутых записей
                ; -----------------------------------------
                ; поиск адреса начала по исходным таблицам Y и X
Address:        LD H, @StationTables.RowHighPage
                LD L, B
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, C
                OR (HL)
                LD L, A
                LD H, B
                ; расчёт числа целых байтов из видимой ширины, младшие три бита проверяются отдельно
                LD B, E
                SRL E
                SRL E
                SRL E
                LD A, E
                ; вычет первого краевого байта
                SUB #01
                RET C                                                           ; выход, если после сдвига ширины нет первого байта

                LD E, A
                ; проверка кратности исходной видимой ширины восьми
                LD A, B
                AND @ScreenConst.PixelOffsetMask
                JR NZ, @Station.ClearScrollWindowBody.SetRuns                   ; переход, если ширина не кратна восьми, не вычитать дополнительный край

                ; вычет дополнительного байта при точной границе ширины
                LD A, E
                SUB #01
                RET C                                                           ; выход, если после вычета точной границы целых байтов не осталось

                LD E, A
                ; расчёт пропуска по двум байтам на неиспользованную пару развёрнутого блока из 30 записей
SetRuns:        LD A, @ClearBodyConst.UnrolledBytes
                SUB E
                ADD A, A
                ; обновление одинакового смещения всех трёх JR перед очисткой
                LD (@ClearBodyState.WholeSkip), A
                LD (@ClearBodyState.LeftSkip), A
                LD (@ClearBodyState.RightSkip), A
                ; выбор маски семи для шага экранной строки и правого сохраняемого поля
                LD E, @ScreenConst.PixelOffsetMask
                LD B, @ClearBodyConst.RightKeep
                ; проверка классификатора C'=FF отрицательного X через байтовый INC
                EXX
                INC C
                EXX
                JP Z, @Station.ClearScrollWindowBody.ClipLeft                   ; переход, если исходный старший X равен FF, очищать без левого поля

                ; выбор сохраняемых трёх левых пикселей, проверка классификатора правого отсечения
                LD B, @ClearBodyConst.LeftKeep
                EXX
                DEC C
                DEC C
                EXX
                JP Z, @Station.ClearScrollWindowBody.ClipRight                  ; переход, если C' обозначает правое отсечение, очищать без правого поля

                ; -----------------------------------------
                ; Очистка с обоими боковыми полями
                ; -----------------------------------------
                ; сохранение начала строки и очистка левого края маской E0
Whole:          LD C, L
                LD A, (HL)
                AND B
                LD (HL), A
                INC L
                XOR A
                JR @Station.ClearScrollWindowBody.WholeBytes

                ; обнуление оставшихся после изменяемого JR целых байтов, затем сохранение трёх правых пикселей
WholeBytes:     LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, (HL)
                AND @ScreenConst.PixelOffsetMask
                LD (HL), A
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.ClearScrollWindowBody.WholeNext                 ; переход, если следующий старший адрес остался внутри восьмистрочного блока

                LD A, L
                ADD A, @ScreenConst.ByteColumns
                LD L, A
                JR C, @Station.ClearScrollWindowBody.WholeNext                  ; переход, если прибавление 32 перенесло младший адрес в следующий экранный блок

                LD A, H
                SUB @ScreenConst.PixelsPerChar
                LD H, A
WholeNext:      DEC D
                JP NZ, @Station.ClearScrollWindowBody.Whole                     ; переход, если остались строки, повторить очистку с обоими полями

                RET

                ; -----------------------------------------
                ; Очистка после отсечения слева
                ; -----------------------------------------
                ; нулевые целые байты начинаются с левой границы экрана, сохраняется только правое поле
ClipLeft:       LD C, L
                XOR A
                JR @Station.ClearScrollWindowBody.LeftBytes

LeftBytes:      LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, (HL)
                AND B
                LD (HL), A
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.ClearScrollWindowBody.LeftNext                  ; переход, если следующий старший адрес остался внутри восьмистрочного блока

                LD A, L
                ADD A, @ScreenConst.ByteColumns
                LD L, A
                JR C, @Station.ClearScrollWindowBody.LeftNext                   ; переход, если прибавление 32 перенесло младший адрес в следующий экранный блок

                LD A, H
                SUB @ScreenConst.PixelsPerChar
                LD H, A
LeftNext:       DEC D
                JP NZ, @Station.ClearScrollWindowBody.ClipLeft                  ; переход, если остались строки, повторить очистку без левого поля

                RET

                ; -----------------------------------------
                ; Очистка после отсечения справа
                ; -----------------------------------------
                ; сохранение левого поля, далее нули до правого края без правой маски
ClipRight:      LD C, L
                LD A, (HL)
                AND B
                LD (HL), A
                INC L
                XOR A
                JR @Station.ClearScrollWindowBody.RightBytes

RightBytes:     LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.ClearScrollWindowBody.RightNext                 ; переход, если следующий старший адрес остался внутри восьмистрочного блока

                LD A, L
                ADD A, @ScreenConst.ByteColumns
                LD L, A
                JR C, @Station.ClearScrollWindowBody.RightNext                  ; переход, если прибавление 32 перенесло младший адрес в следующий экранный блок

                LD A, H
                SUB @ScreenConst.PixelsPerChar
                LD H, A
RightNext:      DEC D
                JP NZ, @Station.ClearScrollWindowBody.ClipRight                 ; переход, если остались строки, повторить очистку без правого поля

                RET

                ; -----------------------------------------
                endmodule
                endmodule
