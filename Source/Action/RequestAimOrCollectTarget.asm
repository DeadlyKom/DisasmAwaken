                module Action
                module RequestAimOrCollectTarget
                ; Документация [прицельный запрос и сбор захваченного объекта](../../Docs/ActionTractorCollect.md)
                ; -----------------------------------------
                ; Запрос прицельных линий либо притягивание и сбор захваченного объекта по режиму силового луча
                ; исходная запись 17, перенесённое ядро банка 5, адреса 7317..741C
                ; In:
                ;   HL, DE, BC и AF входных числовых аргументов не задают, результат сохранения зависит от выбранной ветви
                ;   Mode по 7318 выбирает действие, ноль передаёт управление RequestPairedAimLines с его отдельным договором
                ;   при ненулевом Mode Target0 задаёт полный байт кода, 80..FF дают отказ по знаку, для остальных адрес записи должен быть доступен
                ;   компоненты, поля StateCode, ClassCode, OffsetScaleLow, Unknown11, ReuseByte и PickupKind доступны, запись и SavedSP доступны для изменения
                ;   банк 0 выбран, поля Used, Capacity и байты от Row00 доступны, чтение правила по виду не проверяет границы таблицы
                ;   действуют QueueTextItemBank1 и договор прицельного ребёнка, обычная рамка допускает восемнадцать дополнительных байтов
                ;   обычный стек не пересекается с записью и изменяемым кодом, IRQ и повторный вход исключены, обработчик сам DI не выполняет
                ; Out:
                ;   при Mode=0 действует RequestPairedAimLines, хвостовой JP не создаёт дополнительного возврата
                ;   при ненулевом Mode и отрицательном Target0 HL, DE и BC сохраняются, A равен Target0, F соответствует OR A, RAM и paging сохраняются
                ;   при High первой компоненты=80 или StateCode не 04 Target0 получает FF, A=FF, F сохраняет соответствующий CP, HL указывает проверенное поле
                ;   при принятой записи OffsetScaleLow получает 0, три компоненты подтягиваются к диапазону -256..255 с шагом 50, SavedSP получает входной SP-2
                ;   если близки не все оси, HL указывает запись, D сохраняется, E равно числу близких осей, BC равен последнему шагу 0000 либо FFCE, A=E и F от CP E,3
                ;   когда близки все оси, Target0 получает FF до проверок вместимости, полный алгоритм вида, количества и отказов приведён в документации
                ;   при успехе байт Row00+вид и Used обновлены, первая компонента получает 8000, при бите 4 ReuseByte устанавливается бит 2 PanelEvents.Flags
                ;   после успеха HL=EE1B, DE указывает выбранный байт груза, B содержит новый либо сохранённый Used, C содержит количество
                ;   A содержит младший адрес ReuseByte, F соответствует BIT 4 этого поля, CursorA получает EE1B и в очередь передаётся F36D
                ;   при ненулевом Mode HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, внешнее завершение даёт SP=входной SP+2
                ;   SP временно указывает прямо на три компоненты, обычный SP восстанавливается до последующих проверок и очереди
                ;   после сообщения итоговая страница 10, прочие пути сохраняют paging, отказ очереди не отменяет сбор
                ; Corrupt:
                ;   HL, DE, BC, AF, AF' на прицельном пути, R, временный SP, SavedSP, координаты и поля записи, Target0, байт груза, Used, флаг события, CursorA, очередь, paging и временный CPU-стек по пути
                ; Note:
                ;   не исправлены оборачивание сумм, снятие Target0 до отказа, байтовая индексация пар груза и чтение двух правил из байтов следующей инструкции
                ;   для класса 13 количество и вид читаются из Unknown11 и PickupKind, для класса 10 выбран вид 0F, иначе 1B, количество 1..8 получено из R
                ;   264679 сценариев исполняют обработчик до внешнего RET, четыре прицельных сценария действительно рисуют обе линии
                ;   сверены регистры кроме полного итогового R и тактов, RAM и кратность записей вне восемнадцати обычных временных байтов стека
                ;   M1 до чтения R учтены отдельно, аппаратные IRQ и нативная игра не выполнялись
                ; -----------------------------------------
                ; Проверка существующего байта Mode, его меняет команда силового луча.
Entry:          LD A, #00
                AND A
                JP Z, @Action.RequestPairedAimLines.Entry                       ; переход, если Mode равен нулю, передать управление прицельному запросу без рамки CALL

                ; Проверка знака полного кода Target0, отрицательные значения не преобразуются в адрес.
                LD A, (@ActionMissileTargets.Value.Target0)
                OR A
                RET M                                                           ; выход, если Target0 отрицательный, сохранить запись и захват

                ; Расчёт адреса по исходному коду, преобразователь не проверяет доступность записи.
                CALL @Action.RecordIndexToAddress.Entry
                ; Проверка старшего байта первой компоненты на код недоступности 80.
                INC L
                LD A, (HL)
                CP @ActionTractorCollectConst.InactiveHigh
                JR Z, @Action.RequestAimOrCollectTarget.DropTarget              ; переход, если старший байт равен 80, снять Target0

                ; Расчёт адреса StateCode от старшего байта первой компоненты и проверка состояния 04.
                LD A, L
                ADD A, @ActionTractorCollectConst.HighToState
                LD L, A
                LD A, (HL)
                CP @ActionTractorCollectConst.RequiredState
                JR Z, @Action.RequestAimOrCollectTarget.PullTarget              ; переход, если StateCode равен 04, подготовить притягивание

                ; Снятие недоступного либо неподходящего захвата, саму запись не изменять.
DropTarget:     LD A, @ActionTractorCollectConst.NoTarget
                LD (@ActionMissileTargets.Value.Target0), A
                RET

                ; Обнуление OffsetScaleLow до обработки трёх компонент.
PullTarget:     LD A, L
                ADD A, @ActionTractorCollectConst.StateToValue
                LD L, A
                LD (HL), #00
                ; Восстановление базы записи от адреса OffsetScaleLow и сохранение обычного SP после PUSH базы.
                SUB @FActionRecord.OffsetScaleLow
                LD L, A
                PUSH HL
                LD (@ActionTractorCollectState.SavedSP), SP
                ; Преобразование трёх компонент в стек данных, IRQ не должны использовать этот временный SP.
                LD SP, HL
                POP HL
                ; Создание счётчика компонент со старшим байтом 00 либо FF.
                LD E, #00
                ; Подготовка отрицательного шага для первой компоненты, знак выбирается по исходному старшему байту.
                LD BC, @ActionTractorCollectConst.NegativeStep
                LD A, H
                OR A
                JP P, @Action.RequestAimOrCollectTarget.CheckFirst              ; переход, если первая компонента неотрицательная, проверить её старший байт без инверсии

                CPL
                ; Проверка свёрнутого старшего байта, нуль соответствует исходному 00 либо FF.
CheckFirst:     AND A
                JR NZ, @Action.RequestAimOrCollectTarget.StepFirst              ; переход, если первая компонента вне близкого диапазона, оставить шаг минус 50

                ; Учёт близкой первой оси без изменения её слова.
                LD BC, #0000
                INC E
StepFirst:      BIT 7, H
                JR NZ, @Action.RequestAimOrCollectTarget.AddFirst               ; переход, если первая компонента отрицательная, вычесть отрицательный шаг

                ; Уменьшение положительной первой компоненты на 50, при близком слове шаг равен нулю.
                ADD HL, BC
                JP @Action.RequestAimOrCollectTarget.StoreFirst

                ; Увеличение отрицательной первой компоненты на 50, при близком слове шаг равен нулю.
AddFirst:       SBC HL, BC
                ; Обновление первой компоненты через PUSH и продвижение стека к следующему слову.
StoreFirst:     PUSH HL
                INC SP
                INC SP
                POP HL
                ; Подготовка того же исходного шага для второй компоненты.
                LD BC, @ActionTractorCollectConst.NegativeStep
                LD A, H
                OR A
                JP P, @Action.RequestAimOrCollectTarget.CheckSecond             ; переход, если вторая компонента неотрицательная, проверить старший байт без инверсии

                CPL
                ; Проверка близкого диапазона второй компоненты.
CheckSecond:    AND A
                JR NZ, @Action.RequestAimOrCollectTarget.StepSecond             ; переход, если вторая компонента вне близкого диапазона, оставить шаг минус 50

                ; Учёт близкой второй оси с нулевым шагом.
                LD BC, #0000
                INC E
StepSecond:     BIT 7, H
                JR NZ, @Action.RequestAimOrCollectTarget.AddSecond              ; переход, если вторая компонента отрицательная, вычесть отрицательный шаг

                ; Уменьшение положительной второй компоненты на 50 либо сохранение близкой.
                ADD HL, BC
                JP @Action.RequestAimOrCollectTarget.StoreSecond

                ; Увеличение отрицательной второй компоненты на 50 либо сохранение близкой.
AddSecond:      SBC HL, BC
                ; Обновление второй компоненты и продвижение стека к третьему слову.
StoreSecond:    PUSH HL
                INC SP
                INC SP
                POP HL
                ; Подготовка того же исходного шага для третьей компоненты.
                LD BC, @ActionTractorCollectConst.NegativeStep
                LD A, H
                OR A
                JP P, @Action.RequestAimOrCollectTarget.CheckThird              ; переход, если третья компонента неотрицательная, проверить старший байт без инверсии

                CPL
                ; Проверка близкого диапазона третьей компоненты.
CheckThird:     AND A
                JR NZ, @Action.RequestAimOrCollectTarget.StepThird              ; переход, если третья компонента вне близкого диапазона, оставить шаг минус 50

                ; Учёт близкой третьей оси с нулевым шагом.
                LD BC, #0000
                INC E
StepThird:      BIT 7, H
                JR NZ, @Action.RequestAimOrCollectTarget.AddThird               ; переход, если третья компонента отрицательная, вычесть отрицательный шаг

                ; Уменьшение положительной третьей компоненты на 50 либо сохранение близкой.
                ADD HL, BC
                JP @Action.RequestAimOrCollectTarget.StoreThird

                ; Увеличение отрицательной третьей компоненты на 50 либо сохранение близкой.
AddThird:       SBC HL, BC
                ; Обновление третьей компоненты перед восстановлением обычного CPU-стека.
StoreThird:     PUSH HL
                ; Восстановление SP из операнда SavedSP, записанного до установки стека данных.
RestoreStack:   LD SP, #0000
                POP HL
                ; Проверка числа близких осей после обновления всех трёх слов.
                LD A, E
                CP @ActionTractorCollectConst.CloseAxes
                RET NZ                                                          ; выход, если близки не все три оси, сохранить Target0 для следующего притягивания

                ; Снятие Target0 до проверок вместимости, последующие отказы его не восстанавливают.
                LD A, @ActionTractorCollectConst.NoTarget
                LD (@ActionMissileTargets.Value.Target0), A
                PUSH HL
                ; Расчёт адреса ClassCode и проверка класса 13 с собственными видом и количеством.
                LD A, L
                ADD A, @FActionRecord.ClassCode
                LD L, A
                LD A, (HL)
                CP @ActionTractorCollectConst.PayloadClass
                JR Z, @Action.RequestAimOrCollectTarget.ReadPayload             ; переход, если ClassCode равен 13, прочитать полный байт вида и количества из записи

                ; Проверка класса 10, он выбирает вид 0F, остальные классы вид 1B.
                CP @ActionTractorCollectConst.AlternateClass
                LD E, @ActionTractorCollectConst.AlternateKind
                JR Z, @Action.RequestAimOrCollectTarget.RandomAmount            ; переход, если ClassCode равен 10, сохранить уже выбранный вид 0F

                LD E, @ActionTractorCollectConst.DefaultKind
                ; Расчёт количества 1..8 из фактического R после исходных M1, программный генератор не вызывается.
RandomAmount:   LD A, R
                AND @ActionTractorCollectConst.RandomMask
                INC A
                JR @Action.RequestAimOrCollectTarget.ApplyRule

                ; Чтение полного PickupKind как вида и Unknown11 как количества, ограничения диапазона нет.
ReadPayload:    LD A, L
                ADD A, @ActionTractorCollectConst.ClassToKind
                LD L, A
                LD E, (HL)
                ADD A, @ActionTractorCollectConst.KindToAmount
                LD L, A
                LD A, (HL)
                ; Расчёт адреса правила 741D+вид, после 28 самостоятельных байтов чтение продолжается в код.
ApplyRule:      LD D, #00
                LD HL, @ActionTractorCargoRules.Kind00.Control
                ADD HL, DE
                LD C, A
                ; Чтение Used и поля учёта из двух старших битов правила.
                LD A, (@ActionFlightTonnage.Value.Used)
                LD B, A
                LD A, (HL)
                POP HL
                AND @ActionTractorCollectConst.AccountingMask
                JR NZ, @Action.RequestAimOrCollectTarget.CheckByte              ; переход, если поле учёта C0 ненулевое, сохранить Used без проверки его кандидата

                ; Расчёт кандидата Used по модулю 256, перенос суммы не используется для отказа.
                LD A, B
                ADD A, C
                LD B, A
                ; Проверка беззнакового Capacity против обёрнутого кандидата.
                LD A, (@ActionFlightTonnage.Value.Capacity)
                CP B
                RET C                                                           ; выход, если Capacity меньше кандидата, Target0 уже снят, объект остаётся активным

                ; Расчёт байтового адреса Row00+вид, размер двухбайтовой записи здесь не учитывается.
CheckByte:      PUSH HL
                LD HL, @ActionOwnedCargoRows.Row00.QuantityAndMark
                ADD HL, DE
                EX DE, HL
                POP HL
                ; Расчёт нового байта груза по модулю 256 и проверка границы 201.
                LD A, (DE)
                ADD A, C
                CP @ActionTractorCollectConst.ByteEndLimit
                RET NC                                                          ; выход, если обёрнутый новый байт не меньше 201, ничего не записывать в груз и Used

                ; Обновление выбранного байта и Used только после обеих проверок.
                LD (DE), A
                LD A, B
                LD (@ActionFlightTonnage.Value.Used), A
                ; Отметка собранной записи недоступным словом 8000 в первой компоненте.
                LD (HL), #00
                INC L
                LD (HL), @ActionTractorCollectConst.InactiveHigh
                ; Расчёт адреса ReuseByte и проверка его бита 4 после отметки записи.
                LD A, L
                ADD A, @ActionTractorCollectConst.HighToReuse
                LD L, A
                BIT 4, (HL)
                JR Z, @Action.RequestAimOrCollectTarget.QueuePickup             ; переход, если бит 4 ReuseByte сброшен, не устанавливать бит 2 события

                ; Установка бита 2 существующего поля событий при помеченной записи.
                LD HL, @ActionPanelEvents.Value.Flags
                SET @ActionPanelEventConst.FixedCostBit, (HL)
                ; Выбор звукового потока и сообщения о подборе после необратимого изменения состояния.
QueuePickup:    LD HL, @ActionTractorCollectConst.Sound
                LD (@ActionAyEffectState.CursorA), HL
                PUSH DE
                LD DE, @ControlsFlightText.ObjectCollected
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                RET

                endmodule
                endmodule
