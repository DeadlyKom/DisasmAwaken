# Изменение сохранённых точек

Самостоятельные входы и общие хвосты отделены от обёрток рисования без изменения байтов. Назначение операций и договоры установлены по исходным байтам, банковым поискам и моделям физических изменений.

- [Station.ToggleStoredMapPoint](../Source/Station/ToggleStoredMapPoint.asm)
- [Station.RefreshStoredMapPanels](../Source/Station/RefreshStoredMapPanels.asm)
- [Station.DrawStoredPointToggle](../Source/Station/DrawStoredPointToggle.asm)
- [Station.RemoveFoundStoredPoint](../Source/Station/RemoveFoundStoredPoint.asm)
- [Station.DrawSecondaryPointToggle](../Source/Station/DrawSecondaryPointToggle.asm)
- [Station.RemoveFoundSecondaryPoint](../Source/Station/RemoveFoundSecondaryPoint.asm)
- [Station.RefreshSecondaryListPanels](../Source/Station/RefreshSecondaryListPanels.asm)
- [Station.CenterCurrentMapPoint](../Source/Station/CenterCurrentMapPoint.asm)
- [Station.CenterKeyAndRefreshMap](../Source/Station/CenterKeyAndRefreshMap.asm)

## Два разных списка

A начинается по 990A, B по 993D, оба содержат по десять физических FStoredMapPoint и ограничителю. Запись имеет FirstWord, SecondWord и Variant. Поиск сравнивает только первые четыре байта. Различие пятого поля не создаёт отдельного ключа и не мешает удалению существующего совпадения. Удаление A заменяет только первый байт FF, четыре оставшихся сохраняются.

ToggleStoredMapPoint сначала пишет VariantPanelState.RefreshPending=1. При найденном ключе удаляет первую совпавшую A. При отсутствии ищет первую физическую FF и записывает туда пять выбранных байтов. Если места нет, возвращается до рисунка, Pending уже установлен.

## Вставка B

[ToggleSecondaryMapPoint](../Source/Station/ToggleSecondaryMapPoint.asm) тоже сначала ставит Pending. Найденный четырёхбайтовый ключ удаляется. При отсутствии ключа возможны три пути вставки.

1. Cursor у FF, запись заменяет текущую пустоту.
2. Следующая запись FF, новая запись помещается сразу после Cursor, курсор переходит к ней.
3. Следующая запись занята, но дальше найдена Hole. LDDR переносит исходный диапазон от Cursor до байта перед Hole на пять байтов вправо. Новый ключ записывается на старом Cursor, а прежняя текущая запись оказывается следующей.

Именно третий путь отличается от второго. В исходном коде Insert=Cursor+5, длина LDDR равна Hole+5-Insert. Конец источника Hole-1, конец приёмника Hole+4, поэтому начало источника равно Cursor. После LDDR HL у Cursor-1, INC HL возвращает Cursor для новой записи. Эта арифметика и все исходные байты сохранены.

При отсутствии места выход происходит до нормализации и рисунка, физические записи не меняются, Pending=1. При успехе Cursor сохраняет фактическую позицию записи, затем RefreshSecondaryPointOrder может дополнительно нормализовать его.

## Удаление и очистка B

RemoveFoundSecondaryPoint получает DE у старшего байта SecondWord найденной записи. Три DEC возвращают начало записи. Если следующий первый байт уже 7F..FE, переноса нет. Иначе LDIR копирует весь физический остаток до байта перед концом на пять байтов влево, включая пустоты FF. Только первый байт последней освобождённой записи становится FF, четыре остальных сохраняются. Сам ограничитель не переносится.

[ClearSecondaryMapPoints](../Source/Station/ClearSecondaryMapPoints.asm) ставит Cursor к началу B и заменяет первые байты на FF до точного CP 80. Другие отрицательные коды не являются концом именно этого прохода. Затем нормализуются курсор, число и плотные смещения B. Нормализатор сначала ищет назад положительный байт, и лишь потом ограничивает адрес снизу, поэтому читаемость предшествующих данных является обязательным условием даже при полностью пустом B.

## Выбор курсоров и центрирование

[SelectSecondaryListCursor](../Source/Station/SelectSecondaryListCursor.asm) ищет выбранный ключ в B. При совпадении Cursor получает начало первой совпавшей записи, затем выполняется общий рисунок. Таблица порядка этим путём не пересчитывается. При отсутствии Cursor сохраняется, рисунка нет, Pending уже установлен.

[CycleStoredMapPoint](../Source/Station/CycleStoredMapPoint.asm) использует отдельный изменяемый операнд по 7C99. Первый байт A.Point00==FF немедленно запрещает весь цикл, даже если дальше есть занятые записи. Иначе поиск начинается со следующей физической позиции, FF пропускаются, первый байт 7F..FE возвращает выбор к Point00 без нового чтения её маркера. Два слова передаются в CenterKeyAndRefreshMap, пятое поле не читается напрямую.

CenterCurrentMapPoint передаёт текущие два слова и ставит Pending=1, текущий Variant не читается. Общий CenterKeyAndRefreshMap выбирает абсолютную страницу 11, вызывает SelectMapPoint, который заново ищет Variant по первому совпадению A и центрирует начало карты. Затем абсолютная страница 10 возвращает станцию и выполняется общий рисунок. Нулевой полуразмер вычитает 256 по оригинальной формуле CenterMapView, это не исправляется. Самостоятельный общий вход Pending не ставит.

## Общие хвосты и разные маркеры

RefreshStoredMapPanels делает BeginScreenUpdate, условный TryDrawSystemInfo, безусловный DrawMapPanel и EndScreenUpdate. Окно сведений отдельно не сохраняется, следующая карта задаёт собственное окно. В конце CurrentPage=10, после обычного успешного содержимого ScreenRequest=ClipRequest=0, SectorRequest=1. Снимок банка 7 содержит прежний экран до удаления указателя. RefreshSecondaryListPanels перед этим хвостом выполняет настоящий банковый RefreshSecondaryPointOrder.

Исходные трактовки маркеров различаются. FindStoredMapPoint и FindSecondaryMapPoint допускают 7F как положительный ключ. Поиск места B и цикл A проверяют Sign после INC, поэтому 7F уже завершает их проход. Очистка B сравнивает ровно 80. FF при поиске ключей и цикле является пустотой. Разные условия сохранены и описаны у каждого входа, общий выдуманный универсальный маркер не введён.

Для последовательного исполнения отделены самостоятельные входы 7B9B,7BAE,7C24,7C4A,7D14. Чистые шестибайтовые обёртки DrawStoredPointToggle и DrawSecondaryPointToggle выполняют LD HL с собственным индексом и хвостовой JP в DrawCenteredItem. Соседние входы удаления не являются их продолжением. Стековые FSecondaryInsertFrame и FSecondaryDeleteFrame описывают существующие PUSH и не выделяют новых областей памяти.

## Проверка

[CheckStoredPointEdits](../Tools/Disasm/Research/CheckStoredPointEdits.py) и [отчёт](../Tools/Disasm/Reports/StoredPointEditsVerification.json) проверяют 41984 случая исходных изменений и выборов. Это 5376 переключений A, по 10240 вставок и удалений B, 1024 очистки B, 2816 установок курсора B, 10240 циклических выборов A и 2048 центрирований до общего рисунка. Все 1024 схемы пустот и десять курсоров покрыты, 1793 вставки выполнили реальный LDDR. Сравниваются все физические байты обоих списков, сохранность полей пустот, указатели и результаты центрирования.

[CheckStoredPointRefresh](../Tools/Disasm/Research/CheckStoredPointRefresh.py) и [отчёт](../Tools/Disasm/Reports/StoredPointRefreshVerification.json) отдельно исполняют 88 полных общих хвостов с исходными нормализатором, рамкой, информационной панелью и сценой карты. Проверены количества B=0..10, обе исходные страницы 10 и 18, снимок банка 7, итоговые запросы и таблица порядка. Явно пробуждены 220 HALT. Независимый oracle всего bitmap этой композиции не заявлен. Ни одна из этих проверок не выполняет сборку, аппаратные IRQ или нативную игру.

## События элементов и отложенное действие

Шесть событий имеют исходные десять байтов JP Action, LD HL,операция, CALL ActivateInterfaceCallback, RET. Вход Action расположен по Entry+3 и используется диспетчером. Общий помощник сначала сохраняет адрес операции в NextCallback, затем выбирает интерактивную геометрию, переключение границ либо активацию. Сохранение адреса не означает немедленного исполнения изменения списка. На нулевом селекторе может выполниться только геометрическое действие. Для внешнего Entry требуется исходный JP, тогда как Action обходит только этот префикс. Договоры составлены из точных десяти байтов и [ActivateInterfaceCallback](../Source/Station/ActivateInterfaceCallback.asm), самостоятельная нативная проверка событий этим не заявлена.

- [HandleStoredPointToggle](../Source/Station/HandleStoredPointToggle.asm)
- [HandleSecondaryPointToggle](../Source/Station/HandleSecondaryPointToggle.asm)
- [HandleSecondaryClear](../Source/Station/HandleSecondaryClear.asm)
- [HandleStoredPointCycle](../Source/Station/HandleStoredPointCycle.asm)
- [HandleCurrentMapCenter](../Source/Station/HandleCurrentMapCenter.asm)
- [HandleSecondaryCursor](../Source/Station/HandleSecondaryCursor.asm)
