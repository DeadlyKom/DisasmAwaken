"""Подтверждённые условия интерфейса, без выдуманных назначений неизвестных битов."""

NOTES = {}
COMMENTS = {
    0xBDA8: (["обнуление накопленной ширины перед просмотром текста"], None),
    0xBDAD: (["проверка безусловного ограничителя возврата каретки"], None),
    0xBDAF: ([], "переход, если найден CR, возвращается накопленная ширина"),
    0xBDB1: (["проверка второго безусловного ограничителя перевода строки"], None),
    0xBDB3: ([], "переход, если найден LF, возвращается накопленная ширина"),
    0xBDB5: (["проверка дополнительного разделителя, переданного в B"], None),
    0xBDB6: ([], "переход, если символ равен разделителю B, возвращается накопленная ширина"),
    0xBDB8: (["выбор ширины текущего символа по его восьмибитному коду"], None),
    0xBDBA: (["расчёт новой суммарной ширины в байтовом накопителе"], None),
    0xBDBB: ([], "переход, если сумма ширин превысила 255, возвращается насыщение #FF"),
    0xBDBD: ([], "переход, если байтовая сумма ширин равна нулю, исходный алгоритм также выбирает насыщение"),
    0xBDBF: (["продвижение только после принятия ширины текущего символа"], None),
    0xBDC4: (["выбор #FF без потребления символа, вызвавшего насыщение"], None),
    0xBDC6: (["возврат накопленной ширины с флагами последнего сравнения либо сложения"], None),
    0xBDCD: (["обнуление накопленной ширины с сохранением исходного указателя на стеке"], None),
    0xBDD2: (["проверка безусловного ограничителя CR"], None),
    0xBDD4: ([], "переход, если найден CR, возвращается накопленная ширина"),
    0xBDD6: (["проверка безусловного ограничителя LF"], None),
    0xBDD8: ([], "переход, если найден LF, возвращается накопленная ширина"),
    0xBDDA: (["проверка дополнительного разделителя из B"], None),
    0xBDDB: ([], "переход, если символ равен разделителю B, измерение завершается"),
    0xBDDD: (["выбор ширины по коду символа, внутренний указатель продвигается до проверки суммы"], None),
    0xBDE0: (["расчёт новой суммарной ширины перед проверкой насыщения"], None),
    0xBDE1: ([], "переход, если сумма ширин превысила 255, возвращается #FF"),
    0xBDE3: ([], "переход, если байтовая сумма равна нулю, выбирается исходное насыщение #FF"),
    0xBDE9: (["выбор насыщенной ширины, исходный HL затем восстановится со стека"], None),
    0xBDEB: (["возврат ширины без изменения флагов последней проверки"], None),
    0xBFAD: (["сохранение исходного индекса до чтения геометрии записи"], None),
    0xBFAE: (["выбор начала FInterfaceItem по нулевому смещению поля"], None),
    0xBFB2: (["чтение X, Y, Width и Height в C, B, E и D"], None),
    0xBFBA: (["настройка текстового окна по исходной геометрии до экранного отсечения"], None),
    0xBFBD: (["проверка знака левой байтовой колонки элемента"], None),
    0xBFBF: ([], "переход, если левая колонка неотрицательна, проверяется правый край"),
    0xBFC2: (["расчёт ширины после пропуска отрицательных колонок"], None),
    0xBFC9: (["расчёт исключённой правой колонки исходного прямоугольника"], None),
    0xBFCA: (["проверка, что правая граница не превышает 32 колонки"], None),
    0xBFCC: ([], "переход, если правая граница не превышает 32, ширина сохраняется"),
    0xBFCF: (["расчёт ширины до правого края экрана"], None),
    0xBFD5: (["проверка знака верхней строки знакомест элемента"], None),
    0xBFD7: ([], "переход, если верхняя строка неотрицательна, проверяется нижний край"),
    0xBFDA: (["расчёт высоты после пропуска отрицательных строк знакомест"], None),
    0xBFE1: (["расчёт исключённой нижней строки исходного прямоугольника"], None),
    0xBFE2: (["проверка, что нижняя граница не превышает 24 строки знакомест"], None),
    0xBFE4: ([], "переход, если нижняя граница не превышает 24, высота сохраняется"),
    0xBFE7: (["расчёт высоты до нижнего края экрана"], None),
    0xBFED: (["замена сохранённого индекса указателем Flags, индекс передаётся регистрации через HL"], None),
    0xBFEE: (["регистрация видимых знакомест до фактической заливки bitmap"], None),
    0xBFF1: (["возврат указателя Flags для дальнейшего обработчика рисования элемента"], None),
    0xBEB0: (["сохранение геометрии отдельно от исходного ключа регистрации"], None),
    0xBEB1: (["передача ключа в DE для снятия первой прежней регистрации"], None),
    0xBEB5: (["поиск первой пары со старшим байтом #FF, указатель подготовлен за два шага до первого старшего байта"], None),
    0xBEBA: (["проверка признака свободной пары через переполнение #FF в ноль"], None),
    0xBEBC: ([], "переход, если старший байт не равен #FF, поиск свободной пары продолжается без ограничителя страницы"),
    0xBEBF: (["запись ключа регистрации в найденную пару, сначала старший байт"], None),
    0xBEC2: (["расчёт однобайтового владельца, половина младшего адреса пары плюс один"], None),
    0xBEC5: (["восстановление исходной геометрии перед её отсечением по экрану"], None),
    0xBEC6: (["сохранение кода владельца в альтернативном AF до начала заполнения карты"], None),
    0xBEC7: (["проверка знака левой колонки регистрируемого прямоугольника"], None),
    0xBEC9: ([], "переход, если левая колонка неотрицательна, проверяется правая граница"),
    0xBECC: (["расчёт ширины после пропуска отрицательных колонок"], None),
    0xBED3: (["расчёт исключённой правой колонки прямоугольника"], None),
    0xBED4: (["проверка, что правая граница не превышает 32 колонки"], None),
    0xBED6: ([], "переход, если правая граница не превышает 32, ширина сохраняется"),
    0xBED9: (["расчёт ширины до правого края экрана"], None),
    0xBEDF: (["проверка знака верхней строки знакомест прямоугольника"], None),
    0xBEE1: ([], "переход, если верхняя строка неотрицательна, проверяется нижняя граница"),
    0xBEE4: (["расчёт высоты после пропуска отрицательных строк знакомест"], None),
    0xBEEB: (["расчёт исключённой нижней строки прямоугольника"], None),
    0xBEEC: (["проверка, что нижняя граница не превышает 24 строки"], None),
    0xBEEE: ([], "переход, если нижняя граница не превышает 24, высота сохраняется"),
    0xBEF1: (["расчёт высоты до нижнего края экрана"], None),
    0xBEF7: (["получение адреса первого видимого знакоместа в карте владельцев"], None),
    0xBEFA: (["сохранение видимой высоты в счётчике строк карты"], None),
    0xBEFB: (["расчёт пропуска развёрнутых записей и шага после последнего байта строки"], None),
    0xBF00: (["запись смещения JR, ограничивающего заполнение видимой шириной"], None),
    0xBF03: (["расчёт линейного шага 33 минус видимая ширина после последней записи строки"], None),
    0xBF06: (["возврат сохранённого кода владельца в A для заполнения всей видимой области"], None),
    0xBF07: (["пропуск ненужных записей, операнд JR подготовлен через CellSpanSkip"], None),
    0xBF09: (["заполнение очередной строки карты одним кодом владельца"], None),
    0xBF48: (["расчёт адреса той же начальной колонки следующей строки карты"], None),
    0x9EC7: (["подготовка перекрывающегося заполнения всех 768 ячеек карты нулевым владельцем"], None),
    0x9ED0: (["обнуление первой ячейки значением младшего байта адреса #8600"], None),
    0x9ED1: (["распространение первого нуля на оставшиеся 767 байтов карты"], None),
    0x9EDA: (["подготовка исходной инициализации первых 128 байтов индексной таблицы"], None),
    0x9EE3: (["запись первого свободного байта для последующего распространения"], None),
    0x9EE5: (["заполнение остальных 127 байтов, вторая половина страницы не затрагивается"], None),
    0x9D96: (["чтение пиксельных координат указателя, младший байт X и старший Y"], None),
    0x9D9A: (["расчёт строки знакомест делением пиксельного Y на восемь"], None),
    0x9DA0: (["расчёт колонки знакомест делением пиксельного X на восемь"], None),
    0x9DA6: (["расчёт старшей страницы карты по битам 4 и 3 строки знакомест"], None),
    0x9DAF: (["расчёт младшего строкового вклада, три младших бита строки задают группы по 32 байта"], None),
    0x9DB6: (["расчёт младшего байта адреса с колонкой без переноса в H"], None),
    0x9DB8: (["чтение кода владельца, выходные флаги остаются от адресного сложения"], None),
    0xBE92: (["поиск индексной пары в пределах одной страницы таблицы"], None),
    0xBE95: (["чтение и проверка младшего байта очередной пары"], None),
    0xBE98: ([], "переход, если младший байт пары совпал, требуется проверка старшего"),
    0xBE9A: (["переход к младшему байту следующей пары с проверкой переполнения страницы"], None),
    0xBE9B: ([], "переход, если младший адрес не переполнился, поиск продолжается в той же странице"),
    0xBEA0: (["чтение и проверка старшего байта после совпадения младшего"], None),
    0xBEA2: ([], "переход, если оба байта пары совпали, старший байт помечается свободным"),
    0xBEA4: (["переход к следующей паре после несовпадения старшего байта"], None),
    0xBEA5: ([], "переход, если младший адрес не переполнился, поиск продолжается"),
    0xBEAA: (["освобождение первой совпавшей пары заменой её старшего байта на #FF"], None),
    0x6397: (["сохранение полного входного байта, его старшие биты также участвуют в последующем OR"], None),
    0x6398: (["чтение старших управляющих битов из текущей тени порта"], None),
    0x639D: (["расчёт нового байта страницы объединением сохранённых старших битов со всем входным A"], None),
    0x63A0: (["обновление тени до выполнения аппаратной записи"], None),
    0x63A3: (["подготовка полного адреса порта управления страницами"], None),
    0x63A6: (["передача полного байта A в порт, прерывания этим входом не запрещаются"], None),
    0x63F3: (["чтение первой пары проверяемых слов без изменения их содержимого"], None),
    0x63FA: (["объединение байтов первой пары, ненулевой разряд исключает полностью нулевое состояние"], None),
    0x63FE: (["чтение второй пары проверяемых слов"], None),
    0x6405: (["объединение второй пары с результатом первой, Carry и HalfCarry сбрасываются"], None),
    0xC234: (["начальная позиция внутреннего окна, CursorX равен единице и CursorY равен нулю"], None),
    0xC23A: (["подготовка нулевого знакового расширения координаты X"], None),
    0xC23B: (["проверка исходного знака горизонтальной координаты знакомест"], None),
    0xC23D: ([], "переход, если X неотрицателен, модуль уже находится в A"),
    0xC240: (["получение модуля отрицательной горизонтальной координаты"], None),
    0xC242: (["расчёт пиксельного начала X по исходному преобразованию T"], None),
    0xC245: (["проверка исходного знака X для восстановления знакового начала"], None),
    0xC247: ([], "переход, если X неотрицателен, старший байт начала остаётся нулевым"),
    0xC24A: (["восстановление отрицательного X и его знакового расширения"], None),
    0xC24D: (["расчёт младшего байта начала X с внутренним отступом, перенос в старший байт не добавляется"], None),
    0xC256: (["подготовка нулевого знакового расширения координаты Y"], None),
    0xC258: (["проверка исходного знака вертикальной координаты знакомест"], None),
    0xC25A: ([], "переход, если Y неотрицателен, модуль уже находится в A"),
    0xC25D: (["получение модуля отрицательной вертикальной координаты"], None),
    0xC25F: (["расчёт пиксельного начала Y по исходному преобразованию T"], None),
    0xC262: (["проверка исходного знака Y для восстановления знакового начала"], None),
    0xC264: ([], "переход, если Y неотрицателен, старший байт начала остаётся нулевым"),
    0xC267: (["восстановление отрицательного Y и его знакового расширения"], None),
    0xC26A: (["расчёт младшего байта начала Y с внутренним отступом без исправления переноса"], None),
    0xC273: (["расчёт пиксельной ширины по T с последующим уменьшением на четыре"], None),
    0xC27C: (["расчёт пиксельной высоты по T с последующим уменьшением на одиннадцать"], None),
    0xBFF5: (["сохранение индекса элемента до получения указателя его геометрии"], None),
    0xBFF6: (["выбор первого физического поля записи, координаты X"], None),
    0xBFFA: (["чтение исходных X, Y и ширины в C, B и E"], None),
    0xC000: (["чтение высоты и переход к адресу Flags без чтения самих флагов"], None),
    0xC002: (["настройка текстового окна по исходной геометрии до экранного отсечения"], None),
    0xC005: (["проверка знака левой байтовой колонки элемента"], None),
    0xC007: ([], "переход, если левая колонка неотрицательна, проверяется правый край"),
    0xC00A: (["расчёт оставшейся ширины после пропуска отрицательных колонок"], None),
    0xC011: (["расчёт исключённой правой колонки исходного прямоугольника"], None),
    0xC012: (["проверка, что правая граница не превышает 32 колонки"], None),
    0xC014: ([], "переход, если правая граница не превышает 32, ширина сохраняется"),
    0xC017: (["расчёт ширины до правого края экрана, 32 минус исходная колонка"], None),
    0xC01D: (["проверка знака верхней строки знакомест элемента"], None),
    0xC01F: ([], "переход, если верхняя строка неотрицательна, проверяется нижний край"),
    0xC022: (["расчёт оставшейся высоты после пропуска отрицательных строк знакомест"], None),
    0xC029: (["расчёт исключённой нижней строки исходного прямоугольника"], None),
    0xC02A: (["проверка, что нижняя граница не превышает 24 знакоместа"], None),
    0xC02C: ([], "переход, если нижняя граница не превышает 24, высота сохраняется"),
    0xC02F: (["расчёт высоты до нижнего края экрана, 24 минус исходная строка"], None),
    0xC035: (["восстановление исходного индекса перед хвостовым переходом к заполнению bitmap"], None),
    0xC03A: (["обнуление относительного пиксельного курсора нового текстового окна"], None),
    0xC040: (["проверка знака горизонтального начала окна в знакоместах"], None),
    0xC042: ([], "переход, если горизонтальное начало неотрицательно, модуль уже находится в A"),
    0xC045: (["получение модуля отрицательной горизонтальной координаты перед масштабированием"], None),
    0xC047: (["расчёт младшего байта горизонтального начала по исходному преобразованию T"], None),
    0xC04A: (["проверка исходного знака X для восстановления знака пиксельного начала"], None),
    0xC04C: ([], "переход, если X неотрицателен, старший байт начала остаётся нулевым"),
    0xC04F: (["восстановление отрицательного младшего байта X и его знакового расширения"], None),
    0xC052: (["запись горизонтального начала в операнды текстового вывода"], None),
    0xC059: (["подготовка нулевого знакового расширения для вертикального начала"], None),
    0xC05B: (["проверка знака вертикального начала окна в знакоместах"], None),
    0xC05D: ([], "переход, если вертикальное начало неотрицательно, модуль уже находится в A"),
    0xC060: (["получение модуля отрицательной вертикальной координаты перед масштабированием"], None),
    0xC062: (["расчёт младшего байта вертикального начала по исходному преобразованию T"], None),
    0xC065: (["проверка исходного знака Y для восстановления знака пиксельного начала"], None),
    0xC067: ([], "переход, если Y неотрицателен, старший байт начала остаётся нулевым"),
    0xC06A: (["восстановление отрицательного младшего байта Y и его знакового расширения"], None),
    0xC06D: (["запись вертикального начала в операнды текстового вывода"], None),
    0xC074: (["расчёт пиксельной ширины по исходному преобразованию T, отсечения здесь нет"], None),
    0xC07B: (["расчёт пиксельной высоты по тому же преобразованию без нормализации больших значений"], None),
    0xA3FF: (["сохранение начала X и Y в младших изменяемых операндах восстановителя"], None),
    0xA40B: (["сохранение знакового расширения начала текстового окна"], None),
    0xA417: (["сохранение пиксельных размеров текстового окна"], None),
    0xA423: (["сохранение относительного курсора до переключения окна"], None),
    0xA42F: (["сохранение режима текста, назначение отдельных разрядов ещё не установлено"], None),
    0xA436: (["восстановление младших байтов начала X и Y из последнего снимка"], None),
    0xA440: (["восстановление знакового расширения начала окна"], None),
    0xA44A: (["восстановление пиксельной ширины и высоты"], None),
    0xA454: (["восстановление байта режима текстового вывода"], None),
    0xA459: (["восстановление относительного курсора X и Y"], None),
    0xC3A5: ([], "переход, если бит 0 типа рамки сброшен, выбирается рамка со скосами"),
    0x9EEE: (["расчёт смещения записи, индекс умножается на физический размер FInterfaceItem"], None),
    0x9EF2: (["расчёт младшей части адреса поля от младшего байта базы #F0FD"], None),
    0x9EF6: (["учёт переноса смещения поля в старший байт базы таблицы"], None),
    0x9EFB: (["расчёт полного указателя поля после прибавления смещения записи"], None),
    0x9EFC: (["подготовка выходных флагов по старшему байту базы со смещением, Carry сбрасывается"], None),
    0xC628: (["расчёт байтового индекса строки знакомест умножением B на восемь"], None),
    0xC62F: (["выбор старшего и младшего байтов адреса из соседних страниц таблицы строк"], None),
    0xC635: (["расчёт горизонтального табличного индекса умножением C на восемь"], None),
    0xC63C: (["объединение младших вкладов экранной строки и колонки"], None),
    0xC63F: (["расчёт пропуска лишних пар записи, остаётся ровно E байтов в каждой строке"], None),
    0xC646: (["проверка бита 0 режима заполнения, остальные разряды на этот вход не влияют"], None),
    0xC64C: ([], "переход, если бит 0 режима сброшен, сохраняется заполнение #FF"),
    0xC64E: (["выбор нулевого байта при установленном бите 0 режима"], None),
    0xC64F: (["запись выбранного байта в изменяемый операнд внутреннего цикла"], None),
    0xC652: (["начало восьми пиксельных строк очередного знакоместа по высоте"], None),
    0xC654: (["сохранение исходной байтовой колонки перед развёрнутой записью"], None),
    0xC655: (["загрузка байта, выбранного через RectangleByte до начала рисования"], None),
    0xC657: (["пропуск лишних пар записи через подготовленный RectangleSkip"], None),
    0xC659: (["запись выбранного числа байтов одной пиксельной строки"], None),
    0xC699: (["восстановление исходной колонки перед следующей пиксельной строкой"], None),
    0xC69C: ([], "переход, если остаются пиксельные строки текущего знакоместа"),
    0xC69F: (["расчёт младшего байта адреса следующей строки знакомест"], None),
    0xC6A3: ([], "переход, если младший байт переполнился, старшая часть уже соответствует следующей трети экрана"),
    0xC6A5: (["компенсация восьми увеличений H внутри текущей трети экрана"], None),
    0xC6A9: (["проверка оставшейся высоты после полного знакоместа"], None),
    0xC6AA: ([], "переход, если остаются строки знакомест прямоугольника"),
    0xC093: (["перенос бита 0 типа верхней полосы в Carry, остальные биты типа на рисунок не влияют"], None),
    0xC097: ([], "переход, если бит 0 типа сброшен, верхняя полоса остаётся с пустой серединой"),
    0xC099: (["выбор заполненной середины верхней полосы с боковыми пропусками"], None),
    0xC09C: (["запись установщика узора в операнд первого CALL продолжения FinishBandFrame"], None),
    0xC09F: (["расчёт внутренней ширины без двух крайних байтов рамки"], None),
    0xC0A1: (["расчёт числа средних знакомест без двух верхних и одного нижнего"], None),
    0xC0A7: (["расчёт смещения пропуска неиспользуемых пар записи средних байтов"], None),
    0xC0AE: (["сохранение счётчика высоты до замены DE байтовыми узорами"], None),
    0xC0AF: (["проверка видимости первого верхнего знакоместа"], None),
    0xC0B2: ([], "выход, если верхнее знакоместо достигло нижней границы экрана"),
    0xC0B3: ([], "переход, если верхнее знакоместо выше экрана, его первые три строки пропускаются"),
    0xC0B6: (["обнуление первой пиксельной строки верхней полосы"], None),
    0xC0BC: (["рисование шести средних пикселей в крайних байтах второй строки"], None),
    0xC0C2: (["выбор боковых пикселей для третьей строки"], None),
    0xC0C8: (["сброс Sign перед последовательным продолжением видимой верхней полосы"], None),
    0xC0C9: (["выбор изменяемого узора, адрес первого CALL задаёт StationRaster.BandPattern"], None),
    0xC0CC: ([], "переход, если верхнее знакоместо выше экрана, оставшиеся пять строк пропускаются"),
    0xC0DE: (["коррекция адреса после восьми пиксельных строк верхнего знакоместа"], None),
    0xC0E1: (["проверка видимости второго знакоместа с горизонтальным разделителем"], None),
    0xC0E4: ([], "выход, если знакоместо разделителя достигло нижней границы экрана"),
    0xC0E5: ([], "переход, если знакоместо разделителя выше экрана, первые пять его строк пропускаются"),
    0xC0F1: (["завершение выбираемой полосы и возврат к боковым пикселям"], None),
    0xC0F7: (["обнуление горизонтального разделителя под верхней полосой"], None),
    0xC0FD: (["сброс Sign перед тремя видимыми строками после разделителя"], None),
    0xC101: ([], "переход, если знакоместо разделителя выше экрана, последние три строки пропускаются"),
    0xC10D: (["коррекция адреса после восьми строк знакоместа разделителя"], None),
    0xC110: (["проверка наличия средних знакомест между полосой и нижним краем"], None),
    0xC112: ([], "переход, если средних знакомест нет, остаётся нижний край"),
    0xC114: (["проверка видимости очередного среднего знакоместа"], None),
    0xC117: ([], "выход, если среднее знакоместо достигло нижней границы экрана"),
    0xC118: ([], "переход, если среднее знакоместо выше экрана, все восемь строк пропускаются"),
    0xC133: (["коррекция адреса после восьми строк среднего знакоместа"], None),
    0xC138: (["проверка видимости нижнего знакоместа рамки"], None),
    0xC13B: ([], "выход, если нижнее знакоместо достигло нижней границы экрана"),
    0xC13C: ([], "выход, если нижнее знакоместо ещё выше экрана, вся рамка пропущена"),
    0xC13D: (["обнуление первой строки нижнего знакоместа"], None),
    0xC158: (["рисование шести средних пикселей в предпоследней строке рамки"], None),
    0xC15E: (["обнуление последней пиксельной строки рамки"], None),
    0xC436: (["расчёт внутренней ширины, два крайних байта остаются для боков рамки"], None),
    0xC438: (["расчёт числа знакомест до нижней полосы рамки"], None),
    0xC43C: (["расчёт смещения JR, пропускающего неиспользуемые пары записи средних байтов"], None),
    0xC443: (["сохранение счётчика высоты перед заменой DE байтовыми узорами"], None),
    0xC444: (["проверка видимости верхнего знакоместа рамки"], None),
    0xC447: ([], "выход, если строка рамки достигла нижней границы экрана"),
    0xC448: ([], "переход, если верхнее знакоместо находится выше экрана, его пиксели пропускаются"),
    0xC44B: (["рисование сплошной верхней пиксельной строки рамки"], None),
    0xC451: (["рисование следующей строки со скошенными внешними краями"], None),
    0xC457: (["сброс признака пропуска верхнего знакоместа перед рисованием его боков"], None),
    0xC458: (["выбор боковых пикселей и пустой середины с учётом горизонтального отсечения"], None),
    0xC45B: ([], "переход, если верхнее знакоместо выше экрана, оставшиеся шесть строк не записываются"),
    0xC470: (["коррекция экранного адреса после восьми пиксельных строк верхнего знакоместа"], None),
    0xC473: (["расчёт числа средних знакомест без верхнего и нижнего"], None),
    0xC474: ([], "переход, если средних знакомест нет, остаётся нижняя полоса"),
    0xC476: (["проверка видимости очередного среднего знакоместа рамки"], None),
    0xC479: ([], "выход, если среднее знакоместо достигло нижней границы экрана"),
    0xC47A: ([], "переход, если среднее знакоместо выше экрана, его восемь строк пропускаются"),
    0xC495: (["коррекция адреса после восьми строк среднего знакоместа"], None),
    0xC49A: (["проверка видимости нижнего знакоместа рамки"], None),
    0xC49D: ([], "выход, если нижнее знакоместо достигло нижней границы экрана"),
    0xC49E: ([], "выход, если нижнее знакоместо ещё выше экрана, вся рамка пропущена"),
    0xC4B1: (["завершение рамки скошенной предпоследней пиксельной строкой"], None),
    0xC4B7: (["замыкание рамки сплошной нижней пиксельной строкой"], None),
    0xBF4E: (["восстановление записи левого края и шага колонки после предыдущих отсечений"], None),
    0xBF54: (["восстановление записи правого края перед настройкой нового прямоугольника"], None),
    0xBF59: (["начальное разрешение обоих краёв в альтернативных условиях, Z'=0 и Carry'=0"], None),
    0xBF5D: (["проверка знака исходной байтовой колонки"], None),
    0xBF5E: ([], "переход, если колонка неотрицательна и требуется проверка правого отсечения"),
    0xBF61: (["расчёт остатка внутренней ширины после выхода левого края за нулевую колонку"], None),
    0xBF63: ([], "переход, если сумма колонки и внутренней ширины неотрицательна, запись левого края не отключается"),
    0xBF66: (["отмена левой записи вместе с первым шагом колонки при отрицательном остатке"], None),
    0xBF6D: (["сохранение обрезанной ширины и привязка отрицательной колонки к нулю"], None),
    0xBF70: (["выбор режима Z'=1, левый образец строки будет заменён серединой"], None),
    0xBF74: (["расчёт положения правой части полосы перед проверкой последней колонки"], None),
    0xBF76: (["проверка, помещается ли правый край в 32 байтовые колонки"], None),
    0xBF78: ([], "переход, если колонка плюс внутренняя ширина меньше 31, правое отсечение не требуется"),
    0xBF7B: (["расчёт допустимой внутренней ширины 30 минус исходная колонка"], None),
    0xBF7F: ([], "переход, если допустимая внутренняя ширина неотрицательна, запись правого края сохраняется"),
    0xBF82: (["отмена правой записи и нулевая внутренняя ширина для колонки правее допустимого края"], None),
    0xBF87: (["выбор режима Carry'=1, правый образец строки будет заменён серединой"], None),
    0xBF8B: (["проверка отрицательной строки перед выборкой адреса, исходный индекс остаётся в A"], None),
    0xBF8D: ([], "переход, если строка неотрицательна, для таблицы используется исходный B"),
    0xBF8F: (["привязка отрицательной строки к нулю только для получения начального адреса"], None),
    0xBF91: (["подготовка предыдущего знакового индекса строки для AdvanceClipRow"], None),
    0xBF95: (["расчёт циклического байтового индекса строковой таблицы тремя поворотами"], None),
    0xBF9C: (["выбор старшего и младшего байтов строкового вклада адреса из соседних страниц"], None),
    0xBFA2: (["расчёт циклического байтового индекса горизонтального вклада адреса"], None),
    0xBFA9: (["объединение строкового и горизонтального вкладов младшего байта адреса"], None),
    0xC0AB: (["настройка пропуска лишних средних байтов развёрнутого писателя строки"], None),
    0xC440: (["настройка пропуска лишних средних байтов развёрнутого писателя строки"], None),
    0xC17B: (["сохранение исходной колонки в A и начало записи левого края полосы"], None),
    0xC17E: (["пропуск лишних пар записи по настроенному SpanSkip, исходное смещение ноль выводит 30 средних байтов"], None),
    0xC1BC: (["запись правого края после выбранного числа средних байтов"], None),
    0xC1BD: (["возврат к исходной колонке перед переходом к следующей пиксельной строке знакоместа"], None),
    0xC165: (["продвижение знакового индекса строки рамки в альтернативном L"], None),
    0xC169: (["подготовка признака продолжения для строк выше видимой области"], None),
    0xC16A: ([], "выход, если индекс строки отрицателен, верхнее отсечение ещё требует продолжения"),
    0xC16B: (["проверка нижней границы после 24 видимых строк знакомест"], None),
    0xC16D: (["перевод возвращаемого неотрицательного индекса к нумерации от единицы без изменения Carry"], None),
    0xC16F: (["переход к следующей строке знакомест после обработки её пиксельных строк"], None),
    0xC170: (["расчёт следующей группы Y через младшую часть экранного адреса"], None),
    0xC175: ([], "выход, если прибавление 32 переполнило младший байт, старшая часть уже соответствует новой трети"),
    0xC177: (["компенсация восьми увеличений H при переходе внутри текущей трети экрана"], None),
    0xC1ED: (["выбор полностью нулевой полосы для последующей записи левого края, середины и правого края"], None),
    0xC21F: (["выбор полностью заполненной полосы для последующей записи трёх частей строки"], None),
    0x9CB4: (["привязка индекса элемента к полю Flags существующей записи FInterfaceItem"], None),
    0x9CB9: (["проверка ограничителя в первом указателе списка рисования"], None),
    0x9CBC: ([], "переход, если список рисования сразу содержит ограничитель"),
    0x9CC0: (["проверка ограничителя в следующем указателе перед перестановкой элементов"], None),
    0x9CC3: ([], "переход, если следующая запись завершает список, сортировка закончена"),
    0x9CD0: (["расчёт смещения элемента, индекс умножается на размер записи FInterfaceItem"], None),
    0x9CD4: (["расчёт адреса поля Flags по индексу исходного элемента"], None),
    0x9CD6: (["выделение трёхбитового поля группы без остальных разрядов Flags"], None),
    0x9CD8: (["проверка группы, которую необходимо перенести в начало списка рисования"], None),
    0x9CDE: ([], "переход, если группа текущего элемента не требует переноса в начало списка"),
}

for start in (0xC1C0, 0xC1CF, 0xC1DE, 0xC1F2, 0xC224):
    COMMENTS[start] = (["выбор крайних образцов по альтернативному AF с сохранением обоих AF"], None)
    COMMENTS[start + 5] = ([], "переход, если входной Z' сброшен и левый край сохраняет собственный образец")
    COMMENTS[start + 10] = ([], "переход, если входной Carry' сброшен и правый край сохраняет собственный образец")

from GlyphFacts import COMMENTS as GLYPH_COMMENTS
COMMENTS.update(GLYPH_COMMENTS)

from NumberFacts import COMMENTS as NUMBER_COMMENTS
COMMENTS.update(NUMBER_COMMENTS)

from TextStreamFacts import COMMENTS as STREAM_COMMENTS
COMMENTS.update(STREAM_COMMENTS)

from WordFacts import COMMENTS as WORD_COMMENTS
COMMENTS.update(WORD_COMMENTS)

from JustifyFacts import COMMENTS as JUSTIFY_COMMENTS
COMMENTS.update(JUSTIFY_COMMENTS)

from TextSelectFacts import COMMENTS as SELECT_COMMENTS
COMMENTS.update(SELECT_COMMENTS)

from PaginationFacts import COMMENTS as PAGINATION_COMMENTS
COMMENTS.update(PAGINATION_COMMENTS)

from InnerFrameFacts import COMMENTS as INNER_COMMENTS
COMMENTS.update(INNER_COMMENTS)

from CenteredItemFacts import COMMENTS as CENTERED_COMMENTS
COMMENTS.update(CENTERED_COMMENTS)

from CaptionItemFacts import COMMENTS as CAPTION_COMMENTS
COMMENTS.update(CAPTION_COMMENTS)

from DrawAdapterFacts import COMMENTS as ADAPTER_COMMENTS
COMMENTS.update(ADAPTER_COMMENTS)

from ItemRectFacts import COMMENTS as RECT_COMMENTS
COMMENTS.update(RECT_COMMENTS)

from BandModeFacts import COMMENTS as BAND_MODE_COMMENTS
COMMENTS.update(BAND_MODE_COMMENTS)

from DrawListFacts import COMMENTS as DRAW_LIST_COMMENTS
COMMENTS.update(DRAW_LIST_COMMENTS)

from MoveDrawFacts import COMMENTS as MOVE_DRAW_COMMENTS
COMMENTS.update(MOVE_DRAW_COMMENTS)

from BoundsFacts import COMMENTS as BOUNDS_COMMENTS
COMMENTS.update(BOUNDS_COMMENTS)

from PointerFacts import COMMENTS as POINTER_COMMENTS
COMMENTS.update(POINTER_COMMENTS)

from ToggleFacts import COMMENTS as TOGGLE_COMMENTS
COMMENTS.update(TOGGLE_COMMENTS)

from InterfaceStateFacts import COMMENTS as INTERFACE_STATE_COMMENTS
COMMENTS.update(INTERFACE_STATE_COMMENTS)

from CloseItemFacts import COMMENTS as CLOSE_COMMENTS
COMMENTS.update(CLOSE_COMMENTS)

from ActiveItemFacts import COMMENTS as ACTIVE_COMMENTS
COMMENTS.update(ACTIVE_COMMENTS)

from BoundsToggleFacts import COMMENTS as BOUNDS_TOGGLE_COMMENTS
COMMENTS.update(BOUNDS_TOGGLE_COMMENTS)

from XorOutlineFacts import COMMENTS as XOR_OUTLINE_COMMENTS
COMMENTS.update(XOR_OUTLINE_COMMENTS)

from RemoveDrawFacts import COMMENTS as REMOVE_DRAW_COMMENTS
COMMENTS.update(REMOVE_DRAW_COMMENTS)

from TrackGeometryFacts import COMMENTS as TRACK_COMMENTS
COMMENTS.update(TRACK_COMMENTS)

from ScreenUpdateFacts import COMMENTS as SCREEN_UPDATE_COMMENTS
COMMENTS.update(SCREEN_UPDATE_COMMENTS)

from InterfaceActionFacts import COMMENTS as INTERFACE_ACTION_COMMENTS
COMMENTS.update(INTERFACE_ACTION_COMMENTS)

from RepaintChainFacts import COMMENTS as REPAINT_COMMENTS
COMMENTS.update(REPAINT_COMMENTS)

from MouseInputFacts import COMMENTS as MOUSE_COMMENTS
COMMENTS.update(MOUSE_COMMENTS)

from PointerInputFacts import COMMENTS as POINTER_INPUT_COMMENTS
COMMENTS.update(POINTER_INPUT_COMMENTS)

from StationInterruptFacts import COMMENTS as STATION_IRQ_COMMENTS
COMMENTS.update(STATION_IRQ_COMMENTS)

from WindowGraphicsFacts import COMMENTS as WINDOW_GRAPHICS_COMMENTS
COMMENTS.update(WINDOW_GRAPHICS_COMMENTS)

from MatrixKeyFacts import COMMENTS as MATRIX_KEY_COMMENTS
COMMENTS.update(MATRIX_KEY_COMMENTS)

from SettingsLabelFacts import COMMENTS as SETTINGS_LABEL_COMMENTS
COMMENTS.update(SETTINGS_LABEL_COMMENTS)

from PopupFacts import COMMENTS as POPUP_COMMENTS
COMMENTS.update(POPUP_COMMENTS)

from RowSelectionFacts import COMMENTS as ROW_SELECTION_COMMENTS
COMMENTS.update(ROW_SELECTION_COMMENTS)

from RowHighlightFacts import COMMENTS as ROW_HIGHLIGHT_COMMENTS
COMMENTS.update(ROW_HIGHLIGHT_COMMENTS)

from RowHoverFacts import COMMENTS as ROW_HOVER_COMMENTS
COMMENTS.update(ROW_HOVER_COMMENTS)

from ContextMenuDrawFacts import COMMENTS as CONTEXT_MENU_DRAW_COMMENTS
COMMENTS.update(CONTEXT_MENU_DRAW_COMMENTS)

from MenuCommandFacts import COMMENTS as MENU_COMMAND_COMMENTS
COMMENTS.update(MENU_COMMAND_COMMENTS)

from BackgroundFacts import COMMENTS as BACKGROUND_COMMENTS
COMMENTS.update(BACKGROUND_COMMENTS)

from RebuildFacts import COMMENTS as REBUILD_COMMENTS
COMMENTS.update(REBUILD_COMMENTS)

from EventDispatchFacts import COMMENTS as EVENT_DISPATCH_COMMENTS
COMMENTS.update(EVENT_DISPATCH_COMMENTS)

from RandomStateFacts import COMMENTS as RANDOM_STATE_COMMENTS
COMMENTS.update(RANDOM_STATE_COMMENTS)

from WorldSignatureFacts import STATION_COMMENTS as SIGNATURE_STATION_COMMENTS
COMMENTS.update(SIGNATURE_STATION_COMMENTS)

from MarketFacts import COMMENTS as MARKET_COMMENTS
COMMENTS.update(MARKET_COMMENTS)

from SignatureReturnFacts import COMMENTS as SIGNATURE_RETURN_COMMENTS
COMMENTS.update(SIGNATURE_RETURN_COMMENTS)

from Bank4IndexFacts import COMMENTS as BANK4_INDEX_COMMENTS
COMMENTS.update(BANK4_INDEX_COMMENTS)

from QueuedTextFacts import STATION_COMMENTS as QUEUED_TEXT_STATION_COMMENTS
COMMENTS.update(QUEUED_TEXT_STATION_COMMENTS)

from StationTransitionFacts import STATION_COMMENTS as TRANSITION_STATION_COMMENTS
COMMENTS.update(TRANSITION_STATION_COMMENTS)

from MainLoopControlFacts import COMMENTS as MAIN_LOOP_CONTROL_COMMENTS
COMMENTS.update(MAIN_LOOP_CONTROL_COMMENTS)

from CounterDrawFacts import COMMENTS as COUNTER_DRAW_COMMENTS
COMMENTS.update(COUNTER_DRAW_COMMENTS)

from PlayerRankFacts import COMMENTS as PLAYER_RANK_COMMENTS
COMMENTS.update(PLAYER_RANK_COMMENTS)

from MissionOfferFacts import COMMENTS as MISSION_OFFER_COMMENTS
COMMENTS.update(MISSION_OFFER_COMMENTS)

from MissionHoverFacts import COMMENTS as MISSION_HOVER_COMMENTS
COMMENTS.update(MISSION_HOVER_COMMENTS)

from MissionNameDrawFacts import COMMENTS as MISSION_NAME_DRAW_COMMENTS
COMMENTS.update(MISSION_NAME_DRAW_COMMENTS)

from MissionActionNotes import COMMENTS as MISSION_ACTION_PARTIAL_COMMENTS
COMMENTS.update(MISSION_ACTION_PARTIAL_COMMENTS)

from MissionCompletionFacts import COMMENTS as MISSION_COMPLETION_COMMENTS
COMMENTS.update(MISSION_COMPLETION_COMMENTS)

from StatusDrawFacts import COMMENTS as STATUS_DRAW_COMMENTS
COMMENTS.update(STATUS_DRAW_COMMENTS)

from VariantCountFacts import COMMENTS as VARIANT_COUNT_COMMENTS
COMMENTS.update(VARIANT_COUNT_COMMENTS)

from ItemContourSwitchFacts import COMMENTS as ITEM_CONTOUR_SWITCH_COMMENTS
COMMENTS.update(ITEM_CONTOUR_SWITCH_COMMENTS)

from PeriodicVariantFacts import COMMENTS as PERIODIC_VARIANT_COMMENTS
COMMENTS.update(PERIODIC_VARIANT_COMMENTS)

from MapPanelFacts import COMMENTS as MAP_PANEL_COMMENTS
COMMENTS.update(MAP_PANEL_COMMENTS)

from ItemMoveGuardFacts import COMMENTS as ITEM_MOVE_GUARD_COMMENTS
COMMENTS.update(ITEM_MOVE_GUARD_COMMENTS)

from MapPanFacts import COMMENTS as MAP_PAN_COMMENTS
COMMENTS.update(MAP_PAN_COMMENTS)

from SystemTraitsFacts import COMMENTS as SYSTEM_TRAITS_COMMENTS
COMMENTS.update(SYSTEM_TRAITS_COMMENTS)

from SystemInfoPanelFacts import COMMENTS as SYSTEM_INFO_PANEL_COMMENTS
COMMENTS.update(SYSTEM_INFO_PANEL_COMMENTS)

from MapSelectionPanelFacts import COMMENTS as MAP_SELECTION_PANEL_COMMENTS
COMMENTS.update(MAP_SELECTION_PANEL_COMMENTS)

from MapPanelEventFacts import COMMENTS as MAP_PANEL_EVENT_COMMENTS
COMMENTS.update(MAP_PANEL_EVENT_COMMENTS)

from StoredPointEditFacts import COMMENTS as STORED_POINT_EDIT_COMMENTS
COMMENTS.update(STORED_POINT_EDIT_COMMENTS)

from StoredPointControlFacts import COMMENTS as STORED_POINT_CONTROL_COMMENTS
COMMENTS.update(STORED_POINT_CONTROL_COMMENTS)

from AuxiliaryCycleReadFacts import COMMENTS as AUXILIARY_CYCLE_READ_COMMENTS
COMMENTS.update(AUXILIARY_CYCLE_READ_COMMENTS)

from DecodedMessageFacts import COMMENTS as DECODED_MESSAGE_COMMENTS
COMMENTS.update(DECODED_MESSAGE_COMMENTS)

from DecodedPanelFacts import COMMENTS as DECODED_PANEL_COMMENTS
COMMENTS.update(DECODED_PANEL_COMMENTS)

from MessagePanelFacts import COMMENTS as MESSAGE_PANEL_COMMENTS
COMMENTS.update(MESSAGE_PANEL_COMMENTS)

from MarketPanelHelperFacts import COMMENTS as MARKET_PANEL_HELPER_COMMENTS
COMMENTS.update(MARKET_PANEL_HELPER_COMMENTS)

from PanelHoverFacts import COMMENTS as PANEL_HOVER_COMMENTS
COMMENTS.update(PANEL_HOVER_COMMENTS)

from TradeNumericColumnFacts import COMMENTS as TRADE_NUMERIC_COLUMN_COMMENTS
COMMENTS.update(TRADE_NUMERIC_COLUMN_COMMENTS)

from SettingsParserFacts import COMMENTS as SETTINGS_PARSER_COMMENTS
COMMENTS.update(SETTINGS_PARSER_COMMENTS)

from ScrollBodyClearFacts import COMMENTS as SCROLL_BODY_CLEAR_COMMENTS
COMMENTS.update(SCROLL_BODY_CLEAR_COMMENTS)

from ScrollWindowFacts import COMMENTS as SCROLL_WINDOW_COMMENTS
COMMENTS.update(SCROLL_WINDOW_COMMENTS)

from TradePanelFacts import COMMENTS as TRADE_PANEL_COMMENTS
COMMENTS.update(TRADE_PANEL_COMMENTS)

from ControlPanelGroupFacts import COMMENTS as CONTROL_PANEL_GROUP_COMMENTS
COMMENTS.update(CONTROL_PANEL_GROUP_COMMENTS)

from ShipPeriodicCodeFacts import COMMENTS as SHIP_PERIODIC_CODE_COMMENTS
COMMENTS.update(SHIP_PERIODIC_CODE_COMMENTS)

from SpriteLineTableFacts import COMMENTS as SPRITE_LINE_TABLE_COMMENTS
COMMENTS.update(SPRITE_LINE_TABLE_COMMENTS)

from PreviewFaceFillFacts import COMMENTS as PREVIEW_FACE_FILL_COMMENTS
COMMENTS.update(PREVIEW_FACE_FILL_COMMENTS)
