                module Station
                module DrawMapPanelContents
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [размеры внутренней области, три запроса, paging и два уровня проверки](../../Docs/MapPanel.md)
; -----------------------------------------
; Настройка размеров карты, условное построение таблиц и банковое рисование C000
; исходная запись 4, файловые смещения #1004..#1053
; In:
;   MapPanelState.ItemIndex задаёт индекс доступного FInterfaceItem, банк станции 0 выбран, paging доступен
;   TextWindow соответствует этой панели, для обычного успешного пути X+Width<=32, Y+Height<=24, X,Y неотрицательны, Width и Height не меньше четырёх
;   ScreenRequest, SectorRequest и ClipRequest проверяются целиком, при нуле соответствующие таблицы и параметры уже согласованы с рисуемой областью
;   действуют договоры BuildMapScreenTables, BuildMapQuadrantTables, SetupMapRasterWindow и DrawMapScene для реально вызываемых входов
;   станционные экранные таблицы готовы, все списки и исходные данные C000 доступны, HALT пробуждается по договору сцены
;   прерывания и размещение SP удовлетворяют договорам вложенных проходов
; Out:
;   при Carry=0 от CheckItemRect возврат выполнен до записи размеров, запросы и страница не меняются, HL, DE, AF соответствуют CheckItemRect, BC сохранён
;   после принятой обычной геометрии MapViewState.Width=8*(Width-2), Height=8*(Height-3), мировое начало не изменено
;   ScreenRequest!=0 строит EE..F1 для начала элемента X*8,Y*8 с внутренними отступами 8 и 16
;   SectorRequest!=0 строит четыре страницы F2..F5 по OriginHigh, ClipRequest!=0 задаёт минимум X,Y=0 и максимумы TextWindow.Width-13,Height-14
;   вызов DrawMapScene получает весь байт StationRaster.FillMode, его изменяемый ModeControl обновляется исходным C000
;   после полного рисунка выбран банк станции 0 с ROM 1 и сохранёнными старшими битами CurrentPage, ScreenRequest=0, ClipRequest=0
;   SectorRequest сохраняет прежний полный байт, в том числе 80 либо FF, его обнуления в этом хвосте нет
;   HL, DE, BC и альтернативные пары соответствуют результату DrawMapScene после реально выполненных подготовок, AF=0044
;   IX рабочий согласно C000, IY, I и IFF сохраняются инструкциями при договоре пробуждения, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, viewport, таблицы, параметры отсечения, код и bitmap
; Note:
;   масштабирование начала и размеров выполнено целыми словами, для обычных допустимых размеров младшие байты не создают дополнительного переноса в Y
;   минимумы отсечения равны нулю независимо от положения панели, её экранное смещение уже включено в адресные таблицы
;   два одноразовых запроса сбрасываются только после возврата C000, ожидание HALT до этого места не объявлено завершённым рисунком
;   [Экранные таблицы](../../Docs/MapScreenTables.md) и [секторные таблицы](../../Docs/MapSectorTables.md) имеют отдельные проверенные договоры
;   модель обёртки проверяет пустые сохранённые списки, нулевой источник радиуса и маркеры за пределами окна, полные дуги и непустые сцены проверены отдельными моделями C000
; -----------------------------------------
                ; чтение изменяемого индекса записи основной панели карты
Entry:          LD HL, (@MapPanelState.ItemIndex)
                ; проверка начала, экранных сумм и минимального размера через CheckItemRect
                CALL @Station.CheckItemRect.Entry
                RET NC                                                          ; выход, если CheckItemRect не установил Carry, размеры и запросы не менять

                ; расчёт внутренних размеров в знакоместах, Width-2 и Height-3
                DEC L
                DEC H
                DEC L
                DEC H
                DEC H
                ; масштабирование упакованных внутренних размеров в восемь раз целым словом
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ; перенос размеров в DE и масштабирование исходного X,Y панели в пиксели
                EX DE, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                ; обновление соседних Width и Height существующего viewport карты
                LD (@MapViewState.Width), HL
                ; выбор KARTA с сохранением текущего бита отображаемого экрана
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; чтение полного запроса построения экранных адресов и масок
                LD A, #00
                AND A
                CALL NZ, @Map.BuildMapScreenTables.Entry                        ; вызов, если ScreenRequest ненулевой, построить четыре страницы экранных таблиц
                ; чтение полного запроса построения четырёх мировых секторов
                LD A, #00
                AND A
                CALL NZ, @Map.BuildMapQuadrantTables.Entry                      ; вызов, если SectorRequest ненулевой, обновить четыре секторные страницы
                ; подготовка нулевых минимумов X,Y для локального отсечения карты
                LD DE, @MapClipConst.MinCoordinate
                ; расчёт включённого MaxX как TextWindow.Width-13
                LD A, (@TextWindow.Width)
                SUB @MapPanelConst.ClipWidthTrim
                LD L, A
                ; расчёт включённого MaxY как TextWindow.Height-14
                LD A, (@TextWindow.Height)
                SUB @MapPanelConst.ClipHeightTrim
                LD H, A
                ; чтение полного запроса настройки границ, половин и операндов геометрии
                LD A, #00
                AND A
                CALL NZ, @Map.SetupMapRasterWindow.Entry                        ; вызов, если ClipRequest ненулевой, настроить отсечение и растровые границы
                ; передача полного FillMode в диспетчер режима дуги через C000
                LD A, (@StationRaster.FillMode)
                ; рисование всей композиции карты с её собственным HALT и стековым просмотром секторов
                CALL @Map.DrawMapScene.Entry
                ; возврат банка станции с сохранением текущего показа базового либо теневого экрана
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; сброс только одноразовых запросов экранных таблиц и отсечения после завершённого рисунка
                XOR A
                LD (@MapPanelState.ScreenRequest), A
                LD (@MapPanelState.ClipRequest), A
                RET

                endmodule
                endmodule
