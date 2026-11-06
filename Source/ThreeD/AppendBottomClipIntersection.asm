                module ThreeD
                module AppendBottomClipIntersection
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Добавление пересечения границы с исходным делением и побайтовой проверкой координаты
                ; исходная запись 19, банк 0, смещения #0540..#0587
                ; In:
                ;   две signed16 точки FirstPoint и SecondPoint подготовлены, физический BottomProduct содержит числитель N
                ;   знаковый делитель d=(Second.First-First.First) modulo 65536 ненулевой
                ;   U=N для N>=0, иначе U=-N-1, требуется U<abs(d)*65536 по договору DivideSigned32To16
                ;   OutputSize задаёт байтовое смещение назначения в существующей странице 90, два байта пишутся с оборачиванием INC L
                ;   3DPART находится в банке 0, IRQ не вмешиваются, на CPU-стеке внешний возврат и два дополнительных свободных байта
                ; Out:
                ;   HL равен 9000 OR ((входной OutputSize+2) AND FF), A равен его младшему байту
                ;   в выходной буфер добавлены два байта Second и First, OutputSize увеличен на два по модулю 256
                ;   результат деления прибавляется к First.Second с оборачиванием до 16 бит
                ;   для горизонтальной границы отрицательное слово Second даёт 0, положительное с ненулевым старшим байтом даёт 255, иначе сохраняется младший байт
                ;   фиксированная вторая координата границы равна 95
                ;   F равен флагам последнего INC L, Carry=0, это не флаги попадания точки в окно
                ;   BC соответствует DivideSigned32To16, DE описан по путям в ActionClipIntersections.md
                ;   HL', DE', BC', IXH и IY сохраняются, AF' и IXL соответствуют DivideSigned32To16 после подготовки аргументов
                ;   I, IM, IFF и paging сохраняются, SP после RET равен входному SP+2, R меняется
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
                ; Чтение младшего слова BottomProduct в A и альтернативный A, прежний основной Carry становится альтернативным входным Carry делителя.
Entry:          LD A, (@ThreeDClipProductsData.BottomProduct.LowWord)
                EX AF, AF'
                LD A, (@ThreeDClipProductsData.BottomProduct.LowWord+1)
                ; Чтение координат знаменателя, разность оборачивается до 16 бит с предварительно очищенным Carry.
                LD HL, (@ThreeDClipPoints.SecondPoint.First)
                LD DE, (@ThreeDClipPoints.FirstPoint.First)
                OR A
                SBC HL, DE
                EX DE, HL
                ; Чтение старшего слова числителя, Sign от разности задаёт знак делителя.
                LD HL, (@ThreeDClipProductsData.BottomProduct.HighWord)
                ; Расчёт исходного частного с однокомплементной обработкой отрицательных величин.
                CALL @ThreeD.DivideSigned32To16.Entry
                ; Расчёт координаты пересечения прибавлением базы первой точки с оборачиванием до слова.
                LD DE, (@ThreeDClipPoints.FirstPoint.Second)
                ADD HL, DE
                ; Проверка старшего байта переведённой координаты до выбора выходной пары.
                LD A, H
                AND A
                JR Z, @ThreeD.AppendBottomClipIntersection.StorePoint           ; переход, если старший байт Second равен нулю, записать его младший байт

                JP P, @ThreeD.AppendBottomClipIntersection.UpperX               ; переход, если ненулевой старший байт Second положителен, записать Second=255

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

                ; Ограничение положительного выхода Second полным байтовым значением 255.
UpperX:         LD L, @ActionClipProductConst.SecondMaximum
                ; Запись пары в исходную страницу 90 через байтовый индекс, INC L не переносится в H.
StorePoint:     LD E, L
                LD A, (@ActionClipIntersectionsState.OutputSize)
                LD L, A
                LD H, @ActionClipIntersectionConst.OutputPage
                LD (HL), E
                INC L
                LD (HL), @ActionClipProductConst.FirstMaximum
                INC L
                LD A, L
                LD (@ActionClipIntersectionsState.OutputSize), A
                RET

                endmodule
                endmodule
