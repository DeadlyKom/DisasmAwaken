                module Controls
                module DrawCornerCircleSlice
                ; Документация [алгоритм и проверка](../../Docs/ControlsCornerCircleSlice.md)
                ; [Использование возвращённых Mode-флагов](../../Docs/ControlsCircleWork.md#прямые-потребители-возвращаемых-флагов)
                ; -----------------------------------------
                ; Рисование одного сечения с вертикальным и горизонтальным отсечением
                ; исходная запись 22, банк 1, смещения #1404..#1484
                ; In:
                ;   BC задаёт WorkX в B и WorkY в C, Carry в F prime получен из горизонтального сравнения D236
                ;   Entry принимает состояние угловой ветви D2DA, InsideXEntry принимает состояние ветви D2AA между порогами квадратов
                ;   Radius 9..255 и Flags берутся из записи проекции, IX задаёт рисунок, банк 1 выбран, CPU-стек допускает четырнадцать временных байтов
                ; Out:
                ;   HL, DE, BC, AF и альтернативные пары соответствуют выбранной половине либо одному из двух возвратов до её вызова
                ;   SquareDiff=(Radius²−WorkY²−входной Carry из F prime) AND FFFF, SectionRadius содержит целый корень
                ;   Entry восстанавливает WorkX и задаёт порог ноль, InsideXEntry сохраняет WorkX и задаёт порог WorkX−119 по модулю байта
                ;   на ранних возвратах растр, SavedSP и Direction сохраняются, на остальных путях применяется контракт выбранной половины
                ;   IXH, IY, I, IM, IFF и страница сохраняются, SP=входной SP+2, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, рабочие поля, растр, условные операнды и четырнадцать временных байтов CPU-стека
                ; Note:
                ;   XPlus выбирает неподвижную сторону, YMinus выбирает начальную строку 0 и ход вниз, иначе строку 95 и ход вверх
                ;   на правом пути возврат происходит после построения маски при столбце 31, на левом до построения маски при X<8
                ;   крайние допустимые исходным кодом столбцы и нулевой корень сохранены, проверено 30941 сценариев с настоящими детьми
                ;   регистры кроме R, восемь банков и кратность непиксельных записей сверены, IRQ не вмешиваются
                ; -----------------------------------------
                ; Восстановление исходного горизонтального смещения угловой ветви прибавлением порога 120.
Entry:          LD A, B
                ADD A, @ControlsHorizontalCircleConst.OffsetLimit
                LD (@ControlsCircleWork.Value.WorkX), A
                LD B, A
                XOR A
                JR @Controls.DrawCornerCircleSlice.BuildSection

                ; Расчёт порога A prime для сечения с исходным горизонтальным смещением.
InsideXEntry:   LD A, B
                SUB @ControlsHorizontalCircleConst.ReleaseBias
                ; Сохранение порога и восстановление Carry горизонтальной проверки для вычисления корня.
BuildSection:   EX AF, AF'
                LD DE, (@ControlsBodyProjection.Value.Flags)
                LD A, C
                CALL @Controls.SqrtSquareDiff.Entry
                ; Сохранение радиуса сечения и подготовка начальных Y prime и отрицательного X prime.
                LD (@ControlsCircleWork.Value.SectionRadius), A
                LD A, C
                EXX
                LD E, A
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                NEG
                LD C, A
                EXX
                ; Проверка XPlus перед выбором неподвижной стороны.
                BIT @ControlsProjectConst.XPlusBit, E
                JR Z, @Controls.DrawCornerCircleSlice.PrepareLeft               ; переход, если XPlus сброшен, подготовить левое отсечение

                ; Расчёт левого криволинейного края как 128 плюс WorkX минус SectionRadius.
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                CPL
                ADD A, #81
                ADD A, B
                LD C, #00
                BIT @ControlsProjectConst.YMinusBit, E
                JR NZ, @Controls.DrawCornerCircleSlice.BuildLeftMask            ; переход, если YMinus установлен, построить маску на строке 0

                LD C, #5F
BuildLeftMask:  CALL @Controls.BuildLeftSpanMask.Entry
                LD A, (@ControlsCircleWork.Value.Mode)
                AND A
                LD A, E
                AND #1F
                ; Проверка номера байтового столбца левого края перед выбором правой границы.
                CP #1F
                RET Z                                                           ; выход, если левый край уже в правом столбце 31

                LD A, E
                OR #1F
                LD L, A
                LD C, #FF
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.YMinusBit, A
                CALL NZ, @Controls.DrawRightClippedHalfDown.Entry               ; вызов, если YMinus установлен, рисовать правое отсечение вниз
                CALL Z, @Controls.DrawRightClippedHalfUp.Entry                  ; вызов, если YMinus сброшен, рисовать правое отсечение вверх
                RET

                ; Расчёт правого криволинейного края и проверка допуска относительно пикселя 8.
PrepareLeft:    LD A, (@ControlsCircleWork.Value.SectionRadius)
                ADD A, #80
                SUB B
                CP #08
                RET C                                                           ; выход, если правый край расположен левее пикселя 8

                LD C, #00
                BIT @ControlsProjectConst.YMinusBit, E
                JR NZ, @Controls.DrawCornerCircleSlice.BuildRightMask           ; переход, если YMinus установлен, построить маску на строке 0

                LD C, #5F
                ; Подготовка правой маски и неподвижного левого столбца 1.
BuildRightMask: CALL @Controls.BuildRightSpanMask.Entry
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD A, (@ControlsCircleWork.Value.Mode)
                AND A
                LD B, #00
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.YMinusBit, A
                CALL NZ, @Controls.DrawLeftClippedHalfDown.Entry                ; вызов, если YMinus установлен, рисовать левое отсечение вниз
                CALL Z, @Controls.DrawLeftClippedHalfUp.Entry                   ; вызов, если YMinus сброшен, рисовать левое отсечение вверх
                RET

                endmodule
                endmodule
