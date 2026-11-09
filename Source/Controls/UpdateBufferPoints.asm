                module Controls
                module UpdateBufferPoints
                ; Физические входы [управления и зерно](../../Docs/ActionInputContextData.md)
                ; Документация [алгоритм и проверка](../../Docs/ControlsPointMotion.md)
                ; -----------------------------------------
                ; Последовательная коррекция 35 точек по Y, X и двум табличным коэффициентам
                ; исходная запись 22, банк 1, смещения #0B00..#0E15
                ; In:
                ;   HL, DE, BC, AF и альтернативные регистры входных аргументов не задают, регистр R задаёт источник обновляемых выборок
                ;   банк 1 выбран, 35 FBufferPoint содержат Y=0..95 и байтовый X, таблица коэффициентов 9900..99FF готова
                ;   YControl=9B95, XControl=9B96, TurnControl=9B97 задают три управляющих байта, единицы игрового управления здесь не предполагаются
                ;   код, координаты и стек доступны для записи, YWrapOffset, XWrapOffset и оба YOffset возврата точки равны исходному нулю
                ;   на CPU-стеке внешний возврат, ещё два байта нужны для CALL, договор не включает вмешательство IRQ
                ; Out:
                ;   при возврате 35 записей последовательно обработаны по Y, X и табличной коррекции, Y остаётся в 0..95, X в 0..255
                ;   без третьей фазы HL=C547 при ненулевом XControl либо C501 при нулевом, AF=0054
                ;   после третьей фазы HL=C546 и AF=4642, эти значения F не являются кодом успешности игрового действия
                ;   DE сохраняется, если не было вызовов RespawnPointIndexPos/Neg, иначе содержит D=X и E=Y последнего такого возврата
                ;   B сохраняется кроме пути повторного создания Y при отрицательном YControl, там остаётся последний ограниченный остаток
                ;   C содержит последний шаг X или Y, при вызове возврата точки заменён его шагом, без этих операций сохраняется
                ;   при TurnControl=0 AF' сохраняется, HL', DE', BC' сохраняются без генератора либо содержат его последний результат
                ;   после третьей фазы HL' содержит последнее вычисленное Y либо X до ограничения, DE' последний перекрёстный результат, BC'=0030 либо 0080
                ;   AF' после третьей фазы содержит округлённый модуль последнего перекрёстного произведения и флаги INC, формула приведена в документации
                ;   IX и IY, I, IM и IFF сохраняются, SP=входной SP+2, R точно соответствует выполненным M1 при отсутствии IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', координаты, Seed, фазовые байты, операнды коэффициентов и CALL, TurnYStore, два байта CPU-стека, R
                ; Note:
                ;   при трёх нулевых управляющих байтах RAM не записывается, процедура лишь устанавливает выходные регистры
                ;   нули Y и крайние X не отбрасываются как пустые элементы, повторное создание зависит от направления и исходных границ
                ;   семибитовое произведение всегда содержит единичную поправку, даже нулевой модуль даёт +1 либо -1 по знаковым битам
                ;   TurnControl=C0 даёт нулевой шаг возврата, если понадобится пересоздать точку, цикл SUB 0 не вернёт управление
                ;   страница 99 содержит исходную синусоиду ACTION, индекс со сдвигом QuarterCycle даёт косинус, байты таблицы сохранены отдельно
                ;   модель исполняет настоящие генератор и оба динамических возврата, но не является нативным игровым кадром
                ; -----------------------------------------
                ; -----------------------------------------
                ; Обновление Y с повторным созданием точки на границе
                ; -----------------------------------------
                ; выбор первого физического поля Y таблицы ControlsBufferPoints
Entry:          LD HL, @ControlsBufferPoints.Point00
                ; чтение YControl, нулевое управление пропускает весь проход Y
                LD A, (@ControlsPointMotionState.YControl)
                ; проверка нулевого управления Y перед выбором направления
                AND A
                JP Z, @Controls.UpdateBufferPoints.BeginXPass                   ; переход, если YControl равен нулю, продолжить с BeginXPass

                JP M, @Controls.UpdateBufferPoints.PrepareYUp                   ; переход, если YControl имеет установленный бит 7, подготовить движение в PrepareYUp

                ; вычисление шага вниз, (4*YControl+2) AND FF
                RLA
                RLA
                INC A
                INC A
                LD C, A
                ; вычисление нового Y добавлением шага к текущей координате
AdvanceYDown:   LD A, (HL)
                ADD A, C
                JR C, @Controls.UpdateBufferPoints.ReplaceYDown                 ; переход, если сложение Y со шагом переполнило байт, пересоздать точку в ReplaceYDown

                ; проверка верхней границы YUpperLimit после сложения без переноса
                CP @BufferPointConst.YUpperLimit
                JR C, @Controls.UpdateBufferPoints.YDownKeepX                   ; переход, если новый Y меньше YUpperLimit, сохранить X через YDownKeepX

                ; получение семибитового R для нового Y после пересечения нижней границы
ReplaceYDown:   LD A, R
                AND @BufferPointConst.YIndexMask
                ; проверка остатка от R относительно шага Y
YDownModulo:    CP C
                JR C, @Controls.UpdateBufferPoints.YDownLimit                   ; переход, если остаток меньше шага Y, продолжить с YDownLimit

                ; вычисление остатка повторным вычитанием ненулевого шага
                SUB C
                JR @Controls.UpdateBufferPoints.YDownModulo

                ; проверка верхнего ограничения нового остатка значением YUpperLimit-1
YDownLimit:     CP @BufferPointConst.YUpperLimit - 1
                JR C, @Controls.UpdateBufferPoints.YDownStore                   ; переход, если остаток меньше YUpperLimit-1, продолжить с YDownStore без загрузки ограничителя

                LD A, @BufferPointConst.YUpperLimit - 1
                ; вычисление нового Y с исходным YWrapOffset и сохранение физического поля Y
YDownStore:     ADD A, #00
                LD (HL), A
                ; создание нового X настоящим вызовом NextBufferRandom после пересечения границы Y
                CALL @Controls.NextBufferRandom.Entry
                INC L
                ; проверка нулевого X после генератора
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.YDownLimitX                 ; переход, если X не меньше MinCoordinate, продолжить с YDownLimitX

                ADD A, #01
                ; проверка верхнего ограничения XUpperLimit
YDownLimitX:    CP @BufferPointConst.XUpperLimit
                JR C, @Controls.UpdateBufferPoints.YDownStoreX                  ; переход, если X меньше XUpperLimit, продолжить с YDownStoreX без уменьшения

                SUB #01
                ; сохранение нового X и переход указателя к следующей записи Y,X
YDownStoreX:    LD (HL), A
                INC L
                LD A, L
                ; проверка достижения ByteCount после заполнения всей записи
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceYDown                 ; переход, если младший байт указателя меньше ByteCount, обработать следующую точку в AdvanceYDown

                JP @Controls.UpdateBufferPoints.BeginXPass

                ; сохранение только нового Y, существующий X не изменяется
YDownKeepX:     LD (HL), A
                INC L
                INC L
                LD A, L
                ; проверка завершения 35 записей в проходе Y
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceYDown                 ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYDown

                JP @Controls.UpdateBufferPoints.BeginXPass

                ; вычисление шага вверх с сохранением Carry от NEG в двух RLA, для YControl=80 шаг равен 3
PrepareYUp:     NEG
                RLA
                RLA
                LD C, A
                ; вычисление нового Y вычитанием шага вверх
AdvanceYUp:     LD A, (HL)
                SUB C
                JR C, @Controls.UpdateBufferPoints.ReplaceYUp                   ; переход, если исходный Y меньше шага, пересоздать точку в ReplaceYUp

                ; проверка минимальной координаты Y после вычитания без заёма
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.YUpKeepX                    ; переход, если новый Y не меньше MinCoordinate, сохранить X через YUpKeepX

                ; получение R для повторного создания точки после пересечения верхней границы
ReplaceYUp:     LD A, R
                AND @BufferPointConst.YIndexMask
                ; проверка остатка R относительно шага вверх
YUpModulo:      CP C
                JR C, @Controls.UpdateBufferPoints.YUpLimit                     ; переход, если остаток меньше шага Y, продолжить с YUpLimit

                ; вычисление остатка семибитового R вычитанием шага
                SUB C
                JR @Controls.UpdateBufferPoints.YUpModulo

                ; проверка ограничения остатка значением YUpperLimit-1
YUpLimit:       CP @BufferPointConst.YUpperLimit - 1
                JR C, @Controls.UpdateBufferPoints.YUpStore                     ; переход, если остаток меньше YUpperLimit-1, продолжить с YUpStore

                LD A, @BufferPointConst.YUpperLimit - 1
                ; вычисление отражённого Y=YUpperLimit-остаток, B становится рабочим остатком
YUpStore:       LD B, A
                LD A, @BufferPointConst.YUpperLimit
                SUB B
                LD (HL), A
                ; создание нового X после выхода Y через верхнюю границу
                CALL @Controls.NextBufferRandom.Entry
                INC L
                ; проверка нулевого сгенерированного X
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.YUpLimitX                   ; переход, если X не меньше MinCoordinate, продолжить с YUpLimitX

                ADD A, #01
                ; проверка верхнего ограничения нового X
YUpLimitX:      CP @BufferPointConst.XUpperLimit
                JR C, @Controls.UpdateBufferPoints.YUpStoreX                    ; переход, если X меньше XUpperLimit, продолжить с YUpStoreX

                SUB #01
                ; сохранение нового X и выбор следующего физического поля Y
YUpStoreX:      LD (HL), A
                INC L
                LD A, L
                ; проверка завершения таблицы после повторного создания точки
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceYUp                   ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYUp

                JP @Controls.UpdateBufferPoints.BeginXPass

                ; сохранение нового Y без изменения X
YUpKeepX:       LD (HL), A
                INC L
                INC L
                LD A, L
                ; проверка завершения прохода вверх по всем записям
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceYUp                   ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYUp

                ; -----------------------------------------
                ; Обновление X с возможной заменой Y
                ; -----------------------------------------
                ; выбор поля FBufferPoint.X первой записи перед независимым проходом X
BeginXPass:     LD HL, @ControlsBufferPoints.Point00 + @FBufferPoint.X
                LD A, (@ControlsPointMotionState.XControl)
                ; проверка нулевого XControl перед выбором направления
                AND A
                JP Z, @Controls.UpdateBufferPoints.BeginTurn                    ; переход, если XControl равен нулю, продолжить с BeginTurn

                JP P, @Controls.UpdateBufferPoints.PrepareXLeft                 ; переход, если XControl находится в 1..127, подготовить движение в PrepareXLeft

                ; вычисление шага вправо с Carry от NEG, исходный 80 даёт шаг 3
                NEG
                RLA
                RLA
                LD C, A
                ; вычисление нового X добавлением шага вправо
AdvanceXRight:  LD A, (HL)
                ADD A, C
                JR C, @Controls.UpdateBufferPoints.ReplaceXRight                ; переход, если сложение X со шагом переполнило байт, продолжить с ReplaceXRight

                ; проверка верхнего ограничения X после сложения без переноса
                CP @BufferPointConst.XUpperLimit
                JR C, @Controls.UpdateBufferPoints.XRightKeepY                  ; переход, если новый X меньше XUpperLimit, сохранить Y через XRightKeepY

                ; получение нового X через NextBufferRandom после пересечения правой границы
ReplaceXRight:  CALL @Controls.NextBufferRandom.Entry
                ; проверка остатка сгенерированного байта относительно шага вправо
XRightModulo:   CP C
                JR C, @Controls.UpdateBufferPoints.XRightLimit                  ; переход, если остаток меньше шага X, продолжить с XRightLimit

                ; вычисление остатка повторным вычитанием шага вправо
                SUB C
                JR @Controls.UpdateBufferPoints.XRightModulo

                ; проверка ограничения остатка значением XUpperLimit-1
XRightLimit:    CP @BufferPointConst.XUpperLimit - 1
                JR C, @Controls.UpdateBufferPoints.XRightStore                  ; переход, если остаток меньше XUpperLimit-1, продолжить с XRightStore

                LD A, @BufferPointConst.XUpperLimit - 1
                ; вычисление нового X с исходным XWrapOffset и сохранение поля X
XRightStore:    ADD A, #00
                LD (HL), A
                ; получение нового Y из семи младших битов R
                LD A, R
                AND @BufferPointConst.YIndexMask
                DEC L
                ; проверка нулевой вертикальной координаты
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.XRightYLimit                ; переход, если Y не меньше MinCoordinate, продолжить с XRightYLimit

                ADD A, #01
                ; проверка верхней границы нового Y
XRightYLimit:   CP @BufferPointConst.YUpperLimit
                JR C, @Controls.UpdateBufferPoints.XRightStoreY                 ; переход, если Y меньше YUpperLimit, продолжить с XRightStoreY без свёртки

                ; свёртка больших семибитовых Y вычитанием YFold, это не остаток по высоте растра
                SUB @BufferPointConst.YFold
                ; сохранение нового Y и выбор поля X следующей записи
XRightStoreY:   LD (HL), A
                INC L
                INC L
                INC L
                LD A, L
                ; проверка завершения прохода X после повторного создания точки
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceXRight                ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXRight

                JP @Controls.UpdateBufferPoints.BeginTurn

                ; сохранение нового X без изменения Y
XRightKeepY:    LD (HL), A
                INC L
                INC L
                LD A, L
                ; проверка завершения прохода вправо
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceXRight                ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXRight

                JP @Controls.UpdateBufferPoints.BeginTurn

                ; вычисление шага влево, (4*XControl+2) AND FF
PrepareXLeft:   RLA
                RLA
                INC A
                INC A
                LD C, A
                ; вычисление нового X вычитанием шага влево
AdvanceXLeft:   LD A, (HL)
                SUB C
                JR C, @Controls.UpdateBufferPoints.ReplaceXLeft                 ; переход, если исходный X меньше шага, продолжить с ReplaceXLeft

                ; проверка минимальной координаты X после вычитания без заёма
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.XLeftKeepY                  ; переход, если новый X не меньше MinCoordinate, сохранить Y через XLeftKeepY

                ; получение нового X настоящим вызовом генератора
ReplaceXLeft:   CALL @Controls.NextBufferRandom.Entry
                ; проверка остатка сгенерированного байта относительно шага влево
XLeftModulo:    CP C
                JR C, @Controls.UpdateBufferPoints.XLeftLimit                   ; переход, если остаток меньше шага X, продолжить с XLeftLimit

                ; вычисление остатка повторным вычитанием шага влево
                SUB C
                JR @Controls.UpdateBufferPoints.XLeftModulo

                ; проверка ограничения остатка значением XUpperLimit-1
XLeftLimit:     CP @BufferPointConst.XUpperLimit - 1
                JR C, @Controls.UpdateBufferPoints.XLeftStore                   ; переход, если остаток меньше XUpperLimit-1, продолжить с XLeftStore

                LD A, @BufferPointConst.XUpperLimit - 1
                ; вычисление отражённого X=255-остаток, исходные значения 254 и 255 не исключаются повторно
XLeftStore:     SUB #FF
                NEG
                LD (HL), A
                ; получение нового семибитового Y после пересоздания X
                LD A, R
                AND @BufferPointConst.YIndexMask
                DEC L
                ; проверка нулевого нового Y
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.UpdateBufferPoints.XLeftYLimit                 ; переход, если Y не меньше MinCoordinate, продолжить с XLeftYLimit

                ADD A, #01
                ; проверка верхней границы нового Y
XLeftYLimit:    CP @BufferPointConst.YUpperLimit
                JR C, @Controls.UpdateBufferPoints.XLeftStoreY                  ; переход, если Y меньше YUpperLimit, продолжить с XLeftStoreY без свёртки

                ; свёртка больших значений Y вычитанием YFold
                SUB @BufferPointConst.YFold
                ; сохранение нового Y и переход к полю X следующей записи
XLeftStoreY:    LD (HL), A
                INC L
                INC L
                INC L
                LD A, L
                ; проверка завершения таблицы после пересоздания точки
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceXLeft                 ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXLeft

                JP @Controls.UpdateBufferPoints.BeginTurn

                ; сохранение нового X без изменения Y
XLeftKeepY:     LD (HL), A
                INC L
                INC L
                LD A, L
                ; проверка завершения прохода влево
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.AdvanceXLeft                 ; переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXLeft

                ; -----------------------------------------
                ; Табличная коррекция относительно CenterX, CenterY
                ; -----------------------------------------
                ; вычисление индекса синусоиды как отрицания TurnControl
BeginTurn:      LD A, (@ControlsPointMotionState.TurnControl)
                NEG
                ; проверка необходимости третьего прохода
                AND A
                RET Z                                                           ; выход, если TurnControl равен нулю

                LD L, A
                JP P, @Controls.UpdateBufferPoints.PrepareTurn                  ; переход, если индекс синусоиды неотрицательный, подготовить шаг в PrepareTurn

                ; вычисление модуля отрицательного индекса с сохранением Carry от NEG
                NEG
                ; вычисление шага возврата точки двумя RLA с исходным Carry, значение C0 управления даёт нулевой шаг
PrepareTurn:    RLA
                RLA
                ; обновление изменяемого шага обоих входов повторного создания точки
                LD (@ControlsPointRespawnState.PositiveStep), A
                LD (@ControlsPointRespawnState.NegativeStep), A
                ; поиск синуса по индексу в исходной странице SinePage
                LD H, @BufferPointMotionConst.SinePage
                LD A, (HL)
                ; обновление коэффициентов XSinCoeff и YNegSinCoeff противоположными знаками синуса
                LD (@ControlsPointMotionState.XSinCoeff), A
                NEG
                LD (@ControlsPointMotionState.YNegSinCoeff), A
                ; вычисление индекса косинуса смещением на QuarterCycle по модулю 256
                LD A, L
                ADD A, @BufferPointMotionConst.QuarterCycle
                LD L, A
                LD A, (HL)
                ; обновление двух операндов косинуса для независимого расчёта Y и X
                LD (@ControlsPointMotionState.YCosCoeff), A
                LD (@ControlsPointMotionState.XCosCoeff), A
                ; восстановление знака индекса для выбора физического входа возврата точки
                LD A, L
                SUB @BufferPointMotionConst.QuarterCycle
                LD HL, @Controls.RespawnPointIndexPos.Entry
                JP P, @Controls.UpdateBufferPoints.StoreTurnCalls               ; переход, если индекс синусоиды неотрицательный, сохранить вход RespawnPointIndexPos

                ; выбор входа RespawnPointIndexNeg для отрицательного индекса
                LD HL, @Controls.RespawnPointIndexNeg.Entry
                ; обновление обоих операндов CALL одним выбранным входом возврата точки
StoreTurnCalls: LD (@ControlsPointMotionState.YRespawnCall), HL
                LD (@ControlsPointMotionState.XRespawnCall), HL
                ; поиск первой физической записи FBufferPoint перед третьим проходом
                LD HL, @ControlsBufferPoints.Point00
                ; вычисление знакового смещения исходного Y относительно CenterY
TurnPoint:      LD A, (HL)
                SUB @BufferPointMotionConst.CenterY
                EXX
                LD C, A
                ; вычисление произведения Y-CenterY на YCosCoeff с семибитовым масштабом
                LD E, #00
                ; определение знака произведения по различию знаковых битов двух множителей
                XOR E
                EX AF, AF'
                LD A, E
                ; проверка знакового бита коэффициента перед получением его модуля
                AND A
                JP P, @Controls.UpdateBufferPoints.YCosAbs                      ; переход, если коэффициент неотрицательный, продолжить с YCosAbs

                ; вычисление модуля отрицательного коэффициента, байт 80 сохраняет модуль 128
                NEG
                LD E, A
                ; проверка знака координатного смещения перед умножением модулей
YCosAbs:        LD A, C
                AND A
                JP P, @Controls.UpdateBufferPoints.YCosMultiply                 ; переход, если координатное смещение неотрицательное, продолжить с YCosMultiply

                ; вычисление модуля отрицательного координатного смещения
                NEG
                LD C, A
                ; вычисление старших семи разрядов произведения последовательным накоплением и сдвигами
YCosMultiply:   XOR A
                ; проверка разряда 0 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift1                  ; переход, если разряд 0 коэффициента нулевой, продолжить с YCosShift1 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift1:     RRA
                ; проверка разряда 1 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift2                  ; переход, если разряд 1 коэффициента нулевой, продолжить с YCosShift2 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift2:     RRA
                ; проверка разряда 2 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift3                  ; переход, если разряд 2 коэффициента нулевой, продолжить с YCosShift3 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift3:     RRA
                ; проверка разряда 3 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift4                  ; переход, если разряд 3 коэффициента нулевой, продолжить с YCosShift4 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift4:     RRA
                ; проверка разряда 4 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift5                  ; переход, если разряд 4 коэффициента нулевой, продолжить с YCosShift5 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift5:     RRA
                ; проверка разряда 5 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift6                  ; переход, если разряд 5 коэффициента нулевой, продолжить с YCosShift6 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift6:     RRA
                ; проверка разряда 6 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YCosShift7                  ; переход, если разряд 6 коэффициента нулевой, продолжить с YCosShift7 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YCosShift7:     RRA
                ; вычисление исходной единичной поправки, модуль результата равен floor(произведение/128)+1
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UpdateBufferPoints.YCosSignDone                 ; переход, если знаковые биты множителей совпадают, продолжить с YCosSignDone с положительным результатом

                ; вычисление отрицательного 16-битного результата из округлённого модуля
                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
YCosSignDone:   EX DE, HL
                EXX
                INC L
                LD A, (HL)
                SUB @BufferPointMotionConst.CenterX
                EXX
                LD C, A
                ; вычисление произведения X-CenterX на XSinCoeff с семибитовым масштабом
                LD E, #00
                ; определение знака произведения по различию знаковых битов двух множителей
                XOR E
                EX AF, AF'
                LD A, E
                ; проверка знакового бита коэффициента перед получением его модуля
                AND A
                JP P, @Controls.UpdateBufferPoints.XSinAbs                      ; переход, если коэффициент неотрицательный, продолжить с XSinAbs

                ; вычисление модуля отрицательного коэффициента, байт 80 сохраняет модуль 128
                NEG
                LD E, A
                ; проверка знака координатного смещения перед умножением модулей
XSinAbs:        LD A, C
                AND A
                JP P, @Controls.UpdateBufferPoints.XSinMultiply                 ; переход, если координатное смещение неотрицательное, продолжить с XSinMultiply

                ; вычисление модуля отрицательного координатного смещения
                NEG
                LD C, A
                ; вычисление старших семи разрядов произведения последовательным накоплением и сдвигами
XSinMultiply:   XOR A
                ; проверка разряда 0 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift1                  ; переход, если разряд 0 коэффициента нулевой, продолжить с XSinShift1 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift1:     RRA
                ; проверка разряда 1 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift2                  ; переход, если разряд 1 коэффициента нулевой, продолжить с XSinShift2 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift2:     RRA
                ; проверка разряда 2 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift3                  ; переход, если разряд 2 коэффициента нулевой, продолжить с XSinShift3 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift3:     RRA
                ; проверка разряда 3 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift4                  ; переход, если разряд 3 коэффициента нулевой, продолжить с XSinShift4 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift4:     RRA
                ; проверка разряда 4 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift5                  ; переход, если разряд 4 коэффициента нулевой, продолжить с XSinShift5 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift5:     RRA
                ; проверка разряда 5 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift6                  ; переход, если разряд 5 коэффициента нулевой, продолжить с XSinShift6 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift6:     RRA
                ; проверка разряда 6 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XSinShift7                  ; переход, если разряд 6 коэффициента нулевой, продолжить с XSinShift7 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XSinShift7:     RRA
                ; вычисление исходной единичной поправки, модуль результата равен floor(произведение/128)+1
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UpdateBufferPoints.SumTurnY                     ; переход, если знаковые биты множителей совпадают, продолжить с SumTurnY с положительным результатом

                ; вычисление отрицательного 16-битного результата из округлённого модуля
                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
                ; вычисление нового Y как CenterY плюс два знаковых произведения, единичные поправки сохранены
SumTurnY:       ADD HL, DE
                LD BC, @BufferPointMotionConst.CenterY
                ADD HL, BC
                ; проверка старшего байта нового Y, ненулевой байт означает выход из допустимой области
                LD A, H
                AND A
                JR NZ, @Controls.UpdateBufferPoints.ResetYOut                   ; переход, если старший байт нового Y ненулевой, пересоздать точку в ResetYOut

                LD A, L
                ; проверка нижней границы нового Y
                CP @BufferPointConst.MinCoordinate
                JR C, @Controls.UpdateBufferPoints.ResetYOut                    ; переход, если новый Y меньше MinCoordinate, пересоздать точку в ResetYOut

                ; проверка верхней границы нового Y
                CP @BufferPointConst.YUpperLimit
                JR C, @Controls.UpdateBufferPoints.KeepTurnY                    ; переход, если новый Y меньше YUpperLimit, сохранить его в KeepTurnY

                ; повторное создание точки без расчёта X после недопустимого Y
ResetYOut:      EXX
                ; вызов входа, выбранного через YRespawnCall, исходный операнд указывает RespawnPointIndexPos
                CALL @Controls.RespawnPointIndexPos.Entry
                ; сохранение X, затем Y возвращённой точки и продвижение к следующей записи
                LD (HL), D
                DEC L
                LD (HL), E
                INC L
                INC L
                ; проверка завершения 35 записей после выхода Y за границы
                LD A, L
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.TurnPoint                    ; переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint

                RET

                ; сохранение допустимого Y в операнде TurnYStore до проверки нового X
KeepTurnY:      LD (@ControlsPointMotionState.TurnYStore), A
                EXX
                ; вычисление смещения исходного X относительно CenterX для произведения с косинусом
                LD A, (HL)
                SUB @BufferPointMotionConst.CenterX
                EXX
                LD C, A
                ; вычисление произведения X-CenterX на XCosCoeff с семибитовым масштабом
                LD E, #00
                ; определение знака произведения по различию знаковых битов двух множителей
                XOR E
                EX AF, AF'
                LD A, E
                ; проверка знакового бита коэффициента перед получением его модуля
                AND A
                JP P, @Controls.UpdateBufferPoints.XCosAbs                      ; переход, если коэффициент неотрицательный, продолжить с XCosAbs

                ; вычисление модуля отрицательного коэффициента, байт 80 сохраняет модуль 128
                NEG
                LD E, A
                ; проверка знака координатного смещения перед умножением модулей
XCosAbs:        LD A, C
                AND A
                JP P, @Controls.UpdateBufferPoints.XCosMultiply                 ; переход, если координатное смещение неотрицательное, продолжить с XCosMultiply

                ; вычисление модуля отрицательного координатного смещения
                NEG
                LD C, A
                ; вычисление старших семи разрядов произведения последовательным накоплением и сдвигами
XCosMultiply:   XOR A
                ; проверка разряда 0 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift1                  ; переход, если разряд 0 коэффициента нулевой, продолжить с XCosShift1 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift1:     RRA
                ; проверка разряда 1 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift2                  ; переход, если разряд 1 коэффициента нулевой, продолжить с XCosShift2 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift2:     RRA
                ; проверка разряда 2 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift3                  ; переход, если разряд 2 коэффициента нулевой, продолжить с XCosShift3 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift3:     RRA
                ; проверка разряда 3 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift4                  ; переход, если разряд 3 коэффициента нулевой, продолжить с XCosShift4 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift4:     RRA
                ; проверка разряда 4 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift5                  ; переход, если разряд 4 коэффициента нулевой, продолжить с XCosShift5 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift5:     RRA
                ; проверка разряда 5 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift6                  ; переход, если разряд 5 коэффициента нулевой, продолжить с XCosShift6 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift6:     RRA
                ; проверка разряда 6 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.XCosShift7                  ; переход, если разряд 6 коэффициента нулевой, продолжить с XCosShift7 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
XCosShift7:     RRA
                ; вычисление исходной единичной поправки, модуль результата равен floor(произведение/128)+1
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UpdateBufferPoints.XCosSignDone                 ; переход, если знаковые биты множителей совпадают, продолжить с XCosSignDone с положительным результатом

                ; вычисление отрицательного 16-битного результата из округлённого модуля
                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
XCosSignDone:   EX DE, HL
                ; вычисление смещения исходного Y относительно CenterY для произведения с отрицательным синусом
                EXX
                DEC L
                LD A, (HL)
                SUB @BufferPointMotionConst.CenterY
                EXX
                LD C, A
                ; вычисление произведения Y-CenterY на YNegSinCoeff с семибитовым масштабом
                LD E, #00
                ; определение знака произведения по различию знаковых битов двух множителей
                XOR E
                EX AF, AF'
                LD A, E
                ; проверка знакового бита коэффициента перед получением его модуля
                AND A
                JP P, @Controls.UpdateBufferPoints.YNegSinAbs                   ; переход, если коэффициент неотрицательный, продолжить с YNegSinAbs

                ; вычисление модуля отрицательного коэффициента, байт 80 сохраняет модуль 128
                NEG
                LD E, A
                ; проверка знака координатного смещения перед умножением модулей
YNegSinAbs:     LD A, C
                AND A
                JP P, @Controls.UpdateBufferPoints.YNegSinMultiply              ; переход, если координатное смещение неотрицательное, продолжить с YNegSinMultiply

                ; вычисление модуля отрицательного координатного смещения
                NEG
                LD C, A
                ; вычисление старших семи разрядов произведения последовательным накоплением и сдвигами
YNegSinMultiply:XOR A
                ; проверка разряда 0 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift1               ; переход, если разряд 0 коэффициента нулевой, продолжить с YNegSinShift1 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift1:  RRA
                ; проверка разряда 1 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift2               ; переход, если разряд 1 коэффициента нулевой, продолжить с YNegSinShift2 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift2:  RRA
                ; проверка разряда 2 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift3               ; переход, если разряд 2 коэффициента нулевой, продолжить с YNegSinShift3 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift3:  RRA
                ; проверка разряда 3 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift4               ; переход, если разряд 3 коэффициента нулевой, продолжить с YNegSinShift4 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift4:  RRA
                ; проверка разряда 4 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift5               ; переход, если разряд 4 коэффициента нулевой, продолжить с YNegSinShift5 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift5:  RRA
                ; проверка разряда 5 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift6               ; переход, если разряд 5 коэффициента нулевой, продолжить с YNegSinShift6 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift6:  RRA
                ; проверка разряда 6 модуля коэффициента
                RR E
                JR NC, @Controls.UpdateBufferPoints.YNegSinShift7               ; переход, если разряд 6 коэффициента нулевой, продолжить с YNegSinShift7 без добавления

                ; добавление модуля координаты к частичному произведению
                ADD A, C
YNegSinShift7:  RRA
                ; вычисление исходной единичной поправки, модуль результата равен floor(произведение/128)+1
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UpdateBufferPoints.SumTurnX                     ; переход, если знаковые биты множителей совпадают, продолжить с SumTurnX с положительным результатом

                ; вычисление отрицательного 16-битного результата из округлённого модуля
                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
                ; вычисление нового X как CenterX плюс два знаковых произведения с исходными координатами
SumTurnX:       ADD HL, DE
                LD BC, @BufferPointMotionConst.CenterX
                ADD HL, BC
                ; проверка старшего байта нового X
                LD A, H
                AND A
                JR NZ, @Controls.UpdateBufferPoints.ResetXOut                   ; переход, если старший байт нового X ненулевой, пересоздать точку в ResetXOut

                LD A, L
                ; проверка нижней границы нового X
                CP @BufferPointConst.MinCoordinate
                JR C, @Controls.UpdateBufferPoints.ResetXOut                    ; переход, если новый X меньше MinCoordinate, пересоздать точку в ResetXOut

                ; проверка верхней границы нового X
                CP @BufferPointConst.XUpperLimit
                JR C, @Controls.UpdateBufferPoints.StoreTurnPoint               ; переход, если новый X меньше XUpperLimit, сохранить оба результата в StoreTurnPoint

                ; повторное создание обоих полей после недопустимого X, ранее вычисленный Y не используется
ResetXOut:      EXX
                ; вызов входа, выбранного через XRespawnCall, исходный операнд указывает RespawnPointIndexPos
                CALL @Controls.RespawnPointIndexPos.Entry
                ; сохранение Y и X возвращённой точки и продвижение к следующей записи
                LD (HL), E
                INC L
                LD (HL), D
                INC L
                ; проверка завершения таблицы после выхода X за границы
                LD A, L
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.TurnPoint                    ; переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint

                RET

                ; сохранение отложенного Y и нового X только после успешной проверки обеих координат
StoreTurnPoint: EXX
                LD (HL), #00
                INC L
                LD (HL), A
                INC L
                ; проверка завершения таблицы после сохранения допустимых координат
                LD A, L
                CP @BufferPointConst.ByteCount
                JP C, @Controls.UpdateBufferPoints.TurnPoint                    ; переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint

                ; -----------------------------------------
                RET

                ; -----------------------------------------
                endmodule
                endmodule
