# Пять пустых наведений панелей

Назначение установлено по физическим FInterfaceItem, указателю EventHandler и исходным CP866-заголовкам, не по соседству адресов. Каждая обёртка содержит один исходный JP в отдельный RET. Основное действие Entry+3 при этом не вызывается.

| Панель | Запись | JP-обёртка | Пустой обработчик |
| --- | --- | --- | --- |
| Карта галактики | 11 | [HandleGalaxyMapHover](../Source/Station/HandleGalaxyMapHover.asm), 6C0A | [IgnoreGalaxyMapHover](../Source/Station/IgnoreGalaxyMapHover.asm), 6D43 |
| Инфо о системе | 19 | [HandleSystemInfoHover](../Source/Station/HandleSystemInfoHover.asm), 7676 | [IgnoreSystemInfoHover](../Source/Station/IgnoreSystemInfoHover.asm), 7687 |
| Карта системы | 20 | [HandleSystemMapHover](../Source/Station/HandleSystemMapHover.asm), 7838 | [IgnoreSystemMapHover](../Source/Station/IgnoreSystemMapHover.asm), 7884 |
| Контракт | 32 | [HandleContractHover](../Source/Station/HandleContractHover.asm), AA55 | [IgnoreContractHover](../Source/Station/IgnoreContractHover.asm), AA84 |
| Добро пожаловать! | 45 | [HandleWelcomeHover](../Source/Station/HandleWelcomeHover.asm), 7948 | [IgnoreWelcomeHover](../Source/Station/IgnoreWelcomeHover.asm), 7954 |

Все основные, альтернативные и индексные регистры, полный AF, I, IM и IFF сохраняются. SP после RET равен входному+2, память, bitmap, список рисования, курсор, страница и порты не меняются. Новый кадр CALL не создаётся. Наведение не запускает действие, выбор строки, перерисовку либо закрытие. Это контракт только двух указанных входов каждой панели, отдельные действия за ними остаются самостоятельными алгоритмами.

[CheckPassivePanelHovers](../Tools/Disasm/Research/CheckPassivePanelHovers.py) проверяет EventHandler всех пяти [физических записей](../Source/Station/Data/InterfaceItems.asm), реальные байты JP/RET и текст заголовков. [Отчёт](../Tools/Disasm/Reports/PassivePanelHoversVerification.json) содержит 327680 вызовов обёрток и 327680 прямых RET, для каждой точки проверены все 65536 AF, прочий контекст, все восемь банков и отсутствие OUT. Сборка, IRQ и нативный запуск не выполнялись.
