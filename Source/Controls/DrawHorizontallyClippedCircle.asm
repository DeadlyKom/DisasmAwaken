                module Controls
                module DrawHorizontallyClippedCircle
                ; Документация [алгоритм и проверка](../../Docs/ControlsHorizontalCircle.md)
                ; [Использование возвращённых Mode-флагов](../../Docs/ControlsCircleWork.md#прямые-потребители-возвращаемых-флагов)
                ; -----------------------------------------
                ; Рисование двух половин круга с одним исходно неподвижным горизонтальным краем
                ; исходная запись 22, банк 1, смещения #13DA..#1403
                ; In:
                ;   BC задаёт рабочее горизонтальное смещение в B, DE задаёт XPlus в бите 0 E
                ;   Entry принимает 0<Radius−WorkX<240, InsideEntry принимает OffsetX<120, OffsetX+Radius>=120 и Radius−OffsetX<120
                ;   физическая запись содержит исходный Radius 9..255 и Flags, WorkX соответствует B, CenterY находится в строках 0..95
                ;   IX задаёт рисунок и чередование, банк 1 выбран, на CPU-стеке внешний возврат и восемь временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL, DE, BC и AF содержат результат верхней половины, ранние выходы с активным EXX сохраняют переставленные пары
                ;   HL', DE', BC' содержат сопряжённое состояние верхней половины, A' задаёт порог, F' зависит от сравнений с ним
                ;   IXH и IY сохранены, IXL продолжает чередование через обе половины, Direction=0, SavedSP=входной SP−2
                ;   WorkX при Entry восстановлен прибавлением 120 по модулю байта, при InsideEntry сохранён
                ;   SP=входной SP+2, I, IM, IFF и страница сохранены, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, растр, WorkX, Direction, SavedSP, SavedB на левом пути, операнды ядер и восемь временных байтов CPU-стека
                ; Note:
                ;   порог A prime равен нулю у Entry и OffsetX−119 по модулю байта у InsideEntry
                ;   XPlus выбирает неподвижный правый край, при сброшенном XPlus неподвижен левый край
                ;   подготовка перед верхней половиной заново задаёт адреса, маски, Cprime и Eprime, сохраняя IXL и A prime
                ;   верхняя половина принимает исходный внешний возврат через хвостовой JP
                ;   50808 сценариев подтверждают регистры кроме R, восемь банков, пиксельные интервалы и кратность непиксельных записей
                ; -----------------------------------------
                ; Восстановление горизонтального смещения из внешней ветви прибавлением порога 120.
Entry:          LD A, B
                ADD A, @ControlsHorizontalCircleConst.OffsetLimit
                LD (@ControlsCircleWork.Value.WorkX), A
                LD B, A
                ; Установка порога снятия отсечения для внешней ветви.
                XOR A
                JR @Controls.DrawHorizontallyClippedCircle.SelectSide

                ; Расчёт порога снятия отсечения по исходному горизонтальному смещению внутренней ветви.
InsideEntry:    LD A, B
                SUB @ControlsHorizontalCircleConst.ReleaseBias
                ; Сохранение порога в A prime и выбор неподвижной стороны по XPlus.
SelectSide:     EX AF, AF'
                BIT @ControlsProjectConst.XPlusBit, E
                JR Z, @Controls.DrawHorizontallyClippedCircle.PrepareLeft       ; переход, если XPlus сброшен, подготовить неподвижный левый край

                ; Подготовка правого отсечения и рисование от центра вниз.
                CALL @Controls.PrepareCircleRightClip.Entry
                CALL @Controls.DrawRightClippedHalfDown.Entry
                ; Повторная подготовка правого отсечения для верхней половины, текущая фаза рисунка сохраняется.
                CALL @Controls.PrepareCircleRightClip.Entry
                ; Хвостовая передача верхней половине с исходным внешним возвратом.
                JP @Controls.DrawRightClippedHalfUp.Entry

                ; Подготовка левого отсечения и рисование от центра вниз.
PrepareLeft:    CALL @Controls.PrepareCircleLeftClip.Entry
                CALL @Controls.DrawLeftClippedHalfDown.Entry
                ; Повторная подготовка левого отсечения для верхней половины, текущая фаза рисунка сохраняется.
                CALL @Controls.PrepareCircleLeftClip.Entry
                ; Хвостовая передача верхней половине с исходным внешним возвратом.
                JP @Controls.DrawLeftClippedHalfUp.Entry

                endmodule
                endmodule
