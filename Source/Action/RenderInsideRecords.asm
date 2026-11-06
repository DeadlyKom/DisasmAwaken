                module Action
                module RenderInsideRecords
                ; Документация [алгоритм и проверка](../../Docs/ActionPacketRenderer.md)
                ; -----------------------------------------
                ; Вывод граней и ломаных объекта с внутренними точками без дополнительного отсечения
                ; исходная запись 17, адреса DD23..DDD0
                ; In:
                ;   HL указывает на конечный поток переменных записей объекта с полным нулём в конце, данные не пересекаются с изменяемыми буферами и стеком
                ;   DE и BC входных аргументов не задают, начальный C и остальные регистры сохраняются либо меняются по реально достигнутым детям
                ;   AF, HL', DE', BC', AF', IX и IY содержат контекст вызывающего, ребёнок ориентации использует входной IX
                ;   страница 8E содержит выбранные пятибайтовые FRenderProjectedPoint, Second от 0 до 255, First от 0 до 95
                ;   грани имеют 3..15 вершин выпуклого положительного либо обратного обхода, горизонтальное вырождение допустимо, материалы 0..4
                ;   ломаные имеют 2..15 вершин, индексы выбирают записи целиком внутри страницы, проверены все 40 исходных слотов
                ;   FaceGate до первой грани задаётся вызывающим, он существенен для линий с установленным битом 6
                ;   ACTION банка 0 доступен на запись, исходные маски и шаблоны сохранены, CPU-стек содержит внешний возврат и не пересекается с временным стеком FFE0
                ;   IRQ не вмешиваются в временные SP и общие изменяемые операнды
                ; Out:
                ;   HL указывает на полный нулевой конец списка, A=0, F=54, SP после RET равен входному SP+2
                ;   DE, BC и альтернативные и индексные регистры содержат точный результат последнего достигнутого ребёнка с восстановлением пар вокруг сегмента линии
                ;   полная композиция регистров задана ReferenceActionPacketRenderer.PacketRenderer.render, пустой поток меняет только AF и внешний возврат
                ;   FaceGate равен 1 после неотрицательной ориентации последней грани и 0 после отрицательной, при отсутствии граней сохраняется
                ;   отрицательная ориентация разрешает заливку, неотрицательная пропускает всю запись с сохранением числа вершин
                ;   грань копирует младшие Second и First в страницу 90 и вызывает PreparePolygonFill, дополнительное отсечение не выполняется
                ;   ломаная содержит count-1 открытых сегментов, концы читаются последовательно, при битe 6 и ненулевом FaceGate запись полностью пропускается
                ;   пиксели, рабочие координаты, операнды детей и остаточные CPU/временные стековые слова совпадают с композиционным эталоном
                ;   I, IM, IFF и paging сохраняются, R меняется, порты не используются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, FaceGate, пиксели, рабочие точки и буферы, операнды детей и существующие CPU/временные стековые слова
                ; Note:
                ;   бит 7 заголовка выбирает ломаную, младшая тетрада число вершин, для грани биты 6..4 числовой материал
                ;   для линии бит 6 связывает её с результатом ориентации предыдущей грани, поле 5..4 выбирает AND, OR либо XOR, 10 и 11 оба XOR
                ;   нулевой размер записи не является обычной фигурой, исходный родитель проверяет полный нуль до типа и длины
                ;   вызывающий E4DB выбирает этот вход только при нулевой младшей тетраде объединённых кодов точек
                ;   1850 композиционных сценариев исполняют настоящих детей, сверены регистры кроме R, вся физическая RAM и кратность записей
                ;   проверены все счётчики указанного профиля, оба обхода, границы окна, 40 слотов и перенос HL через страницу
                ;   альтернативный родитель DBBD с отсечением, все сочетания потоков, R/T, IRQ, сборка и нативное исполнение не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Следующая запись объекта
                ; Чтение полного заголовка, нуль завершает поток раньше разделения типов.
Entry:          LD A, (HL)
                AND A
                RET Z                                                           ; выход, если достигнут полный нулевой заголовок, поток объекта закончился

                JP M, @Action.RenderInsideRecords.LineRecord                    ; переход, если установлен бит 7 заголовка, обработать ломаную

                ; -----------------------------------------
                ; Ориентация и материал грани
                ; Выбор числа вершин и проверка ориентации настоящим CheckFaceOrientation.
                AND @ActionPacketRendererConst.CountMask
                LD B, A
                CALL @Action.CheckFaceOrientation.Entry
                JP P, @Action.RenderInsideRecords.RejectFace                    ; переход, если результат ориентации неотрицателен, отметить отказ и пропустить грань

                ; Обновление FaceGate нулём после разрешённой отрицательной ориентации.
                XOR A
                LD (@ActionPacketRendererState.FaceGate), A
                ; Расчёт материала из разрядов 6..4 заголовка четырьмя циклическими сдвигами.
                LD A, (HL)
                INC HL
                RRCA
                RRCA
                RRCA
                RRCA
                AND @ActionPacketRendererConst.MaterialMask
                ; Обновление операнда Mode подготовителя заливки номером материала.
                LD (@ActionPolygonPreparationState.Mode), A
                ; -----------------------------------------
                ; Копирование внутреннего контура
                ; Выбор страницы 90 и расчёт выходного размера как удвоенного числа вершин.
                LD DE, @ActionPolygonPreparationState.Vertices
                LD A, B
                ADD A, A
                LD (@ActionClipIntersectionsState.OutputSize), A
                ; Выбор страницы 8E и сохранение счётчика вершин в альтернативном AF.
                LD B, @ActionPacketRendererConst.PointPage
                RRCA
                ; Чтение следующего индекса, копирование младших Second и First без повторного отсечения.
NextFacePoint:  EX AF, AF'
                LD C, (HL)
                INC HL
                LD A, (BC)
                LD (DE), A
                INC E
                INC C
                INC C
                LD A, (BC)
                LD (DE), A
                INC E
                EX AF, AF'
                ; Проверка числа оставшихся вершин с сохранением рабочего AF копировщика.
                DEC A
                JP NZ, @Action.RenderInsideRecords.NextFacePoint                ; переход, если остались вершины грани, скопировать следующую пару координат

                ; Заполнение скопированного контура через настоящий PreparePolygonFill и его строковое ядро.
                CALL @Action.PreparePolygonFill.Entry
                JP @Action.RenderInsideRecords.Entry

                ; -----------------------------------------
                ; Отказ ориентации и пропуск записи
                ; Обновление FaceGate единицей, связанные линии затем могут быть пропущены.
RejectFace:     LD A, #01
                LD (@ActionPacketRendererState.FaceGate), A
                ; Расчёт полного размера записи как число индексов плюс заголовок и продвижение HL.
SkipRecord:     INC B
                LD C, B
                LD B, #00
                ADD HL, BC
                JP @Action.RenderInsideRecords.Entry

                ; -----------------------------------------
                ; Ломаная и связь с предыдущей гранью
                ; Выбор числа вершин и проверка бита связи с FaceGate.
LineRecord:     AND @ActionPacketRendererConst.CountMask
                LD B, A
                BIT @ActionPacketRendererConst.AttachBit, (HL)
                JR Z, @Action.RenderInsideRecords.PrepareLineMode               ; переход, если бит связи с предыдущей гранью сброшен, рисовать независимо от FaceGate

                ; Проверка сохранённого результата ориентации предыдущей грани.
                LD A, (@ActionPacketRendererState.FaceGate)
                AND A
                JR NZ, @Action.RenderInsideRecords.SkipRecord                   ; переход, если FaceGate ненулевой, пропустить связанную ломаную

                ; -----------------------------------------
                ; Операция пикселей
                ; Расчёт числа открытых сегментов как число вершин минус один и выбор поля режима 5..4.
PrepareLineMode:DEC B
                LD A, (HL)
                INC HL
                AND @ActionPacketRendererConst.LineModeMask
                JR Z, @Action.RenderInsideRecords.SetClearMode                  ; переход, если поле режима равно 00, выбрать AND с инверсными масками

                ; Проверка числового селектора OR, оставшиеся 10 и 11 оба означают XOR.
                CP @ActionPacketRendererConst.OrSelector
                JR Z, @Action.RenderInsideRecords.SetOrMode                     ; переход, если поле режима равно 01, выбрать OR с прямыми масками

                ; Подготовка XOR и проверки Carry для прямых масок.
                LD DE, @ActionPacketRendererConst.XorModeWord
                LD A, @ActionLineRasterConst.SetOffset
                JP @Action.RenderInsideRecords.StoreLineMode

                ; Подготовка AND и проверки отсутствия Carry для инверсных масок.
SetClearMode:   LD DE, @ActionPacketRendererConst.AndModeWord
                LD A, @ActionLineRasterConst.ClearOffset
                JP @Action.RenderInsideRecords.StoreLineMode

                ; Подготовка OR и проверки Carry для прямых масок.
SetOrMode:      LD DE, @ActionPacketRendererConst.OrModeWord
                LD A, @ActionLineRasterConst.SetOffset
                ; Обновление пары рабочих opcode и операнда выбора таблицы масок растеризатора.
StoreLineMode:  LD (@ActionLineRasterState.PixelOpcode), DE
                LD (@ActionLineRasterState.MaskOffset), A
                ; -----------------------------------------
                ; Открытые сегменты ломаной
                ; Чтение первого конца, следующая итерация перенесёт его в FirstPoint.
                LD D, @ActionPacketRendererConst.PointPage
                LD E, (HL)
                INC HL
                LD A, (DE)
                LD (@ActionLineRasterState.SecondPoint), A
                ; Выбор младшей First на два байта дальше младшей Second, старшие координаты здесь не используются.
                INC E
                INC E
                LD A, (DE)
                LD (@ActionLineRasterState.SecondPoint+1), A
                ; Чтение следующего индекса и сохранение счётчика и указателя потока вокруг вызова рисователя.
NextLinePoint:  LD D, @ActionPacketRendererConst.PointPage
                LD E, (HL)
                INC HL
                PUSH BC
                PUSH HL
                ; Обновление первого конца предыдущим вторым и чтение нового второго конца.
                LD HL, (@ActionLineRasterState.SecondPoint)
                LD (@ActionLineRasterState.FirstPoint), HL
                LD A, (DE)
                LD (@ActionLineRasterState.SecondPoint), A
                ; Выбор младшей First нового конца в той же странице 8E.
                INC E
                INC E
                LD A, (DE)
                LD (@ActionLineRasterState.SecondPoint+1), A
                ; Рисование одного открытого сегмента через DrawLinearLine.
                CALL @Action.DrawLinearLine.Entry
                ; Восстановление указателя потока и счётчика, ребёнок имеет право менять основные пары.
                POP HL
                POP BC
                DJNZ @Action.RenderInsideRecords.NextLinePoint

                JP @Action.RenderInsideRecords.Entry

                ; -----------------------------------------
                endmodule
                endmodule
