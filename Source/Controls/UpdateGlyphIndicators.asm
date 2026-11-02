                module Controls
                module UpdateGlyphIndicators
                ; Документация [алгоритм и проверка](../../Docs/ControlsGlyphIndicators.md)
                ; -----------------------------------------
                ; Очистка двух экранных зон и обновление до трёх трёхстрочных знаков с точными байтовыми ограничениями
                ; исходная запись 23, банк 1, смещения #0543..#066F
                ; In:
                ;   HL входных аргументов не задаёт, DE и B сохраняются только на пути без единого знака, C и AF числовых аргументов не задают
                ;   физические Control, First, Second и Third из ActionGlyphIndicatorState задают режим, запрет, координаты и байт выбора формы
                ;   банк 1 выбран, RestoreSP доступен для самомодификации, используются четыре исходных знака и их восемь фаз
                ;   на CPU-стеке внешний возврат, ещё два байта нужны для CALL, рамка и код не перекрываются с очищаемыми зонами
                ;   IRQ не вмешиваются, код не запрещает их самостоятельно, во время очистки SP действительно направляется в пиксельную RAM
                ; Out:
                ;   при отсутствии знаков HL=0000, DE и B сохраняются, C=Second.X OR Second.Y, A=80, F=42
                ;   при наличии знаков HL и DE соответствуют последнему OrThreeRowGlyph, B содержит его ограниченный Y
                ;   на выходе по маркеру второго C=Second.X OR Second.Y, A=80, F=42, третий знак пропущен
                ;   на выходе по ненулевому ThirdGate C сохраняет удвоенную фазу второго знака, A=ThirdGate, F соответствует AND этого байта
                ;   на полном пути C содержит удвоенную фазу третьего знака, A и F соответствуют его последнему OR
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   RestoreSP содержит входной SP, 64 очищаемых байта обнулены до OR, пиксели знаков затем установлены
                ;   R учитывает 71 M1 очистки и допуска первого, 9 M1 проверки второго, 3 M1 проверки ThirdGate и выбранные координатные пути с рисователями
                ; Corrupt:
                ;   HL, DE, BC, AF, RestoreSP, 64 очищаемых байта и байты OR знаков, два байта CPU-стека, R
                ; Note:
                ;   FirstMode=1 пропускает первый знак, все остальные байты режима допускают его, ThirdGate=0 допускает третий после проверки второго
                ;   точный маркер отсутствия второго равен OR всех трёх его байтов с результатом 80, это не отдельная проверка SignSource=80
                ;   координаты первого и второго ограничены X=152..165, третьего X=176..189, все Y=104..117
                ;   X сначала складывается по модулю байта с центром, знаковое переполнение выбирает нижнюю границу, затем идут беззнаковые сравнения
                ;   Y складывается с 70 по модулю байта без отдельной ветви переполнения, заменить это обычным целочисленным clamp нельзя
                ;   первый и второй рисователи вызываются CALL, третий получает хвостовой JP либо последовательное исполнение в соседнем файле
                ;   смысл исходных векторов в игре и Unknown83 не установлен, локальный экранный алгоритм проверен на всех байтовых координатах
                ; -----------------------------------------
                ; сохранение настоящего входного SP в операнде RestoreSP перед использованием SP как указателя очистки
Entry:          LD (@ControlsGlyphIndicatorsState.RestoreSP), SP
                ; подготовка нулевого слова, два PUSH с DEC SP очищают четыре столбца и сохраняют промежуточный
                LD HL, #0000
                LD SP, @ControlsGlyphIndicatorsConst.TopRow0SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow1SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow2SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow3SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow4SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow5SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow6SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.TopRow7SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow0SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow1SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow2SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow3SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow4SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow5SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow6SP
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, @ControlsGlyphIndicatorsConst.BottomRow7SP
                PUSH HL
                DEC SP
                PUSH HL
                ; восстановление обычного SP, исходный нулевой операнд уже заменён сохранённым входным значением
                LD SP, #0000
                ; -----------------------------------------
                ; Допуск первого знака
                ; проверка числового FirstMode перед обработкой First
                LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                DEC A
                JR Z, @Controls.UpdateGlyphIndicators.CheckSecond               ; переход, если FirstMode равен SkipFirstMode, сразу проверить второй вход

                ; вычисление байтового X первого знака, знаковое переполнение исходного ADD обрабатывается отдельно
                LD A, (@ActionGlyphIndicatorState.First.X)
                ADD A, @ControlsGlyphIndicatorsConst.LeftCenterX
                JP PO, @Controls.UpdateGlyphIndicators.ClampFirstXLow           ; переход, если сложение First.X с LeftCenterX не дало знакового переполнения, продолжить ограничение

                ; выбор LeftMinX при знаковом переполнении, исходное поведение сохраняется
                LD A, @ControlsGlyphIndicatorsConst.LeftMinX
                ; проверка нижней границы уже байтового X первого знака
ClampFirstXLow: CP @ControlsGlyphIndicatorsConst.LeftMinX
                JR NC, @Controls.UpdateGlyphIndicators.ClampFirstXHigh          ; переход, если байтовый X не меньше LeftMinX, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.LeftMinX
                ; проверка исключённой верхней границы X первого знака
ClampFirstXHigh:CP @ControlsGlyphIndicatorsConst.LeftEndX
                JR C, @Controls.UpdateGlyphIndicators.FirstXReady               ; переход, если байтовый X меньше LeftEndX, горизонтальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.LeftMaxX
                ; вычисление байтового Y первого знака без отдельной ветви знакового переполнения
FirstXReady:    LD C, A
                LD A, (@ActionGlyphIndicatorState.First.Y)
                ADD A, @ControlsGlyphIndicatorsConst.CenterY
                ; проверка нижней границы Y первого знака
                CP @ControlsGlyphIndicatorsConst.MinY
                JR NC, @Controls.UpdateGlyphIndicators.ClampFirstYHigh          ; переход, если байтовый Y не меньше MinY, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.MinY
                ; проверка исключённой верхней границы Y первого знака
ClampFirstYHigh:CP @ControlsGlyphIndicatorsConst.EndY
                JR C, @Controls.UpdateGlyphIndicators.FirstYReady               ; переход, если байтовый Y меньше EndY, вертикальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.MaxY
                ; проверка знака First.SignSource перед выбором плюса или креста
FirstYReady:    LD B, A
                LD A, (@ActionGlyphIndicatorState.First.SignSource)
                AND A
                LD DE, @ControlsThreeRowGlyphs.Plus00
                JP P, @Controls.UpdateGlyphIndicators.DrawFirst                 ; переход, если First.SignSource неотрицателен, использовать Plus00

                LD DE, @ControlsThreeRowGlyphs.Cross00
                ; рисование первого знака настоящим CALL, после него обычный SP восстанавливается RET рисователя
DrawFirst:      CALL @Controls.OrThreeRowGlyph.Entry
                ; -----------------------------------------
                ; Маркер второго входа
                ; вычисление OR всех трёх байтов Second, в C остаётся OR только X и Y
CheckSecond:    LD A, (@ActionGlyphIndicatorState.Second.X)
                LD C, A
                LD A, (@ActionGlyphIndicatorState.Second.Y)
                OR C
                LD C, A
                LD A, (@ActionGlyphIndicatorState.Second.SignSource)
                OR C
                ; проверка точного значения VectorSentinel, остальные результаты OR допускают второй знак
                CP @ControlsGlyphIndicatorsConst.VectorSentinel
                RET Z                                                           ; выход, если OR трёх байтов Second равен VectorSentinel, второй и третий знаки пропущены

                ; вычисление байтового X второго знака с исходной ветвью знакового переполнения
                LD A, (@ActionGlyphIndicatorState.Second.X)
                ADD A, @ControlsGlyphIndicatorsConst.LeftCenterX
                JP PO, @Controls.UpdateGlyphIndicators.ClampSecondXLo           ; переход, если сложение Second.X с LeftCenterX не дало знакового переполнения

                LD A, @ControlsGlyphIndicatorsConst.LeftMinX
                ; проверка нижней границы X второго знака
ClampSecondXLo: CP @ControlsGlyphIndicatorsConst.LeftMinX
                JR NC, @Controls.UpdateGlyphIndicators.ClampSecondXHi           ; переход, если байтовый X не меньше LeftMinX, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.LeftMinX
                ; проверка исключённой верхней границы X второго знака
ClampSecondXHi: CP @ControlsGlyphIndicatorsConst.LeftEndX
                JR C, @Controls.UpdateGlyphIndicators.SecondXReady              ; переход, если байтовый X меньше LeftEndX, горизонтальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.LeftMaxX
                ; вычисление байтового Y второго знака
SecondXReady:   LD C, A
                LD A, (@ActionGlyphIndicatorState.Second.Y)
                ADD A, @ControlsGlyphIndicatorsConst.CenterY
                ; проверка нижней границы Y второго знака
                CP @ControlsGlyphIndicatorsConst.MinY
                JR NC, @Controls.UpdateGlyphIndicators.ClampSecondYHi           ; переход, если байтовый Y не меньше MinY, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.MinY
                ; проверка исключённой верхней границы Y второго знака
ClampSecondYHi: CP @ControlsGlyphIndicatorsConst.EndY
                JR C, @Controls.UpdateGlyphIndicators.SecondYReady              ; переход, если байтовый Y меньше EndY, вертикальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.MaxY
                ; проверка знака Second.SignSource перед выбором заполненного или полого квадрата
SecondYReady:   LD B, A
                LD A, (@ActionGlyphIndicatorState.Second.SignSource)
                AND A
                LD DE, @ControlsThreeRowGlyphs.Solid00
                JP P, @Controls.UpdateGlyphIndicators.DrawSecond                ; переход, если Second.SignSource неотрицателен, использовать Solid00

                LD DE, @ControlsThreeRowGlyphs.Hollow00
                ; рисование второго знака настоящим CALL после возможного первого
DrawSecond:     CALL @Controls.OrThreeRowGlyph.Entry
                ; -----------------------------------------
                ; Допуск третьего знака
                ; проверка полного байта ThirdGate, ненулевое значение завершает обновление
                LD A, (@ActionGlyphIndicatorState.Control.ThirdGate)
                AND A
                RET NZ                                                          ; выход, если ThirdGate ненулевой, сохранить адреса второго знака и вернуть значение запрета в A

                ; вычисление X третьего знака с центром RightCenterX, физическая запись Third хранит Y перед X
                LD A, (@ActionGlyphIndicatorState.Third.X)
                ADD A, @ControlsGlyphIndicatorsConst.RightCenterX
                JP PO, @Controls.UpdateGlyphIndicators.ClampThirdXLow           ; переход, если сложение Third.X с RightCenterX не дало знакового переполнения

                LD A, @ControlsGlyphIndicatorsConst.RightMinX
                ; проверка нижней границы X третьего знака
ClampThirdXLow: CP @ControlsGlyphIndicatorsConst.RightMinX
                JR NC, @Controls.UpdateGlyphIndicators.ClampThirdXHigh          ; переход, если байтовый X не меньше RightMinX, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.RightMinX
                ; проверка исключённой верхней границы X третьего знака
ClampThirdXHigh:CP @ControlsGlyphIndicatorsConst.RightEndX
                JR C, @Controls.UpdateGlyphIndicators.ThirdXReady               ; переход, если байтовый X меньше RightEndX, горизонтальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.RightMaxX
                ; вычисление байтового Y третьего знака
ThirdXReady:    LD C, A
                LD A, (@ActionGlyphIndicatorState.Third.Y)
                ADD A, @ControlsGlyphIndicatorsConst.CenterY
                ; проверка нижней границы Y третьего знака
                CP @ControlsGlyphIndicatorsConst.MinY
                JR NC, @Controls.UpdateGlyphIndicators.ClampThirdYHigh          ; переход, если байтовый Y не меньше MinY, проверить верхнюю границу

                LD A, @ControlsGlyphIndicatorsConst.MinY
                ; проверка исключённой верхней границы Y третьего знака
ClampThirdYHigh:CP @ControlsGlyphIndicatorsConst.EndY
                JR C, @Controls.UpdateGlyphIndicators.ThirdYReady               ; переход, если байтовый Y меньше EndY, вертикальная координата готова

                LD A, @ControlsGlyphIndicatorsConst.MaxY
                ; проверка знака Third.SignSource, оба пути используют внешний возврат обновления
ThirdYReady:    LD B, A
                LD A, (@ActionGlyphIndicatorState.Third.SignSource)
                AND A
                LD DE, @ControlsThreeRowGlyphs.Solid00
                JP P, @Controls.OrThreeRowGlyph.Entry                           ; переход, если Third.SignSource неотрицателен, хвостом рисовать Solid00

                ; выбор Hollow00 перед последовательным продолжением в OrThreeRowGlyph.asm
                LD DE, @ControlsThreeRowGlyphs.Hollow00
                ; JP @Controls.OrThreeRowGlyph.Entry, продолжение в OrThreeRowGlyph.asm

                ; -----------------------------------------
                endmodule
                endmodule
