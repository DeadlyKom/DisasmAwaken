                module Action
                module AppendLeftClipIntersection
                ; Документация [алгоритм и проверка](../../Docs/ActionClipIntersections.md)
                ; -----------------------------------------
                ; Добавление пересечения границы с исходным делением и побайтовой проверкой координаты
                ; исходная запись 17, банковое окно ACTION банка 0, смещения #658B..#65E3
                ; In:
                ;   две signed16 точки FirstPoint и SecondPoint подготовлены, физический LeftProduct содержит числитель N
                ;   знаковый делитель d=(Second.Second-First.Second) modulo 65536 ненулевой
                ;   U=N для N>=0, иначе U=-N-1, требуется U<abs(d)*65536 по договору DivideSigned32To16
                ;   OutputSize задаёт байтовое смещение назначения в существующей странице 90, два байта пишутся с оборачиванием INC L
                ;   ACTION находится в банке 0, IRQ не вмешиваются, на CPU-стеке внешний возврат и два дополнительных свободных байта
                ; Out:
                ;   HL равен 9000 OR ((входной OutputSize+2) AND FF), A равен его младшему байту
                ;   в выходной буфер добавлены два байта Second и First, OutputSize увеличен на два по модулю 256
                ;   результат деления прибавляется к First.First с оборачиванием до 16 бит
                ;   для вертикальной границы отрицательное слово First даёт 0, иначе младший байт с битом 7 даёт 95, иначе младший байт сохраняется даже при значении 96..127 или ненулевом старшем
                ;   фиксированная вторая координата границы равна 0
                ;   F равен флагам последнего INC L, Carry=0, это не флаги попадания точки в окно
                ;   BC соответствует DivideSigned32To16, DE описан по путям в ActionClipIntersections.md
                ;   HL', DE', BC', IXH и IY сохраняются, AF' и IXL соответствуют DivideSigned32To16 после подготовки аргументов
                ;   I, IM, IFF и paging сохраняются, SP после RET равен входному SP+2, R меняется
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IXL, R, два выходных байта, OutputSize и два байта CPU-стека
                ; Note:
                ;   однокомплементное частное исходного делителя не заменяется обычным знаковым делением
                ;   правило вертикальной координаты не является насыщением в диапазон 0..95, исходные значения 96..127 не исправляются
                ;   все 65536 промежуточных слов и 256 выходных смещений проверены для этого входа, всего 69888 сценариев на вход
                ;   общая серия четырёх входов содержит 279552 сценария с настоящим делителем, точными регистрами и флагами кроме R, всей RAM и кратностью записей
                ;   все совместные входы, R/T, IRQ, сборка и нативный запуск не доказаны
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
