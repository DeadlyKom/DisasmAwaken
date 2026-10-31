                module D3D
                module RenderPreviewClippedFaces
                ; Документация [отказы кодов сторон, прямой и отсечённый контур, разнесённое состояние линии и полный bitmap](../../Docs/PreviewClippedFaceStream.md)
                ; -----------------------------------------
                ; Полный поток граней и полилиний с кодами сторон и обоими отсекателями
                ; исходная запись 6, банк 4, файловые смещения #1BE9..#1D4E
                ; In:
                ;   HL поток заголовков и индексных байтов, заканчивается полным нулём, DE не задаёт геометрию
                ;   BC содержит контекст для первого исполненного обработчика, AF не является параметром
                ;   HL', DE', BC', AF', IX, IY исходный контекст вложенной арифметики и рисователей
                ;   индексы задают пятибайтовые FPreviewProjectedVertex страницы C6 с согласованными словами координат и кодами
                ;   положительная грань содержит 3..15 вершин и режим 0..4, полилиния 2..15, контуры допустимы для исходной заливки
                ;   операнды границ и таблицы строк подготовлены, проверенное окно имеет нулевые минимумы и верхние пределы 127,95
                ;   RejectCode задаёт разрешение первой условной полилинии, CPU-стек и рабочие области помощников доступны
                ; Out:
                ;   HL указывает на завершающий нуль без его пропуска, DE принадлежит последнему вычислению или рисователю
                ;   BC контекст последнего пути, после пропуска B=0,C=N+1, после полилинии B=0,C её входной
                ;   AF содержит A=0,F=54 от завершающего AND A
                ;   HL', DE', BC', AF', IX и IY определяются последовательной композицией помощников, полного конечного оракула всех регистров нет
                ;   RejectCode меняет только результат ориентации положительной грани, геометрический отказ затем его не устанавливает
                ;   физическое состояние линии хранит последнее исходное ребро, даже если оно не нарисовано или передано отсекателю
                ;   ByteCount и C8 принадлежат последнему скопированному контуру или отсечению, автоматического очищения между записями нет
                ;   SP после RET равен входному+2, I, IFF и IM сохранены, выбранный банк не меняется
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, bitmap, рабочие концы, состояние линии и углов, кэши, C8, параметры заливки и ребра, операнды и CPU-стек
                ; Note:
                ;   после принятой ориентации код 0 любой вершины либо общая внешняя сторона подавляют грань без изменения RejectCode=0
                ;   прямой контур копирует младшие координатные байты, смешанный вызывает E171 и рисуется только при Carry=0
                ;   каждая полилиния выбирает согласованные pixel opcode, boundary opcode и смещение масок
                ;   сегмент с нулевым кодом конца либо общей внешней стороной не рисуется, смешанный проходит EAB6
                ;   после отсечения линия рисуется только при Z=1, это обычные четыре выходных байта, IX текущего индекса восстанавливается
                ;   1170 потоков проверили полный bitmap и параметры 258 заливок и 1177 рёбер, реальные помощники не подменялись
                ;   все конечные регистры, ненулевые минимумы, режимы заполнения 5..7, IRQ и игровой запуск остаются открытыми
                ; -----------------------------------------
                ; -----------------------------------------
                ; Заголовок и положительная грань
                ; -----------------------------------------
                ; чтение полного заголовка без продвижения указателя
Entry:          LD A, (HL)
                ; проверка завершения потока полным нулём
                AND A
                RET Z                                                           ; выход, если полный заголовок равен нулю, HL остаётся на нём

                JP M, @D3D.RenderPreviewClippedFaces.Polyline                   ; переход, если bit7 заголовка установлен, обработать полилинию

                ; извлечение младшего числового поля числа индексных байтов
                AND @PreviewFaceStreamConst.CountMask
                LD B, A
                ; расчёт ориентации исходным определителем с обычной либо разреженной тройкой
                CALL @D3D.ComputePreviewFaceOrientation.Entry
                JP P, @D3D.RenderPreviewClippedFaces.RejectFace                 ; переход, если S определителя сброшен, установить отказ предыдущей ориентации

                ; обнуление отказа ориентации до последующих геометрических проверок
                XOR A
                LD (@PreviewFaceGateState.Value.RejectCode), A
                ; проверка полных кодов всех вершин и накопление их OR в C
                CALL @D3D.CollectPreviewFaceCodes.Entry
                JR C, @D3D.RenderPreviewClippedFaces.SkipRecord                 ; переход, если встретился полный нулевой код вершины, пропустить грань

                ; проверка общей внешней стороны по дополнению старшей тетрады накопленных кодов
                CPL
                AND @PreviewClipDispatchConst.ComplementMask
                JR NZ, @D3D.RenderPreviewClippedFaces.SkipRecord                ; переход, если после дополнения остался бит общей внешней стороны, пропустить грань

                ; повторное чтение принятого заголовка и переход к первому индексу
CopyPolygon:    LD A, (HL)
                INC HL
                ; расчёт индекса заполнения из исходного поля 6..4 четырьмя RRCA
                RRCA
                RRCA
                RRCA
                RRCA
                AND @PreviewFaceStreamConst.FillMask
                ; сохранение режима заливки после всех ранних отказов
                LD (@PreviewFillMode.Value.Index), A
                ; проверка младшей тетрады накопленных кодов, нуль означает все вершины внутри
                LD A, C
                AND @PreviewFaceStreamConst.CountMask
                JR NZ, @D3D.RenderPreviewClippedFaces.ClipPolygon               ; переход, если есть внешние вершины, отсечь весь замкнутый контур

                ; -----------------------------------------
                ; Прямое копирование внутреннего контура
                ; -----------------------------------------
                ; выбор начала пар колонка и строка страницы C8
                LD DE, @PreviewPolygonPrepConst.FirstPointRow - 1
                ; расчёт байтового размера двух координат на каждую вершину
                LD A, B
                ADD A, A
                LD (@PreviewContourSize.Value.ByteCount), A
                ; выбор страницы проекции и возврат от 2*N к числу вершин
                LD B, @PreviewFaceMathConst.VertexPage
                RRCA
                ; сохранение счётчика в AF' перед чтением младшего байта колонки
CopyVertex:     EX AF, AF'
                ; поиск проекции по очередному байтовому индексу
                LD C, (HL)
                INC HL
                ; чтение и запись колонки, затем продвижение внутри C8
                LD A, (BC)
                LD (DE), A
                INC E
                ; выбор младшего байта строки через смещение поля FirstAxis
                INC C
                INC C
                ; чтение и запись строки после колонки
                LD A, (BC)
                LD (DE), A
                INC E
                ; восстановление и уменьшение числа оставшихся вершин
                EX AF, AF'
                DEC A
                JP NZ, @D3D.RenderPreviewClippedFaces.CopyVertex                ; переход, если остались вершины прямого контура, продолжить копирование

                ; рисование принятого внутреннего контура настоящим растровым заполнением
                CALL @D3D.FillPreviewPolygon.Entry
                JP @D3D.RenderPreviewClippedFaces.Entry

                ; отсечение замкнутой последовательности индексов настоящим E171
ClipPolygon:    CALL @D3D.ClipPreviewPolygon.Entry
                CALL NC, @D3D.FillPreviewPolygon.Entry                          ; вызов, если обход вернул Carry=0, заполнить принятый отсечённый контур
                JP @D3D.RenderPreviewClippedFaces.Entry

                ; установка отказа только по неотрицательной ориентации
RejectFace:     LD A, #01
                LD (@PreviewFaceGateState.Value.RejectCode), A
                ; расчёт размера заголовка и N индексных байтов для пропуска записи
SkipRecord:     INC B
                LD C, B
                LD B, #00
                ; продвижение полного указателя к следующему заголовку
                ADD HL, BC
                JP @D3D.RenderPreviewClippedFaces.Entry

                ; -----------------------------------------
                ; Условная полилиния и режим ребра
                ; -----------------------------------------
                ; извлечение числа вершин отрицательной записи
Polyline:       AND @PreviewFaceStreamConst.CountMask
                LD B, A
                ; проверка зависимости полилинии от предыдущей ориентации
                BIT @PreviewFaceStreamConst.GateBit, (HL)
                JR Z, @D3D.RenderPreviewClippedFaces.LineMode                   ; переход, если bit6 заголовка сброшен, рисовать независимо от прежнего RejectCode

                ; проверка целого прежнего RejectCode, нуль разрешает условную полилинию
                LD A, (@PreviewFaceGateState.Value.RejectCode)
                AND A
                JR NZ, @D3D.RenderPreviewClippedFaces.SkipRecord                ; переход, если прежний RejectCode ненулевой, пропустить условную полилинию

                ; расчёт N-1 соседних сегментов без автоматического замыкания
LineMode:       DEC B
                LD A, (HL)
                INC HL
                ; извлечение двухбитового поля операции линии
                AND @PreviewFaceStreamConst.LineModeMask
                JR Z, @D3D.RenderPreviewClippedFaces.SelectAnd                  ; переход, если поле операции нулевое, выбрать AND

                ; проверка отдельного кода OR, остальные два ненулевых кода означают XOR
                CP @PreviewFaceStreamConst.OrMode
                JR Z, @D3D.RenderPreviewClippedFaces.SelectOr                   ; переход, если поле операции равно 01, выбрать OR

                ; выбор согласованной пары XOR и условия растрового перехода
                LD DE, @PreviewFaceStreamConst.XorPair
                LD A, @PreviewFaceStreamConst.SetMaskLow
                JP @D3D.RenderPreviewClippedFaces.StoreLineMode

                ; выбор AND и инверсных масок очистки
SelectAnd:      LD DE, @PreviewFaceStreamConst.AndPair
                LD A, @PreviewFaceStreamConst.ClearMaskLow
                JP @D3D.RenderPreviewClippedFaces.StoreLineMode

                ; выбор OR и прямых масок установки
SelectOr:       LD DE, @PreviewFaceStreamConst.OrPair
                LD A, @PreviewFaceStreamConst.SetMaskLow
                ; сохранение двух opcode в физическом состоянии ребра и обновление операнда таблицы масок
StoreLineMode:  LD (@PreviewEdgeMode.Value.PixelOpcode), DE
                LD (@PreviewEdgeRasterState.MaskOffset), A
                ; выбор страницы записей FPreviewProjectedVertex и первого индекса полилинии
                LD IXH, @PreviewFaceMathConst.VertexPage
                LD A, (HL)
                LD IXL, A
                INC HL
                ; чтение и сохранение слова колонки первого текущего конца
                LD E, (IX + @FPreviewProjectedVertex.SecondAxis)
                LD D, (IX + @FPreviewProjectedVertex.SecondAxis + 1)
                LD (@PreviewLineCoordinates.Value.CurrentColumn), DE
                ; чтение и сохранение слова строки первого текущего конца
                LD E, (IX + @FPreviewProjectedVertex.FirstAxis)
                LD D, (IX + @FPreviewProjectedVertex.FirstAxis + 1)
                LD (@PreviewLineTail.Value.CurrentRow), DE
                ; сохранение полного кода сторон первого текущего конца
                LD A, (IX + @FPreviewProjectedVertex.Outcode)
                LD (@PreviewLineTail.Value.CurrentCode), A
                ; -----------------------------------------
                ; Следующий сегмент с исходными словами концов
                ; -----------------------------------------
                ; чтение очередного индекса с сохранением указателя следующего байта
NextLinePoint:  LD A, (HL)
                LD IXL, A
                INC HL
                ; сохранение счётчика оставшихся сегментов и указателя потока
                PUSH BC
                PUSH HL
                ; перенос колонки прежнего текущего конца в предыдущий
                LD HL, (@PreviewLineCoordinates.Value.CurrentColumn)
                LD (@PreviewLineCoordinates.Value.PreviousColumn), HL
                ; перенос строки прежнего текущего конца в предыдущий
                LD HL, (@PreviewLineTail.Value.CurrentRow)
                LD (@PreviewLineCoordinates.Value.PreviousRow), HL
                ; перенос прежнего кода сторон и его сохранение в B для проверки сегмента
                LD A, (@PreviewLineTail.Value.CurrentCode)
                LD (@PreviewLineTail.Value.PreviousCode), A
                LD B, A
                ; чтение и сохранение колонки нового текущего конца
                LD E, (IX + @FPreviewProjectedVertex.SecondAxis)
                LD D, (IX + @FPreviewProjectedVertex.SecondAxis + 1)
                LD (@PreviewLineCoordinates.Value.CurrentColumn), DE
                ; чтение и сохранение строки нового текущего конца
                LD E, (IX + @FPreviewProjectedVertex.FirstAxis)
                LD D, (IX + @FPreviewProjectedVertex.FirstAxis + 1)
                LD (@PreviewLineTail.Value.CurrentRow), DE
                ; проверка полного нулевого кода предыдущего конца, последующие LD сохраняют её Z
                AND A
                ; чтение и сохранение полного кода нового текущего конца
                LD A, (IX + @FPreviewProjectedVertex.Outcode)
                LD (@PreviewLineTail.Value.CurrentCode), A
                JR Z, @D3D.RenderPreviewClippedFaces.ResumeLine                 ; переход, если код предыдущего конца нулевой, пропустить сегмент

                ; проверка полного нулевого кода текущего конца
                AND A
                JR Z, @D3D.RenderPreviewClippedFaces.ResumeLine                 ; переход, если код текущего конца нулевой, пропустить сегмент

                ; накопление OR кодов двух концов в B
                OR B
                LD B, A
                ; проверка общей внешней стороны по дополнению старшей тетрады OR
                CPL
                AND @PreviewClipDispatchConst.ComplementMask
                JR NZ, @D3D.RenderPreviewClippedFaces.ResumeLine                ; переход, если есть общая внешняя сторона, пропустить сегмент

                ; проверка прямой младшей тетрады общего кода для выбора отсекателя
                LD A, B
                AND @PreviewFaceStreamConst.CountMask
                JR NZ, @D3D.RenderPreviewClippedFaces.ClipLine                  ; переход, если хотя бы один конец внешний, вызвать отсечение сегмента

                ; копирование младших координат предыдущего конца в начало растрового ребра
                LD A, (@PreviewLineCoordinates.Value.PreviousColumn)
                LD (@PreviewEdgeEndpoints.Value.StartPoint), A
                LD A, (@PreviewLineCoordinates.Value.PreviousRow)
                LD (@PreviewEdgeEndpoints.Value.StartPoint + 1), A
                ; копирование младших координат текущего конца в завершение растрового ребра
                LD A, (@PreviewLineCoordinates.Value.CurrentColumn)
                LD (@PreviewEdgeEndpoints.Value.EndPoint), A
                LD A, (@PreviewLineTail.Value.CurrentRow)
                LD (@PreviewEdgeEndpoints.Value.EndPoint + 1), A
                ; рисование настоящего растрового сегмента с исключённым конечным пикселем
DrawEdge:       CALL @D3D.RasterizePreviewEdge.Entry
                ; восстановление указателя потока и счётчика после рисования либо отказа
ResumeLine:     POP HL
                POP BC
                ; переход к следующему соседнему сегменту по восстановленному счётчику
                DJNZ @D3D.RenderPreviewClippedFaces.NextLinePoint

                JP @D3D.RenderPreviewClippedFaces.Entry

                ; -----------------------------------------
                ; Отсечение смешанного сегмента
                ; -----------------------------------------
                ; копирование полного предыдущего конца в первый рабочий конец отсекателя
ClipLine:       LD HL, (@PreviewLineCoordinates.Value.PreviousColumn)
                LD (@PreviewClipFirst.Value.SecondAxis), HL
                LD HL, (@PreviewLineCoordinates.Value.PreviousRow)
                LD (@PreviewClipFirst.Value.FirstAxis), HL
                LD A, (@PreviewLineTail.Value.PreviousCode)
                LD (@PreviewClipFirst.Value.Outcode), A
                ; копирование полного текущего конца во второй рабочий конец отсекателя
                LD HL, (@PreviewLineCoordinates.Value.CurrentColumn)
                LD (@PreviewClipSecond.Value.SecondAxis), HL
                LD HL, (@PreviewLineTail.Value.CurrentRow)
                LD (@PreviewClipSecond.Value.FirstAxis), HL
                LD A, (@PreviewLineTail.Value.CurrentCode)
                LD (@PreviewClipSecond.Value.Outcode), A
                ; сохранение индексного регистра текущей проекции вокруг арифметики отсекателя
                PUSH IX
                ; вызов настоящего EAB6 с обменом внутреннего первого конца при необходимости
                CALL @D3D.DispatchPreviewClipSegment.Entry
                ; восстановление текущего индекса без изменения Z результата отсечения
                POP IX
                JR NZ, @D3D.RenderPreviewClippedFaces.ResumeLine                ; переход, если отсекатель не вернул обычные четыре выходных байта, пропустить сегмент

                ; чтение четырёх байтов принятого сегмента из начала страницы C8
                LD HL, @PreviewPolygonPrepConst.FirstPointRow - 1
                LD A, (HL)
                INC L
                ; сохранение колонки первого отсечённого конца
                LD (@PreviewEdgeEndpoints.Value.StartPoint), A
                LD A, (HL)
                INC L
                ; сохранение строки первого отсечённого конца
                LD (@PreviewEdgeEndpoints.Value.StartPoint + 1), A
                LD A, (HL)
                INC L
                ; сохранение колонки второго отсечённого конца
                LD (@PreviewEdgeEndpoints.Value.EndPoint), A
                LD A, (HL)
                ; сохранение строки второго отсечённого конца
                LD (@PreviewEdgeEndpoints.Value.EndPoint + 1), A
                JP @D3D.RenderPreviewClippedFaces.DrawEdge

                ; -----------------------------------------
                endmodule
                endmodule
