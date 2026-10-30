                module Map
                module MapClipCases
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [геометрический порядок, направленные равенства, состояние углов и два протокола возврата](../../Docs/ClipCases.md)
; -----------------------------------------
; Табличные решения отсечения по двум зонам, пересечения, отметки углов и общий возврат
; исходная запись 7, файловые смещения #14DD..#18E1
; In:
;   файл содержит общий Entry и отдельные Case-входы таблицы, обычным CALL к Entry обработчик не вызывается
;   MapClipWork.FirstPoint и SecondPoint содержат соответствующие выбранной паре зон 16-битные точки
;   CornerBlock проверяется целиком, ноль разрешает запросы углов, ненулевой байт подавляет их, SeenFlags задаёт прежние отметки
;   у прямого Case-входа OutputSize=0, доступна выходная страница, на стеке три слова Entry и настоящий адрес возврата
;   Entry общего возврата получает уже две оставшиеся копии Entry и настоящий адрес, OutputSize содержит накопленное число байтов
;   приватные продолжения требуют произведения, уже вычисленные предшествующей частью, их состав виден по исходным CALL и реестру путей
;   KARTA выбран, границы и коды согласованы с текущей фазой настройки, действуют договоры MultiplySigned16 и DivideSigned32To16
;   каждое исполненное деление имеет ненулевой знаменатель и допустимое частное, стек и рабочие поля доступны
; Out:
;   порядок добавленных пересечений, углов, второй точки и отметок определяется парой зон и явными условиями ClipCaseDecisions
;   при BlockCode=1 прямые табличные входы добавляют не более двух точек, при BlockCode=0 в проверенных путях не более четырёх
;   OutputSize увеличивается на два для каждой добавленной точки, в коде поле называется MapClipWork.OutputSize
;   SeenFlags изменяется только установкой младших четырёх битов, старшая тетрада сохраняется
;   обычный выход - HL и BC рабочие, DE=Entry, AF содержит A=OutputSize и F от CP OutputSize,4
;   специальный выход - HL=D5B0, BC=00D3, AF=D481, DE рабочий, состояние вывода сохраняет уже сделанные записи
;   HL', DE', BC', IY, I и IFF инструкции группы и помощников сохраняют, AF' и IX рабочие
;   общий Entry снимает два слова и настоящий возврат, Case-вход через обычный RET снимает три слова и настоящий возврат
;   при исполнении через DispatchMapClipEdge итоговый SP после возврата равен входному SP этой обёртки+2
; Corrupt:
;   HL, DE, BC, AF, AF', IX, младшие биты SeenFlags, вычисленные слоты произведений, OutputSize и выходные точки
; Note:
;   [Все 81 пары и 241 путь](../../Docs/ClipCaseDecisions.md) содержат точные условия и действия, включая входы с внутренней первой точкой
;   знак 32-битной разности произведений выбирает порядок соседних пересечений, равенство принадлежит неотрицательной ветви
;   BIT проверяет прежнюю отметку угла, следующий SET не меняет флаги, условный запрос может использовать прежний результат BIT
;   отметка угла не равна его выводу, ненулевой CornerBlock подавляет только фактическую запись отдельного помощника
;   Entry содержит CP 4, поэтому Z означает ровно две выходные точки, A специального выхода D4 не является размером
;   D48B меняет внутренний первый конец местами со вторым, прямые цели дискового снимка не приняты за достижимые после записи рабочих полей
;   геометрическая модель BlockCode=1 и проверка точных путей BlockCode=0/1 являются разными свидетельствами
;   проверены исходный профиль и пять окон с нулевыми минимумами, весь диапазон координат, все runtime-фазы, IRQ, сборка и игровой запуск не доказаны
; -----------------------------------------
                ; чтение байтового размера результата перед снятием двух оставшихся подставных возвратов
Entry:          LD A, (@MapClipWork.OutputSize)
                POP DE
                POP DE
                ; проверка результата ровно из двух двухбайтовых точек, Z возвращается вызывающему конвейеру
                CP #04
                RET

                ; вход таблицы, обе точки в одной и той же внешней зоне, новая точка не добавляется
SameZone:       RET

                ; вход таблицы, первая точка внутри, вторая снизу справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseI_BR:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
NeedRightForBR: CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
PickBRExit:     CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.AppendBottomClipIntersection.UseProduct              ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @Map.AppendRightClipIntersection.UseProduct
                ; вход таблицы, первая точка справа, вторая снизу справа
CaseR_BR:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                JP NZ, @Map.AppendBottomRightCorner.Entry                       ; переход, если нижний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая снизу слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseI_BL:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
NeedLeftForBL:  CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
PickBLExit:     CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.AppendLeftClipIntersection.UseProduct                ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @Map.AppendBottomClipIntersection.UseProduct
                ; вход таблицы, первая точка снизу, вторая снизу слева
CaseB_BL:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                JP NZ, @Map.AppendBottomLeftCorner.Entry                        ; переход, если нижний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая сверху справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseI_TR:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
NeedRightForTR: CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
PickTRExit:     CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.AppendRightClipIntersection.UseProduct               ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @Map.AppendTopClipIntersection.UseProduct
                ; вход таблицы, первая точка сверху, вторая сверху справа
CaseT_TR:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                JP NZ, @Map.AppendTopRightCorner.Entry                          ; переход, если верхний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                RET

                ; вход таблицы, первая точка внутри, вторая сверху слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseI_TL:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
NeedLeftForTL:  CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
PickTLExit:     CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.AppendTopClipIntersection.UseProduct                 ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @Map.AppendLeftClipIntersection.UseProduct
                ; вход таблицы, первая точка слева, вторая сверху слева
CaseL_TL:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                JP NZ, @Map.AppendTopLeftCorner.Entry                           ; переход, если верхний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                RET

                ; вход таблицы, первая точка справа, вторая внутри
CaseR_I:        CALL @Map.AppendRightClipIntersection.Entry
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка справа, вторая слева
CaseR_L:        CALL @Map.AppendRightClipIntersection.Entry
                JP @Map.AppendLeftClipIntersection.Entry

                ; вход таблицы, первая точка справа, вторая снизу
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_B:        CALL @Map.ComputeRightClipProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishRtoB:     CALL @Map.ComputeBottomClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP P, @Map.AppendBottomRightCorner.Entry                        ; переход, если бит 31 разности BottomProduct минус RightProduct сброшен

                CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.AppendBottomClipIntersection.UseProduct

                ; вход таблицы, первая точка справа, вторая снизу слева
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_BL:       CALL @Map.ComputeRightClipProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishRtoBL:    CALL @Map.ComputeBottomClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.MapClipCases.CrossRtoBL                              ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @Map.AppendBottomRightCorner.Entry
                JP @Map.MapClipCases.CaseB_BL

CrossRtoBL:     CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.MapClipCases.NeedLeftForBL

                ; вход таблицы, первая точка справа, вторая сверху
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_T:        CALL @Map.ComputeRightClipProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishRtoT:     CALL @Map.ComputeTopClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.AppendTopClipIntersection.UseProduct

                ; вход таблицы, первая точка справа, вторая сверху справа
                ; проверка направления отрезка по разности X2 минус X1
CaseR_TR:       CALL @Map.SubtractClipPointX.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности X2 минус X1 установлен

                RET

                ; вход таблицы, первая точка справа, вторая сверху слева
                ; вычисление кэшированного числителя RightProduct для правой границы
CaseR_TL:       CALL @Map.ComputeRightClipProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishRtoTL:    CALL @Map.ComputeTopClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.MapClipCases.NeedLeftForTL

                ; вход таблицы, первая точка слева, вторая внутри
CaseL_I:        CALL @Map.AppendLeftClipIntersection.Entry
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка слева, вторая справа
CaseL_R:        CALL @Map.AppendLeftClipIntersection.Entry
                JP @Map.AppendRightClipIntersection.Entry

                ; вход таблицы, первая точка слева, вторая снизу
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_B:        CALL @Map.ComputeLeftClipProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishLtoB:     CALL @Map.ComputeBottomClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.AppendBottomClipIntersection.UseProduct

                ; вход таблицы, первая точка слева, вторая снизу справа
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_BR:       CALL @Map.ComputeLeftClipProduct.Entry
                ; вычисление кэшированного числителя BottomProduct для нижней границы
FinishLtoBR:    CALL @Map.ComputeBottomClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.MapClipCases.NeedRightForBR

                ; вход таблицы, первая точка слева, вторая снизу слева
                ; проверка направления отрезка по разности X2 минус X1
CaseL_BL:       CALL @Map.SubtractClipPointX.Entry
                JP P, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности X2 минус X1 сброшен

                RET

                ; вход таблицы, первая точка слева, вторая сверху
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_T:        CALL @Map.ComputeLeftClipProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishLtoT:     CALL @Map.ComputeTopClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP P, @Map.AppendTopLeftCorner.Entry                            ; переход, если бит 31 разности TopProduct минус LeftProduct сброшен

                CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.AppendTopClipIntersection.UseProduct

                ; вход таблицы, первая точка слева, вторая сверху справа
                ; вычисление кэшированного числителя LeftProduct для левой границы
CaseL_TR:       CALL @Map.ComputeLeftClipProduct.Entry
                ; вычисление кэшированного числителя TopProduct для верхней границы
FinishLtoTR:    CALL @Map.ComputeTopClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.MapClipCases.CrossLtoTR                              ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @Map.AppendTopLeftCorner.Entry
                JP @Map.MapClipCases.CaseT_TR

CrossLtoTR:     CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.MapClipCases.NeedRightForTR

                ; вход таблицы, первая точка снизу, вторая внутри
CaseB_I:        CALL @Map.AppendBottomClipIntersection.Entry
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка снизу, вторая справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_R:        CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishBtoR:     CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @Map.AppendBottomClipIntersection.UseProduct
                JP @Map.AppendRightClipIntersection.UseProduct

                ; вход таблицы, первая точка снизу, вторая слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_L:        CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishBtoL:     CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP P, @Map.AppendBottomLeftCorner.Entry                         ; переход, если бит 31 разности BottomProduct минус LeftProduct сброшен

                CALL @Map.AppendBottomClipIntersection.UseProduct
                JP @Map.AppendLeftClipIntersection.UseProduct

                ; вход таблицы, первая точка снизу, вторая снизу справа
                ; проверка направления отрезка по разности Y2 минус Y1
CaseB_BR:       CALL @Map.SubtractClipPointY.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности Y2 минус Y1 установлен

                RET

                ; вход таблицы, первая точка снизу, вторая сверху
CaseB_T:        CALL @Map.AppendBottomClipIntersection.Entry
                JP @Map.AppendTopClipIntersection.Entry

                ; вход таблицы, первая точка снизу, вторая сверху справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_TR:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishBtoTR:    CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @Map.AppendBottomClipIntersection.UseProduct
                ; вычисление кэшированного числителя TopProduct для верхней границы
                CALL @Map.ComputeTopClipProduct.Entry
                JP @Map.MapClipCases.PickTRExit

                ; вход таблицы, первая точка снизу, вторая сверху слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseB_TL:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishBtoTL:    CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.MapClipCases.CrossBtoTL                              ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @Map.AppendBottomLeftCorner.Entry
                JP @Map.MapClipCases.CaseL_TL

CrossBtoTL:     CALL @Map.AppendBottomClipIntersection.UseProduct
                ; вычисление кэшированного числителя TopProduct для верхней границы
                CALL @Map.ComputeTopClipProduct.Entry
                JP @Map.MapClipCases.PickTLExit

                ; вход таблицы, первая точка снизу справа, вторая внутри
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_I:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.MapClipCases.RightToInside                           ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @Map.AppendBottomRightCorner.Entry                     ; вызов, если нижний правый угол уже отмечен, запросить его добавление
BottomToInside: CALL @Map.AppendBottomClipIntersection.UseProduct
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка снизу справа, вторая справа
                ; проверка направления отрезка по разности X2 минус X1
CaseBR_R:       CALL @Map.SubtractClipPointX.Entry
                JP P, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности X2 минус X1 сброшен

                RET

                ; вход таблицы, первая точка снизу справа, вторая слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_L:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.MapClipCases.RightToLeft                             ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @Map.AppendBottomRightCorner.Entry                     ; вызов, если нижний правый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishBtoL

RightToLeft:    CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.AppendLeftClipIntersection.Entry

                ; вход таблицы, первая точка снизу справа, вторая снизу
CaseBR_B:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                JP NZ, @Map.AppendBottomRightCorner.Entry                       ; переход, если нижний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                RET

                ; вход таблицы, первая точка снизу справа, вторая снизу слева
CaseBR_BL:      CALL @Map.MapClipCases.CaseBR_B
                JP @Map.MapClipCases.CaseB_BL

                ; вход таблицы, первая точка снизу справа, вторая сверху
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_T:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.MapClipCases.FinishRtoT                              ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                CALL @Map.MapClipCases.CaseBR_B
                CALL @Map.AppendBottomClipIntersection.UseProduct
                JP @Map.AppendTopClipIntersection.Entry

                ; вход таблицы, первая точка снизу справа, вторая сверху слева
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBR_TL:      CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус RightProduct
                CALL @Map.SubtractBottomRightProducts.Entry
                JP M, @Map.MapClipCases.FinishRtoTL                             ; переход, если бит 31 разности BottomProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний правый угол
                BIT @MapClipCornerBit.BottomRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomRight, (HL)
                CALL NZ, @Map.AppendBottomRightCorner.Entry                     ; вызов, если нижний правый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishBtoTL

                ; вход таблицы, первая точка снизу слева, вторая внутри
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_I:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.MapClipCases.BottomToInside                          ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @Map.AppendBottomLeftCorner.Entry                      ; вызов, если нижний левый угол уже отмечен, запросить его добавление
LeftToInside:   CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка снизу слева, вторая справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_R:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.MapClipCases.FinishBtoR                              ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                CALL @Map.MapClipCases.CaseBL_L
                CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.AppendRightClipIntersection.Entry

                ; вход таблицы, первая точка снизу слева, вторая слева
CaseBL_L:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                JP NZ, @Map.AppendBottomLeftCorner.Entry                        ; переход, если нижний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                RET

                ; вход таблицы, первая точка снизу слева, вторая снизу
                ; проверка направления отрезка по разности Y2 минус Y1
CaseBL_B:       CALL @Map.SubtractClipPointY.Entry
                JP P, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности Y2 минус Y1 сброшен

                RET

                ; вход таблицы, первая точка снизу слева, вторая сверху
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_T:       CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.MapClipCases.BottomToTop                             ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @Map.AppendBottomLeftCorner.Entry                      ; вызов, если нижний левый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishLtoT

BottomToTop:    CALL @Map.AppendBottomClipIntersection.UseProduct
                JP @Map.AppendTopClipIntersection.Entry

                ; вход таблицы, первая точка снизу слева, вторая сверху справа
                ; вычисление кэшированного числителя BottomProduct для нижней границы
CaseBL_TR:      CALL @Map.ComputeBottomClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности BottomProduct минус LeftProduct
                CALL @Map.SubtractBottomLeftProducts.Entry
                JP M, @Map.MapClipCases.FinishBtoTR                             ; переход, если бит 31 разности BottomProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, нижний левый угол
                BIT @MapClipCornerBit.BottomLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.BottomLeft, (HL)
                CALL NZ, @Map.AppendBottomLeftCorner.Entry                      ; вызов, если нижний левый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishLtoTR

                ; вход таблицы, первая точка снизу слева, вторая сверху слева
CaseBL_TL:      CALL @Map.MapClipCases.CaseBL_L
                JP @Map.MapClipCases.CaseL_TL

                ; вход таблицы, первая точка сверху, вторая внутри
CaseT_I:        CALL @Map.AppendTopClipIntersection.Entry
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка сверху, вторая справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_R:        CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishTtoR:     CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP P, @Map.AppendTopRightCorner.Entry                           ; переход, если бит 31 разности TopProduct минус RightProduct сброшен

                CALL @Map.AppendTopClipIntersection.UseProduct
                JP @Map.AppendRightClipIntersection.UseProduct

                ; вход таблицы, первая точка сверху, вторая слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_L:        CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishTtoL:     CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @Map.AppendTopClipIntersection.UseProduct
                JP @Map.AppendLeftClipIntersection.UseProduct

                ; вход таблицы, первая точка сверху, вторая снизу
CaseT_B:        CALL @Map.AppendTopClipIntersection.Entry
                JP @Map.AppendBottomClipIntersection.Entry

                ; вход таблицы, первая точка сверху, вторая снизу справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_BR:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
FinishTtoBR:    CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.MapClipCases.CrossTtoBR                              ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @Map.AppendTopRightCorner.Entry
                JP @Map.MapClipCases.CaseR_BR

CrossTtoBR:     CALL @Map.AppendTopClipIntersection.UseProduct
                ; вычисление кэшированного числителя BottomProduct для нижней границы
                CALL @Map.ComputeBottomClipProduct.Entry
                JP @Map.MapClipCases.PickBRExit

                ; вход таблицы, первая точка сверху, вторая снизу слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseT_BL:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
FinishTtoBL:    CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @Map.AppendTopClipIntersection.UseProduct
                ; вычисление кэшированного числителя BottomProduct для нижней границы
                CALL @Map.ComputeBottomClipProduct.Entry
                JP @Map.MapClipCases.PickBLExit

                ; вход таблицы, первая точка сверху, вторая сверху слева
                ; проверка направления отрезка по разности Y2 минус Y1
CaseT_TL:       CALL @Map.SubtractClipPointY.Entry
                JP P, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности Y2 минус Y1 сброшен

                RET

                ; вход таблицы, первая точка сверху справа, вторая внутри
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_I:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.MapClipCases.TopToInside                             ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @Map.AppendTopRightCorner.Entry                        ; вызов, если верхний правый угол уже отмечен, запросить его добавление
RightToInside:  CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка сверху справа, вторая справа
CaseTR_R:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                JP NZ, @Map.AppendTopRightCorner.Entry                          ; переход, если верхний правый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                RET

                ; вход таблицы, первая точка сверху справа, вторая слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_L:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.MapClipCases.FinishTtoL                              ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                CALL @Map.MapClipCases.CaseTR_R
                CALL @Map.AppendRightClipIntersection.UseProduct
                JP @Map.AppendLeftClipIntersection.Entry

                ; вход таблицы, первая точка сверху справа, вторая снизу
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_B:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.MapClipCases.TopToBottom                             ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @Map.AppendTopRightCorner.Entry                        ; вызов, если верхний правый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishRtoB

TopToBottom:    CALL @Map.AppendTopClipIntersection.UseProduct
                JP @Map.AppendBottomClipIntersection.Entry

                ; вход таблицы, первая точка сверху справа, вторая снизу справа
CaseTR_BR:      CALL @Map.MapClipCases.CaseTR_R
                JP @Map.MapClipCases.CaseR_BR

                ; вход таблицы, первая точка сверху справа, вторая снизу слева
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTR_BL:      CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя RightProduct для правой границы
                CALL @Map.ComputeRightClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус RightProduct
                CALL @Map.SubtractTopRightProducts.Entry
                JP M, @Map.MapClipCases.FinishTtoBL                             ; переход, если бит 31 разности TopProduct минус RightProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний правый угол
                BIT @MapClipCornerBit.TopRight, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopRight, (HL)
                CALL NZ, @Map.AppendTopRightCorner.Entry                        ; вызов, если верхний правый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishRtoBL

                ; вход таблицы, первая точка сверху справа, вторая сверху
                ; проверка направления отрезка по разности Y2 минус Y1
CaseTR_T:       CALL @Map.SubtractClipPointY.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности Y2 минус Y1 установлен

                RET

                ; вход таблицы, первая точка сверху слева, вторая внутри
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_I:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.MapClipCases.LeftToInside                            ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @Map.AppendTopLeftCorner.Entry                         ; вызов, если верхний левый угол уже отмечен, запросить его добавление
TopToInside:    CALL @Map.AppendTopClipIntersection.UseProduct
                JP @Map.AppendSecondClipPoint.Entry

                ; вход таблицы, первая точка сверху слева, вторая справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_R:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.MapClipCases.LeftToRight                             ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @Map.AppendTopLeftCorner.Entry                         ; вызов, если верхний левый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishTtoR

LeftToRight:    CALL @Map.AppendLeftClipIntersection.UseProduct
                JP @Map.AppendRightClipIntersection.Entry

                ; вход таблицы, первая точка сверху слева, вторая слева
                ; проверка направления отрезка по разности X2 минус X1
CaseTL_L:       CALL @Map.SubtractClipPointX.Entry
                JP M, @Map.UnwindClipFrame.Entry                                ; переход, если старший бит разности X2 минус X1 установлен

                RET

                ; вход таблицы, первая точка сверху слева, вторая снизу
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_B:       CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.MapClipCases.FinishLtoB                              ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                CALL @Map.MapClipCases.CaseTL_T
                CALL @Map.AppendTopClipIntersection.UseProduct
                JP @Map.AppendBottomClipIntersection.Entry

                ; вход таблицы, первая точка сверху слева, вторая снизу справа
                ; вычисление кэшированного числителя TopProduct для верхней границы
CaseTL_BR:      CALL @Map.ComputeTopClipProduct.Entry
                ; вычисление кэшированного числителя LeftProduct для левой границы
                CALL @Map.ComputeLeftClipProduct.Entry
                ; проверка порядка пересечений по разности TopProduct минус LeftProduct
                CALL @Map.SubtractTopLeftProducts.Entry
                JP M, @Map.MapClipCases.FinishLtoBR                             ; переход, если бит 31 разности TopProduct минус LeftProduct установлен

                LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                CALL NZ, @Map.AppendTopLeftCorner.Entry                         ; вызов, если верхний левый угол уже отмечен, запросить его добавление
                JP @Map.MapClipCases.FinishTtoBR

                ; вход таблицы, первая точка сверху слева, вторая сверху
CaseTL_T:       LD HL, @MapClipWork.Corners.SeenFlags
                ; проверка прежней отметки, верхний левый угол
                BIT @MapClipCornerBit.TopLeft, (HL)
                JP NZ, @Map.AppendTopLeftCorner.Entry                           ; переход, если верхний левый угол уже отмечен, запросить его добавление

                ; сохранение отметки этого угла, условие от предыдущего BIT остаётся действительным
                SET @MapClipCornerBit.TopLeft, (HL)
                RET

                ; вход таблицы, первая точка сверху слева, вторая сверху справа
CaseTL_TR:      CALL @Map.MapClipCases.CaseTL_T
                JP @Map.MapClipCases.CaseT_TR

                endmodule
                endmodule
