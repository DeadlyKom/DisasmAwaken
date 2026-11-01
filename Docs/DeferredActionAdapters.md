# Установка отложенных действий

Семь исходных обработчиков имеют одинаковую композицию, JP во внутренний вход, LD HL адреса цели, CALL [ActivateInterfaceCallback](../Source/Station/ActivateInterfaceCallback.asm), RET. Входной HL параметром не является, DE задаёт выбранную запись интерфейса, AF селектор общего действия.

| Установщик | Адрес | Отложенная цель |
|---|---|---|
| [InstallShipTradeCallback](../Source/Station/InstallShipTradeCallback.asm) | `#79BD` | [ConfirmShipModelTrade](../Source/Station/ConfirmShipModelTrade.asm) |
| [InstallHelpPanelsCallback](../Source/Station/InstallHelpPanelsCallback.asm) | `#7A88` | [OpenHelpPanels](../Source/Station/OpenHelpPanels.asm) |
| [InstallMissionOfferCallback](../Source/Station/InstallMissionOfferCallback.asm) | `#AA33` | [RefreshMissionOfferPanels](../Source/Station/RefreshMissionOfferPanels.asm) |
| [InstallFlightButtonCallback](../Source/Station/InstallFlightButtonCallback.asm) | `#7B46` | [EmptyFlightCallback](../Source/Station/EmptyFlightCallback.asm) |
| [InstallContractMapCallback](../Source/Station/InstallContractMapCallback.asm) | `#7CBC` | [CenterContractMap](../Source/Station/CenterContractMap.asm) |
| [InstallGalaxyNewsCallback](../Source/Station/InstallGalaxyNewsCallback.asm) | `#7AA4` | [OpenGalaxyNewsPanel](../Source/Station/OpenGalaxyNewsPanel.asm) |
| [InstallMapPanelsCallback](../Source/Station/InstallMapPanelsCallback.asm) | `#7ABA` | [OpenMapPanelGroup](../Source/Station/OpenMapPanelGroup.asm) |

Общий обработчик прежде всего записывает адрес в `ActiveItemState.NextCallback`. При A=0 он пробует интерактивную геометрию, а если действия нет, переключает сохранённую и большую геометрию через ToggleItemBounds. Этот путь возвращает Carry и не устанавливает новую активную цель.

При ненулевом A выполняется ActivateItem. Он переносит выбранный элемент в конец списка, при необходимости закрывает прежний активный элемент и меняет контур. Затем записывает выбранную цель в `ActiveItemState.Callback`. В его выходном Carry находится bit7 `InterfaceState.EventCode`, поэтому Carry этого пути не следует принимать за результат исполнения новой цели.

Новая цель в этих обёртках не вызывается. Выполнение возложено на последующий внешний вызов callback, в частности механизм [закрытия активного элемента](ActiveItem.md). Подтверждение сделки, открытие справки и генерация предложения имеют самостоятельные входные договоры. Одной установки их адреса недостаточно для выполнения этих алгоритмов.

[CheckDeferredActionAdapters.py](../Tools/Disasm/Research/CheckDeferredActionAdapters.py) проверяет 7168 пар запусков обёртки и прямого общего обработчика. Охвачены все 256 селекторов, EventCode с нулевым и установленным старшим битом, уже установленный контур и запрет его переключения. Сверены регистры, порты и память вне 256 байтов CPU-стека фикстуры. Адреса NextCallback и Callback проверены независимо, достижение новой цели запрещено наблюдателем. [Отчёт](../Tools/Disasm/Reports/DeferredActionAdaptersVerification.json).

При активации исполняется настоящий IM2, музыка выключена. Дополнительный CALL обёртки уменьшает физический SP прерываемого кода на два. Поэтому `StationIrqState.SavedSP` сверяется отдельно с точным ожидаемым адресом, остальные различия памяти не игнорируются. Независимый bitmap, сборка и нативная игра здесь не проверялись.
