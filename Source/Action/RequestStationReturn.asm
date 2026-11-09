                module Action
                module RequestStationReturn
                ; Документация [команда возврата к станции](../../Docs/ActionStationReturnCommand.md)
                ; -----------------------------------------
                ; Однократная команда возврата к станции с переходом в банковый подготовитель загрузки
                ; исходная запись 17, перенесённое ядро банка 5, адреса 7606..7629
                ; In:
                ;   HL, DE и BC задают сохраняемый на отказе контекст, AF входного аргумента не задаёт
                ;   CommandDelay допускает обработку только при нуле, ReturnSystem.Value=FF означает отсутствие оборудования
                ;   банк 0 выбран для CursorA, paging разблокирован, Controls банка 1 содержит PrepareStationReload и его CodeSource
                ;   общая область состояния HighPairs и области сохранения удовлетворяют PrepareStationReload, IRQ не вмешиваются до DI
                ;   на пути отказа на CPU-стеке читаемое слово возврата, на принятом пути старый стек намеренно отбрасывается
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, записи и OUT отсутствуют
                ;   при нулевой задержке CursorA получает EE1B, CommandDelay получает 20 до проверки оборудования
                ;   при ReturnSystem.Value=FF HL=EE1B, DE и BC сохраняются, A=0, F=50, paging сохраняется, обычный RET задаёт SP=входной SP+2
                ;   при допуске ReturnSystem.Value получает FF до сохранения состояния, OUT 7FFD получает 19, выбран банк 1 и теневой экран
                ;   следует JP PrepareStationReload, обычного возврата к клавиатурному диспетчеру нет
                ;   на границе PC=4200 получены HL=DE23, DE=4300, BC=0, A=3F, IX и альтернативные регистры сохранены
                ;   768 атрибутов базового экрана обнулены, два байта LowPairs переставлены, 512 байтов состояния сохранены в 4000..41FF с уже записанным ReturnSystem.Value=FF
                ;   256 байтов следующей стадии перенесены в 4200..42FF, IY=5C3A, SP=5FFF, I=3F, IM=1, IFF сброшен, итоговая страница 19
                ;   F и R соответствуют точным формулам PrepareStationReload с входным F от INC кода оборудования, по 5FFD/5FFE остаётся слово 4200
                ; Corrupt:
                ;   HL, DE, BC, AF, IY, SP, I, IM, IFF, R, CommandDelay, CursorA, ReturnSystem.Value, счётчик, атрибуты, блоки сохранения и новый стек на соответствующих путях
                ; Note:
                ;   название оборудования взято из совпавшего авторского описания, его FF расходуется перед переходом и попадает в сохранённый блок
                ;   сканер клавиатуры имеет старую рамку, но успешный путь её не восстанавливает, PrepareStationReload заменяет SP
                ;   1792 сценария исполняют настоящий банковый переход и три LDIR, сверены точные регистры включая R, все банки RAM и кратность записей
                ;   проверка останавливается перед первой инструкцией перенесённого кода 4200, TR-DOS и загрузка STATIONF этой моделью не исполняются
                ; -----------------------------------------
                ; Проверка задержки перед однократным запросом возврата к станции.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, состояние сохранить

                ; Выбор исходного звукового потока до проверки наличия оборудования.
                LD HL, @ActionStationReturnConst.Sound
                LD (@ActionAyEffectState.CursorA), HL
                ; Обновление задержки независимо от последующего отказа по оборудованию.
                LD A, @ActionStationReturnConst.Delay
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Проверка полного кода ReturnSystem.Value, только FF запрещает переход.
                LD A, (@ActionShipEquipment.ReturnSystem.Value)
                INC A
                RET Z                                                           ; выход, если ReturnSystem.Value равен FF, уже выбранные поток и задержку сохранить

                ; Списание системы возврата до сохранения состояния следующим банковым обработчиком.
                LD A, @ActionStationReturnConst.SpentEquipment
                LD (@ActionShipEquipment.ReturnSystem.Value), A
                ; Выбор банка 1 с теневым экраном для настоящего подготовителя загрузки станции.
                LD A, @ActionStationReturnConst.Page
                LD BC, @Hardware.PagingPort
                OUT (C), A
                ; Передача в Controls без рамки CALL, подготовитель заменит CPU-стек и перейдёт в свою копию 4200.
                JP @Controls.PrepareStationReload.Entry

                endmodule
                endmodule
