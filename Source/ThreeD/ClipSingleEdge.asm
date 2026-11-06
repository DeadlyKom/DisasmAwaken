                module ThreeD
                module ClipSingleEdge
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Отсечение одиночного ребра с обменом внутренней первой точки и рамкой трёх возвратов
                ; исходная запись 19, банк 0, смещения #0941..#099A
                ; In:
                ;   FirstPoint и SecondPoint содержат signed16 координаты и согласованные парные ClipCode, размеры и исходные поля доступны на запись
                ;   SeenFlags содержит прежние отметки углов, их старшая тетрада должна сохраняться, входной размер и CornerBlock несущественны
                ;   для каждого достигнутого деления d ненулевой, U=N при N>=0 либо -N-1, требуется U<abs(d)*65536
                ;   3DPART находится в банке 0, CPU-стек содержит внешний возврат и допускает три служебных слова с вложенными рамками, IRQ не вмешиваются
                ; Out:
                ;   если FirstPoint.ClipCode=F0, обе пятибайтовые точки полностью меняются местами, в том числе при двух внутренних точках
                ;   CornerBlock=1, OutputSize начинается с нуля, SeenFlags обновляется установкой младших отметок без очистки прежних
                ;   в страницу 90 записано до двух точек в порядке выбранного табличного пути, углы фактически не добавляются
                ;   при обычном полном выходе A=OutputSize, F от CP размера,4, DE=Finish, HL и BC определяются последней цепочкой помощников
                ;   при специальном выходе через ExitClipContour HL=CA5B, BC=00C8, AF=C989
                ;   HL', DE', BC', IY, I, IM, IFF и paging сохраняются, AF' и IX соответствуют последним достигнутым помощникам
                ;   SP после RET равен входному SP+2, R меняется, исходный порядок точек не восстанавливается
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX по помощникам, R, обе точки при обмене, CornerBlock, размер, младшие отметки углов, достигнутые произведения, выходные пары и временные слова CPU-стека
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   сначала выполняется обмен, затем пересчитывается индекс таблицы, переносить исходную пару зон до обмена на фактический путь нельзя
                ;   Finish является общим продолжением для трёх подставных возвратов, его POP DE снимают два оставшихся слова перед внешним RET
                ;   24832 сценария исполняют настоящий диспетчер и все помощники, проверены все регистры кроме R, вся физическая RAM и кратность записей
                ;   числовой эталон композиционный по исходным путям, точное R/T, все совместные входы, независимое геометрическое доказательство, IRQ, сборка и нативный вывод не заявляются
                ; -----------------------------------------
                ; -----------------------------------------
                ; Подготовка одиночного ребра
                ; Установка полного запрета фактического вывода углов, прежние отметки SeenFlags не очищаются.
Entry:          LD A, @ActionSingleEdgeConst.NoCorners
                LD (@ActionClipPointWritersState.CornerBlock), A
                ; Проверка внутренней первой точки по полному парному коду F0.
                LD A, (@ThreeDClipPoints.FirstPoint.ClipCode)
                CP @ActionVertexCodeConst.InverseMask
                JR NZ, @ThreeD.ClipSingleEdge.PickCase                          ; переход, если первая точка не имеет внутреннего кода F0, сохранить исходный порядок

                ; Обмен кодов и обоих слов точек, выполняется также при двух внутренних концах.
                LD B, A
                LD A, (@ThreeDClipPoints.SecondPoint.ClipCode)
                LD (@ThreeDClipPoints.FirstPoint.ClipCode), A
                LD A, B
                LD (@ThreeDClipPoints.SecondPoint.ClipCode), A
                LD HL, (@ThreeDClipPoints.FirstPoint.Second)
                LD DE, (@ThreeDClipPoints.SecondPoint.Second)
                LD (@ThreeDClipPoints.SecondPoint.Second), HL
                LD (@ThreeDClipPoints.FirstPoint.Second), DE
                LD HL, (@ThreeDClipPoints.FirstPoint.First)
                LD DE, (@ThreeDClipPoints.SecondPoint.First)
                LD (@ThreeDClipPoints.SecondPoint.First), HL
                LD (@ThreeDClipPoints.FirstPoint.First), DE
                ; -----------------------------------------
                ; Выбор обработчика после обмена
                ; Обнуление размера и расчёт индекса по текущему порядку двух точек.
PickCase:       XOR A
                LD (@ActionClipIntersectionsState.OutputSize), A
                LD A, (@ThreeDClipPoints.FirstPoint.ClipCode)
                CPL
                AND @ActionVertexCodeConst.InverseMask
                LD L, A
                LD A, (@ThreeDClipPoints.SecondPoint.ClipCode)
                AND @ActionPolygonConst.OutsideMask
                OR L
                LD L, A
                ; Чтение младшего и старшего байтов цели из исходных страниц CF и D0.
                LD H, @ActionPolygonConst.TableLowPage
                LD E, (HL)
                INC H
                LD D, (HL)
                EX DE, HL
                ; Сохранение трёх одинаковых возвратов Finish поверх внешнего адреса, CALL обработчика не используется.
                LD DE, @ThreeD.ClipSingleEdge.Finish
                PUSH DE
                PUSH DE
                PUSH DE
                JP (HL)

                ; -----------------------------------------
                ; Общий возврат одиночного ребра
                ; Чтение размера, снятие двух оставшихся подставных слов и проверка двух выходных точек.
Finish:         LD A, (@ActionClipIntersectionsState.OutputSize)
                POP DE
                POP DE
                CP @ActionSingleEdgeConst.SegmentBytes
                RET

                ; -----------------------------------------
                endmodule
                endmodule
