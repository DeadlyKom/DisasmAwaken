                module Controls
                module DrawVerticalCircleSlice
                ; Документация [алгоритм и проверка](../../Docs/ControlsVerticalCircleSlice.md)
                ; -----------------------------------------
                ; Рисование вертикально отсечённого кругового сечения с двумя криволинейными краями
                ; исходная запись 22, банк 1, смещения #1485..#14CA
                ; In:
                ;   BC задаёт B=OffsetX в 0..119 и C=WorkY, входной Carry установлен
                ;   Radius в 9..255 не меньше WorkY, Radius²−WorkY² меньше (120−OffsetX)²
                ;   CenterX равен 128±OffsetX согласно XPlus, YMinus выбирает направление, IX задаёт рисунок и чередование
                ;   банк 1 выбран, на CPU-стеке внешний возврат и место для четырнадцати временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL, DE, BC содержат конечные адреса и маски половины, AF восстановлен от проверки YMinus
                ;   HL', DE', BC' содержат конечное состояние половины, AF', IXH и IY сохранены, IXL чередуется после каждой строки
                ;   SquareDiff=(Radius²−WorkY²−1) AND FFFF, SectionRadius содержит целый корень, CenterY равен 0 либо 95
                ;   при равенстве Radius и WorkY SectionRadius=FF, края расположены в обратном порядке, растр и SavedSP сохранены
                ;   SP=входной SP+2, I, IM, IFF и страница сохранены, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IXL, R, рабочие поля круга, растр и условные операнды ядра, четырнадцать временных байтов CPU-стека
                ; Note:
                ;   проверено 136370 сценариев, включая 118619 касаний, регистры кроме R, все банки и кратность непиксельных записей
                ;   полный диспетчер, R и кратность пиксельных записей остаются за пределами этого договора
                ; -----------------------------------------
                ; Чтение радиуса и флагов из записи проекции после сравнения квадратов вызывающим кодом.
Entry:          LD DE, (@ControlsBodyProjection.Value.Flags)
                ; Расчёт корня разности квадратов с исходным заёмом, равенство радиуса и смещения даёт обёрнутую разность FFFF.
                LD A, C
                CALL @Controls.SqrtSquareDiff.Entry
                LD (@ControlsCircleWork.Value.SectionRadius), A
                ; Подготовка начального Yprime из WorkY и отрицательного Xprime из радиуса сечения.
                LD A, C
                EXX
                LD E, A
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                NEG
                LD C, A
                EXX
                ; Проверка YMinus для выбора начальной строки и последующего направления.
                XOR A
                BIT @ControlsProjectConst.YMinusBit, E
                JR NZ, @Controls.DrawVerticalCircleSlice.SetBoundary            ; переход, если YMinus установлен, начать на верхней строке 0

                LD A, #5F
                ; Запись граничной строки в CenterY для обоих построителей масок.
SetBoundary:    LD (@ControlsCircleWork.Value.CenterY), A
                LD C, A
                ; Расчёт левого края как CenterX минус SectionRadius по модулю байта.
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                LD L, A
                LD A, (@ControlsCircleWork.Value.CenterX)
                SUB L
                CALL @Controls.BuildLeftSpanMask.Entry
                ; Расчёт правого края как CenterX плюс SectionRadius на той же граничной строке.
                LD A, (@ControlsCircleWork.Value.CenterY)
                LD C, A
                LD A, (@ControlsCircleWork.Value.SectionRadius)
                LD L, A
                LD A, (@ControlsCircleWork.Value.CenterX)
                ADD A, L
                CALL @Controls.BuildRightSpanMask.Entry
                ; Проверка YMinus перед выбором половины, рисователь восстанавливает AF для второй проверки.
                LD A, (@ControlsBodyProjection.Value.Flags)
                BIT @ControlsProjectConst.YMinusBit, A
                CALL NZ, @Controls.DrawCircleHalfDown.Entry                     ; вызов, если YMinus установлен, рисовать вниз от строки 0
                CALL Z, @Controls.DrawCircleHalfUp.Entry                        ; вызов, если YMinus сброшен, рисовать вверх от строки 95
                RET

                endmodule
                endmodule
