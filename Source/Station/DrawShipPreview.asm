                module Station
                module DrawShipPreview
                ; Документация [станционная цепочка, геометрия и настоящее IM2-пробуждение](../../Docs/ShipPreviewCallbacks.md)
                ; -----------------------------------------
                ; Рамка корабельного просмотра, выбор периодического callback, настройка банка 4 и первый кадр
                ; исходная запись 4, файловые смещения #0B23..#0B77
                ; In:
                ;   HL заменяется изменяемым ShipPanelState.PreviewIndex, DE и BC исходный контекст рамки
                ;   AF не задаёт выбор модели, ShipPanelState.Selector содержит полный байтовый селектор
                ;   HL', DE', BC', AF', IX, IY исходный контекст вызовов матриц и графики
                ;   действуют договоры DrawCaptionItem, CheckItemRect, SetupPreviewModel и RenderPreviewFrame, страницы и таблицы подготовлены
                ;   HALT требует разрешённых IRQ с сохранением контекста, в проверке I=80 и IM2 загрузчика, музыка выключена
                ;   аппаратная блокировка смены банка снята, окно станции 0 доступно, код и CPU-стек не перекрываются рабочими областями
                ; Out:
                ;   HL, DE и BC активного кадра принадлежат RenderPreviewFrame, AF после возврата равен выбранной станционной странице и флагам её OR
                ;   при отказе геометрии HL=0, DE=EmptyCallback.Entry, B=(Selector-1) AND FF, C от SUB Height,14 перед SetupPreviewModel
                ;   HL', DE', BC', AF' при отказе принадлежат SetupPreviewModel, IX и IY сохранены, при кадре действуют договоры его помощников
                ;   MenuCommandState.PeriodicCall равен AnimateShipPreview.Entry только при Carry CheckItemRect, иначе EmptyCallback.Entry
                ;   верхняя строка H=(TextWindow.Height-14) AND FF, верхняя колонка L=(TextWindow.Width-13) AND FF, нижние пределы нулевые
                ;   начало проекции задаётся словом ((Y SHL 8) OR X)*8 по модулю 65536, оно передаётся через DE' после EXX
                ;   банк 0 выбран с ROM 1, отображаемая страница сохраняется в старших битах CurrentPage, SP после RET равен входному+2
                ;   временный C9 сохраняет все регистры и память без чтения индекса, полный активный путь сохраняет I и IM, кадр устанавливает IFF
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по помощникам, IFF при кадре, окно, регистрация, периодический callback, банк, D3D и bitmap
                ; Note:
                ;   рамка рисуется до проверки геометрии, неанимируемые малые размеры всё равно проходят настройку D3D
                ;   SetBandFillMode выбирает рамку по биту FillMode, ResetBandMode затем восстанавливает все шесть обычных слов
                ;   Carry CheckItemRect проверяет и байтовые границы, и минимум 4x4, этот код не проверяет положение указателя мыши
                ;   младшие компоненты геометрии не нормализуются, три ADD HL,HL масштабируют полное слово с исходным переносом
                ;   возвратный банк не восстанавливает произвольный старый номер, выбирается банк станции 0
                ;   независимый bitmap всего просмотра и IRQ вне точек HALT не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Рамка и разрешение анимации
                ; -----------------------------------------
                ; чтение изменяемого индекса физического элемента просмотра
Entry:          LD HL, #0000
                ; подготовка заполненных либо обычных участков рамки по существующему FillMode
                CALL @Station.SetBandFillMode.Entry
                ; регистрация элемента, рамка, заголовок и настройка его текстового окна
                CALL @Station.DrawCaptionItem.Entry
                ; восстановление обычных шести операндов после текущей рамки
                CALL @Station.ResetBandMode.Entry
                ; повторное чтение того же изменяемого индекса для проверки геометрии
                LD HL, (@ShipPanelState.PreviewIndex)
                ; проверка знаков начала, байтовых экранных границ и минимума 4x4
                CALL @Station.CheckItemRect.Entry
                ; подготовка пустого периодического callback для геометрического отказа
                LD HL, @Station.EmptyCallback.Entry
                JR NC, @Station.DrawShipPreview.SetCallback                     ; переход, если CheckItemRect сбросил Carry, оставить пустой периодический callback

                ; разрешение будущих кадров только при принятой геометрии
                LD HL, @Station.AnimateShipPreview.Entry
                ; сохранение выбранного адреса в операнде периодического CALL MainLoop
SetCallback:    LD (@MenuCommandState.PeriodicCall), HL
                ; расчёт пиксельного начала умножением упакованного Y,X на восемь по модулю 65536
                EX DE, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                ; перенос пиксельного начала в DE' для BuildSpriteLineTable внутри E13C
                EXX
                ; выбор банка D3D с сохранением старших управляющих битов страницы
                LD A, @ShipPreviewConst.PreviewPage
                CALL @Station.SelectRamBank.Entry
                ; обнуление нижних пределов отсечения
                LD DE, #0000
                ; расчёт верхней колонки L из ширины текстового окна минус 13
                LD A, (@TextWindow.Width)
                SUB @ShipPreviewConst.ColumnInset
                LD L, A
                ; расчёт верхней строки H из высоты текстового окна минус 14
                LD A, (@TextWindow.Height)
                SUB @ShipPreviewConst.RowInset
                LD H, A
                ; чтение полного селектора для настройки модели
                LD A, (@ShipPanelState.Selector)
                ; настройка существующих операндов границ, таблиц строк и смещения модели
                CALL @D3D.SetupPreviewModel.Entry
                ; проверка выбранного периодического callback на пустой адрес
                LD HL, (@MenuCommandState.PeriodicCall)
                LD DE, @Station.EmptyCallback.Entry
                ; сброс Carry перед полным сравнением двух адресов
                OR A
                SBC HL, DE
                JR Z, @Station.DrawShipPreview.ReturnBank0                      ; переход, если сохранён EmptyCallback.Entry, завершить настройку без первого кадра

                ; ожидание IRQ с сохранением контекста при уже выбранном банке 4
                HALT
                ; повторное чтение селектора перед полным рисующим кадром
                LD A, (@ShipPanelState.Selector)
                CALL @D3D.RenderPreviewFrame.Entry
                ; возврат окна RAM к банку станции 0, отображаемый экран здесь не переключается
ReturnBank0:    LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                RET

                endmodule
                endmodule
