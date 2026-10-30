                module Map
                module DrawMapScene
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [порядок слоёв, ограничители списков, HALT, SP и выходные регистры](../../Docs/MapScene.md)
; -----------------------------------------
; XOR-композиция дуги, шести видов маркеров, цепочки и видимых секторных точек карты
; исходная запись 7, файловые смещения #0000..#0230
; In:
;   AF - A содержит параметр режима закрывающих масок дуги, остальные входные регистры не задают сцену
;   KARTA выбран, код доступен для самомодификации, MapViewState и экранные таблицы подготовлены
;   основной пятибайтовый ключ, MapSelection, SecondaryPointState.Cursor и оба сохранённых списка доступны
;   действуют контракты DrawClippedMapArc, XorMapPointMarker и DrawMapPointChain, отрицательные ограничители достижимы
;   четыре MapSectorTables содержат по 128 слов, bitmap и обычный стек доступны
;   источник пробуждения HALT и сохранение состояния обработчиком обеспечиваются окружением, во время стекового чтения требуется допустимый режим IRQ
; Out:
;   bitmap получает последовательную XOR-композицию дуги, маркеров, необязательной цепочки и всех принятых секторных точек
;   HL - последнее исходное слово Cell11, DE - OriginLow, BC - старший байт 0 и младший (1-Height)&FF
;   AF - Carry сброшен, если последняя точка Cell11 принята, установлен, если отклонена, остальные биты рабочие
;   HL', DE', BC' - при наличии принятой секторной точки содержат F100+X, адрес её экранного байта, B'=X и сохранённый C перед сканером
;   при отсутствии принятых секторных точек HL', DE', BC' сохраняют основные пары непосредственно перед EXX в C150
;   IX сохраняет результат предшествующих обходов и DrawMapPointChain, IY и I инструкции процедуры и вызываемых помощников сохраняют
;   SP восстановлен из операнда C22E, после обычного RET равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap, состояние дуги и изменяемые операнды сканера
; Note:
;   слово по 988E задаёт байтовый радиус через выбор старшего байта либо половины младшего и умножение на три, игровая роль источника ещё неизвестна
;   первый список пропускает FF и заканчивается на 80..FE, второй заканчивается на любом 80..FF, курсор пропускается только при FF
;   дополнительные коды 0 пропускают запись, 1..127 рисуют, 80..FF завершают, отдельной проверки количества нет
;   в исходном снимке отрицательный ограничитель дополнительных кодов принадлежит соседним InterfaceChoices, общая граница не переносится
;   HALT расположен перед секторными точками, после EXX в C150 обратного обмена в конце нет
;   [Подготовка дуги](../../Docs/ArcWorkspace.md), [спрайты](../../Docs/MapMarkerSprites.md) и [общие коды](../../Docs/AuxiliaryMapPoints.md) разобраны отдельно
;   модель 1024 сцен исполняет исходные вызовы и сравнивает весь bitmap, IRQ, нативный запуск и полный игровой цикл этим не доказаны
; -----------------------------------------
                ; сохранение входного параметра режима в операнде первого LD A диспетчера дуги
Entry:          LD (@MapArcPatch.ModeControl), A
                ; чтение слова источника радиуса, его игровое назначение ещё не установлено
                LD HL, (#988E)
                ; проверка старшего байта источника радиуса для выбора масштаба
                LD A, H
                AND A
                JR NZ, @Map.DrawMapScene.ScaleRadius                            ; переход, если старший байт источника ненулевой, умножить именно его на три

                ; расчёт целой половины младшего байта, AND A уже сбросил входной перенос
                LD A, L
                RRA
                ; расчёт Radius как утроенного выбранного байта по модулю 256
ScaleRadius:    LD L, A
                ADD A, A
                ADD A, L
                LD (@MapArcState.Radius), A
                ; чтение раздельных младших и старших пар полных мировых координат
                LD DE, (#9841)
                LD BC, (#983F)
                ; перепаковка WorldX в DE и WorldY в BC без арифметического изменения координат
                LD A, D
                LD D, C
                LD C, A
                ; сборка полного OriginX из низкого и высокого байтов начала карты
                LD A, (@MapViewState.OriginLow)
                LD L, A
                LD A, (@MapViewState.OriginHigh)
                LD H, A
                ; расчёт оборачиваемого WorldX-OriginX с очищенным Carry
                AND A
                EX DE, HL
                SBC HL, DE
                ; чтение только младшего HalfX из изменяемого операнда перед вычитанием центра окна
                LD DE, (#E109)
                LD D, #00
                ; расчёт полного знакового смещения WorldX-OriginX-HalfX
                OR A
                SBC HL, DE
                ; сохранение старшего байта знакового смещения X в A' до вычисления модуля
                LD A, H
                EX AF, AF'
                ; проверка бита 15 смещения X перед двоичным изменением знака
                LD A, H
                AND A
                JP P, @Map.DrawMapScene.AbsXReady                               ; переход, если оборачиваемое смещение X неотрицательно, модуль уже получен

                ; расчёт полного 16-битного модуля отрицательного X, 8000 остаётся 8000
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; сохранение только младшего байта полного модуля X до грубой проверки
AbsXReady:      LD A, L
                LD (@MapArcState.AbsX), A
                ; выбор байтового Radius как полного слова для грубого отбрасывания по X
                LD DE, (@MapArcState.Radius)
                LD D, #00
                ; расчёт absX-Radius после очистки Carry
                OR A
                SBC HL, DE
                JR C, @Map.DrawMapScene.PrepareY                                ; переход, если absX меньше Radius, горизонтальная грубая проверка пройдена

                ; расчёт остатка absX-Radius-HalfX для проверки видимого горизонтального охвата
                LD DE, (#E109)
                LD D, #00
                OR A
                SBC HL, DE
                JR NC, @Map.DrawMapScene.DrawMarkers                            ; переход, если absX не меньше Radius+HalfX, пропустить дугу и продолжить маркеры

                ; сборка полного OriginY перед вычитанием WorldY
PrepareY:       LD A, (#6301)
                LD L, A
                LD A, (#6303)
                LD H, A
                ; расчёт оборачиваемого OriginY-WorldY с очищенным Carry
                OR A
                SBC HL, BC
                ; расчёт OriginY-WorldY+HalfY, направление этой разности противоположно разности X
                LD DE, (#E006)
                LD D, #00
                ADD HL, DE
                ; сохранение старшего байта знаковой разности Y в E перед вычислением модуля
                LD E, H
                LD A, H
                AND A
                JP P, @Map.DrawMapScene.AbsYReady                               ; переход, если оборачиваемая разность Y неотрицательна, модуль уже получен

                ; расчёт полного модуля отрицательной разности Y
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; сохранение младшего байта модуля Y, при раннем отказе по X это поле не обновлялось
AbsYReady:      LD A, L
                LD (@MapArcState.AbsY), A
                ; выбор Radius как полного слова для вертикальной грубой проверки
                LD BC, (@MapArcState.Radius)
                LD B, #00
                ; расчёт absY-Radius с очищенным Carry
                OR A
                SBC HL, BC
                JR C, @Map.DrawMapScene.BuildQuadrant                           ; переход, если absY меньше Radius, подготовить два признака квадранта

                ; расчёт остатка absY-Radius-HalfY перед отказом от дуги
                LD BC, (#E006)
                LD B, #00
                OR A
                SBC HL, BC
                JR NC, @Map.DrawMapScene.DrawMarkers                            ; переход, если absY не меньше Radius+HalfY, пропустить дугу и продолжить маркеры

                ; получение сохранённого знака X и сборка двух признаков неотрицательности разностей
BuildQuadrant:  EX AF, AF'
                LD H, A
                ; обнуление остальных разрядов перед построением QuadrantCode
                XOR A
                ; получение отрицания знака разности Y и перенос его в будущий бит 1
                RLC E
                CCF
                RLA
                ; получение отрицания знака X и включение его в бит 0 кода
                RLC H
                CCF
                RLA
                ; обновление QuadrantCode значением 0..3, исходные старшие разряды этим писателем сбрасываются
                LD (@MapArcState.QuadrantCode), A
                ; передача усечённых AbsX/AbsY, Radius и QuadrantCode диспетчеру отсечения дуги
                CALL @Map.DrawClippedMapArc.Entry
                ; чтение основного ключа для первого, основного маркера после дуги
DrawMarkers:    LD DE, (#983F)
                LD BC, (#9841)
                LD HL, @MapMarkerSprites.Primary.Phase0
                CALL @Map.XorMapPointMarker.Entry
                ; чтение MapSelection для второго, выбранного маркера
                LD DE, (@MapSelection.FirstWord)
                LD BC, (@MapSelection.SecondWord)
                LD HL, @MapMarkerSprites.Selected.Phase0
                CALL @Map.XorMapPointMarker.Entry
                ; чтение курсора второго списка, только FF в первом байте запрещает этот маркер
                LD HL, (@SecondaryPointState.Cursor)
                LD E, (HL)
                ; проверка специального отсутствующего курсора по переполнению FF+1
                INC E
                JR Z, @Map.DrawMapScene.BeginStored                             ; переход, если первый байт курсора равен FF, пропустить его маркер

                DEC E
                INC HL
                LD D, (HL)
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                LD HL, @MapMarkerSprites.Cursor.Phase0
                CALL @Map.XorMapPointMarker.Entry
                ; начало первого сохранённого списка, записи имеют пять байтов
BeginStored:    LD HL, #990A
ReadStored:     LD E, (HL)
                ; проверка пустой записи FF перед проверкой отрицательного ограничителя
                INC E
                JR Z, @Map.DrawMapScene.SkipStored                              ; переход, если первый байт записи равен FF, пропустить пять байтов

                ; восстановление первого байта и проверка диапазона завершения 80..FE
                DEC E
                JP M, @Map.DrawMapScene.BeginAuxiliary                          ; переход, если первый байт записи находится в 80..FE, завершить первый список

                INC HL
                LD D, (HL)
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                INC HL
                PUSH HL
                LD HL, @MapMarkerSprites.Stored.Phase0
                CALL @Map.XorMapPointMarker.Entry
                POP HL
                JP @Map.DrawMapScene.ReadStored

                ; расчёт адреса следующей записи после пустого пятибайтового элемента
SkipStored:     LD BC, #0005
                ADD HL, BC
                JP @Map.DrawMapScene.ReadStored

                ; начало параллельного обхода четырёхбайтовых ключей и однобайтовых кодов
BeginAuxiliary: LD IX, @MapAuxiliaryPoints.Key00
                LD HL, @MapAuxiliaryCodes.State
ReadAuxCode:    LD A, (HL)
                INC HL
                ; проверка целого управляющего кода на ноль и отрицательный диапазон
                AND A
                JR Z, @Map.DrawMapScene.NextAuxiliary                           ; переход, если код равен нулю, пропустить рисование и продвинуть ключ

                JP M, @Map.DrawMapScene.BeginSecondary                          ; переход, если код находится в 80..FF, закончить дополнительные маркеры

                PUSH HL
                ; чтение двух слов ключа, Variant в этих физических записях отсутствует
                LD E, (IX + @FMapCoordinateKey.FirstWord)
                LD D, (IX + @FMapCoordinateKey.FirstWord+1)
                LD C, (IX + @FMapCoordinateKey.SecondWord)
                LD B, (IX + @FMapCoordinateKey.SecondWord+1)
                LD HL, @MapMarkerSprites.ActiveAux.Phase0
                CALL @Map.XorMapPointMarker.Entry
                POP HL
                ; расчёт следующего ключа с шагом четыре без проверки ёмкости таблицы
NextAuxiliary:  LD BC, #0004
                ADD IX, BC
                JP @Map.DrawMapScene.ReadAuxCode

                ; начало второго пятибайтового списка, здесь FF также завершает обход
BeginSecondary: LD HL, #993D
ReadSecondary:  LD A, (HL)
                ; проверка старшего бита первого байта очередного ключа
                OR A
                JP M, @Map.DrawMapScene.DrawChain                               ; переход, если первый байт находится в 80..FF, закончить второй список

                LD E, A
                INC HL
                LD D, (HL)
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                INC HL
                PUSH HL
                LD HL, @MapMarkerSprites.Secondary.Phase0
                CALL @Map.XorMapPointMarker.Entry
                POP HL
                JP @Map.DrawMapScene.ReadSecondary

                ; подготовка второго списка и сохранённого порядка для построения цепочки
DrawChain:      LD HL, #993D
                LD DE, #9970
                ; проверка наличия хотя бы первой записи второго списка
                BIT 7, (HL)
                CALL Z, @Map.DrawMapPointChain.Entry                            ; вызов, если первый байт второго списка меньше 80, построить цепочку
                ; ожидание внешнего пробуждения перед отдельным слоем секторных пикселей
                HALT
                ; сохранение обычного SP в операнде восстановления перед чтением таблиц через POP
                LD (@MapScenePatch.SavedStack), SP
                ; обмен наборами регистров, обратного EXX после всего сканера нет
                EXX
                ; чтение младших координат начала для четырёх направлений фильтрации
                LD DE, (@MapViewState.OriginLow)
                ; обновление двух прямых порогов X значением Width
                LD A, (@MapViewState.Width)
                LD (@MapScenePatch.WidthFirst), A
                LD (@MapScenePatch.WidthSecond), A
                ; расчёт обратного порога X как (1-Width)&FF
                DEC A
                NEG
                LD (@MapScenePatch.InverseWidthB), A
                LD (@MapScenePatch.InverseWidthA), A
                ; обновление прямого порога Y в загружаемом младшем байте BC
                LD A, (@MapViewState.Height)
                LD (@MapScenePatch.HeightPositive), A
                ; расчёт обратного порога Y как (1-Height)&FF
                DEC A
                NEG
                LD (@MapScenePatch.HeightNegative), A
                LD BC, #8070
                ; начало стекового просмотра перед Cell00, первое POP пропускает предшествующее слово масок
                LD SP, #F1FE
                POP HL
                ; чтение очередной пары X,Y из секторной страницы через POP, всего 128 слов
Scan00:         POP HL
                LD A, H
                ; расчёт Y-Origin с сохранением байтового займа
                SUB D
                JP C, @Map.DrawMapScene.Next00                                  ; переход, если разность Y дала заём, пропустить точку

                ; проверка прямого порога размера по Y
                CP C
                JP NC, @Map.DrawMapScene.Next00                                 ; переход, если прямая разность Y не меньше размера, пропустить точку

                EX AF, AF'
                LD A, L
                ; расчёт X-Origin с сохранением байтового займа
                SUB E
                JP C, @Map.DrawMapScene.Next00                                  ; переход, если разность X дала заём, пропустить точку

                ; проверка прямого порога размера по X
                CP #D0
                JP NC, @Map.DrawMapScene.Next00                                 ; переход, если прямая разность X не меньше размера, пропустить точку

                EXX
                LD B, A
                EX AF, AF'
                LD L, A
                LD H, #EE
                ; расчёт экранного адреса из RowHigh, RowLow и ColumnByte перед XOR одноразрядной PixelMask
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, B
                ADD A, (HL)
                LD E, A
                INC H
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                EXX
Next00:         DJNZ @Map.DrawMapScene.Scan00

                LD B, #80
                ; чтение очередной пары X,Y из секторной страницы через POP, всего 128 слов
Scan10:         POP HL
                LD A, H
                ; расчёт Y-Origin с сохранением байтового займа
                SUB D
                JP C, @Map.DrawMapScene.Next10                                  ; переход, если разность Y дала заём, пропустить точку

                ; проверка прямого порога размера по Y
                CP C
                JP NC, @Map.DrawMapScene.Next10                                 ; переход, если прямая разность Y не меньше размера, пропустить точку

                EX AF, AF'
                LD A, E
                ; расчёт Origin-X с сохранением байтового займа
                SUB L
                JP C, @Map.DrawMapScene.Next10                                  ; переход, если разность X дала заём, пропустить точку

                ; проверка обратного порога (1-размер)&FF по X
                CP #31
                JP C, @Map.DrawMapScene.Next10                                  ; переход, если обратная разность X меньше порога (1-размер)&FF, пропустить точку

                EXX
                NEG
                LD B, A
                EX AF, AF'
                LD L, A
                LD H, #EE
                ; расчёт экранного адреса из RowHigh, RowLow и ColumnByte перед XOR одноразрядной PixelMask
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, B
                ADD A, (HL)
                LD E, A
                INC H
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                EXX
Next10:         DJNZ @Map.DrawMapScene.Scan10

                LD BC, #8091
                ; чтение очередной пары X,Y из секторной страницы через POP, всего 128 слов
Scan01:         POP HL
                LD A, D
                ; расчёт Origin-Y с сохранением байтового займа
                SUB H
                JP C, @Map.DrawMapScene.Next01                                  ; переход, если разность Y дала заём, пропустить точку

                ; проверка обратного порога (1-размер)&FF по Y
                CP C
                JP C, @Map.DrawMapScene.Next01                                  ; переход, если обратная разность Y меньше порога (1-размер)&FF, пропустить точку

                EX AF, AF'
                LD A, L
                ; расчёт X-Origin с сохранением байтового займа
                SUB E
                JP C, @Map.DrawMapScene.Next01                                  ; переход, если разность X дала заём, пропустить точку

                ; проверка прямого порога размера по X
                CP #D0
                JP NC, @Map.DrawMapScene.Next01                                 ; переход, если прямая разность X не меньше размера, пропустить точку

                EXX
                LD B, A
                EX AF, AF'
                NEG
                LD L, A
                LD H, #EE
                ; расчёт экранного адреса из RowHigh, RowLow и ColumnByte перед XOR одноразрядной PixelMask
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, B
                ADD A, (HL)
                LD E, A
                INC H
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                EXX
Next01:         DJNZ @Map.DrawMapScene.Scan01

                LD B, #80
                ; чтение очередной пары X,Y из секторной страницы через POP, всего 128 слов
Scan11:         POP HL
                LD A, D
                ; расчёт Origin-Y с сохранением байтового займа
                SUB H
                JP C, @Map.DrawMapScene.Next11                                  ; переход, если разность Y дала заём, пропустить точку

                ; проверка обратного порога (1-размер)&FF по Y
                CP C
                JP C, @Map.DrawMapScene.Next11                                  ; переход, если обратная разность Y меньше порога (1-размер)&FF, пропустить точку

                EX AF, AF'
                LD A, E
                ; расчёт Origin-X с сохранением байтового займа
                SUB L
                JP C, @Map.DrawMapScene.Next11                                  ; переход, если разность X дала заём, пропустить точку

                ; проверка обратного порога (1-размер)&FF по X
                CP #31
                JP C, @Map.DrawMapScene.Next11                                  ; переход, если обратная разность X меньше порога (1-размер)&FF, пропустить точку

                EXX
                NEG
                LD B, A
                EX AF, AF'
                NEG
                LD L, A
                LD H, #EE
                ; расчёт экранного адреса из RowHigh, RowLow и ColumnByte перед XOR одноразрядной PixelMask
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, B
                ADD A, (HL)
                LD E, A
                INC H
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                EXX
Next11:         DJNZ @Map.DrawMapScene.Scan11

                ; восстановление обычного стека без обратного обмена основного и альтернативного набора
                LD SP, #0000
                RET

                endmodule
                endmodule
