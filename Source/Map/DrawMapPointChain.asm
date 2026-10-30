                module Map
                module DrawMapPointChain
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [формат заголовка, преобразование координат, открытая цепочка и обмен наборов при раннем выходе](../../Docs/MapPointChain.md)
; -----------------------------------------
; Построение относительных точек и рисование открытой индексированной цепочки из N-1 отрезков
; исходная запись 7, файловые смещения #11AC..#12ED
; In:
;   HL - начало пятибайтовых FStoredMapPoint, FirstWord содержит старшие X,Y, SecondWord младшие X,Y
;   DE - FStoredMapOrder либо совместимый заголовок с N индексами, N=Layout AND 0F, известный экземпляр имеет ёмкость 10
;   каждый индекс есть смещение 5*k выбранной точки, 0<=k<N, Variant в расчёте координат не используется
;   MapViewState.OriginLow/OriginHigh задают вычитаемое начало, KARTA выбран, действуют условия RasterizeMapLine
;   входные массивы не перекрывают F800, F900, рабочие поля таблицы и код, нужный текущему вызову
; Out:
;   N=0 или N=1 даёт ранний выход без изменения HL, DE, BC, альтернативных и индексных регистров
;   у этого раннего выхода A=0, F=54 для N=0 и F=42 для N=1, рабочие поля и режим линии не меняются
;   при N>=2 сформированы N FProjectedPoint по F800 с 16-битными X,Y относительно начала и исходными ClipCodes
;   если все точки имеют общую внешнюю сторону, выполнен ранний возврат с обменёнными HL/DE/BC и HL'/DE'/BC'
;   для этого выхода HL=F801+5*N, DE=входной DE', BC=(G SHL 8)|последний младший код, A=K SHL 4, F от AND F0
;   HL'=входной DE, DE'=F800+5*N, BC'=(входной B SHL 8)|старший Y начала, A'=5*N, F'=42 OR((5*N)AND 28)
;   иначе обработаны N-1 соседних пар индексов, автоматического ребра от последнего к первому нет
;   внутренние пары переданы прямо в RasterizeMapLine, внешние проходят общий код отсечения, общий внешний бит пропускает пару
;   у обычного окончания HL=входной DE+1+N, DE рабочий, BC=старший Y начала при B=0, AF рабочий
;   HL'=F801+5*N, DE'=входной DE', BC'=(G SHL 8)|последний младший код, AF' рабочий
;   IX=F800|последний индекс, IY сохранён, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, точные различия ранних выходов перечислены выше
; Note:
;   G есть OR всех полных ClipCodes, K есть AND их младших кодов, проверка K выполняется через дополненную старшую тетраду G
;   Layout содержит код режима в битах 5..4, 00 Clear, 01 Set, 10 и 11 Xor, биты 7..6 этим входом игнорируются
;   код не проверяет ёмкость 10 и не исправляет индексы, N=11..15 требует расширенных входных массивов, которых у известного экземпляра нет
;   верхние и нижние индивидуальные пересечения не включены в полную экранную модель этого конвейера, их помощники проверены отдельно
;   имя описывает открытый обход индексов, полный геометрический разбор всех табличных случаев остаётся отдельной задачей
; -----------------------------------------
                ; проверка количества точек по младшей тетраде заголовка до чтения индексов
Entry:          LD A, (DE)
                AND @MapClipConst.CountMask
                RET Z                                                           ; выход, если N=0, входные массивы и рабочее состояние не менять

                ; проверка минимального количества двух точек для одного отрезка
                DEC A
                RET Z                                                           ; выход, если N=1, единственная точка не образует отрезка

                INC A
                ; сохранение указателя заголовка и выбор прежнего рабочего массива относительных точек
                PUSH DE
                LD DE, @MapClipState.Points
                ; расчёт относительного X, младший байт источника смещён на 2, старший находится в начале записи
ConvertPoint:   EX AF, AF'
                INC HL
                INC HL
                LD A, (@MapViewState.OriginLow)
                LD C, A
                LD A, (HL)
                SUB C
                LD (DE), A
                INC DE
                DEC HL
                DEC HL
                ; вычитание старшего X начала с заёмом от младшей части, итог оборачивается до 16 бит
                LD A, (@MapViewState.OriginHigh)
                LD C, A
                LD A, (HL)
                SBC A, C
                LD (DE), A
                INC DE
                INC HL
                INC HL
                INC HL
                ; расчёт относительного Y по байтам источника 3 и 1 с раздельным вычитанием начала
                LD A, (@MapViewState.OriginLow + 1)
                LD C, A
                LD A, (HL)
                SUB C
                LD (DE), A
                INC DE
                DEC HL
                DEC HL
                LD A, (@MapViewState.OriginHigh + 1)
                LD C, A
                LD A, (HL)
                SBC A, C
                LD (DE), A
                INC DE
                INC DE
                INC HL
                INC HL
                INC HL
                INC HL
                EX AF, AF'
                DEC A
                JP NZ, @Map.DrawMapPointChain.ConvertPoint                      ; переход, если остаются непреобразованные точки, следующая исходная запись имеет размер 5

                ; возврат заголовка и передача его через альтернативный HL классификатору
                POP HL
                EXX
                ; построение кодов границ для всех относительных координат без изменения входного списка
                CALL @Map.BuildMapPointOutcodes.Entry
                RET Z                                                           ; выход, если классификатор вернул нулевой общий код, основные и альтернативные наборы остаются обменёнными

                ; проверка общей внешней стороны всех точек через дополнение агрегированных кодов
                LD B, A
                CPL
                AND @MapClipConst.Complement
                RET NZ                                                          ; выход, если у всех точек есть общая внешняя сторона, наборы регистров остаются обменёнными

                ; восстановление исходного набора после успешной общей проверки и чтение количества рёбер N-1
                EXX
                LD A, (HL)
                AND @MapClipConst.CountMask
                LD B, A
                DEC B
                LD A, (HL)
                INC HL
                AND @MapChainConst.StyleMask
                JR Z, @Map.DrawMapPointChain.SelectClear                        ; переход, если код режима Layout в битах 5..4 равен 00, выбрать Clear

                CP @MapChainConst.SetStyle
                JR Z, @Map.DrawMapPointChain.SelectSet                          ; переход, если код режима Layout в битах 5..4 равен 01, выбрать Set

                ; выбор Xor для кодов режима 10 и 11, используется одноразрядная фазовая маска
                LD DE, @MapLineConst.XorMode
                LD A, @MapLineConst.SetMaskLow
                JP @Map.DrawMapPointChain.StoreMode

                ; выбор AND C и JR NC для инверсной фазовой маски очистки
SelectClear:    LD DE, @MapLineConst.ClearMode
                LD A, @MapLineConst.ClearMaskLow
                JP @Map.DrawMapPointChain.StoreMode

                ; выбор OR C и JR C для одноразрядной фазовой маски установки
SelectSet:      LD DE, @MapLineConst.SetMode
                LD A, @MapLineConst.SetMaskLow
                ; сохранение кодов режима и смещения таблицы, затем выбор первой индексированной точки
StoreMode:      LD (@MapLineWork.Mode.PixelOpcode), DE
                LD (@MapLinePatch.MaskOffset), A
                LD IXH, @MapChainConst.PointPage
                LD A, (HL)
                LD IXL, A
                INC HL
                LD E, (IX + FProjectedPoint.X)
                LD D, (IX + FProjectedPoint.X + 1)
                LD (@MapChainWork.CurrentPoint.X), DE
                LD E, (IX + FProjectedPoint.Y)
                LD D, (IX + FProjectedPoint.Y + 1)
                LD (@MapChainWork.CurrentPoint.Y), DE
                LD A, (IX + FProjectedPoint.ClipCodes)
                LD (@MapChainWork.CurrentPoint.ClipCodes), A
                ; поиск следующего индекса цепочки, текущая точка становится предыдущей независимо от результата рисования
NextEdge:       LD A, (HL)
                LD IXL, A
                INC HL
                PUSH BC
                PUSH HL
                LD HL, (@MapChainWork.CurrentPoint.X)
                LD (@MapChainWork.PreviousPoint.X), HL
                LD HL, (@MapChainWork.CurrentPoint.Y)
                LD (@MapChainWork.PreviousPoint.Y), HL
                LD A, (@MapChainWork.CurrentPoint.ClipCodes)
                LD (@MapChainWork.PreviousPoint.ClipCodes), A
                LD B, A
                LD E, (IX + FProjectedPoint.X)
                LD D, (IX + FProjectedPoint.X + 1)
                LD (@MapChainWork.CurrentPoint.X), DE
                LD E, (IX + FProjectedPoint.Y)
                LD D, (IX + FProjectedPoint.Y + 1)
                LD (@MapChainWork.CurrentPoint.Y), DE
                AND A
                LD A, (IX + FProjectedPoint.ClipCodes)
                LD (@MapChainWork.CurrentPoint.ClipCodes), A
                JR Z, @Map.DrawMapPointChain.FinishEdge                         ; переход, если прежний ClipCodes равен нулю, пропустить ребро как отключённое

                AND A
                JR Z, @Map.DrawMapPointChain.FinishEdge                         ; переход, если новый ClipCodes равен нулю, пропустить ребро как отключённое

                ; проверка общей внешней стороны только двух концов текущего ребра
                OR B
                LD B, A
                CPL
                AND @MapClipConst.Complement
                JR NZ, @Map.DrawMapPointChain.FinishEdge                        ; переход, если оба конца лежат по одну внешнюю сторону, ребро не рисовать

                LD A, B
                AND @MapClipConst.CountMask
                JR NZ, @Map.DrawMapPointChain.ClipEdge                          ; переход, если хотя бы один конец имеет внешние биты, передать ребро в отсечение

                ; копирование младших X,Y двух внутренних концов прямо в аргументы рисователя
                LD A, (@MapChainWork.PreviousPoint.X)
                LD (@MapLineWork.Start.X), A
                LD A, (@MapChainWork.PreviousPoint.Y)
                LD (@MapLineWork.Start.Y), A
                LD A, (@MapChainWork.CurrentPoint.X)
                LD (@MapLineWork.Finish.X), A
                LD A, (@MapChainWork.CurrentPoint.Y)
                LD (@MapLineWork.Finish.Y), A
                ; рисование принятой пары с исходным исключением последнего пикселя
DrawEdge:       CALL @Map.RasterizeMapLine.Entry
                ; восстановление следующего индекса и внешнего счётчика, новая итерация продолжает открытую цепочку
FinishEdge:     POP HL
                POP BC
                DJNZ @Map.DrawMapPointChain.NextEdge

                RET

                ; подготовка полных знаковых концов и их ClipCodes для разнесённой таблицы отсечения
ClipEdge:       LD HL, (@MapChainWork.PreviousPoint.X)
                LD (@MapClipWork.FirstPoint.X), HL
                LD HL, (@MapChainWork.PreviousPoint.Y)
                LD (@MapClipWork.FirstPoint.Y), HL
                LD A, (@MapChainWork.PreviousPoint.ClipCodes)
                LD (@MapClipWork.FirstPoint.ClipCodes), A
                LD HL, (@MapChainWork.CurrentPoint.X)
                LD (@MapClipWork.SecondPoint.X), HL
                LD HL, (@MapChainWork.CurrentPoint.Y)
                LD (@MapClipWork.SecondPoint.Y), HL
                LD A, (@MapChainWork.CurrentPoint.ClipCodes)
                LD (@MapClipWork.SecondPoint.ClipCodes), A
                PUSH IX
                ; вызов отсечения на его собственном тройном кадре, IX текущего индекса защищён внешним PUSH
                CALL @Map.DispatchMapClipEdge.Entry
                POP IX
                JR NZ, @Map.DrawMapPointChain.FinishEdge                        ; переход, если отсечение не вернуло ровно четыре выходных байта, пропустить рисование ребра

                ; чтение двух принятых выходных точек из страницы F9 для общего рисователя
                LD HL, @MapClipState.Output
                LD A, (HL)
                INC L
                LD (@MapLineWork.Start.X), A
                LD A, (HL)
                INC L
                LD (@MapLineWork.Start.Y), A
                LD A, (HL)
                INC L
                LD (@MapLineWork.Finish.X), A
                LD A, (HL)
                LD (@MapLineWork.Finish.Y), A
                JP @Map.DrawMapPointChain.DrawEdge

                endmodule
                endmodule
