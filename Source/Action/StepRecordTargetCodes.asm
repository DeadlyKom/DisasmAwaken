                module Action
                module StepRecordTargetCodes
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordCodeStep.md)
                ; -----------------------------------------
                ; Подвод двух байтов записи к рассчитанным кодам с различными правилами ограничения шага
                ; исходная запись 17, перенесённое ядро в фиксированной RAM, физический банк 5, смещения #04A2..#04F1
                ; In:
                ;   основной Entry принимает HL=Left0, DE=Right0, BC=Right1, AF числового аргумента не задаёт
                ;   HL'=Left1, DE'=Left2, BC'=Right2, AF' числового аргумента не задаёт, шесть координат являются signed16
                ;   IX указывает FActionRecord, OffsetPhase1, OffsetPhase2 и TargetCodeStep читаются, два первых поля доступны для записи
                ;   TargetCodeStep является стабильным числовым шагом 0..FF, вмешательство IRQ и пересечение записи со стеком либо кодом исключены
                ;   основной вход требует 16 дополнительных байтов CPU-стека и договор EncodeHalfCoordinateDeltas, включая таблицы и входные конфигурации 7FFD
                ;   дополнительный ApplyCodes принимает B и C как готовые целевые байты, HL, DE и AF числовых аргументов не задают, геометрия им не вызывается
                ; Out:
                ;   H=модуль обёрнутой разности OffsetPhase2-C, L=модуль обёрнутой разности OffsetPhase1-B, каждый модуль 0..80
                ;   D=исходный OffsetPhase2, E=(исходный OffsetPhase2-C) AND FF
                ;   BC содержит рассчитанные целевые коды у Entry либо сохраняет входные коды ApplyCodes
                ;   AF при втором модуле меньше TargetCodeStep содержит A=этот модуль, F от CP с TargetCodeStep, второе поле не записывается
                ;   AF иначе содержит A=новый OffsetPhase2, F от его исходного ADD, запись выполняется даже при нулевом шаге
                ;   HL', DE', BC', AF' возвращаются от дочерней геометрии у Entry, на прямом ApplyCodes сохраняются от входа
                ;   IX, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   основной вход заканчивается конфигурацией 7FFD=10 после OUT 11 и 10, ApplyCodes не переключает банки и не пишет CPU-стек
                ;   R получает S M1 у ApplyCodes и 1+G+S M1 у Entry, G стоимость EncodeHalfCoordinateDeltas, S стоимость ApplyCodes, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, DE
                ;   BC только у Entry
                ;   AF
                ;   HL', DE', BC', AF' только у Entry
                ;   R, OffsetPhase1 и OffsetPhase2 по условиям, основной вход также 16 байтов стека и эффекты EncodeHalfCoordinateDeltas
                ; Note:
                ;   для первого поля модули 0 и 1 не обновляются, при большем модуле TargetCodeStep делится на степени двойки до шага не больше расстояния
                ;   для второго поля слишком большой TargetCodeStep сразу запрещает обновление, петля его уменьшения при стабильном TargetCodeStep недостижима
                ;   разность вычисляется по модулю байта и трактуется как signed8, код 80 после NEG остаётся 80
                ;   нулевой шаг может записывать прежнее значение обратно, отсутствие движения не означает отсутствия записи RAM
                ;   1089536 сценариев проверили оба входа, полный домен 256 разностей на 256 шагов для обоих полей, реальные дочерние процедуры, RAM и кратность записей
                ;   в модели Entry учтён один M1 CALL перед геометрией, R и полные M1 обоих входов сравниваются без исключения регистра
                ;   полные игровые роли полей, полное произведение пяти байтов и шести координат, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Расчёт целевых B и C настоящей геометрической цепочкой, её 14 байтов стека дополняются этим CALL.
Entry:          CALL @Action.EncodeHalfCoordinateDeltas.Entry
                ; Чтение первого текущего кода, дополнительный вход с уже подготовленными целевыми B и C.
ApplyCodes:     LD A, (IX + @FActionRecord.OffsetPhase1)
                LD D, A
                ; Расчёт обёрнутой байтовой разности первого текущего кода и B.
                SUB B
                LD E, A
                JP P, @Action.StepRecordTargetCodes.StoreFirstDist              ; переход, если обёрнутая первая разность неотрицательна как signed8, использовать её модуль без NEG

                NEG
                ; Сохранение первого модуля расстояния, значение 80 после отрицания сохраняется.
StoreFirstDist: LD L, A
                ; Проверка исходной мёртвой зоны первой компоненты, расстояния ноль и один не записываются.
                CP @ActionCodeStepConst.FirstMinDiff
                JR C, @Action.StepRecordTargetCodes.ReadSecondCode              ; переход, если первый модуль меньше двух, пропустить запись OffsetPhase1

                ; Чтение числового предельного шага, он не является набором независимых флагов.
                LD A, (IX + @FActionRecord.TargetCodeStep)
                ; Проверка текущего шага относительно первого расстояния.
LimitFirstStep: CP L
                JR C, @Action.StepRecordTargetCodes.FirstStepSign               ; переход, если шаг меньше первого расстояния, выбрать знак движения

                JR Z, @Action.StepRecordTargetCodes.FirstStepSign               ; переход, если шаг равен первому расстоянию, выбрать знак движения

                ; Расчёт уменьшенного шага, Carry от строгого сравнения сброшен, поэтому RRA сдвигает с нулём сверху.
                RRA
                JP @Action.StepRecordTargetCodes.LimitFirstStep

                ; Проверка направления по исходной обёрнутой первой разности.
FirstStepSign:  BIT 7, E
                JR NZ, @Action.StepRecordTargetCodes.StoreFirstCode             ; переход, если первая разность отрицательна, прибавить положительный шаг

                ; Расчёт отрицательного шага для положительной первой разности.
                NEG
                ; Обновление первого кода по модулю байта, при нулевом шаге прежний байт также записывается.
StoreFirstCode: ADD A, D
                LD (IX + @FActionRecord.OffsetPhase1), A
                ; Чтение второго текущего кода для независимого правила обновления.
ReadSecondCode: LD A, (IX + @FActionRecord.OffsetPhase2)
                LD D, A
                ; Расчёт обёрнутой разности второго кода и C.
                SUB C
                LD E, A
                JP P, @Action.StepRecordTargetCodes.StoreSecondDist             ; переход, если обёрнутая вторая разность неотрицательна как signed8, использовать её модуль без NEG

                NEG
                ; Сохранение второго модуля расстояния в H.
StoreSecondDist:LD H, A
                ; Проверка запрета второй записи при шаге больше расстояния, первый байт уже мог измениться.
                CP (IX + @FActionRecord.TargetCodeStep)
                RET C                                                           ; выход, если второй модуль меньше TargetCodeStep, сохранить OffsetPhase2 без записи

                ; Повторное чтение стабильного TargetCodeStep, после предыдущей проверки он уже не больше второго расстояния.
                LD A, (IX + @FActionRecord.TargetCodeStep)
                ; Проверка повторно прочитанного шага, при стабильном поле следующая петля RRA не выполняется.
LimitSecondStep:CP H
                JR Z, @Action.StepRecordTargetCodes.SecondStepSign              ; переход, если шаг равен второму расстоянию, выбрать знак движения

                JR C, @Action.StepRecordTargetCodes.SecondStepSign              ; переход, если шаг меньше второго расстояния, выбрать знак движения

                ; Исходное уменьшение шага сохранено, при стабильном TargetCodeStep эта ветвь недостижима.
                RRA
                JP @Action.StepRecordTargetCodes.LimitSecondStep

                ; Проверка направления по исходной обёрнутой второй разности.
SecondStepSign: BIT 7, E
                JR NZ, @Action.StepRecordTargetCodes.StoreSecondCode            ; переход, если вторая разность отрицательна, прибавить положительный шаг

                ; Расчёт отрицательного шага для положительной второй разности.
                NEG
                ; Обновление второго кода, последний ADD задаёт возвращаемые A и F.
StoreSecondCode:ADD A, D
                LD (IX + @FActionRecord.OffsetPhase2), A
                RET

                endmodule
                endmodule
