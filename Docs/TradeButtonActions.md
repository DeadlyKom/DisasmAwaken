# Обработчики четырёх кнопок торгового режима

Обработчик каждой кнопки выбирает адрес продолжения в HL, вызывает [ActivateInterfaceCallback](../Source/Station/ActivateInterfaceCallback.asm), после его возврата последовательно исполняет соседнюю процедуру выбора режима. Адрес продолжения одновременно сохраняется как следующая цель callback. Между файлами нет дополнительной инструкции JP либо CALL, поэтому порядок включения жёсткий.

| Обработчик, include (0) | Адрес | Продолжение, include (1) |
|---|---|---|
| [HandleShipSaleButton](../Source/Station/HandleShipSaleButton.asm) | `#7A1B` | [SelectSaleMode](../Source/Station/SelectSaleMode.asm) |
| [HandleShipPurchaseButton](../Source/Station/HandleShipPurchaseButton.asm) | `#7A5B` | [SelectPurchaseMode](../Source/Station/SelectPurchaseMode.asm) |
| [HandleEquipmentPurchaseButton](../Source/Station/HandleEquipmentPurchaseButton.asm) | `#7B11` | [SelectEquipmentPurchase](../Source/Station/SelectEquipmentPurchase.asm) |
| [HandleEquipmentSaleButton](../Source/Station/HandleEquipmentSaleButton.asm) | `#7B2B` | [SelectEquipmentSale](../Source/Station/SelectEquipmentSale.asm) |

При нулевом селекторе общий обработчик пробует геометрию либо переключает её сохранённый вариант. Он возвращает Carry, после чего первая RET C продолжения запрещает смену режима. При ненулевом селекторе происходит активация. Её выходной Carry равен bit7 InterfaceState.EventCode, этот бит также может запретить немедленную смену режима. Само сохранение callback происходит до этих решений.

Разрешённые корабельные продолжения сбрасывают строку будущей 3D-модели в банке 4, устанавливают запрос отложенной перерисовки и переключают контуры двух кнопок. Продажа при собственном типе FF возвращает режим покупки. [Точный договор корабельных режимов](ModelTradeMode.md).

Разрешённые продолжения оснащения записывают полный OwnedMode, ноль для покупки либо единицу для продажи, и переключают контуры двух кнопок. Они не исполняют торговый LANG. [Точный договор режима оснащения](EquipmentTradeMode.md), [потребитель режима и сделка](EquipmentTrade.md).

[CheckTradeButtonActions.py](../Tools/Disasm/Research/CheckTradeButtonActions.py) сравнивает 2058 пар полных запусков с последовательной композицией тех же исходных помощников. Охвачены все байты селектора и обе ветви bit7 события для каждой кнопки, отдельно отсутствие собственного корабля при продаже. Режим, NextCallback, активный Callback, сброс строки банка 4 и запрос перерисовки проверены независимыми условиями. Сверены все общие, альтернативные и индексные регистры, порты и память вне 256 байтов CPU-стека фикстуры. [Отчёт](../Tools/Disasm/Reports/TradeButtonActionsVerification.json).

В этой модели у новой кнопки уже установлен контур, дополнительные IRQ активации не требуются. Геометрические и контурные помощники имеют собственные проверки. Независимый bitmap всего действия, сборка и нативная игра не подтверждены.
