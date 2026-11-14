                module ThreeD
                module AppendRightClipIntersection
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Добавление пересечения границы с исходным делением и побайтовой проверкой координаты
                ; исходная запись 19, банк 0, смещения #05E7..#0640
                ; In:
                ;   BC задаёт сохраняемый контекст при N>=0 и d>=0, AF - исходный Carry через EX AF, AF' передаётся в альтернативный входной Carry делителя
                ;   две signed16 точки FirstPoint и SecondPoint подготовлены, физический RightProduct содержит числитель N
                ;   знаковый делитель d=(SecondPoint.Second-FirstPoint.Second) modulo 65536 ненулевой
                ;   U=N для N>=0, иначе U=-N-1, требуется U<abs(d)*65536 по договору DivideSigned32To16
                ;   OutputSize задаёт байтовое смещение назначения в существующей странице 90, два байта пишутся с оборачиванием INC L
                ;   3DPART находится в банке 0, IRQ не вмешиваются, на CPU-стеке внешний возврат и два дополнительных свободных байта
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
                ;   фиксированная координата Second равна 255 и записывается первым байтом пары
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IXL, R, два выходных байта, OutputSize и два байта CPU-стека
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   однокомплементное частное исходного делителя не заменяется обычным знаковым делением
                ;   правило вертикальной координаты не является насыщением в диапазон 0..95, исходные значения 96..127 не исправляются
                ;   все 65536 промежуточных слов и 256 выходных смещений проверены для этого входа, всего 69888 сценариев на вход
                ;   общая серия четырёх входов содержит 279552 сценария с настоящим делителем, точными регистрами и флагами кроме R, всей RAM и кратностью записей
                ;   все совместные входы, R/T, IRQ, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка числителя
                ; Чтение младшего слова RightProduct в A и альтернативный A, прежний основной Carry становится альтернативным входным Carry делителя.
Entry:          LD A, (@ThreeDClipProductsData.RightProduct.LowWord)
                EX AF, AF'
                LD A, (@ThreeDClipProductsData.RightProduct.LowWord+1)
                ; Чтение координат знаменателя, разность оборачивается до 16 бит с предварительно очищенным Carry.
                LD HL, (@ThreeDClipPoints.SecondPoint.Second)
                LD DE, (@ThreeDClipPoints.FirstPoint.Second)
                OR A
                SBC HL, DE
                EX DE, HL
                ; Чтение старшего слова числителя, Sign от разности задаёт знак делителя.
                LD HL, (@ThreeDClipProductsData.RightProduct.HighWord)
                ; Расчёт исходного частного с однокомплементной обработкой отрицательных величин.
                CALL @ThreeD.DivideSigned32To16.Entry
                ; Расчёт координаты пересечения прибавлением базы первой точки с оборачиванием до слова.
                LD DE, (@ThreeDClipPoints.FirstPoint.First)
                ADD HL, DE
                ; Проверка старшего байта переведённой координаты до выбора выходной пары.
                LD A, H
                AND A
                JP M, @ThreeD.AppendRightClipIntersection.NegativeY             ; переход, если полное слово First отрицательно, записать First=0

                ; Проверка знака только младшего байта First, положительный старший байт здесь больше не учитывается.
                LD A, L
                AND A
                JP P, @ThreeD.AppendRightClipIntersection.StorePoint            ; переход, если младший байт First не имеет бита 7, записать его без проверки границы 96

                LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                LD (HL), @ActionClipProductConst.SecondMaximum
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
                LD (HL), @ActionClipProductConst.SecondMaximum
                INC L
                LD (HL), @ActionClipProductConst.ZeroBound
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                ; Запись пары в исходную страницу 90 через байтовый индекс, INC L не переносится в H.
StorePoint:     LD D, L
                LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                LD (HL), @ActionClipProductConst.SecondMaximum
                INC L
                LD (HL), D
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                endmodule
                endmodule
