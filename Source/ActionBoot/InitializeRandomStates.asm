                module ActionBoot
                module InitializeRandomStates
                ; Документация [инициализация потоков и полная модель](../../Docs/ActionRandomInitialization.md)
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
                ; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
                ; -----------------------------------------
                ; Начальное заполнение слов состояний от регистра R и повторных вызовов обработчика #EB72
                ; исходная запись 17, файловые смещения #0149..#0197
                ; In:
                ;   DE и младший C сохраняются, R задаёт начальный LowWord потока Stream0 и число прогревочных вызовов
                ;   подключён банк 0 с исходным NextRandomWord0 и StepFoldedRandom, все 15 физических состояний доступны
                ;   код по 4306, системный переходник 5CC2, два операнда режима и шесть байтов ниже входного SP доступны без перекрытия, IRQ не вмешиваются
                ; Out:
                ;   HL - последнее новое LowWord потока Stream0, DE сохранён, B=0, C сохранён, A=2E, F от последнего StepFoldedRandom
                ;   HL'=Stream0, DE'=последнее новое слово, B'=0, C'=младший байт последней смеси n, AF' сохранён
                ;   IX, IY, I, IM, IFF и выбранная страница сохранены, SP обычного возврата равен входному SP+2
                ;   LowWord и FoldByte Stream0 обновлены, LowWord потоков 3, 4, 1, 5, 8, 9, 10 и 2 заполнены, их FoldByte сохранены
                ;   по 5CC2 записаны POP AF и RET, ActionOverlayModeState.Mode=1, ActionPanelGaugesState.ThirdValue=2E
                ; Corrupt:
                ;   HL, BC только по B, AF, HL', DE', BC', R, Stream0 и восемь младших слов других потоков, переходник, два операнда и шесть временных байтов стека
                ; Note:
                ;   LD A,R считывает R после четырёх M1 от входа, старший байт начального слова остаётся C9 от подготовки переходника
                ;   N=(считанный R AND 3)+1, прогрев вызывает NextRandomWord0 N раз, затем выполняются ещё семь вызовов
                ;   первый из восьми копируемых результатов получен последним прогревочным вызовом, это не девятый независимый поток
                ;   R изменяется на 491+70*N M1 в младших семи разрядах с сохранением бита 7, максимум временного стека равен шести байтам
                ;   512 сценариев охватывают все начальные R в исходном и подготовленном ненулевом профиле состояний, полный 24-битный домен не перебран
                ;   период, равномерность и все игровые назначения потоков этой инициализацией не установлены
                ; -----------------------------------------
                ; Установка двух исходных команд POP AF и RET в системный переходник TR-DOS.
Entry:          LD HL, #C9F1
                LD (#5CC2), HL
                ; Получение младшего байта семени после четырёх M1, H остаётся C9.
                LD A, R
                LD L, A
                LD (@ActionRandomStreams.Stream0.LowWord), HL
                ; Расчёт числа прогревочных вызовов от одного до четырёх.
                AND #03
                INC A
                LD B, A
                ; Прогрев единственного Stream0 с исходным сохранением счётчика BC.
WarmRandom:     PUSH BC
                CALL @Action.NextRandomWord0.Entry
                POP BC
                DJNZ @ActionBoot.InitializeRandomStates.WarmRandom

                ; Заполнение восьми LowWord последовательными результатами Stream0 без изменения их FoldByte.
                LD (@ActionRandomStreams.Stream3.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream4.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream1.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream5.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream8.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream9.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream10.LowWord), HL
                CALL @Action.NextRandomWord0.Entry
                LD (@ActionRandomStreams.Stream2.LowWord), HL
                ; Установка исходного режима без наложения и начального значения третьей шкалы.
                LD A, #01
                LD (@ActionOverlayModeState.Mode), A
                LD A, #2E
                LD (@ActionPanelGaugesState.ThirdValue), A
                RET


                endmodule
                endmodule
