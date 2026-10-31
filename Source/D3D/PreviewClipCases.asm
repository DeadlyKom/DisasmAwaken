                module D3D
                module PreviewClipCases
                ; Документация [81 пара зон, 241 явный путь, готовность кэшей, отметки углов и два вида внешнего кадра](../../Docs/PreviewClipCases.md)
                ; -----------------------------------------
                ; Решения отсечения по паре зон, порядок пересечений и накопление отметок углов
                ; исходная запись 6, банк 4, файловые смещения #21EB..#25E7
                ; In:
                ;   HL, DE, BC и AF рабочий входной контекст выбранного обработчика, координаты читаются из физических записей
                ;   HL', DE', BC' сохраняются, AF' и IX используются вложенной арифметикой, IY сохраняется
                ;   PreviewClipFirst и PreviewClipSecond содержат слова колонок и строк с соответствующими кодами сторон
                ;   SeenFlags содержит прежние отметки, BlockCode=0 разрешает запись углов, любой ненуль подавляет её
                ;   ByteCount и страница C8 доступны, каждый делитель имеет ненулевой знаменатель и допустимое слово частного
                ;   EAB6 устанавливает три возврата EB08, E171 устанавливает E1E2 над сохранёнными BC и HL
                ;   внутренние продолжения требуют уже готовые кэши, входить в них без предшествующего пути нельзя
                ; Out:
                ;   HL, DE, BC и AF обычного RET равны контексту последнего действия пути, BIT и SET учитываются после него
                ;   HL', DE', BC' сохранены, AF' и IX определяются исполненными умножениями и делениями, IY сохранён
                ;   порядок добавлений, конкретные условия и отметки каждого входа перечислены в PreviewClipCaseDecisions
                ;   SeenFlags меняет только младшие четыре бита установкой отметок, старшая тетрада сохраняется
                ;   при BlockCode!=0 путь добавляет не более двух точек, при BlockCode=0 в проверенной области не более четырёх
                ;   обычный RET снимает одно слово, окончательные регистры и SP определяются внешним кадром
                ;   специальный выход UnwindPreviewClipFrame снимает три слова, для трёх EB08 даёт HL=EBF2, BC=00EA, AF=EBA9
                ;   I, IFF и IM сохраняются, физические записи концов и BlockCode эта группа не изменяет
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX по исполненному пути, SeenFlags, выбранные кэши, ByteCount, выходные точки и CPU-стек
                ; Note:
                ;   Entry состоит из RET и не является общим эпилогом, оба эпилога принадлежат внешним диспетчерам
                ;   разность двух 32-битных произведений выбирает порядок пересечений по биту 31, равенство входит в неотрицательную ветвь
                ;   BIT читает прежнюю отметку, SET её устанавливает без изменения флагов, поэтому последующий CALL NZ проверяет прежний BIT
                ;   отметить угол и добавить угол разные действия, BlockCode подавляет только запись углового помощника
                ;   все 71 физическая цель и 241 путь проверены, готовность кэшей установлена для обеих ветвей каждого условия
                ;   178612 исполнений охватывают шесть нулевых минимумов, все начальные SeenFlags и оба режима BlockCode
                ;   полный символьный конечный контекст каждого пути, ненулевые минимумы, все крайние координаты, IRQ и нативный запуск не доказаны
                ; -----------------------------------------
                ; пустой табличный обработчик, переход к возврату, установленному внешним диспетчером
Entry:          RET

                ; вход таблицы, первая точка внутри, вторая снизу справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseI_BR:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
NeedRightForBR: CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
PickBRExit:     CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.AppendPreviewClipBottomIntersection.FromProduct      ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                ; вход таблицы, первая точка справа, вторая снизу справа
CaseR_BR:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                JP NZ, @D3D.AppendPreviewClipBottomRight.Entry                  ; переход, если нижний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая снизу слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseI_BL:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
NeedLeftForBL:  CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
PickBLExit:     CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.AppendPreviewClipLeftIntersection.FromProduct        ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                ; вход таблицы, первая точка снизу, вторая снизу слева
CaseB_BL:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                JP NZ, @D3D.AppendPreviewClipBottomLeft.Entry                   ; переход, если нижний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая сверху справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseI_TR:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
NeedRightForTR: CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
PickTRExit:     CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.AppendPreviewClipRightIntersection.FromProduct       ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                ; вход таблицы, первая точка сверху, вторая сверху справа
CaseT_TR:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                JP NZ, @D3D.AppendPreviewClipTopRight.Entry                     ; переход, если верхний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая сверху слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseI_TL:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
NeedLeftForTL:  CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
PickTLExit:     CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.AppendPreviewClipTopIntersection.FromProduct         ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                ; вход таблицы, первая точка слева, вторая сверху слева
CaseL_TL:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                JP NZ, @D3D.AppendPreviewClipTopLeft.Entry                      ; переход, если верхний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                RET

                ; вход таблицы, первая точка справа, вторая внутри
CaseR_I:        CALL @D3D.AppendPreviewClipRightIntersection.Entry
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка справа, вторая слева
CaseR_L:        CALL @D3D.AppendPreviewClipRightIntersection.Entry
                JP @D3D.AppendPreviewClipLeftIntersection.Entry

                ; вход таблицы, первая точка справа, вторая снизу
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_B:        CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishRtoB:     CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP P, @D3D.AppendPreviewClipBottomRight.Entry                   ; переход, если бит 31 разности BottomProduct минус RightProduct сброшен

                CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.AppendPreviewClipBottomIntersection.FromProduct

                ; вход таблицы, первая точка справа, вторая снизу слева
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_BL:       CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishRtoBL:    CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.PreviewClipCases.CrossRtoBL                          ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipBottomRight.Entry
                JP @D3D.PreviewClipCases.CaseB_BL

CrossRtoBL:     CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.PreviewClipCases.NeedLeftForBL

                ; вход таблицы, первая точка справа, вторая сверху
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_T:        CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishRtoT:     CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.AppendPreviewClipTopIntersection.FromProduct

                ; вход таблицы, первая точка справа, вторая сверху справа
                ; проверка направления отрезка по разности колонки второго конца минус колонка первого
CaseR_TR:       CALL @D3D.SubtractPreviewClipColumns.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности колонки второго конца минус колонка первого установлен

                RET

                ; вход таблицы, первая точка справа, вторая сверху слева
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_TL:       CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishRtoTL:    CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.PreviewClipCases.NeedLeftForTL

                ; вход таблицы, первая точка слева, вторая внутри
CaseL_I:        CALL @D3D.AppendPreviewClipLeftIntersection.Entry
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка слева, вторая справа
CaseL_R:        CALL @D3D.AppendPreviewClipLeftIntersection.Entry
                JP @D3D.AppendPreviewClipRightIntersection.Entry

                ; вход таблицы, первая точка слева, вторая снизу
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_B:        CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishLtoB:     CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.AppendPreviewClipBottomIntersection.FromProduct

                ; вход таблицы, первая точка слева, вторая снизу справа
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_BR:       CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishLtoBR:    CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.PreviewClipCases.NeedRightForBR

                ; вход таблицы, первая точка слева, вторая снизу слева
                ; проверка направления отрезка по разности колонки второго конца минус колонка первого
CaseL_BL:       CALL @D3D.SubtractPreviewClipColumns.Entry
                JP P, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности колонки второго конца минус колонка первого сброшен

                RET

                ; вход таблицы, первая точка слева, вторая сверху
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_T:        CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishLtoT:     CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP P, @D3D.AppendPreviewClipTopLeft.Entry                       ; переход, если бит 31 разности TopProduct минус LeftProduct сброшен

                CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.AppendPreviewClipTopIntersection.FromProduct

                ; вход таблицы, первая точка слева, вторая сверху справа
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_TR:       CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishLtoTR:    CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.PreviewClipCases.CrossLtoTR                          ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipTopLeft.Entry
                JP @D3D.PreviewClipCases.CaseT_TR

CrossLtoTR:     CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.PreviewClipCases.NeedRightForTR

                ; вход таблицы, первая точка снизу, вторая внутри
CaseB_I:        CALL @D3D.AppendPreviewClipBottomIntersection.Entry
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка снизу, вторая справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_R:        CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishBtoR:     CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                JP @D3D.AppendPreviewClipRightIntersection.FromProduct

                ; вход таблицы, первая точка снизу, вторая слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_L:        CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishBtoL:     CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP P, @D3D.AppendPreviewClipBottomLeft.Entry                    ; переход, если бит 31 разности BottomProduct минус LeftProduct сброшен

                CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                JP @D3D.AppendPreviewClipLeftIntersection.FromProduct

                ; вход таблицы, первая точка снизу, вторая снизу справа
                ; проверка направления отрезка по разности строки второго конца минус строка первого
CaseB_BR:       CALL @D3D.SubtractPreviewClipRows.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности строки второго конца минус строка первого установлен

                RET

                ; вход таблицы, первая точка снизу, вторая сверху
CaseB_T:        CALL @D3D.AppendPreviewClipBottomIntersection.Entry
                JP @D3D.AppendPreviewClipTopIntersection.Entry

                ; вход таблицы, первая точка снизу, вторая сверху справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_TR:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishBtoTR:    CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                ; вычисление кэшированного числителя TopProduct для верхней границы
                CALL @D3D.BuildPreviewClipTopProduct.Entry
                JP @D3D.PreviewClipCases.PickTRExit

                ; вход таблицы, первая точка снизу, вторая сверху слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_TL:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishBtoTL:    CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.PreviewClipCases.CrossBtoTL                          ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipBottomLeft.Entry
                JP @D3D.PreviewClipCases.CaseL_TL

CrossBtoTL:     CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                ; вычисление кэшированного числителя TopProduct для верхней границы
                CALL @D3D.BuildPreviewClipTopProduct.Entry
                JP @D3D.PreviewClipCases.PickTLExit

                ; вход таблицы, первая точка снизу справа, вторая внутри
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_I:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.PreviewClipCases.RightToInside                       ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomRight.Entry                ; вызов, если нижний правый угол уже отмечен, запросить его добавление
BottomToInside: CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка снизу справа, вторая справа
                ; проверка направления отрезка по разности колонки второго конца минус колонка первого
CaseBR_R:       CALL @D3D.SubtractPreviewClipColumns.Entry
                JP P, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности колонки второго конца минус колонка первого сброшен

                RET

                ; вход таблицы, первая точка снизу справа, вторая слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_L:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.PreviewClipCases.RightToLeft                         ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomRight.Entry                ; вызов, если нижний правый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishBtoL

RightToLeft:    CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.AppendPreviewClipLeftIntersection.Entry

                ; вход таблицы, первая точка снизу справа, вторая снизу
CaseBR_B:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                JP NZ, @D3D.AppendPreviewClipBottomRight.Entry                  ; переход, если нижний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                RET

                ; вход таблицы, первая точка снизу справа, вторая снизу слева
CaseBR_BL:      CALL @D3D.PreviewClipCases.CaseBR_B
                JP @D3D.PreviewClipCases.CaseB_BL

                ; вход таблицы, первая точка снизу справа, вторая сверху
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_T:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.PreviewClipCases.FinishRtoT                          ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @D3D.PreviewClipCases.CaseBR_B
                CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                JP @D3D.AppendPreviewClipTopIntersection.Entry

                ; вход таблицы, первая точка снизу справа, вторая сверху слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_TL:      CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipBottomRight.Entry
                JP M, @D3D.PreviewClipCases.FinishRtoTL                         ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomRight.Entry                ; вызов, если нижний правый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishBtoTL

                ; вход таблицы, первая точка снизу слева, вторая внутри
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_I:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.PreviewClipCases.BottomToInside                      ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomLeft.Entry                 ; вызов, если нижний левый угол уже отмечен, запросить его добавление
LeftToInside:   CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка снизу слева, вторая справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_R:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.PreviewClipCases.FinishBtoR                          ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @D3D.PreviewClipCases.CaseBL_L
                CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.AppendPreviewClipRightIntersection.Entry

                ; вход таблицы, первая точка снизу слева, вторая слева
CaseBL_L:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                JP NZ, @D3D.AppendPreviewClipBottomLeft.Entry                   ; переход, если нижний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                RET

                ; вход таблицы, первая точка снизу слева, вторая снизу
                ; проверка направления отрезка по разности строки второго конца минус строка первого
CaseBL_B:       CALL @D3D.SubtractPreviewClipRows.Entry
                JP P, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности строки второго конца минус строка первого сброшен

                RET

                ; вход таблицы, первая точка снизу слева, вторая сверху
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_T:       CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.PreviewClipCases.BottomToTop                         ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomLeft.Entry                 ; вызов, если нижний левый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishLtoT

BottomToTop:    CALL @D3D.AppendPreviewClipBottomIntersection.FromProduct
                JP @D3D.AppendPreviewClipTopIntersection.Entry

                ; вход таблицы, первая точка снизу слева, вторая сверху справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_TR:      CALL @D3D.BuildPreviewClipBottomProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipBottomLeft.Entry
                JP M, @D3D.PreviewClipCases.FinishBtoTR                         ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipBottomLeft.Entry                 ; вызов, если нижний левый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishLtoTR

                ; вход таблицы, первая точка снизу слева, вторая сверху слева
CaseBL_TL:      CALL @D3D.PreviewClipCases.CaseBL_L
                JP @D3D.PreviewClipCases.CaseL_TL

                ; вход таблицы, первая точка сверху, вторая внутри
CaseT_I:        CALL @D3D.AppendPreviewClipTopIntersection.Entry
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка сверху, вторая справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_R:        CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishTtoR:     CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP P, @D3D.AppendPreviewClipTopRight.Entry                      ; переход, если бит 31 разности TopProduct минус RightProduct сброшен

                CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                JP @D3D.AppendPreviewClipRightIntersection.FromProduct

                ; вход таблицы, первая точка сверху, вторая слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_L:        CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishTtoL:     CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                JP @D3D.AppendPreviewClipLeftIntersection.FromProduct

                ; вход таблицы, первая точка сверху, вторая снизу
CaseT_B:        CALL @D3D.AppendPreviewClipTopIntersection.Entry
                JP @D3D.AppendPreviewClipBottomIntersection.Entry

                ; вход таблицы, первая точка сверху, вторая снизу справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_BR:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishTtoBR:    CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.PreviewClipCases.CrossTtoBR                          ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @D3D.AppendPreviewClipTopRight.Entry
                JP @D3D.PreviewClipCases.CaseR_BR

CrossTtoBR:     CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                ; вычисление кэшированного числителя BottomProduct для нижней границы
                CALL @D3D.BuildPreviewClipBottomProduct.Entry
                JP @D3D.PreviewClipCases.PickBRExit

                ; вход таблицы, первая точка сверху, вторая снизу слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_BL:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishTtoBL:    CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                ; вычисление кэшированного числителя BottomProduct для нижней границы
                CALL @D3D.BuildPreviewClipBottomProduct.Entry
                JP @D3D.PreviewClipCases.PickBLExit

                ; вход таблицы, первая точка сверху, вторая сверху слева
                ; проверка направления отрезка по разности строки второго конца минус строка первого
CaseT_TL:       CALL @D3D.SubtractPreviewClipRows.Entry
                JP P, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности строки второго конца минус строка первого сброшен

                RET

                ; вход таблицы, первая точка сверху справа, вторая внутри
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_I:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.PreviewClipCases.TopToInside                         ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopRight.Entry                   ; вызов, если верхний правый угол уже отмечен, запросить его добавление
RightToInside:  CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка сверху справа, вторая справа
CaseTR_R:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                JP NZ, @D3D.AppendPreviewClipTopRight.Entry                     ; переход, если верхний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                RET

                ; вход таблицы, первая точка сверху справа, вторая слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_L:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.PreviewClipCases.FinishTtoL                          ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @D3D.PreviewClipCases.CaseTR_R
                CALL @D3D.AppendPreviewClipRightIntersection.FromProduct
                JP @D3D.AppendPreviewClipLeftIntersection.Entry

                ; вход таблицы, первая точка сверху справа, вторая снизу
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_B:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.PreviewClipCases.TopToBottom                         ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopRight.Entry                   ; вызов, если верхний правый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishRtoB

TopToBottom:    CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                JP @D3D.AppendPreviewClipBottomIntersection.Entry

                ; вход таблицы, первая точка сверху справа, вторая снизу справа
CaseTR_BR:      CALL @D3D.PreviewClipCases.CaseTR_R
                JP @D3D.PreviewClipCases.CaseR_BR

                ; вход таблицы, первая точка сверху справа, вторая снизу слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_BL:      CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @D3D.BuildPreviewClipRightProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @D3D.SubtractPreviewClipTopRight.Entry
                JP M, @D3D.PreviewClipCases.FinishTtoBL                         ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopRight.Entry                   ; вызов, если верхний правый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishRtoBL

                ; вход таблицы, первая точка сверху справа, вторая сверху
                ; проверка направления отрезка по разности строки второго конца минус строка первого
CaseTR_T:       CALL @D3D.SubtractPreviewClipRows.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности строки второго конца минус строка первого установлен

                RET

                ; вход таблицы, первая точка сверху слева, вторая внутри
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_I:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.PreviewClipCases.LeftToInside                        ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopLeft.Entry                    ; вызов, если верхний левый угол уже отмечен, запросить его добавление
TopToInside:    CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                JP @D3D.AppendPreviewClipSecond.Entry

                ; вход таблицы, первая точка сверху слева, вторая справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_R:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.PreviewClipCases.LeftToRight                         ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopLeft.Entry                    ; вызов, если верхний левый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishTtoR

LeftToRight:    CALL @D3D.AppendPreviewClipLeftIntersection.FromProduct
                JP @D3D.AppendPreviewClipRightIntersection.Entry

                ; вход таблицы, первая точка сверху слева, вторая слева
                ; проверка направления отрезка по разности колонки второго конца минус колонка первого
CaseTL_L:       CALL @D3D.SubtractPreviewClipColumns.Entry
                JP M, @D3D.UnwindPreviewClipFrame.Entry                         ; переход, если старший бит разности колонки второго конца минус колонка первого установлен

                RET

                ; вход таблицы, первая точка сверху слева, вторая снизу
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_B:       CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.PreviewClipCases.FinishLtoB                          ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @D3D.PreviewClipCases.CaseTL_T
                CALL @D3D.AppendPreviewClipTopIntersection.FromProduct
                JP @D3D.AppendPreviewClipBottomIntersection.Entry

                ; вход таблицы, первая точка сверху слева, вторая снизу справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_BR:      CALL @D3D.BuildPreviewClipTopProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @D3D.BuildPreviewClipLeftProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @D3D.SubtractPreviewClipTopLeft.Entry
                JP M, @D3D.PreviewClipCases.FinishLtoBR                         ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @D3D.AppendPreviewClipTopLeft.Entry                    ; вызов, если верхний левый угол уже отмечен, запросить его добавление
                JP @D3D.PreviewClipCases.FinishTtoBR

                ; вход таблицы, первая точка сверху слева, вторая сверху
CaseTL_T:       LD HL, @PreviewClipCorners.Value.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                JP NZ, @D3D.AppendPreviewClipTopLeft.Entry                      ; переход, если верхний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                RET

                ; вход таблицы, первая точка сверху слева, вторая сверху справа
CaseTL_TR:      CALL @D3D.PreviewClipCases.CaseTL_T
                JP @D3D.PreviewClipCases.CaseT_TR

                endmodule
                endmodule
