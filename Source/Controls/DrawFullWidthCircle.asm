                module Controls
                module DrawFullWidthCircle
                ; Документация [алгоритм и проверка](../../Docs/ControlsFullWidthCircle.md)
                ; -----------------------------------------
                ; Заливка внутренних полос и двух остаточных половин широкого круга
                ; исходная запись 22, банк 1, смещения #1340..#138B
                ; In:
                ;   BC задаёт WorkX в B и WorkY в C, состояние соответствует выбранному входу из D236
                ;   Radius 9..255 и Flags заданы проекцией, XPlus выбирает активную сторону остаточной половины
                ;   CenterY находится в строках 0..95, начальный DE содержит Radius и Flags
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
                ;   первый проход идёт вверх от CenterY, второй вниз, фаза IXL между ними сохраняется
                ;   половина получает B=0, C=FF и байтовые края 1 и 31, за пределами растра её начальная проверка возвращает без пикселей
                ;   7016 сценариев на четыре входа сверяют регистры кроме R, все банки и непиксельные записи
                ; -----------------------------------------
                ; Восстановление исходного WorkX и установка нулевого порога снятия отсечения.
Entry:          LD A, B
                ADD A, @ControlsHorizontalCircleConst.OffsetLimit
                LD B, A
                LD (@ControlsCircleWork.Value.WorkX), A
                XOR A
                JR @Controls.DrawFullWidthCircle.BuildSection

                ; Расчёт порога снятия отсечения по исходному горизонтальному смещению.
InsideXEntry:   LD A, #88
                ADD A, B
                INC A
                ; Сохранение порога и расчёт длины полноширинной полосы по дальнему горизонтальному плечу.
BuildSection:   EX AF, AF'
                LD A, @ControlsHorizontalCircleConst.OffsetLimit
                ADD A, B
                CALL @Controls.SqrtSquareDiff.Entry
                LD (@ControlsCircleWork.Value.SectionRadius), A
                ; Подготовка длины полосы для прохода вверх от строки центра.
                LD B, A
                LD A, (@ControlsCircleWork.Value.CenterY)
                CALL @Controls.FillInteriorRowsUp.Entry
                ; Подготовка двух неподвижных байтовых краёв на строке после полосы.
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.XPlusBit, A
                CALL Z, @Controls.DrawLeftClippedHalfUp.Entry                   ; вызов, если XPlus сброшен, продолжить левое отсечение вверх
                CALL NZ, @Controls.DrawRightClippedHalfUp.Entry                 ; вызов, если XPlus установлен, продолжить правое отсечение вверх
                ; Восстановление длины полосы и строки центра для второго прохода вниз.
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                LD B, A
                LD A, (@ControlsCircleWork.Value.CenterY)
                CALL @Controls.FillInteriorRowsDown.Entry
                ; Подготовка остаточной нижней половины с текущей фазой рисунка.
                CALL @Controls.LoadCircleClipState.Entry
                CALL @Controls.PrepareInteriorSpan.Entry
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.XPlusBit, A
                CALL Z, @Controls.DrawLeftClippedHalfDown.Entry                 ; вызов, если XPlus сброшен, продолжить левое отсечение вниз
                CALL NZ, @Controls.DrawRightClippedHalfDown.Entry               ; вызов, если XPlus установлен, продолжить правое отсечение вниз
                RET

                endmodule
                endmodule
