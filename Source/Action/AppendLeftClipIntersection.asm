                module Action
                module AppendLeftClipIntersection
                ; Документация [алгоритм и проверка](../../Docs/ActionClipIntersections.md)
                ; -----------------------------------------
                ; Добавление пересечения границы с исходным делением и побайтовой проверкой координаты
                ; исходная запись 17, банковое окно ACTION банка 0, смещения #658B..#65E3
                ; In:
                ;   BC задаёт сохраняемый контекст при N>=0 и d>=0, AF - исходный Carry через EX AF, AF' передаётся в альтернативный входной Carry делителя
                ;   две signed16 точки FirstPoint и SecondPoint подготовлены, физический LeftProduct содержит числитель N
                ;   знаковый делитель d=(SecondPoint.Second-FirstPoint.Second) modulo 65536 ненулевой
                ;   U=N для N>=0, иначе U=-N-1, требуется U<abs(d)*65536 по договору DivideSigned32To16
                ;   OutputSize задаёт байтовое смещение назначения в существующей странице 90, два байта пишутся с оборачиванием INC L
                ;   ACTION находится в банке 0, IRQ не вмешиваются, на CPU-стеке внешний возврат и два дополнительных свободных байта
                ; Out:
                ;   HL равен 9000 OR ((входной OutputSize+2) AND FF)
                ;   DE сохраняет исходный FirstPoint.First при отрицательном слове пересечения либо установленном бите 7 младшего байта этого слова, иначе D равен записанному First, E равен младшему байту исходного FirstPoint.First
                ;   BC содержит старшее слово исходного N при N<0, иначе исходный d при d<0, иначе сохраняется
                ;   AF - A равен младшему байту HL, F равен флагам последнего INC L, Carry=0, это не флаги попадания точки в окно
                ;   HL', DE', BC' сохраняются
                ;   AF' - A' равен младшему байту результата DivideSigned32To16, F' соответствует договору делителя для подготовленных аргументов
                ;   IXH сохраняется, IXL равен числу отрицательных аргументов N и d минус один по модулю 256
                ;   IY сохраняется
                ;   I, IM, IFF и paging сохраняются, SP после RET равен входному SP+2, R меняется
                ;   в выходной буфер добавлены два байта Second и First, OutputSize увеличен на два по модулю 256
                ;   результат деления прибавляется к FirstPoint.First с оборачиванием до 16 бит
                ;   для вертикальной границы отрицательное слово First даёт 0, иначе младший байт с битом 7 даёт 95, иначе младший байт сохраняется даже при значении 96..127 или ненулевом старшем
                ;   фиксированная координата Second равна 0 и записывается первым байтом пары
                ;   R получает K M1 собственного писателя плюс полную стоимость DivideSigned32To16, CALL и конечный RET писателя включены, старший бит R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IXL, R, два выходных байта, OutputSize и два байта CPU-стека
                ; Note:
                ;   однокомплементное частное исходного делителя не заменяется обычным знаковым делением
                ;   правило вертикальной координаты не является насыщением в диапазон 0..95, исходные значения 96..127 не исправляются
                ;   все 65536 промежуточных слов и 256 выходных смещений проверены для этого входа, всего 69888 сценариев на вход
                ;   общая серия четырёх входов содержит 279552 сценария с настоящим делителем, точными регистрами и флагами кроме R, всей RAM и кратностью записей
                ;   все совместные входы, R/T, IRQ, сборка и нативный запуск не доказаны
                ;   K=29 при отрицательном слове translated, иначе 31 при бите 7 младшего байта и 32 при сброшенном бите
                ;   translated равно wrap16(частное+база), N=1 при отрицательном числителе, D=1 при отрицательном знаменателе, иначе соответствующий признак нулевой
                ;   U=(abs(числитель)-N)//abs(знаменатель), стоимость делителя равна 130+12*N+10*D-2*(N XOR D)-popcount(U) M1, числа стоимости десятичные
                ;   новая серия 69888 случаев этого входа проверяет точный R и полное число M1, общая новая серия четырёх писателей содержит 279552 случая
                ;   прежние ограничения R относятся к исходной серии, все совместные входы, точные T, IRQ и нативная игра остаются непроверенными
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка числителя
                ; Чтение младшего слова LeftProduct в A и альтернативный A, прежний основной Carry становится альтернативным входным Carry делителя.
Entry:          LD A, (@ActionClipProductsData.LeftProduct.LowWord)
                EX AF, AF'
                LD A, (@ActionClipProductsData.LeftProduct.LowWord+1)
                ; Чтение координат знаменателя, разность оборачивается до 16 бит с предварительно очищенным Carry.
                LD HL, (@ActionClipPoints.SecondPoint.Second)
                LD DE, (@ActionClipPoints.FirstPoint.Second)
                OR A
                SBC HL, DE
                EX DE, HL
                ; Чтение старшего слова числителя, Sign от разности задаёт знак делителя.
                LD HL, (@ActionClipProductsData.LeftProduct.HighWord)
                ; Расчёт исходного частного с однокомплементной обработкой отрицательных величин.
                CALL @Action.DivideSigned32To16.Entry
                ; Расчёт координаты пересечения прибавлением базы первой точки с оборачиванием до слова.
                LD DE, (@ActionClipPoints.FirstPoint.First)
                ADD HL, DE
                ; Проверка старшего байта переведённой координаты до выбора выходной пары.
                LD A, H
                AND A
                JP M, @Action.AppendLeftClipIntersection.NegativeY              ; переход, если полное слово First отрицательно, записать First=0

                ; Проверка знака только младшего байта First, положительный старший байт здесь больше не учитывается.
                LD A, L
                AND A
                JP P, @Action.AppendLeftClipIntersection.StorePoint             ; переход, если младший байт First не имеет бита 7, записать его без проверки границы 96

                LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                LD (HL), @ActionClipProductConst.ZeroBound
                INC L
                LD (HL), @ActionClipProductConst.FirstMaximum
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                ; Запись пары в исходную страницу 90 через байтовый индекс, INC L не переносится в H.
NegativeY:      LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                XOR A
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                ; Запись пары в исходную страницу 90 через байтовый индекс, INC L не переносится в H.
StorePoint:     LD D, L
                LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                LD (HL), @ActionClipProductConst.ZeroBound
                INC L
                LD (HL), D
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                endmodule
                endmodule
