                module Action
                module CheckObjectPhaseTransition
                ; Документация [алгоритм и проверка](../../Docs/ActionPhaseTransition.md)
                ; -----------------------------------------
                ; Проверка случайного ожидания и перехода к фазовому смещению записи
                ; исходная запись 17, адреса E935..E97B
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord
                ;   доступны поля StateCode, SavedStateCode, PhaseMoveTimer, Unknown1B, Unknown1D и Unknown1F
                ;   выбран ACTION банка 0, действуют условия NextRandomWord5, четыре байта ниже SP не пересекают запись и поток 5, IRQ не вмешиваются
                ; Out:
                ;   HL=новое слово потока 5, DE и BC сохраняются
                ;   при H>=FA и L>=EF прежний StateCode сохраняется в SavedStateCode, затем StateCode=13
                ;   после случайной проверки каждый байт Unknown1B, Unknown1D и Unknown1F сворачивается как b при b<80 либо FF XOR b
                ;   если свёрнутые значения меньше 2, 2 и 6 соответственно, текущее StateCode сохраняется в SavedStateCode, StateCode=14 и PhaseMoveTimer=1E
                ;   если оба перехода разрешены, итог SavedStateCode=13 независимо от состояния при входе
                ;   при отказе A равен первому недопустимому свёрнутому байту, F соответствует его CP с порогом
                ;   при трёх успешных проверках A равен состоянию перед записью 14, F остаётся от третьего CP с порогом 6
                ;   HL', DE' и BC' равны результату NextRandomWord5, AF', IX, IY, I/IM/IFF и paging сохраняются
                ;   SP после RET равен входному SP+2, внешний возврат сохраняется, временная рамка занимает четыре байта
                ;   R учитывает 67 M1 вызова с потоком, 3 M1 проверки H, ещё 3 при H>=FA и ещё 6 при выполнении случайного перехода
                ;   каждое достигнутое поле добавляет 6 M1 и ещё один для отрицательного байта, успешный переход 14 добавляет ещё 9 M1
                ; Corrupt:
                ;   HL, AF, HL', DE', BC', R, состояние потока 5, условные поля записи и четыре временных байта CPU-стека, SP внешним RET
                ; Note:
                ;   свёртка отрицательного байта выполняется CPL без прибавления единицы, FF превращается в 0, 80 в 7F
                ;   вторая группа проверок выполняется даже после состояния 13, это исходный порядок записей, а не взаимоисключающий выбор
                ;   пороги сравнивают отдельные байты, роль слов 1A..1F и их физические единицы здесь не назначаются
                ;   78848 сценариев сравнивают реальные инструкции и поток с независимой формулой, точные регистры, флаги, R, восемь банков и кратность записей
                ;   полное произведение всех входов, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись
                ; -----------------------------------------
                ; Обновление физического потока 5, результат HL используется обеими случайными проверками.
Entry:          CALL @Action.NextRandomWord5.Entry
                ; Проверка старшего байта нового слова перед допуском случайного ожидания.
                LD A, H
                CP @ActionPhaseTransitionConst.RandomHighMin
                JR C, @Action.CheckObjectPhaseTransition.CheckFirst             ; переход, если H меньше FA, пропустить случайный переход и проверить поля записи

                ; Проверка младшего байта того же нового слова без повторного вызова генератора.
                LD A, L
                CP @ActionPhaseTransitionConst.RandomLowMin
                JR C, @Action.CheckObjectPhaseTransition.CheckFirst             ; переход, если L меньше EF, пропустить случайный переход и проверить поля записи

                ; Сохранение текущего состояния перед установкой ожидания 13, последующие проверки не пропускаются.
                LD A, (IX + @FActionRecord.StateCode)
                LD (IX + @FActionRecord.SavedStateCode), A
                LD (IX + @FActionRecord.StateCode), @ActionPhaseTransitionConst.WaitState
                ; Проверка первого байта, отрицательная половина сворачивается побитовым дополнением.
CheckFirst:     LD A, (IX + @FActionRecord.Unknown1B)
                OR A
                JP P, @Action.CheckObjectPhaseTransition.FoldFirst              ; переход, если бит 7 Unknown1B сброшен, сравнить исходный байт с порогом

                CPL
                ; Проверка допуска первого свёрнутого байта, допустимы только значения 0 и 1.
FoldFirst:      CP @ActionPhaseTransitionConst.PairFoldLimit
                RET NC                                                          ; выход, если первый свёрнутый байт не меньше 2, сохранить результат случайной проверки

                ; Проверка знака второго байта перед такой же свёрткой без прибавления единицы.
                LD A, (IX + @FActionRecord.Unknown1D)
                OR A
                JP P, @Action.CheckObjectPhaseTransition.FoldSecond             ; переход, если бит 7 Unknown1D сброшен, сравнить исходный байт с порогом

                CPL
                ; Проверка допуска второго свёрнутого байта, допустимы только значения 0 и 1.
FoldSecond:     CP @ActionPhaseTransitionConst.PairFoldLimit
                RET NC                                                          ; выход, если второй свёрнутый байт не меньше 2, не менять таймер смещения

                ; Проверка знака третьего байта, для него используется отдельный порог.
                LD A, (IX + @FActionRecord.Unknown1F)
                OR A
                JP P, @Action.CheckObjectPhaseTransition.FoldThird              ; переход, если бит 7 Unknown1F сброшен, сравнить исходный байт с порогом

                CPL
                ; Проверка допуска третьего свёрнутого байта, допустимы значения 0..5.
FoldThird:      CP @ActionPhaseTransitionConst.ThirdFoldLimit
                RET NC                                                          ; выход, если третий свёрнутый байт не меньше 6, не устанавливать фазовое смещение

                ; Сохранение текущего состояния, в том числе уже установленного 13, перед переходом в 14.
                LD A, (IX + @FActionRecord.StateCode)
                LD (IX + @FActionRecord.SavedStateCode), A
                LD (IX + @FActionRecord.StateCode), @ActionPhaseTransitionConst.RiseState
                ; Обновление длительности фазового смещения исходным значением 30.
                LD (IX + @FActionRecord.PhaseMoveTimer), @ActionPhaseTransitionConst.RiseTimer
                RET

                endmodule
                endmodule
