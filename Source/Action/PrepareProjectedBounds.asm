                module Action
                module PrepareProjectedBounds
                ; Документация [допуск и координаты](../../Docs/ActionProjectedBounds.md)
                ; -----------------------------------------
                ; Фильтрация старших байтов координат и подготовка допуска, знакового X и модулей двух проекций
                ; исходная запись 17, код ACTION банка 0, адреса E299..E30E
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, исходные HL, DE и B сохраняются только до первого отношения
                ;   Output0 и Output1 из ActionPatchedVectorState задают два слова координат, Output2 знаменатель всех трёх отношений
                ;   ScaledBound задаёт слово первого числителя, Gate и CompanionMask задают полные байтовые маски дополнительного отбора
                ;   действует договор DivideScaledLogarithmic на точных таблицах двух построителей, выбран банк 0 ACTION
                ;   операнды Limit, ProjectedX, AbsoluteX и AbsoluteY доступны для записи, два байта CPU-стека доступны для CALL, IRQ не вмешиваются
                ; Out:
                ;   при модуле signed8 старшего байта Output0 либо Output1 не меньше 10 исполнение передаётся E40F, HL, DE и BC сохраняются, A проверенный модуль, F от CP с 10
                ;   при ненулевом пересечении Gate AND CompanionMask исполнение передаётся E40F, HL и DE сохраняются, B входной, C=Gate, A пересечение, F от AND
                ;   после первого отношения без Carry Limit получает его арифметическую половину, знаковый бит исходного слова сохраняется
                ;   после второго отношения без Carry ProjectedX получает знаковое слово X, AbsoluteX его модуль по модулю 65536
                ;   при третьем отношении без Carry AbsoluteY получает модуль Y, HL этот модуль, DE исходное знаковое слово Y, BC результат третьего отношения
                ;   при полном успехе исполнение продолжается по E30F в CaptureProjectedRecord, AF и AF' соответствуют вычислению модуля Y и последнему отношению
                ;   при Carry от любого отношения исполнение передаётся E40F, HL, DE, BC, AF и AF' соответствуют этому отношению, предшествующие записи остаются выполненными
                ;   HL', DE', BC', IX, IY, SP, I, IM и IFF сохраняются, дополнительных портовых операций нет, на CPU-стеке используется максимум два дополнительных байта
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R, два байта временного CPU-стека, выбранные изменяемые JR делителя, Limit, ProjectedX, AbsoluteX и AbsoluteY по достигнутому пути
                ; Note:
                ;   проверяется модуль только старшего байта, это не сравнение полного модуля слова с 0A00
                ;   обе ненулевые маски без общего установленного разряда пропускают расчёт, проверкой двух булевых значений AND не заменяется
                ;   при переполнении первого, второго или третьего отношения число уже записанных выходных слов равно соответственно 0, 1 или 3
                ;   арифметическая половина слова отношения может иметь старший бит 1, преждевременное насыщение или беззнаковый сдвиг не добавлены
                ;   модуль 8000 остаётся 8000, при отрицательном Y A содержит инверсию его исходного старшего байта и F=92 OR (A AND 28)
                ;   при неотрицательном Y A остаётся от последнего отношения, F=54 OR (HIGH(Y) AND 28), это не флаги нулевого HL
                ;   это последовательный фрагмент без RET, продолжения E30F и E40F не входят в локальную модель
                ;   игровой смысл CompanionMask и полный предшествующий обход ещё не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Отбор по старшим байтам координат
                ; Проверка знака старшего байта Output0 перед его байтовым модулем.
Entry:          LD A, (@ActionPatchedVectorState.Output0 + 1)
                AND A
                JP P, @Action.PrepareProjectedBounds.CheckHighX                 ; переход, если старший байт Output0 неотрицателен, байтовый модуль уже получен

                NEG
                ; Проверка байтового модуля старшей части X относительно HighByteLimit.
CheckHighX:     CP @ActionProjectedBoundsConst.HighByteLimit
                JP NC, @Action.InsertRenderQueue.Entry                          ; переход, если модуль старшего байта Output0 не меньше 10, пропустить этот расчёт

                ; Проверка знака старшего байта Output1 перед его байтовым модулем.
                LD A, (@ActionPatchedVectorState.Output1 + 1)
                AND A
                JP P, @Action.PrepareProjectedBounds.CheckHighY                 ; переход, если старший байт Output1 неотрицателен, байтовый модуль уже получен

                NEG
                ; Проверка байтового модуля старшей части Y относительно того же HighByteLimit.
CheckHighY:     CP @ActionProjectedBoundsConst.HighByteLimit
                JP NC, @Action.InsertRenderQueue.Entry                          ; переход, если модуль старшего байта Output1 не меньше 10, пропустить этот расчёт

                ; -----------------------------------------
                ; Проверка пересечения масок отбора
                ; Расчёт Gate AND CompanionMask по полным байтам, не по признакам их ненулевого значения.
                LD A, (@ActionProjectedCaptureState.Gate)
                LD C, A
                LD A, (@ActionProjectedBoundsState.CompanionMask)
                AND C
                JP NZ, @Action.InsertRenderQueue.Entry                          ; переход, если Gate и CompanionMask имеют общий установленный бит, расчёт не выполнять

                ; -----------------------------------------
                ; Расчёт допуска
                ; Подготовка Output2 как знаменателя и изменяемого ScaledBound как числителя первого отношения.
                LD DE, (@ActionPatchedVectorState.Output2)
                LD HL, #0000
                CALL @Action.DivideScaledLogarithmic.Entry
                JP C, @Action.InsertRenderQueue.Entry                           ; переход, если первое отношение вернуло Carry, выходные слова не обновлять

                ; Расчёт арифметической половины слова отношения и сохранение в Limit, знаковый бит не отбрасывается.
                SRA H
                RR L
                LD (@ActionProjectedCaptureState.Limit), HL
                ; -----------------------------------------
                ; Расчёт знакового X и его модуля
                ; Подготовка исходного Output0 и того же Output2 для второго отношения.
                LD DE, (@ActionPatchedVectorState.Output2)
                LD HL, (@ActionPatchedVectorState.Output0)
                CALL @Action.DivideScaledLogarithmic.Entry
                JP C, @Action.InsertRenderQueue.Entry                           ; переход, если отношение X вернуло Carry, сохранить уже обновлённый Limit

                ; Сохранение знакового ProjectedX до вычисления модуля.
                LD (@ActionProjectedCaptureState.ProjectedX), HL
                BIT 7, H
                JR Z, @Action.PrepareProjectedBounds.StoreAbsX                  ; переход, если отношение X неотрицательно, модуль уже получен

                ; Расчёт модуля отрицательного X по модулю 65536.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Сохранение AbsoluteX для последующего отбора, знак отдельно остаётся в ProjectedX.
StoreAbsX:      LD (@ActionProjectedBoundsState.AbsoluteX), HL
                ; -----------------------------------------
                ; Расчёт знакового Y и его модуля
                ; Подготовка Output1 и Output2 для третьего отношения.
                LD DE, (@ActionPatchedVectorState.Output2)
                LD HL, (@ActionPatchedVectorState.Output1)
                CALL @Action.DivideScaledLogarithmic.Entry
                JP C, @Action.InsertRenderQueue.Entry                           ; переход, если отношение Y вернуло Carry, сохранить Limit, ProjectedX и AbsoluteX

                ; Сохранение знакового Y в DE перед вычислением модуля в HL.
                LD D, H
                LD E, L
                BIT 7, H
                JR Z, @Action.PrepareProjectedBounds.StoreAbsY                  ; переход, если отношение Y неотрицательно, модуль уже получен

                ; Расчёт модуля отрицательного Y по модулю 65536, DE сохраняет знаковый результат.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Сохранение AbsoluteY перед последовательным продолжением в CaptureProjectedRecord.
StoreAbsY:      LD (@ActionProjectedBoundsState.AbsoluteY), HL
                ; JP @Action.CaptureProjectedRecord.Entry, продолжение в CaptureProjectedRecord.asm

                ; -----------------------------------------
                endmodule
                endmodule
