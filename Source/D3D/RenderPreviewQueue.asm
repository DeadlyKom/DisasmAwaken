                module D3D
                module RenderPreviewQueue
                ; Документация [восстановление настоящего SP, десять полей узла, выбор рисователя и неизменность Next](../../Docs/PreviewQueueRender.md)
                ; -----------------------------------------
                ; Обход связанной очереди, загрузка параметров узла и выбор внутреннего либо отсечённого рисователя
                ; исходная запись 6, банк 4, файловые смещения #2EF1..#2F5D
                ; In:
                ;   HL имеет сохраняемый младший L только для пустой очереди, DE, BC и AF не задают параметры обхода
                ;   HL', DE', BC', AF', IX, IY исходный контекст вложенных матриц, проектора, классификатора и рисователя
                ;   PreviewDrawState.Head задаёт ацикличную цепочку на странице C7, индекс 1 конец, индекс 0 допустим
                ;   поля каждого FPreviewQueueNode доступны продвижением только L, ModelOffset задаёт допустимую пару указателей модели
                ;   параметры исходных помощников, таблицы строк, операнды границ и настоящий CPU-стек подготовлены
                ; Out:
                ;   HL адрес Next последнего обработанного узла, при пустой цепочке H=C7 и L входной
                ;   DE и BC, альтернативные и индексные регистры принадлежат последнему исполненному помощнику
                ;   AF содержит A=1,F=42 от CP 1 при завершении цепочки
                ;   Flags, ModelOffset, три параметра ориентации и четыре изменяемых слова загружены из последнего узла
                ;   узлы C7, их Next и Head не изменяются, матрицы, проекции, состояние рисователей и bitmap рабочие
                ;   SP после RET равен входному+2, I, IFF и IM сохраняются, банк не переключается
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по помощникам, параметры объекта, матрицы, проекция, коды сторон, bitmap, рабочие операнды и CPU-стек
                ; Note:
                ;   пустая очередь меняет только H и AF, остальные основные, альтернативные и индексные регистры сохраняются
                ;   каждый узел безусловно проходит BuildPreviewModelMatrix, ComposePreviewMatrix, ProjectPreviewModelGroups и ClassifyPreviewVertices
                ;   нулевой результат классификатора либо общая внешняя сторона пропускают рисование, младшая тетрада выбирает DBE9 либо DD4F
                ;   после любого пути адрес Next восстанавливается со стека, следующий узел не вычисляется прибавлением 14
                ;   144 цепочки и 816 узлов проверены с реальными помощниками и всеми 11 смещениями моделей
                ;   все конечные регистры непустой цепочки, независимый bitmap кадра, IRQ и нативный запуск не доказаны
                ; -----------------------------------------
                ; чтение головы активной очереди и выбор страницы физических узлов
Entry:          LD A, (@PreviewDrawState.Value.Head)
                LD H, @PreviewQueueConst.Page
                JP @D3D.RenderPreviewQueue.CheckNext

                ; -----------------------------------------
                ; Параметры очередного объекта
                ; -----------------------------------------
                ; сохранение адреса Next узла для возврата после рисования
NextObject:     PUSH HL
                ; переход к паре Flags и ModelOffset, продвижение остаётся внутри страницы C7
                INC L
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                ; запись пары флагов и байтового смещения модели в состояние рисования
                LD (@PreviewDrawState.Value.Flags), DE
                ; чтение первых двух параметров ориентации из полей AngleFirst и AngleSecond
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                ; сохранение первых двух параметров в физическом экземпляре ориентации
                LD (@PreviewObjectAngles.Value.First), DE
                ; чтение и сохранение третьего параметра AngleThird
                LD A, (HL)
                INC L
                LD (@PreviewObjectAngles.Value.Third), A
                ; чтение FirstResult и подготовка изменяемого слова первого результата проектора
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (@PreviewTransformState.ResultFirst), DE
                ; чтение SecondResult и подготовка изменяемого слова второго результата
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (@PreviewTransformState.ResultSecond), DE
                ; чтение ThirdResult и подготовка изменяемого слова третьего результата
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (@PreviewTransformState.ResultThird), DE
                ; чтение SecondInput для изменяемого операнда второй исходной координаты
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (@PreviewTransformState.InputSecond), DE
                ; выбор физических Flags и ModelOffset для построения матрицы объекта
                LD HL, @PreviewDrawState.Value.Flags
                ; построение исходной матрицы модели по трём параметрам ориентации
                CALL @D3D.BuildPreviewModelMatrix.Entry
                ; композиция матрицы объекта с матрицей сцены
                CALL @D3D.ComposePreviewMatrix.Entry
                ; проекция физических групп выбранной модели в страницу C6
                CALL @D3D.ProjectPreviewModelGroups.Entry
                ; классификация записанных вершин по текущему окну и накопление общего кода
                CALL @D3D.ClassifyPreviewVertices.Entry
                JR Z, @D3D.RenderPreviewQueue.ResumeNode                        ; переход, если классификатор вернул Z=1, пропустить рисование объекта

                ; сохранение общего кода и проверка общей внешней стороны по дополнению старшей тетрады
                LD B, A
                CPL
                AND @PreviewClipDispatchConst.ComplementMask
                JR NZ, @D3D.RenderPreviewQueue.ResumeNode                       ; переход, если дополнение старшей тетрады ненулевое, пропустить объект с общей внешней стороной

                ; проверка младшей тетрады общего кода для выбора рисователя
                LD A, B
                AND @PreviewClipDispatchConst.SideMask
                JR NZ, @D3D.RenderPreviewQueue.ClippedFaces                     ; переход, если есть внешние вершины, выбрать полный поток с отсечением

                ; рисование полностью внутренней проекции проходом DD4F
                CALL @D3D.RenderPreviewInsideFaces.Entry
                JP @D3D.RenderPreviewQueue.ResumeNode

                ; рисование смешанной проекции проходом DBE9 с отсечением
ClippedFaces:   CALL @D3D.RenderPreviewClippedFaces.Entry
                ; -----------------------------------------
                ; Следующий узел и завершение цепочки
                ; -----------------------------------------
                ; восстановление адреса Next и чтение исходной ссылки узла
ResumeNode:     POP HL
                LD A, (HL)
                ; проверка точного маркера конца, нулевой индекс остаётся допустимым узлом
CheckNext:      CP @PreviewQueueConst.EndMarker
                RET Z                                                           ; выход, если прочитанный индекс равен 1, активная цепочка завершена

                ; выбор младшего адреса следующего узла без изменения страницы C7
                LD L, A
                JP @D3D.RenderPreviewQueue.NextObject

                ; -----------------------------------------
                endmodule
                endmodule
