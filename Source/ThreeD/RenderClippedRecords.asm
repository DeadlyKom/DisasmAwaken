                module ThreeD
                module RenderClippedRecords
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Вывод записей объекта с проверкой кодов точек и отсечением граней и открытых сегментов
                ; исходная запись 19, банк 0, смещения #1BBD..#1D22
                ; In:
                ;   HL указывает на конечный поток переменных записей OBJECT3D с полным нулём в конце, поток не пересекается с изменяемыми буферами и стеком
                ;   DE, BC и AF начальных координат не задают, остальные регистры содержат контекст вызывающего и числовых детей
                ;   страница 8E содержит пятибайтовые FRenderProjectedPoint, парные ClipCode согласованы с полными координатами либо равны нулю для локального отказа
                ;   грани имеют 3..15 вершин выпуклого прямого либо обратного обхода, материалы 0..4, ломаные 2..15 вершин
                ;   для каждого достигнутого пересечения выполняется договор исходных знаковых умножителя и делителя, ненулевой знаменатель и допустимое частное
                ;   после отсечения заполняемый контур удовлетворяет профилю PreparePolygonFill, маски, шаблоны и таблица CF/D0 сохранены
                ;   FaceGate задаёт предыдущее состояние до первой грани, исходные 40 слотов точек и индексы целиком помещаются в странице 8E
                ;   3DPART банка 0 доступен для самомодификации, на CPU-стеке внешний возврат и место рамок детей, IRQ не вмешиваются в временные SP и общие операнды
                ; Out:
                ;   HL указывает на полный нулевой конец списка
                ;   DE и BC содержат точный результат композиции ReferenceActionPacketRenderer.render(clipped=True)
                ;   AF содержит A=0, F=54, SP после RET равен входному SP+2
                ;   альтернативные и индексные регистры содержат точный результат композиции ReferenceActionPacketRenderer.render(clipped=True)
                ;   FaceGate обновляется только по знаку ориентации грани, нулевой код и общий внешний предел после отрицательной ориентации не возвращают ему единицу
                ;   грани с нулевым кодом либо общей внешней стороной пропущены, внутренние грани копируются напрямую, пересекающие окно проходят ClipPolygon
                ;   после ClipPolygon заполнение выполняется только при сброшенном Carry, то есть наличии хотя бы трёх выходных точек в обычном договоре
                ;   для каждого открытого сегмента нулевые коды либо общая внешняя сторона подавляют рисование, внутренние концы рисуются напрямую
                ;   внешний сегмент передаётся ClipSingleEdge, IX сохраняется вокруг него, рисование разрешено только при подтверждённых четырёх выходных байтах
                ;   BC и HL восстанавливаются вокруг каждого сегмента, конец предыдущего сохраняется в полных NextSecond/NextFirst/NextCode даже при пропуске сегмента
                ;   пиксели, рабочие точки, размеры, операнды и остаточные CPU/временные стековые слова совпадают с композиционным эталоном
                ;   I, IM, IFF и paging сохраняются, R меняется, порты не используются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, FaceGate, рабочие точки и коды, пиксели, операнды детей и существующие CPU/временные стековые слова
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   нулевой код первой точки проверяется по флагам AND A до чтения кода второй, инструкции LD A и LD в память эти флаги не меняют
                ;   проверка общего внешнего предела использует инверсную старшую тетраду, младшая задаёт наличие хотя бы одной внешней точки
                ;   поля 6..4 грани и 5..4 линии являются числовыми селекторами, бит связи линии с ориентацией отделён от операции пикселей
                ;   3906 композиционных сценариев исполняют настоящих детей, сверены регистры кроме R, вся физическая RAM и кратность записей
                ;   пройдены 856 отсечений контуров и 516 отсечений сегментов, проверены три внешние группы контуров и девять областей концов
                ;   проверенные внешние координаты Second -64..319 и First -40..135 не объявляются доказательством всех произвольных 16-битных входов
                ;   все совместные потоки, достижимость синтетических нулевых кодов после общего сканера, R/T, IRQ, сборка и нативная игра не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Следующая запись объекта
                ; Чтение полного заголовка, нуль завершает поток до разделения типов.
Entry:          LD A, (HL)
                AND A
                RET Z                                                           ; выход, если достигнут полный нулевой заголовок, поток объекта закончился

                JP M, @ThreeD.RenderClippedRecords.LineRecord                   ; переход, если установлен бит 7 заголовка, обработать ломаную

                ; -----------------------------------------
                ; Ориентация и общие коды грани
                ; Выбор числа вершин и проверка ориентации настоящим CheckFaceOrientation.
                AND @ActionClippedPacketRendererConst.LowNibbleMask
                LD B, A
                CALL @ThreeD.CheckFaceOrientation.Entry
                JP P, @ThreeD.RenderClippedRecords.RejectFace                   ; переход, если результат ориентации неотрицателен, отметить отказ и пропустить грань

                ; Обновление FaceGate нулём после отрицательной ориентации и сбор кодов индексированных вершин.
                XOR A
                LD (@ActionPacketRendererState.FaceGate), A
                CALL @ThreeD.CombineListedVertexCodes.Entry
                JR C, @ThreeD.RenderClippedRecords.SkipRecord                   ; переход, если найден нулевой код вершины, пропустить всю грань

                ; Проверка общей внешней стороны по отсутствующему разряду инверсной старшей тетрады.
                CPL
                AND @ActionVertexCodeConst.InverseMask
                JR NZ, @ThreeD.RenderClippedRecords.SkipRecord                  ; переход, если все вершины находятся снаружи одной стороны, пропустить грань

                ; Расчёт номера материала из разрядов 6..4 заголовка грани.
                LD A, (HL)
                INC HL
                RRCA
                RRCA
                RRCA
                RRCA
                AND @ActionPacketRendererConst.MaterialMask
                ; Обновление операнда Mode подготовителя заливки.
                LD (@ActionPolygonPreparationState.Mode), A
                ; Проверка наличия хотя бы одной внешней точки грани по младшей тетраде общего кода.
                LD A, C
                AND @ActionClippedPacketRendererConst.LowNibbleMask
                JR NZ, @ThreeD.RenderClippedRecords.ClipFace                    ; переход, если хотя бы одна вершина снаружи, получить замкнутый отсечённый контур

                ; -----------------------------------------
                ; Прямое копирование внутренней грани
                ; Расчёт байтового размера и копирование младших Second и First в страницу 90.
                LD DE, @ActionPolygonPreparationState.Vertices
                LD A, B
                ADD A, A
                LD (@ActionClipIntersectionsState.OutputSize), A
                LD B, @ActionPacketRendererConst.PointPage
                ; Сохранение счётчика вершин в альтернативном AF для цикла копирования.
                RRCA
                ; Чтение очередного индекса и запись двух младших координат без отсечения.
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
                ; Проверка числа оставшихся вершин с восстановлением рабочего AF на следующей итерации.
                DEC A
                JP NZ, @ThreeD.RenderClippedRecords.NextFacePoint               ; переход, если остались вершины внутренней грани, скопировать следующую пару

                ; Заливка напрямую скопированного контура.
                CALL @ThreeD.PreparePolygonFill.Entry
                JP @ThreeD.RenderClippedRecords.Entry

                ; -----------------------------------------
                ; Отсечение замкнутой грани
                ; Получение нового списка страницы 90 через настоящий ClipPolygon.
ClipFace:       CALL @ThreeD.ClipPolygon.Entry
                CALL NC, @ThreeD.PreparePolygonFill.Entry                       ; вызов, если Carry сброшен после отсечения, заполнить контур из хотя бы трёх точек
                JP @ThreeD.RenderClippedRecords.Entry

                ; Обновление FaceGate единицей только для неотрицательной ориентации.
RejectFace:     LD A, #01
                LD (@ActionPacketRendererState.FaceGate), A
                ; Расчёт полного размера пропускаемой записи, число индексов плюс заголовок.
SkipRecord:     INC B
                LD C, B
                LD B, #00
                ADD HL, BC
                JP @ThreeD.RenderClippedRecords.Entry

                ; -----------------------------------------
                ; Ломаная и связь с ориентацией
                ; Выбор числа вершин и проверка независимого бита связи с FaceGate.
LineRecord:     AND @ActionClippedPacketRendererConst.LowNibbleMask
                LD B, A
                BIT @ActionPacketRendererConst.AttachBit, (HL)
                JR Z, @ThreeD.RenderClippedRecords.PrepareLineMode              ; переход, если бит связи с предыдущей гранью сброшен, рисовать независимо от FaceGate

                ; Проверка сохранённого результата ориентации предыдущей грани.
                LD A, (@ActionPacketRendererState.FaceGate)
                AND A
                JR NZ, @ThreeD.RenderClippedRecords.SkipRecord                  ; переход, если FaceGate ненулевой, пропустить связанную ломаную

                ; -----------------------------------------
                ; Режим пикселей открытых сегментов
                ; Расчёт числа сегментов и выбор числового поля операции 5..4.
PrepareLineMode:DEC B
                LD A, (HL)
                INC HL
                AND @ActionPacketRendererConst.LineModeMask
                JR Z, @ThreeD.RenderClippedRecords.SetClearMode                 ; переход, если селектор равен 00, выбрать AND и инверсные маски

                ; Проверка отдельного селектора OR, значения 10 и 11 оба означают XOR.
                CP @ActionPacketRendererConst.OrSelector
                JR Z, @ThreeD.RenderClippedRecords.SetOrMode                    ; переход, если селектор равен 01, выбрать OR и прямые маски

                ; Подготовка XOR и проверки Carry для прямой маски.
                LD DE, @ActionPacketRendererConst.XorModeWord
                LD A, @ActionLineRasterConst.SetOffset
                JP @ThreeD.RenderClippedRecords.StoreLineMode

                ; Подготовка AND и проверки отсутствия Carry для инверсной маски.
SetClearMode:   LD DE, @ActionPacketRendererConst.AndModeWord
                LD A, @ActionLineRasterConst.ClearOffset
                JP @ThreeD.RenderClippedRecords.StoreLineMode

                ; Подготовка OR и проверки Carry для прямой маски.
SetOrMode:      LD DE, @ActionPacketRendererConst.OrModeWord
                LD A, @ActionLineRasterConst.SetOffset
                ; Обновление рабочих opcode и операнда выбора масок DrawLinearLine.
StoreLineMode:  LD (@ActionLineRasterState.PixelOpcode), DE
                LD (@ActionLineRasterState.MaskOffset), A
                ; -----------------------------------------
                ; Полная первая точка ломаной
                ; Чтение двух слов координат и парного ClipCode, старшие координаты нужны отсекателю.
                LD IXH, @ActionPacketRendererConst.PointPage
                LD A, (HL)
                LD IXL, A
                INC HL
                LD E, (IX + FRenderProjectedPoint.Second)
                LD D, (IX + FRenderProjectedPoint.Second + 1)
                LD (@ActionClippedPacketRendererState.NextSecond), DE
                LD E, (IX + FRenderProjectedPoint.First)
                LD D, (IX + FRenderProjectedPoint.First + 1)
                LD (@ActionClippedPacketRendererState.NextFirst), DE
                LD A, (IX + FRenderProjectedPoint.ClipCode)
                LD (@ActionClippedPacketRendererState.NextCode), A
                ; Выбор следующей точки и сохранение счётчика и указателя потока вокруг обработки сегмента.
NextLinePoint:  LD A, (HL)
                LD IXL, A
                INC HL
                PUSH BC
                PUSH HL
                ; Обновление текущей первой точки предыдущей следующей точкой и сохранение её кода.
                LD HL, (@ActionClippedPacketRendererState.NextSecond)
                LD (@ActionClippedPacketRendererState.CurrentSecond), HL
                LD HL, (@ActionClippedPacketRendererState.NextFirst)
                LD (@ActionClippedPacketRendererState.CurrentFirst), HL
                LD A, (@ActionClippedPacketRendererState.NextCode)
                LD (@ActionClippedPacketRendererState.CurrentCode), A
                LD B, A
                ; Обновление следующей точки полными координатами новой индексированной записи.
                LD E, (IX + FRenderProjectedPoint.Second)
                LD D, (IX + FRenderProjectedPoint.Second + 1)
                LD (@ActionClippedPacketRendererState.NextSecond), DE
                LD E, (IX + FRenderProjectedPoint.First)
                LD D, (IX + FRenderProjectedPoint.First + 1)
                LD (@ActionClippedPacketRendererState.NextFirst), DE
                ; Проверка нулевого кода первой точки, следующие LD сохраняют её флаг Zero до JR.
                AND A
                LD A, (IX + FRenderProjectedPoint.ClipCode)
                LD (@ActionClippedPacketRendererState.NextCode), A
                JR Z, @ThreeD.RenderClippedRecords.NextSegment                  ; переход, если код первой точки нулевой, пропустить сегмент независимо от уже прочитанной второй

                ; Проверка нулевого кода второй точки после обновления NextCode.
                AND A
                JR Z, @ThreeD.RenderClippedRecords.NextSegment                  ; переход, если код второй точки нулевой, пропустить сегмент

                ; Расчёт общего кода и проверка общей внешней стороны двух концов.
                OR B
                LD B, A
                CPL
                AND @ActionVertexCodeConst.InverseMask
                JR NZ, @ThreeD.RenderClippedRecords.NextSegment                 ; переход, если оба конца снаружи одной стороны, пропустить сегмент

                ; Проверка наличия хотя бы одного внешнего конца по младшей тетраде.
                LD A, B
                AND @ActionClippedPacketRendererConst.LowNibbleMask
                JR NZ, @ThreeD.RenderClippedRecords.ClipSegment                 ; переход, если хотя бы один конец снаружи, получить отсечённую пару точек

                ; Копирование младших координат двух внутренних концов в рабочие слова растеризатора.
                LD A, (@ActionClippedPacketRendererState.CurrentSecond)
                LD (@ActionLineRasterState.FirstPoint), A
                LD A, (@ActionClippedPacketRendererState.CurrentFirst)
                LD (@ActionLineRasterState.FirstPoint+1), A
                LD A, (@ActionClippedPacketRendererState.NextSecond)
                LD (@ActionLineRasterState.SecondPoint), A
                LD A, (@ActionClippedPacketRendererState.NextFirst)
                LD (@ActionLineRasterState.SecondPoint+1), A
                ; Рисование разрешённого прямого либо отсечённого сегмента настоящим DrawLinearLine.
DrawSegment:    CALL @ThreeD.DrawLinearLine.Entry
                ; Восстановление указателя потока и счётчика сегментов независимо от пути отказа или рисования.
NextSegment:    POP HL
                POP BC
                DJNZ @ThreeD.RenderClippedRecords.NextLinePoint

                JP @ThreeD.RenderClippedRecords.Entry

                ; -----------------------------------------
                ; Отсечение открытого сегмента
                ; Копирование двух полных точек в физические ActionClipPoints с сохранением IX вокруг ClipSingleEdge.
ClipSegment:    LD HL, (@ActionClippedPacketRendererState.CurrentSecond)
                LD (@ThreeDClipPoints.FirstPoint.Second), HL
                LD HL, (@ActionClippedPacketRendererState.CurrentFirst)
                LD (@ThreeDClipPoints.FirstPoint.First), HL
                LD A, (@ActionClippedPacketRendererState.CurrentCode)
                LD (@ThreeDClipPoints.FirstPoint.ClipCode), A
                LD HL, (@ActionClippedPacketRendererState.NextSecond)
                LD (@ThreeDClipPoints.SecondPoint.Second), HL
                LD HL, (@ActionClippedPacketRendererState.NextFirst)
                LD (@ThreeDClipPoints.SecondPoint.First), HL
                LD A, (@ActionClippedPacketRendererState.NextCode)
                LD (@ThreeDClipPoints.SecondPoint.ClipCode), A
                PUSH IX
                CALL @ThreeD.ClipSingleEdge.Entry
                POP IX
                JR NZ, @ThreeD.RenderClippedRecords.NextSegment                 ; переход, если ClipSingleEdge не подтвердил ровно четыре выходных байта, пропустить рисование сегмента

                ; Копирование подтверждённых четырёх выходных координат в два рабочих слова линии.
CopyClippedPair:LD HL, @ActionPolygonPreparationState.Vertices
                LD A, (HL)
                INC L
                LD (@ActionLineRasterState.FirstPoint), A
                LD A, (HL)
                INC L
                LD (@ActionLineRasterState.FirstPoint+1), A
                LD A, (HL)
                INC L
                LD (@ActionLineRasterState.SecondPoint), A
                LD A, (HL)
                LD (@ActionLineRasterState.SecondPoint+1), A
                JP @ThreeD.RenderClippedRecords.DrawSegment

                ; -----------------------------------------
                endmodule
                endmodule
