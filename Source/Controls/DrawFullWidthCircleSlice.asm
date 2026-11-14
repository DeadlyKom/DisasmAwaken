                module Controls
                module DrawFullWidthCircleSlice
                ; Документация [алгоритм и проверка](../../Docs/ControlsFullWidthCircle.md)
                ; [Использование возвращённых Mode-флагов](../../Docs/ControlsCircleWork.md#прямые-потребители-возвращаемых-флагов)
                ; -----------------------------------------
                ; Заливка внутренней полосы от вертикальной границы и одной остаточной половины
                ; исходная запись 22, банк 1, смещения #138C..#13D9
                ; In:
                ;   BC задаёт WorkX в B и WorkY в C, состояние соответствует выбранному входу из D236
                ;   Radius 9..255 и Flags заданы проекцией, XPlus выбирает активную сторону остаточной половины
                ;   YMinus задаёт старт на строке 0 или 95, радиус и флаги перечитываются из проекции
                ;   IX задаёт рисунок и чередование, банк 1 выбран, CPU-стек допускает четырнадцать временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL, DE, BC, AF и альтернативные пары содержат состояние последнего прохода, выход с активным EXX сохраняет перестановку
                ;   SquareDiff и SectionRadius получают разность квадратов и её целый корень, Entry восстанавливает WorkX, InsideXEntry сохраняет его
                ;   полосы меняют только внутренние столбцы 1..30, последующая половина продолжает рисунок со следующей строки
                ;   IXH, IY, I, IM, IFF и страница сохраняются, SP=входной SP+2, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, растр, рабочие поля, операнды полос и ядер, четырнадцать временных байтов CPU-стека
                ; Note:
                ;   порог A prime нулевой при Entry, при InsideXEntry равен WorkX−119 по модулю байта
                ;   радиус полного внутреннего участка вычисляется по горизонтальному плечу 120+WorkX
                ;   число строк полосы равно SectionRadius−WorkY, направление начинается от соответствующей вертикальной границы
                ;   половина получает B=0, C=FF и байтовые края 1 и 31, за пределами растра её начальная проверка возвращает без пикселей
                ;   7016 сценариев на четыре входа сверяют регистры кроме R, все банки и непиксельные записи
                ; -----------------------------------------
                ; Восстановление WorkX угловой ветви и установка нулевого порога.
Entry:          LD A, B
                ADD A, @ControlsHorizontalCircleConst.OffsetLimit
                LD B, A
                LD (@ControlsCircleWork.Value.WorkX), A
                XOR A
                JR @Controls.DrawFullWidthCircleSlice.BuildSection

                ; Расчёт порога для вертикального сечения с исходным горизонтальным смещением.
InsideXEntry:   LD A, B
                SUB @ControlsHorizontalCircleConst.ReleaseBias
                ; Сохранение порога, чтение проекции и расчёт радиуса полноширинной части.
BuildSection:   EX AF, AF'
                LD DE, (@ControlsBodyProjection.Value.Flags)
                LD A, @ControlsHorizontalCircleConst.OffsetLimit
                ADD A, B
                CALL @Controls.SqrtSquareDiff.Entry
                LD (@ControlsCircleWork.Value.SectionRadius), A
                ; Расчёт оставшейся длины полосы от вертикальной границы, проверка направления YMinus.
                SUB C
                LD B, A
                BIT @ControlsProjectConst.YMinusBit, E
                JR Z, @Controls.DrawFullWidthCircleSlice.StartAtBottom          ; переход, если YMinus сброшен, начинать от нижней строки 95

                XOR A
                CALL @Controls.FillInteriorRowsDown.Entry
                ; Подготовка остаточной нижней половины после полосы.
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.XPlusBit, A
                CALL Z, @Controls.DrawLeftClippedHalfDown.Entry                 ; вызов, если XPlus сброшен, продолжить левое отсечение вниз
                CALL NZ, @Controls.DrawRightClippedHalfDown.Entry               ; вызов, если XPlus установлен, продолжить правое отсечение вниз
                RET

                ; Начало верхнего прохода от нижней границы растра.
StartAtBottom:  LD A, #5F
                CALL @Controls.FillInteriorRowsUp.Entry
                ; Подготовка остаточной верхней половины после полосы.
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.XPlusBit, A
                CALL Z, @Controls.DrawLeftClippedHalfUp.Entry                   ; вызов, если XPlus сброшен, продолжить левое отсечение вверх
                CALL NZ, @Controls.DrawRightClippedHalfUp.Entry                 ; вызов, если XPlus установлен, продолжить правое отсечение вверх
                RET

                endmodule
                endmodule
