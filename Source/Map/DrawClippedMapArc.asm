                module Map
                module DrawClippedMapArc
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [четыре положения центра, квадраты, заём корня и проверка всего bitmap](../../Docs/ArcDispatcher.md)
; -----------------------------------------
; Выбор отсечённых проходов дуги по положению центра и пересечениям границ окна
; исходная запись 7, файловые смещения #1FC3..#2207
; In:
;   MapArcState.AbsY и AbsX содержат байтовые модули смещений центра, Radius содержит радиус, KARTA выбран
;   QuadrantCode - бит 0 означает неотрицательность X, бит 1 неотрицательность обратной разности Y, старшие биты этим диспетчером не проверяются
;   параметр в операнде MapArcPatch.ModeControl выбирает битом 0 четыре условия закрывающих масок
;   SetupMapRasterWindow выполнен, операнды сравнений, копии половин, таблицы и границы строк согласованы
;   действуют требования табличных подготовок, строковых поисков и RasterizeArcEdges, обычный стек и bitmap доступны
; Out:
;   до проверки радиуса записаны четыре кода JR, бит 0 параметра даёт 38 при единице и 30 при нуле
;   при Radius<9 рисования нет, HL, DE, BC и альтернативные пары сохранены, AF - A=Radius, F от CP Radius,9
;   иначе OffsetY/OffsetX сначала получают AbsY/AbsX, вычислены байтовые CenterX и RowY по двум признакам квадранта
;   выбраны один или два начальных края, одна вертикальная половина либо два прохода по принадлежности центра окну и сравнениям квадратов
;   на ветвях вне Y смещения корректируются на HalfY, на ветвях вне обеих осей сначала корректируются обе координаты
;   StartY и SqrtTarget обновляются только на ветвях вычисления корня, RowY может быть заменён граничной строкой на двухкраевом Y-входе
;   bitmap инвертирован исходными проходами, LeftMask, RasterDown и RasterStack изменены фактически вызванными помощниками
;   для Radius>=9 HL, DE, BC, AF и альтернативные регистры рабочие, флаги относятся к последнему сравнению либо сохранённому AF подготовки
;   IX, IY, I и IFF сами инструкции сохраняют, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', рабочее состояние дуги, bitmap и четыре кода JR
; Note:
;   основные и альтернативные входные регистры геометрию не задают, параметры читаются из исходных полей и операндов
;   LookupSquare сохраняет Carry, ветви центра внутри X и вне Y передают в корень вычитания Y дополнительную единицу
;   касание Radius=внешнее смещение Y может дать разность FFFF и корень FF, особенность не исправляется геометрическим ограничением нулём
;   INC только младших счётчиков и возврат с EXX по нулевому C' сохраняются по договору RasterizeArcEdges
;   условные вызовы противоположных направлений опираются на сохранение полного AF обёртками, каждая пара выполняет только выбранное направление
;   [Ядро](../../Docs/ArcKernel.md), [физическое состояние](../../Docs/ArcWorkspace.md) и [фазы операндов](../../Docs/MapRuntimeProfiles.md) описаны отдельно
;   модель проверила четыре выровненных окна и все радиусы основного профиля, произвольные окна, IRQ, сборка и нативный запуск этим не доказаны
; -----------------------------------------
                ; чтение изменяемого параметра, бит 0 выбирает условие четырёх закрывающих масок
Entry:          LD A, #00
                ; перенос младшего бита параметра режима в Carry, остальные биты не управляют выбором
                RRA
                ; подготовка кода JR C для поиска установленного граничного бита
                LD A, @MapArcConst.TestSetBit
                JR C, @Map.DrawClippedMapArc.StoreTailMode                      ; переход, если бит 0 параметра установлен, записать четыре кода JR C

                ; выбор кода JR NC при нулевом бите параметра
                LD A, @MapArcConst.TestClearBit
                ; обновление четырёх кодов переходов до любой проверки радиуса
StoreTailMode:  LD (@MapArcPatch.LowTailJump), A
                LD (@MapArcPatch.HighTailJump), A
                LD (@MapArcPatch.RightLowJump), A
                LD (@MapArcPatch.LeftHighJump), A
                ; чтение Radius для проверки минимального обрабатываемого радиуса
                LD A, (@MapArcState.Radius)
                ; проверка порога Radius=9, режим переходов уже записан
                CP @MapArcConst.MinRadius
                RET C                                                           ; выход, если Radius меньше 9, рисование не начинается, выбранный режим уже сохранён

                ; копирование двух абсолютных байтовых смещений в рабочие OffsetY и OffsetX
                LD BC, (@MapArcState.AbsY)
                LD (@MapArcState.OffsetY), BC
                ; чтение Radius и QuadrantCode как соседнего слова перед расчётом центра
                LD DE, (@MapArcState.QuadrantCode)
                ; расчёт RowY как HalfY-AbsY для верхней половины либо HalfY+AbsY для нижней
                LD A, (@MapArcState.HalfY)
                BIT @MapArcBit.NonnegativeY, E
                JR NZ, @Map.DrawClippedMapArc.FinishCenterY                     ; переход, если бит 1 QuadrantCode установлен, вычесть AbsY из HalfY

                ADD A, C
                ADD A, C
FinishCenterY:  SUB C
                LD (@MapArcState.RowY), A
                ; расчёт CenterX как HalfX+AbsX для правой половины либо HalfX-AbsX для левой
                LD A, (@MapArcState.ReferenceX)
                BIT @MapArcBit.NonnegativeX, E
                JR Z, @Map.DrawClippedMapArc.FinishCenterX                      ; переход, если бит 0 QuadrantCode сброшен, вычесть AbsX из HalfX

                ADD A, B
                ADD A, B
FinishCenterX:  SUB B
                LD (@MapArcState.CenterX), A
                ; проверка AbsY относительно HalfY, её Carry сохраняется в альтернативном AF
                LD A, C
                CP #00
                EX AF, AF'
                ; проверка AbsX относительно HalfX для первого разделения положения центра
                LD A, B
                CP #00
                JP NC, @Map.DrawClippedMapArc.OutsideX                          ; переход, если AbsX не меньше HalfX, центр находится вне X

                ; возврат результата сравнения Y после успешной проверки внутреннего X
                EX AF, AF'
                JP NC, @Map.DrawClippedMapArc.OutsideY                          ; переход, если AbsY не меньше HalfY, центр находится вне Y при внутреннем X

                ; расчёт Radius+AbsX, перенос исключает укладывание обеих сторон в меньшую половину окна
                LD A, B
                ADD A, D
                JR C, @Map.DrawClippedMapArc.TestFarX                           ; переход, если Radius+AbsX переполнил байт, проверить дальнюю X-границу

                ; проверка полного горизонтального размещения относительно HalfX
                CP #00
                JP C, @Map.DrawClippedMapArc.FullSpanPair                       ; переход, если Radius+AbsX меньше HalfX, оба горизонтальных края помещаются в окне

                ; расчёт Radius-AbsX для различения одной либо двух пересечённых X-границ
TestFarX:       LD A, D
                SUB B
                JP C, @Map.DrawClippedArcPair.Entry                             ; переход, если Radius меньше AbsX, дальняя X-граница не пересекается

                ; проверка достижения дальней X-границы по остатку Radius-AbsX
                CP #00
                JP C, @Map.DrawClippedArcPair.Entry                             ; переход, если Radius-AbsX меньше HalfX, выбрать одну боковую границу

                ; расчёт предела AbsX-HalfX+1 для обхода за двумя боковыми границами
                LD A, (@MapArcState.HalfXLimit)
                SUB B
                NEG
                INC A
                ; сохранение предела в A' перед вычислением вертикального отступа от центра
ClipBothX:      EX AF, AF'
                ; расчёт аргумента дальней X-границы как HalfX+AbsX
                LD A, (@MapArcState.HalfXSquare)
                ADD A, B
                ; расчёт корня из Radius^2-дальняяX^2, ADD уже определил входной Carry
                CALL @Map.SqrtSquareDiff.Entry
                ; сохранение вертикального отступа и подготовка числа шагов от исходной RowY вверх
                LD (@MapArcState.StartY), A
                LD B, A
                LD A, (@MapArcState.RowY)
                ; поиск строки верхней части за пределом двух боковых пересечений
                CALL @Map.SeekRasterRowUp.Entry
                ; подготовка счётчиков корня и двух крайних колонок для отсечённого входа вверх
                CALL @Map.LoadClippedArcInputs.Entry
                CALL @Map.ResetRasterSpanEdges.Entry
                ; проверка X-половины для выбора исходного одиночного края
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeX, A
                CALL Z, @Map.DrawArcRightUp.Entry                               ; вызов, если бит 0 QuadrantCode сброшен, начать правый край вверх
                CALL NZ, @Map.DrawArcLeftUp.Entry                               ; вызов, если бит 0 QuadrantCode установлен, начать левый край вверх
                ; поиск симметричной нижней части от исходной RowY по сохранённому корню
                LD A, (@MapArcState.StartY)
                LD B, A
                LD A, (@MapArcState.RowY)
                CALL @Map.SeekRasterRowDown.Entry
                ; повторная подготовка счётчиков и крайних колонок перед проходом вниз
                CALL @Map.LoadClippedArcInputs.Entry
                CALL @Map.ResetRasterSpanEdges.Entry
                ; проверка X-половины перед нижним одиночным проходом
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeX, A
                CALL Z, @Map.DrawArcRightDown.Entry                             ; вызов, если бит 0 QuadrantCode сброшен, начать правый край вниз
                CALL NZ, @Map.DrawArcLeftDown.Entry                             ; вызов, если бит 0 QuadrantCode установлен, начать левый край вниз
                RET

                ; возврат сохранённого сравнения Y для центра, уже лежащего вне X
OutsideX:       EX AF, AF'
                JP NC, @Map.DrawClippedMapArc.OutsideXY                         ; переход, если AbsY не меньше HalfY, центр лежит вне обеих осей

                ; расчёт внешнего расстояния X как AbsX-HalfX
                LD A, B
                SUB #00
                LD B, A
                ; проверка достижения ближайшей границы радиусом, касание тоже завершается
                LD A, D
                SUB B
                RET C                                                           ; выход, если Radius меньше внешнего расстояния X, дуга не достигает окна

                RET Z                                                           ; выход, если Radius равен внешнему расстоянию X, касание не рисуется

                ; расчёт остатка Radius-внешнийX-Width для проверки дальней границы
                SUB #F0
                JP NC, @Map.DrawClippedMapArc.RestoreWideX                      ; переход, если Radius-внешнийX не меньше Width, достигнута дальняя X-граница

                ; восстановление полного AbsX в OffsetX после проверки внешнего расстояния
                LD A, B
                ADD A, #00
                LD (@MapArcState.OffsetX), A
                LD B, A
                ; подготовка нулевого A-предела для двух проходов одиночного края
                XOR A
                JP @Map.DrawClippedArcPair.UseLimit

                ; восстановление AbsX и нулевого предела перед двумя отсечёнными X-частями
RestoreWideX:   LD A, B
                ADD A, #00
                LD B, A
                LD (@MapArcState.OffsetX), A
                XOR A
                JP @Map.DrawClippedMapArc.ClipBothX

                ; расчёт внешнего Y как AbsY-HalfY с сохранением скорректированного OffsetY
OutsideY:       LD A, C
                SUB #00
                LD C, A
                LD (@MapArcState.OffsetY), A
                ; проверка достижения горизонтальной границы по Radius-внешнийY
                LD A, D
                SUB C
                RET C                                                           ; выход, если Radius меньше внешнего расстояния Y, дуга не достигает окна

                ; расчёт полного квадрата Radius через разнесённую исходную таблицу
                LD A, D
                CALL @Map.LookupSquare.Entry
                LD H, D
                LD L, E
                ; расчёт остатка Radius^2-внешнийY^2 с сохранённым Carry таблицы
                LD A, C
                CALL @Map.LookupSquare.Entry
                SBC HL, DE
                ; расчёт квадрата расстояния ближней X-границы HalfX-AbsX
                LD A, (@MapArcState.HalfXSquare)
                SUB B
                CALL @Map.LookupSquare.Entry
                ; сравнение горизонтального охвата на Y-границе с ближней X-границей
                SBC HL, DE
                JP C, @Map.DrawClippedMapArc.BothAtYEdge                        ; переход, если Radius^2-внешнийY^2 меньше (HalfX-AbsX)^2, на Y-границе помещаются два края

                ; восстановление Radius^2-внешнийY^2 перед сравнением с дальней X-границей
                ADD HL, DE
                ; расчёт квадрата HalfX+AbsX и сравнение с тем же горизонтальным охватом
                LD A, (@MapArcState.HalfXSquare)
                ADD A, B
                CALL @Map.LookupSquare.Entry
                SBC HL, DE
                JP NC, @Map.DrawClippedMapArc.FarAtYEdge                        ; переход, если Radius^2-внешнийY^2 не меньше (HalfX+AbsX)^2, нужен участок за дальней X-границей

                ; расчёт предела AbsX-HalfX+3 из изменяемого HalfX-2 с последующим INC
                LD A, B
                SUB #00
                INC A
                ; сохранение предела в A', основной Carry теперь взят из исходного сравнения X с HalfX
StartYOneEdge:  EX AF, AF'
                ; возврат Radius и QuadrantCode перед корнем вертикального отсечения
                LD DE, (@MapArcState.QuadrantCode)
                ; расчёт корня Radius^2-внешнийY^2-Carry, внутри X заём равен единице, вне X нулю
                LD A, C
                CALL @Map.SqrtSquareDiff.Entry
                LD (@MapArcState.StartY), A
                ; подготовка начальных E'=внешнийY и C'=-StartY modulo 256
                LD A, C
                EXX
                LD E, A
                LD A, (@MapArcState.StartY)
                NEG
                LD C, A
                EXX
                ; проверка X-половины для выбора первого края на горизонтальной границе
                BIT @MapArcBit.NonnegativeX, E
                JR Z, @Map.DrawClippedMapArc.RightAtYEdge                       ; переход, если бит 0 QuadrantCode сброшен, выбрать правый начальный край

                ; расчёт левого X как HalfX+AbsX-StartY-1, CPL сохраняет исходный дополнительный минус один
                LD A, (@MapArcState.StartY)
                CPL
                ADD A, #00
                ADD A, B
                ; выбор верхней строки 0 либо нижней MaxY по признаку обратного Y
                LD C, #00
                BIT @MapArcBit.NonnegativeY, E
                JR NZ, @Map.DrawClippedMapArc.PrepareClipLeft                   ; переход, если бит 1 QuadrantCode установлен, оставить верхнюю строку 0

                LD C, #00
                ; подготовка активного левого пикселя и фиксированной правой колонки окна
PrepareClipLeft:CALL @Map.PrepareLeftRasterPoint.Entry
                ; замена правого младшего адреса колонкой ColumnByte[MaxX] и маской 01
                LD A, E
                AND #E0
                OR #1E
                LD L, A
                LD C, #01
                ; выбор направления от граничной строки к видимой области по признаку Y
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeY, A
                CALL NZ, @Map.DrawArcLeftDown.Entry                             ; вызов, если бит 1 QuadrantCode установлен, начать левый край от верхней границы вниз
                CALL Z, @Map.DrawArcLeftUp.Entry                                ; вызов, если бит 1 QuadrantCode сброшен, начать левый край от нижней границы вверх
                RET

                ; расчёт правого X как StartY+HalfX-AbsX без дополнительного минуса левой ветви
RightAtYEdge:   LD A, (@MapArcState.StartY)
                ADD A, #00
                SUB B
                ; выбор верхней либо нижней строки для правого одиночного края
                LD C, #00
                BIT @MapArcBit.NonnegativeY, E
                JR NZ, @Map.DrawClippedMapArc.PrepClipRight                     ; переход, если бит 1 QuadrantCode установлен, оставить верхнюю строку 0

                LD C, #00
                ; подготовка правого пикселя, помощник сохраняет входной B в LeftMask
PrepClipRight:  CALL @Map.PrepareRightRasterPoint.Entry
                ; замена левого младшего адреса колонкой ColumnByte[0] и маской 80
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD B, #80
                ; выбор направления от горизонтальной границы для правого края
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeY, A
                CALL NZ, @Map.DrawArcRightDown.Entry                            ; вызов, если бит 1 QuadrantCode установлен, начать правый край от верхней границы вниз
                CALL Z, @Map.DrawArcRightUp.Entry                               ; вызов, если бит 1 QuadrantCode сброшен, начать правый край от нижней границы вверх
                RET

                ; подготовка двух краёв внутри X, заём предыдущего SBC остаётся входом корня
BothAtYEdge:    LD DE, (@MapArcState.QuadrantCode)
                ; расчёт корня Radius^2-внешнийY^2-1, при точном касании разность оборачивается в FFFF
                LD A, C
                CALL @Map.SqrtSquareDiff.Entry
                LD (@MapArcState.StartY), A
                ; подготовка байтовых счётчиков из внешнего Y и отрицательного корня
                LD A, C
                EXX
                LD E, A
                LD A, (@MapArcState.StartY)
                NEG
                LD C, A
                EXX
                ; выбор и сохранение граничной RowY, ноль для центра сверху либо MaxY для центра снизу
                XOR A
                BIT @MapArcBit.NonnegativeY, E
                JR NZ, @Map.DrawClippedMapArc.SetYBoundary                      ; переход, если бит 1 QuadrantCode установлен, сохранить RowY=0

                LD A, (@MapArcState.MaxY)
SetYBoundary:   LD (@MapArcState.RowY), A
                LD C, A
                ; расчёт левого X как CenterX-StartY с исходным байтовым оборачиванием
                LD A, (@MapArcState.StartY)
                LD L, A
                LD A, (@MapArcState.CenterX)
                SUB L
                CALL @Map.PrepareLeftRasterPoint.Entry
                ; расчёт правого X как CenterX+StartY на той же граничной строке
                LD A, (@MapArcState.RowY)
                LD C, A
                LD A, (@MapArcState.StartY)
                LD L, A
                LD A, (@MapArcState.CenterX)
                ADD A, L
                CALL @Map.PrepareRightRasterPoint.Entry
                ; выбор движения обоих краёв внутрь окна по признаку Y
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeY, A
                CALL NZ, @Map.DrawArcBothDown.Entry                             ; вызов, если бит 1 QuadrantCode установлен, начать оба края от верхней границы вниз
                CALL Z, @Map.DrawArcBothUp.Entry                                ; вызов, если бит 1 QuadrantCode сброшен, начать оба края от нижней границы вверх
                RET

                ; расчёт предела AbsX-HalfX+3 перед дальней X-границей
FarAtYEdge:     LD A, B
                SUB #00
                INC A
                ; сохранение предела и восстановление Radius перед корнем дальней X-границы
StartYFarEdge:  EX AF, AF'
                LD DE, (@MapArcState.QuadrantCode)
                ; расчёт корня Radius^2-(HalfX+AbsX)^2 с Carry от байтового сложения аргумента
                LD A, (@MapArcState.HalfXSquare)
                ADD A, B
                CALL @Map.SqrtSquareDiff.Entry
                ; сохранение корня и расчёт числа строк root-внешнийY до первого видимого участка
                LD (@MapArcState.StartY), A
                SUB C
                LD B, A
                ; проверка верхней либо нижней половины для выбора начальной горизонтальной границы
                BIT @MapArcBit.NonnegativeY, E
                JR Z, @Map.DrawClippedMapArc.FromBottomEdge                     ; переход, если бит 1 QuadrantCode сброшен, начать от нижней границы

                ; поиск от верхней строки вниз на рассчитанное число шагов
                XOR A
                CALL @Map.SeekRasterRowDown.Entry
                ; подготовка счётчиков farX и root и крайних колонок перед нижним направлением
                CALL @Map.LoadClippedArcInputs.Entry
                CALL @Map.ResetRasterSpanEdges.Entry
                ; выбор активного края по признаку X после поиска строки
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeX, A
                CALL Z, @Map.DrawArcRightDown.Entry                             ; вызов, если бит 0 QuadrantCode сброшен, начать правый край вниз
                CALL NZ, @Map.DrawArcLeftDown.Entry                             ; вызов, если бит 0 QuadrantCode установлен, начать левый край вниз
                RET

                ; поиск от нижней строки MaxY вверх на рассчитанное число шагов
FromBottomEdge: LD A, (@MapArcState.MaxY)
                CALL @Map.SeekRasterRowUp.Entry
                ; подготовка счётчиков и колонок для движения от нижней границы вверх
                CALL @Map.LoadClippedArcInputs.Entry
                CALL @Map.ResetRasterSpanEdges.Entry
                ; выбор активного края на верхнем направлении
                LD A, (@MapArcState.QuadrantCode)
                BIT @MapArcBit.NonnegativeX, A
                CALL Z, @Map.DrawArcRightUp.Entry                               ; вызов, если бит 0 QuadrantCode сброшен, начать правый край вверх
                CALL NZ, @Map.DrawArcLeftUp.Entry                               ; вызов, если бит 0 QuadrantCode установлен, начать левый край вверх
                RET

                ; расчёт внешних расстояний X и Y, центр лежит вне обеих осей
OutsideXY:      LD A, B
                SUB #00
                LD B, A
                LD A, C
                SUB #00
                LD C, A
                ; обновление обоих скорректированных Offset до проверок достижимости угла
                LD (@MapArcState.OffsetY), BC
                ; расчёт остатка Radius^2-внешнийY^2 для проверки угла
                LD A, D
                CALL @Map.LookupSquare.Entry
                LD H, D
                LD L, E
                LD A, C
                CALL @Map.LookupSquare.Entry
                SBC HL, DE
                RET C                                                           ; выход, если Radius^2 меньше внешнегоY^2, горизонтальная граница недостижима

                ; сравнение оставшегося квадрата с внешнимX^2, угол должен попадать в радиус
                LD A, B
                CALL @Map.LookupSquare.Entry
                SBC HL, DE
                RET C                                                           ; выход, если Radius^2-внешнийY^2 меньше внешнегоX^2, угол окна не достигается

                ; восстановление вертикального остатка и расчёт расстояния до дальней границы внешнийX+Width
                ADD HL, DE
                LD A, B
                ADD A, #F8
                JR C, @Map.DrawClippedMapArc.RestoreNearX                       ; переход, если внешнийX+Width переполнил байт, дальняя граница недостижима этим радиусом

                ; сравнение вертикального остатка с квадратом дальней X-границы при отсутствии байтового переноса
                CALL @Map.LookupSquare.Entry
                SBC HL, DE
                JP NC, @Map.DrawClippedMapArc.RestoreFarX                       ; переход, если Radius^2-внешнийY^2 не меньше (внешнийX+Width)^2, выбрать дальнейший вертикальный участок

                ; восстановление полного AbsX, нулевой предел выбирает одиночный вход на Y-границе
RestoreNearX:   LD A, B
                ADD A, #00
                LD (@MapArcState.OffsetX), A
                LD B, A
                XOR A
                JP @Map.DrawClippedMapArc.StartYOneEdge

                ; восстановление полного AbsX, нулевой предел выбирает участок за дальней X-границей
RestoreFarX:    LD A, B
                ADD A, #00
                LD B, A
                LD (@MapArcState.OffsetX), A
                XOR A
                JP @Map.DrawClippedMapArc.StartYFarEdge

                ; подготовка полного симметричного пролёта и проход вверх
FullSpanPair:   CALL @Map.PrepareArcFullSpan.Entry
                CALL @Map.DrawArcBothUp.Entry
                ; повторная подготовка исходного симметричного пролёта для завершающего прохода вниз
                CALL @Map.PrepareArcFullSpan.Entry
                JP @Map.DrawArcBothDown.Entry

                endmodule
                endmodule
