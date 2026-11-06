                module Action
                module ClassifyProjectedVertices
                ; Документация [алгоритм и проверка](../../Docs/ActionVertexCodes.md)
                ; -----------------------------------------
                ; Заполнение кодов границ экранных точек и накопление общего кода объекта
                ; исходная запись 17, адреса DEF3..DFB5
                ; In:
                ;   NextOffset содержит 4+5*n, n от 1 до 50, последовательные FRenderProjectedPoint начинаются по 8E00
                ;   Second является второй экранной координатой, First первой, старший байт 80 у Second обозначает отказ перспективы
                ;   RAM страницы 8E доступна на запись, CPU-стек содержит внешний возврат, дополнительно нужны два байта сохранённого HL
                ;   ACTION доступен в банке 0, IRQ не вмешиваются, нулевое и несогласованное число записей вне этого договора
                ; Out:
                ;   HL, DE, IX и IY сохраняются, B=5*n, C содержит стороны последней обработанной точки либо нуль при маркере отказа
                ;   для каждой достигнутой точки без маркера ClipCode получает пару тетрад, младшая содержит признаки выхода, старшая их побитовое отрицание
                ;   младшие биты 3..0 означают First<0, First>=96, Second<0, Second>=256, противоположные признаки одной оси не совмещаются
                ;   если маркера нет, A равен OR всех записанных ClipCode, F равен флагам логического OR этого байта
                ;   при полном проходе A'=5*n, F' равен флагам последнего CP B с равными операндами
                ;   при маркере 80xx A=0/F=44, AF' хранит накопление предыдущих точек, остальные ещё не достигнутые коды сохраняются
                ;   HL', DE', BC' сохраняются, SP после RET равен входному SP+2, I, IM, IFF и paging сохраняются, R меняется, портов нет
                ; Corrupt:
                ;   BC, AF, AF', R, достигнутые ClipCode и два байта CPU-стека
                ; Note:
                ;   для Second исходный код сначала различает старший байт 80 как маркер, затем знак и ненулевой положительный старший байт
                ;   граница First=96 проверяется по младшему байту только при нулевом старшем, отрицательное слово получает только отрицательную сторону
                ;   перемещение INC L намеренно не переносится в H, договор ограничен записями одной страницы
                ;   нулевой результат означает маркер, обычный код всегда содержит хотя бы по одному биту каждой пары и не равен нулю
                ;   525288 сценариев проверяют два полных словарных среза, длины 1..50, поздние отказы, регистры, флаги, всю RAM и кратность записей
                ;   R, время, пустой буфер, несогласованные смещения, все совместные входы, IRQ и нативный вывод не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка прохода одной страницы
                ; Сохранение HL, очистка альтернативного накопителя и расчёт конечного байтового смещения как NextOffset-4.
Entry:          PUSH HL
                XOR A
                EX AF, AF'
                LD HL, @ActionVertexGroupConst.WorkPage+1
                LD A, (@ActionVertexGroupState.NextOffset)
                SUB @ActionObjectVerticesConst.InitialOffset
                LD B, A
                ; -----------------------------------------
                ; Классификация второй координаты
                ; Очистка сторон текущей точки, чтение старшего байта Second и переход к старшему байту First.
NextPoint:      LD C, #00
                LD A, (HL)
                INC L
                INC L
                ; Проверка полного старшего байта 80 как маркера отказа перспективы до остальных знаковых проверок.
                CP @ActionPerspectiveConst.RejectedHigh
                JR Z, @Action.AbortProjectedVertexScan.Entry                    ; переход, если старший байт Second равен 80, завершить весь проход без отката кодов

                JR NC, @Action.ClassifyProjectedVertices.SecondNegative         ; переход, если старший байт Second больше 80, установить отрицательную сторону

                ; Проверка ненулевого положительного старшего байта Second, такая точка лежит за границей 256.
                AND A
                JP NZ, @Action.ClassifyProjectedVertices.SecondHigh             ; переход, если положительный Second не меньше 256, установить старшую сторону

                ; Проверка старшего байта First, знак задаёт отрицательную сторону, ненулевое положительное слово старшую.
                LD A, (HL)
                AND A
                JP M, @Action.ClassifyProjectedVertices.FirstNegative           ; переход, если First отрицателен, установить отрицательную сторону

                JP NZ, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если старший байт положительного First ненулевой, установить сторону First>=96

                DEC L
                LD A, (HL)
                INC L
                ; Проверка First>=96 при нулевом старшем байте.
                CP @ActionVertexCodeConst.FirstLimit
                JR NC, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если First не меньше 96, установить старшую сторону

                INC L
                ; Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                ; Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.
                INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedVertices.NextPoint              ; переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую

                POP HL
                EX AF, AF'
                RET

                ; Установка стороны Second<0, маркер 80xx уже исключён.
SecondNegative: SET @ActionVertexCodeConst.SecondNegBit, C
                ; Проверка старшего байта First, знак задаёт отрицательную сторону, ненулевое положительное слово старшую.
                LD A, (HL)
                AND A
                JP M, @Action.ClassifyProjectedVertices.FirstNegative           ; переход, если First отрицателен, установить отрицательную сторону

                JP NZ, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если старший байт положительного First ненулевой, установить сторону First>=96

                DEC L
                LD A, (HL)
                INC L
                ; Проверка First>=96 при нулевом старшем байте.
                CP @ActionVertexCodeConst.FirstLimit
                JR NC, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если First не меньше 96, установить старшую сторону

                INC L
                ; Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                ; Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.
                INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedVertices.NextPoint              ; переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую

                POP HL
                EX AF, AF'
                RET

                ; Установка стороны First>=96, противоположный отрицательный признак здесь не ставится.
FirstHigh:      SET @ActionVertexCodeConst.FirstHighBit, C
                INC L
                ; Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                ; Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.
                INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedVertices.NextPoint              ; переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую

                POP HL
                EX AF, AF'
                RET

                ; Установка стороны Second>=256.
SecondHigh:     SET @ActionVertexCodeConst.SecondHighBit, C
                ; Проверка старшего байта First, знак задаёт отрицательную сторону, ненулевое положительное слово старшую.
                LD A, (HL)
                AND A
                JP M, @Action.ClassifyProjectedVertices.FirstNegative           ; переход, если First отрицателен, установить отрицательную сторону

                JP NZ, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если старший байт положительного First ненулевой, установить сторону First>=96

                DEC L
                LD A, (HL)
                INC L
                ; Проверка First>=96 при нулевом старшем байте.
                CP @ActionVertexCodeConst.FirstLimit
                JR NC, @Action.ClassifyProjectedVertices.FirstHigh              ; переход, если First не меньше 96, установить старшую сторону

                INC L
                ; Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                ; Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.
                INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedVertices.NextPoint              ; переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую

                POP HL
                EX AF, AF'
                RET

                ; Установка стороны First<0.
FirstNegative:  SET @ActionVertexCodeConst.FirstNegBit, C
                INC L
                ; Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                ; Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.
                INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedVertices.NextPoint              ; переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую

                POP HL
                EX AF, AF'
                RET

                ; -----------------------------------------
                endmodule
                endmodule
