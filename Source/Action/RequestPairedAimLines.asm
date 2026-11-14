                module Action
                module RequestPairedAimLines
                ; Документация [алгоритм и проверка](../../Docs/ActionPairedAimLines.md)
                ; -----------------------------------------
                ; Фазовый допуск двух XOR-линий к прицелу с расходом третьей шкалы и включением захвата цели
                ; исходная запись 17, адреса 63B6..6416
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, Phase и PhaseStep задают байтовый фазовый допуск
                ;   ThirdValue содержит значение третьей шкалы, поля точки ActionAimPoint доступны, допустим профиль Y от 0 до 88
                ;   линейный буфер 8000..8BFF и путь равных концов на строке 95 доступны, таблицы прямых масок E010 сохранены
                ;   перенесённый код банка 5 и ACTION банка 0 доступны для самомодификации, CPU-стек не пересекается с пикселями, IRQ исключены
                ; Out:
                ;   Phase получает Phase+PhaseStep по модулю 256 на всех путях, только Carry суммы допускает дальнейшую обработку
                ;   без Carry A/F соответствуют сумме и остальные данные сохраняются, при ThirdValue<2 A/F соответствуют CP 2 и линии не рисуются
                ;   после полного допуска ThirdValue уменьшается на два, ThirdRequest получает 1, Gate захвата проецируемой записи получает 0
                ;   CursorA получает EE34, рабочие команды растеризатора настроены на XOR и прямую таблицу масок
                ;   целевая точка получает X+8 и Y+6 с двумя отдельными поправками по R, младший бит задаёт модуль 0/1, бит 4 знак поправки
                ;   реальные линии рисуются от упакованных 5F40 и 5FC0 к одной сохранённой точке, конечные точки каждого нормализованного отрезка исключены
                ;   используется DrawPacked по DDFC, при совпавшем конце нулевой B запускает 256 итераций влево вместо пустого вывода
                ;   после рисования HL, DE, BC, AF и AF' соответствуют второй прямой растеризации, HL'/DE'/BC', IX, IY, I/IM/IFF и paging сохраняются
                ;   SP после внешнего RET равен входному SP+2, первая линия использует дополнительную рамку в четыре байта, R сверяется точно на всех путях, обе прямые линии учитываются по полному числу M1
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R по достигнутому пути, Phase, ThirdValue, ThirdRequest, Gate, CursorA, рабочие и кодовые операнды растеризатора, пиксели и CPU-стек, SP внешним RET
                ; Note:
                ;   фазовый шаг является числовым параметром частоты допуска, PhaseStep=0 не даёт Carry, игровой вызывающий код этого входа ещё отдельно не установлен
                ;   буфер FirstPoint/SecondPoint не обновляется, два конца передаются непосредственно HL и DE, подмена обычным входом DDF0 изменила бы равные случаи
                ;   77824 сценария включили все пары Phase/PhaseStep, все значения ThirdValue, все X и разные Y/R, 512 совпавших концов сохранены как исходная особенность
                ;   сверены все регистры включая R, восемь банков, кратность записей и полное число M1 всех 77824 путей
                ;   между первым RET растеризатора и вторым DrawPacked учитываются LD HL,nn, POP DE и хвостовой JP, это три M1
                ;   профиль Y>88, полный игровой вызов, точные T растеризатора, полное произведение входов, аппаратные IRQ, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Расчёт нового фазового байта с изменяемым шагом, сумма сохраняется до проверки допуска.
Entry:          LD A, @ActionPairedAimConst.DefaultPhase
                ADD A, @ActionPairedAimConst.DefaultStep
                LD (@ActionPairedAimState.Phase), A
                RET NC                                                          ; выход, если байтовая сумма не дала Carry, фазовый байт уже обновлён

                ; Проверка наличия двух делений третьей шкалы перед расходом и выводом.
                LD A, (@ActionPanelGaugesState.ThirdValue)
                CP @ActionPairedAimConst.Cost
                RET C                                                           ; выход, если ThirdValue меньше двух, третью шкалу и экран сохранить

                ; Расчёт и запись ThirdValue после расхода двух делений.
                SUB @ActionPairedAimConst.Cost
                LD (@ActionPanelGaugesState.ThirdValue), A
                ; Обновление запроса третьей шкалы и разрешение CaptureProjectedRecord нулевым Gate.
                LD A, #01
                LD (@ActionPanelGaugesState.ThirdRequest), A
                XOR A
                LD (@ActionProjectedCaptureState.Gate), A
                ; Обновление курсора AY-канала A, фактический вывод звука выполняет кадровый потребитель позднее.
                LD HL, @ActionAyStreams.PairedAimRow00
                LD (@ActionAyEffectState.CursorA), HL
                ; Обновление рабочих команд до XOR C, JR C и смещения прямых пиксельных масок.
                LD HL, @ActionPairedAimConst.XorMode
                LD A, @ActionLineRasterConst.SetOffset
                LD (@ActionLineRasterState.PixelOpcode), HL
                LD (@ActionLineRasterState.MaskOffset), A
                ; Расчёт отдельной поправки X, младший бит R задаёт модуль, бит 4 выбирает отрицание.
                LD A, R
                LD C, A
                AND #01
                BIT 4, C
                JR Z, @Action.RequestPairedAimLines.SetX                        ; переход, если бит 4 первого прочитанного R сброшен, поправку X не отрицать

                NEG
                ; Расчёт X конечной точки по текущему прицелу, смещению 8 и исходной байтовой поправке.
SetX:           LD E, A
                LD A, (@ActionAimPoint.Value.X)
                ADD A, @ActionPairedAimConst.XOffset
                ADD A, E
                LD E, A
                ; Расчёт поправки Y по отдельному более позднему чтению R с теми же правилами модуля и знака.
                LD A, R
                LD C, A
                AND #01
                BIT 4, C
                JR Z, @Action.RequestPairedAimLines.SetY                        ; переход, если бит 4 второго прочитанного R сброшен, поправку Y не отрицать

                NEG
                ; Расчёт Y конечной точки по текущему прицелу, смещению 6 и байтовой поправке.
SetY:           LD D, A
                LD A, (@ActionAimPoint.Value.Y)
                ADD A, @ActionPairedAimConst.YOffset
                ADD A, D
                LD D, A
                ; Сохранение одного целевого DE для двух прямых входов растеризатора с разными неподвижными концами.
                PUSH DE
                ; Выбор первой неподвижной точки, Second=64 и First=95, и настоящий прямой вход без проверки равенства.
                LD HL, @ActionPairedAimConst.FirstPoint
                CALL @Action.DrawLinearLine.DrawPacked
                ; Выбор второй неподвижной точки, Second=192 и First=95, восстановление того же целевого DE.
                LD HL, @ActionPairedAimConst.SecondPoint
                POP DE
                JP @Action.DrawLinearLine.DrawPacked

                endmodule
                endmodule
