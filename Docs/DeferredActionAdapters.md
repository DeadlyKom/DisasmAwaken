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


## Входной HL обёртки и побочные эффекты

Семь установщиков сначала загружают собственную цель в HL, затем вызывают ActivateInterfaceCallback. Поэтому на пути A=0 с выполненной интерактивной геометрией сохранённый общим помощником HL равен адресу новой цели, а не исходному HL обёртки. То же различие действует на пути ненулевого A. Ни одна из этих ветвей не исполняет новый callback непосредственно в установщике. Пути ToggleItemBounds и ActivateItem сохраняют свои отдельные договоры.

Уточнённые договоры относятся к InstallShipTradeCallback, InstallHelpPanelsCallback, InstallMissionOfferCallback, InstallFlightButtonCallback, InstallContractMapCallback, InstallGalaxyNewsCallback и InstallMapPanelsCallback. H' сохраняется, только L' является рабочим на перерисовке, AF' рабочий на том же пути, IY сохраняется. Corrupt включает R, NextCallback, побочные записи выбранного помощника и временную RAM CPU-стека. Запись NextCallback выполняется до выбора ветви A и до результата геометрии.

[Факты семейства](../Tools/Disasm/Research/DeferredActionAdapterFacts.py) исправляют прежнюю подстановку формулировки HL, не меняя общий алгоритм или код установщиков. [Существующая композиционная модель](../Tools/Disasm/Research/CheckDeferredActionAdapters.py) содержит по 1024 профиля для каждой из семи обёрток, все A и оба значения Carry события. [Отчёт](../Tools/Disasm/Reports/DeferredActionAdaptersVerification.json) отдельно ограничивает независимость bitmap, музыку, нативное выполнение и 256 временных байтов стека фикстуры, сохранённый SP настоящего IRQ сверяется отдельно. Уточнение договоров не расширяет эти границы и не требует повторного исполнения неизменённой модели.
