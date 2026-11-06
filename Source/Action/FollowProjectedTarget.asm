                module Action
                module FollowProjectedTarget
                ; Документация [сопровождение и цель](../../Docs/ActionAimFollow.md)
                ; -----------------------------------------
                ; Сглаживание экранной точки и назначение первой свободной цели по запросу
                ; исходная запись 17, код ACTION банка 0, адреса E36A..E40E
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, сохраняются только по ранним путям
                ;   HL' задаёт адрес записи для кодирования цели, DE', BC', IX и IY сохраняются
                ;   CompanionMask запрещает обработку при любом ненулевом байте, AbsoluteX и AbsoluteY содержат модули отношений
                ;   знаки берутся из старших байтов Output0 и Output1, Position хранит байты X и Y, Request задаёт ненулевой запрос захвата
                ;   ACTION выбран в банке 0, paging не заблокирован, Controls и его очередь банка 1 удовлетворяют договору QueueTextItem
                ;   SP сохраняется, для сообщения нужны восемнадцать дополнительных байтов ниже SP, IRQ не вмешиваются
                ; Out:
                ;   все пути продолжаются по E40F, внешнего RET нет, SP сохраняется
                ;   при CompanionMask не равном нулю HL, DE, BC сохраняются, A содержит маску, F соответствует AND маски
                ;   иначе BC=AbsoluteX и DE=AbsoluteY, при ненулевом старшем байте A=HIGH(X) OR HIGH(Y), F соответствует OR
                ;   при X не меньше 16 либо Y не меньше 16 выходные AF задаются соответствующим CP 16, HL сохранён, записей RAM нет
                ;   после допуска C=119 плюс либо минус X, E=43 плюс либо минус Y, знаки определяются Output0 и Output1
                ;   Position получает два сглаженных байта, CompanionMask получает 1 до проверки Request
                ;   при нулевом Request HL содержит новую Position, B=D=0, A=0, F=54, прочее состояние сохраняется
                ;   ненулевой Request обнуляется, CursorA сначала получает CaptureSound, проверяется первый Target0..Target2 со значением FF
                ;   при свободной цели A=(((HL' - A100) mod 65536) >> 6) AND FF, выбранный Target получает этот код
                ;   HL при записи кода содержит старший байт разности HL' - A100 и младший байт HL' << 2, BC=5F00, DE адрес выбранного Target
                ;   AF' после записи кода содержит A'=HIGH(входного HL') и прежний F', остальные альтернативные пары сохранены
                ;   при трёх занятых целях CursorA=FullSound, в очередь банка 1 передаётся указатель F258, затем выбирается страница 10
                ;   после сообщения HL=EE1B, DE=9B1D, BC содержит целевую экранную точку, AF соответствует INC последнего Target с исходным Carry=0
                ;   I, IM и IFF сохраняются, портов нет кроме двух OUT 7FFD по пути сообщения
                ; Corrupt:
                ;   HL, DE, BC, AF, AF' при кодировании, R, Position, CompanionMask, Request, CursorA, выбранный Target, банковая очередь и временная рамка по достигнутому пути
                ; Note:
                ;   для каждой оси d=(цель - старый байт) mod 256, d=FF заменяется нулём, остальные d трактуются как signed8 и делятся арифметически на два
                ;   старый байт плюс шаг оборачивается по модулю 256, разность -1 подавляется, но разность -3 даёт шаг -2
                ;   F после кодирования берёт S, Z и PV из младшего байта HL, биты 5 и 3 из A, Carry из бита 14 разности указателя, H=N=0
                ;   локальный код не проверяет допустимость и выравнивание HL', смысл кода записи доказан для шагов 64 от A100
                ;   занятая очередь может молча отклонить текст, обновления точки, запроса и звука уже выполнены и не отменяются
                ;   временная рамка сообщения независимо проверена по глубине, её остаточное содержимое в этой модели не вычисляется
                ;   полный обход, отрисовка E40F, IRQ, воспроизведение AY и нативная игра не входят в локальный договор
                ; -----------------------------------------
                ; -----------------------------------------
                ; Допуск сопровождения
                ; Проверка полного CompanionMask, ненулевой байт сохраняет прежнюю точку и запрос.
Entry:          LD A, (@ActionProjectedBoundsState.CompanionMask)
                AND A
                JP NZ, @Action.InsertRenderQueue.Entry                          ; переход, если CompanionMask ненулевой, перейти к очереди отрисовки

                ; Чтение AbsoluteX и AbsoluteY, модули должны помещаться в младшие байты.
                LD BC, #0000
                LD DE, #0000
                LD A, B
                OR D
                JP NZ, @Action.InsertRenderQueue.Entry                          ; переход, если старший байт хотя бы одного модуля ненулевой, сопровождение пропустить

                ; Проверка малого горизонтального расстояния от центра.
                LD A, C
                CP @ActionAimFollowConst.DistanceLimit
                JP NC, @Action.InsertRenderQueue.Entry                          ; переход, если AbsoluteX не меньше 16, сопровождение пропустить

                ; Проверка малого вертикального расстояния от центра.
                LD A, E
                CP @ActionAimFollowConst.DistanceLimit
                JP NC, @Action.InsertRenderQueue.Entry                          ; переход, если AbsoluteY не меньше 16, сопровождение пропустить

                ; -----------------------------------------
                ; Расчёт целевой экранной точки
                ; Проверка знака исходного Output0, знак отношения отдельно не используется.
                LD A, (@ActionPatchedVectorState.Output0 + 1)
                AND A
                LD A, C
                JP P, @Action.FollowProjectedTarget.TranslateX                  ; переход, если Output0 неотрицателен, смещение X оставить положительным

                ; Расчёт отрицательного смещения X по модулю 256.
                NEG
                ; Перевод смещения X к экранному центру 119.
TranslateX:     ADD A, @ActionAimFollowConst.CenterX
                LD C, A
                ; Проверка знака исходного Output1 для вертикального смещения.
                LD A, (@ActionPatchedVectorState.Output1 + 1)
                AND A
                LD A, E
                JP P, @Action.FollowProjectedTarget.TranslateY                  ; переход, если Output1 неотрицателен, смещение Y оставить положительным

                ; Расчёт отрицательного смещения Y по модулю 256.
                NEG
                ; Перевод смещения Y к экранному центру 43.
TranslateY:     ADD A, @ActionAimFollowConst.CenterY
                LD E, A
                ; -----------------------------------------
                ; Обновление сопровождающей точки
                ; Расчёт разности целевого X и прежнего X, INC выделяет единственное значение FF.
                LD HL, (@ActionAimFollowState.Position)
                LD A, L
                SUB C
                NEG
                INC A
                JR Z, @Action.FollowProjectedTarget.StepX                       ; переход, если разность X равна -1, оставить нулевой шаг

                DEC A
                ; Расчёт арифметической половины signed8-разности X и нового байта X.
StepX:          SRA A
                ADD A, L
                LD L, A
                ; Расчёт разности целевого Y и прежнего Y с той же обработкой FF.
                LD A, H
                SUB E
                NEG
                INC A
                JR Z, @Action.FollowProjectedTarget.StepY                       ; переход, если разность Y равна -1, оставить нулевой шаг

                DEC A
                ; Расчёт арифметической половины signed8-разности Y и нового байта Y.
StepY:          SRA A
                ADD A, H
                LD H, A
                ; Сохранение обоих байтов Position и установка CompanionMask до проверки запроса.
                LD (@ActionAimFollowState.Position), HL
                LD A, #01
                LD (@ActionProjectedBoundsState.CompanionMask), A
                ; -----------------------------------------
                ; Проверка запроса цели
                ; Чтение полного Request, нулевой запрос завершает только сопровождение.
                LD A, (@ActionAimFollowState.Request)
                AND A
                JR Z, @Action.InsertRenderQueue.Entry                           ; переход, если Request равен нулю, новый код цели не записывать

                ; Снятие Request и выбор потока CaptureSound до поиска свободной цели.
                XOR A
                LD (@ActionAimFollowState.Request), A
                LD HL, @ActionAimFollowConst.CaptureSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Поиск первого свободного Target, исходный FF после INC становится нулём.
                LD DE, @ActionMissileTargets.Value.Target0
                LD A, (DE)
                INC A
                JR Z, @Action.FollowProjectedTarget.EncodeRecord                ; переход, если Target0 равен FF, записать код в первый слот

                ; Проверка Target1 после занятого Target0.
                LD DE, @ActionMissileTargets.Value.Target1
                LD A, (DE)
                INC A
                JR Z, @Action.FollowProjectedTarget.EncodeRecord                ; переход, если Target1 равен FF, записать код во второй слот

                ; Проверка Target2 после двух занятых слотов.
                LD DE, @ActionMissileTargets.Value.Target2
                LD A, (DE)
                INC A
                JR Z, @Action.FollowProjectedTarget.EncodeRecord                ; переход, если Target2 равен FF, записать код в третий слот

                ; -----------------------------------------
                ; Сообщение при трёх занятых целях
                ; Замена звука на FullSound, предшествующие обновления состояния сохраняются.
                LD HL, @ActionAimFollowConst.FullSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Сохранение адреса Target2 на время передачи строки в настоящую очередь Controls банка 1.
                PUSH DE
                LD DE, @ActionAimFollowConst.FullText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                JP @Action.InsertRenderQueue.Entry

                ; -----------------------------------------
                ; Кодирование адреса записи
                ; Перенос HL' в основной HL через AF', входной F' сохраняется, A' получает старший байт адреса.
EncodeRecord:   EXX
                LD A, L
                EX AF, AF'
                LD A, H
                EXX
                LD H, A
                EX AF, AF'
                LD L, A
                ; Расчёт смещения относительно A100 по модулю 65536.
                LD BC, @ActionAimFollowConst.RecordBias
                ADD HL, BC
                ; Расчёт восьмибитного кода шага 64 через две пары SLA и RLA, полный младший байт не проверяется.
                LD A, H
                SLA L
                RLA
                SLA L
                RLA
                ; Сохранение кода только в выбранный свободный Target.
                LD (DE), A
                ; JP @Action.InsertRenderQueue.Entry, продолжение в InsertRenderQueue.asm

                ; -----------------------------------------
                endmodule
                endmodule
