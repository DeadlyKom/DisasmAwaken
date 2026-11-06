                module Action
                module CreateMissileForTarget
                ; Документация [создание записи ракеты](../../Docs/ActionMissileCreation.md)
                ; -----------------------------------------
                ; Проверка существования записи цели, поиск свободного слота, инициализация ракеты и создание обратной связи у цели
                ; исходная запись 17, перенесённое ядро банка 5, адреса 60AE..6144
                ; In:
                ;   HL и DE числовых аргументов не задают, C код существующей записи цели, B аргумента не задаёт, AF не задаёт условия допуска
                ;   для создания C относится к допустимой записи исходного массива, процедура сама диапазон C не проверяет
                ;   действуют договоры RecordIndexToAddress, TransformVectorTransposed, SelectMissileStock, FindReusableRecord и RecordIYToIndex
                ;   входная конфигурация выбирает банк 0 и не блокирует 7FFD, канал A и Controls банка 1 доступны, CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются
                ; Out:
                ;   при потерянной цели HL=EDA8, DE и BC сохраняются, AF=8090, IY и альтернативные регистры сохраняются
                ;   потерянная цель задаёт CursorA=EDA8 в банке 0 и передаёт текст F248 очереди банка 1, приём сообщения не гарантирован
                ;   при отсутствии слота HL адрес выбранного счётчика ракет, DE=0040, B=1A, C входной код цели, AF=8042, IY адрес маркера
                ;   при создании HL=0040, DE адрес LinkedIndex цели, B=1A, C входной код цели, A код нового слота, F=45 OR (A AND 28), IY адрес нового слота
                ;   после расчёта HL', DE' и BC' содержат три компоненты вектора, при отказе по слоту A'=01 и F' от вычислителя, при успехе AF'=0044
                ;   IX, I, IM и IFF сохраняются, SP=входной SP+2, Carry=1 только при создании, Z установлен и при успехе, и при отказе по слоту
                ;   запас не уменьшается, неизвестный параметр Unknown13 получает 0A при выборе Fallback либо 32 при выборе Preferred
                ;   при потерянной цели OUT 7FFD получает 11 и 10, на других путях переключений банков нет
                ; Corrupt:
                ;   HL, DE, BC и AF по выбранному пути, HL', DE', BC' и AF' после расчёта, IY после поиска, R, рамка до восемнадцати байтов, состояние геометрии, InitParameter, ReuseByte, поля новой записи, LinkedIndex и LinkFlags цели, CursorA и очередь на пути потерянной цели
                ; Note:
                ;   поле Component0.High=80 означает потерянную цель, все другие байты этого поля принимаются без дополнительной проверки
                ;   вектор расчёта равен 0, 0, 400, выходные компоненты находятся в диапазоне -395..396, знаковое переполнение здесь невозможно
                ;   неизвестные поля инициализируются исходными константами, их игровой смысл не выдумывается
                ;   создание не выполняет проверку ненулевого запаса и не списывает его, предварительный допуск и последующее списание относятся к вызывающему коду
                ;   фактический AY-вывод и движение ракеты не выполняются этой процедурой
                ; -----------------------------------------
                ; Поиск адреса цели по входному C, числовой диапазон кода здесь не проверяется.
Entry:          LD A, C
                CALL @Action.RecordIndexToAddress.Entry
                ; Проверка старшего байта первой компоненты, полный код 80 означает отсутствующую запись.
                INC L
                LD A, (HL)
                CP #80
                JR NZ, @Action.CreateMissileForTarget.BuildComponents           ; переход, если Component0.High цели не равен 80, подготовить новую запись

                ; -----------------------------------------
                ; Обработка потерянной цели
                ; Подготовка потока AY-канала A в банке 0, фактический вывод выполнит потребитель ECA8 позднее.
LostTarget:     LD HL, @ActionMissileCreateConst.ActionSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Сохранение DE перед передачей сообщения о потерянной цели очереди Controls банка 1.
                PUSH DE
                LD DE, @ActionMissileCreateConst.LostText
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Формирование Carry=0 отказа независимо от приёма сообщения, AF становится 8090.
                AND A
                RET

                ; -----------------------------------------
                ; Расчёт трёх компонентов новой записи
                ; Сохранение входных BC и замена альтернативных компонентов исходным вектором 0, 0, 400.
BuildComponents:PUSH BC
                EXX
                LD HL, #0000
                LD D, H
                LD E, L
                LD BC, @ActionMissileCreateConst.InitialComp2
                ; Расчёт по временно транспонированной матрице с настоящим восстановлением SP.
                CALL @Action.TransformVectorTransposed.Entry
                ; Перенос рассчитанных компонентов в альтернативный набор и восстановление входного кода цели в C.
                EXX
                POP BC
                ; Сохранение исходного значения 01 для будущего Unknown11 в альтернативном A.
                LD A, #01
                EX AF, AF'
                ; Выбор поля запаса только для параметра новой записи, уменьшения запаса здесь нет.
                CALL @Action.SelectMissileStock.Entry
                ; Проверка адреса выбранного поля, младший байт 12 соответствует Fallback.
                LD A, L
                CP #12
                LD A, @ActionMissileCreateConst.FallbackParam
                JR Z, @Action.CreateMissileForTarget.FindSlot                   ; переход, если выбран Fallback, оставить параметр Unknown13 равным 0A

                ; Выбор исходного параметра 32 для поля Preferred, единицы и потребитель Unknown13 ещё не установлены.
                LD A, @ActionMissileCreateConst.PreferredParam
                ; -----------------------------------------
                ; Поиск свободного слота
                ; Значение 1A предназначено для Unknown0D, его полный игровой смысл ещё неизвестен.
FindSlot:       LD B, #1A
                ; Обновление операнда инициализации Unknown13 перед поиском, запись сохраняется и при отказе по слотам.
                LD (@ActionMissileCreateState.InitParameter), A
                ; Сохранение кода цели и значения Unknown0D перед итератором.
                PUSH BC
                CALL @Action.FindReusableRecord.Entry
                POP BC
                RET Z                                                           ; выход, если достигнут маркер без доступного слота, Carry=0, запас и цель не изменены

                ; -----------------------------------------
                ; Создание новой записи
                ; Копирование трёх рассчитанных компонентов, альтернативные значения после EXX остаются сохранены.
InitializeSlot: EXX
                LD (IY + FActionRecord.Components.Component0.Low), L
                LD (IY + FActionRecord.Components.Component0.High), H
                LD (IY + FActionRecord.Components.Component1.Low), E
                LD (IY + FActionRecord.Components.Component1.High), D
                LD (IY + FActionRecord.Components.Component2.Low), C
                LD (IY + FActionRecord.Components.Component2.High), B
                EXX
                ; Инициализация известных по фактическим записям полей, неизвестный игровой смысл сохранён в именах Unknown.
                XOR A
                LD (IY + FActionRecord.Unknown06), #90
                LD (IY + FActionRecord.Unknown07), A
                LD (IY + FActionRecord.Unknown08), A
                LD (IY + FActionRecord.Unknown09), A
                LD (IY + FActionRecord.Unknown0A), #08
                LD (IY + FActionRecord.LinkedIndex), A
                LD (IY + FActionRecord.LinkFlags), A
                LD (IY + FActionRecord.Unknown0D), B
                LD (IY + FActionRecord.TargetIndex), C
                ; Восстановление значения 01 для Unknown11, в альтернативном AF остаётся 0044.
                EX AF, AF'
                LD (IY + FActionRecord.Unknown11), A
                LD (IY + FActionRecord.ClassCode), @ActionMissileCreateConst.MissileClass
                ; Инициализация Unknown13, непосредственный байт заранее изменён выбором поля запаса.
                LD (IY + FActionRecord.Unknown13), #00
                LD (IY + FActionRecord.Unknown25), #02
                ; -----------------------------------------
                ; Создание обратной связи у цели
                ; Повторный поиск исходной цели по сохранённому C.
                LD A, C
                CALL @Action.RecordIndexToAddress.Entry
                LD A, L
                ; Расчёт адреса LinkFlags, младший байт базы кратен 40, добавление 0C не требует переноса в H.
                ADD A, FActionRecord.LinkFlags
                LD L, A
                ; Установка бита 1 LinkFlags при создании ссылки на новую ракету, остальные разряды сохраняются.
                SET 1, (HL)
                ; Выбор предыдущего физического поля LinkedIndex у той же цели.
                DEC L
                EX DE, HL
                ; Расчёт кода нового слота из IY с сохранением HL=0040.
                CALL @Action.RecordIYToIndex.Entry
                ; Обновление LinkedIndex цели кодом новой записи.
                LD (DE), A
                ; Формирование Carry=1 успешного создания, Z сохраняется от адресного преобразователя.
                SCF
                RET

                ; -----------------------------------------
                endmodule
                endmodule
