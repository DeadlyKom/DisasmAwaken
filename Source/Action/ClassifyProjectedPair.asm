                module Action
                module ClassifyProjectedPair
                ; Документация [алгоритм и проверка](../../Docs/ActionProjectedPairCodes.md)
                ; -----------------------------------------
                ; Заполнение кодов двух проецированных точек и накопление их парных признаков границ
                ; исходная запись 17, адреса EC54..ECA7
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, по 8E00 и 8E05 доступны две FRenderProjectedPoint
                ;   Second содержит вторую экранную координату, First первую, полный старший байт 80 у Second является маркером отказа
                ;   страница 8E доступна на запись, ACTION банка 0 выбран, на CPU-стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL=8E0B, DE сохраняется, B=0A, C содержит тетраду сторон второй точки либо ноль при её маркере
                ;   ClipCode обеих записей обновляются всегда, при маркере соответствующей точки записывается ноль без прекращения прохода
                ;   обычный код равен ((стороны XOR 0F)<<4) OR стороны, младшая тетрада задаёт внешние стороны, старшая их отрицание
                ;   биты 3..0 означают First<0, First>=96, Second<0, Second>=256, противоположные признаки одной оси не совмещаются
                ;   A равен OR обычных кодов, F соответствует логическому OR, при двух маркерах A=0 и F=44
                ;   HL', DE', BC' сохраняются, AF'=0A/4A после последнего CP 0A, IX, IY, I/IM/IFF и paging сохраняются
                ;   SP после внешнего RET равен входному SP+2, дополнительных записей CPU-стека и портов нет
                ;   R учитывает обе итерации, 6 M1 вне обработки точек, маркер добавляет 14, обычная точка от 33 до 39
                ; Corrupt:
                ;   HL, BC, AF, AF', R и два ClipCode, SP внешним RET
                ; Note:
                ;   в отличие от ClassifyProjectedVertices маркер не завершает весь обход, исправлять это различие нельзя
                ;   Second имеет допустимый диапазон 0..255, First 0..95, знак и ненулевой положительный старший байт проверяются отдельно
                ;   268705 сценариев покрыли четыре полных словарных среза и 9^4 углов, все четыре комбинации маркеров
                ;   сверены точные регистры, флаги, R, вся 64K RAM и точная последовательность двух записей
                ;   полное произведение четырёх слов, аппаратные IRQ, время, сборка и нативный вывод не проверялись
                ; -----------------------------------------
                ; Подготовка двух пятибайтовых FRenderProjectedPoint и очистка альтернативного OR-накопителя.
Entry:          LD HL, @ActionVertexGroupConst.WorkPage + 1
                XOR A
                EX AF, AF'
                LD B, FRenderProjectedPoint + FRenderProjectedPoint
                ; Обновление тетрады сторон текущей точки перед чтением старшего байта Second.
NextPoint:      LD C, #00
                LD A, (HL)
                INC L
                INC L
                ; Проверка маркера отказа перспективы до интерпретации знака Second.
                CP @ActionPerspectiveConst.RejectedHigh
                JR Z, @Action.ClassifyProjectedPair.StoreRejected               ; переход, если старший байт Second равен 80, записать нулевой код только текущей точки

                JR NC, @Action.ClassifyProjectedPair.SecondNegative             ; переход, если старший байт Second больше 80, установить сторону Second<0

                ; Проверка положительного Second, ненулевой старший байт означает выход за 255.
                AND A
                JP NZ, @Action.ClassifyProjectedPair.SecondHigh                 ; переход, если положительный Second не меньше 256, установить старшую сторону

                JP @Action.ClassifyProjectedPair.CheckFirst

                ; Установка отрицательной стороны Second, маркер 80xx уже исключён.
SecondNegative: SET @ActionVertexCodeConst.SecondNegBit, C
                JP @Action.ClassifyProjectedPair.CheckFirst

                ; Установка положительной внешней стороны Second>=256.
SecondHigh:     SET @ActionVertexCodeConst.SecondHighBit, C
                ; Проверка знака и старшего байта первой экранной координаты.
CheckFirst:     LD A, (HL)
                AND A
                JP M, @Action.ClassifyProjectedPair.FirstNegative               ; переход, если First отрицателен, установить отрицательную сторону

                JP NZ, @Action.ClassifyProjectedPair.FirstHigh                  ; переход, если старший байт положительного First ненулевой, установить сторону First>=96

                ; Проверка нижней границы выхода First>=96 при нулевом старшем байте.
                DEC L
                LD A, (HL)
                INC L
                CP @ActionVertexCodeConst.FirstLimit
                JR NC, @Action.ClassifyProjectedPair.FirstHigh                  ; переход, если First не меньше 96, установить старшую сторону

                JP @Action.ClassifyProjectedPair.StoreCode

                ; Установка отрицательной стороны First без одновременной установки положительной.
FirstNegative:  SET @ActionVertexCodeConst.FirstNegBit, C
                JP @Action.ClassifyProjectedPair.StoreCode

                ; Установка положительной внешней стороны First>=96.
FirstHigh:      SET @ActionVertexCodeConst.FirstHighBit, C
                ; Расчёт парных тетрад ClipCode и обновление накопителя обычных точек в альтернативном AF.
StoreCode:      INC L
                LD A, C
                RLCA
                RLCA
                RLCA
                RLCA
                XOR @ActionVertexCodeConst.InverseMask
                OR C
                LD (HL), A
                EX AF, AF'
                OR (HL)
                EX AF, AF'
                ; Проверка смещения конца текущей записи, после второй точки оно равно 0A.
CheckEnd:       INC L
                LD A, L
                INC L
                CP B
                JP NZ, @Action.ClassifyProjectedPair.NextPoint                  ; переход, если смещение конца записи не равно 0A, обработать вторую точку

                ; Восстановление накопленного OR двух обычных кодов, нулевые маркеры его не изменяли.
                EX AF, AF'
                RET

                ; Обновление только ClipCode текущего отказа, вторая точка всё равно будет обработана.
StoreRejected:  INC L
                LD (HL), C
                JP @Action.ClassifyProjectedPair.CheckEnd

                endmodule
                endmodule
