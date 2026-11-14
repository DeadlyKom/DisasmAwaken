# Трёхбайтовый генератор со свёрткой переносов

[Общее ядро](../Source/Action/StepFoldedRandom.asm) и 15 внешних входов относятся к ACTION банка 0. Каждый вход выполняет EXX, выбирает собственную трёхбайтовую запись и входит в общее ядро. Ядро обновляет запись и возвращает новое слово в основной HL, обратный EXX восстанавливает DE и BC вызывающего.

## Физические записи

FFoldedRandomState имеет размер три байта. LowWord занимает смещения 0..1,
FoldByte смещение 2. FoldByte — числовой байт modulo 256, не набор флагов.

| Поток | Вход | Физический экземпляр | Адрес состояния | Начальный LowWord | FoldByte |
| --- | --- | --- | --- | --- | --- |
| 0 | [NextRandomWord0](../Source/Action/NextRandomWord0.asm), EB72 | [Stream0](../Source/Action/Data/FoldRandomStream0.asm) | EBDE | 101 | 0 |
| 1 | [NextRandomWord1](../Source/Action/NextRandomWord1.asm), EB87 | [Stream1](../Source/Action/Data/FoldRandomStream1.asm) | EC02 | 93 | 0 |
| 2 | [NextRandomWord2](../Source/Action/NextRandomWord2.asm), EBB8 | [Stream2](../Source/Action/Data/FoldRandomStream2.asm) | EBEA | 10 | 0 |
| 3 | [NextRandomWord3](../Source/Action/NextRandomWord3.asm), EB79 | [Stream3](../Source/Action/Data/FoldRandomStream3.asm) | EBDB | 2055 | 0 |
| 4 | [NextRandomWord4](../Source/Action/NextRandomWord4.asm), EB80 | [Stream4](../Source/Action/Data/FoldRandomStream4.asm) | EBFF | 247 | 0 |
| 5 | [NextRandomWord5](../Source/Action/NextRandomWord5.asm), EB8E | [Stream5](../Source/Action/Data/FoldRandomStream5.asm) | EC05 | 29 | 0 |
| 6 | [NextRandomWord6](../Source/Action/NextRandomWord6.asm), EB95 | [Stream6](../Source/Action/Data/FoldRandomStream6.asm) | EBF9 | 44 | 0 |
| 7 | [NextRandomWord7](../Source/Action/NextRandomWord7.asm), EB9C | [Stream7](../Source/Action/Data/FoldRandomStream7.asm) | EBFC | 21 | 0 |
| 8 | [NextRandomWord8](../Source/Action/NextRandomWord8.asm), EBA3 | [Stream8](../Source/Action/Data/FoldRandomStream8.asm) | EBE1 | 9 | 0 |
| 9 | [NextRandomWord9](../Source/Action/NextRandomWord9.asm), EBAA | [Stream9](../Source/Action/Data/FoldRandomStream9.asm) | EBE4 | 231 | 0 |
| 10 | [NextRandomWord10](../Source/Action/NextRandomWord10.asm), EBB1 | [Stream10](../Source/Action/Data/FoldRandomStream10.asm) | EBE7 | 327 | 0 |
| 11 | [NextRandomWord11](../Source/Action/NextRandomWord11.asm), EBBF | [Stream11](../Source/Action/Data/FoldRandomStream11.asm) | EBED | 333 | 0 |
| 12 | [NextRandomWord12](../Source/Action/NextRandomWord12.asm), EBC6 | [Stream12](../Source/Action/Data/FoldRandomStream12.asm) | EBF0 | 200 | 0 |
| 13 | [NextRandomWord13](../Source/Action/NextRandomWord13.asm), EBCD | [Stream13](../Source/Action/Data/FoldRandomStream13.asm) | EBF3 | 13 | 0 |
| 14 | [NextRandomWord14](../Source/Action/NextRandomWord14.asm), EBD4 | [Stream14](../Source/Action/Data/FoldRandomStream14.asm) | EBF6 | 781 | 1 |

Все 45 байтов состояний EBDB..EC07 оформлены физическими экземплярами STRUCT. Восстановлены все 105 байтов пятнадцати входов EB72..EBDA, включая 84 байта, ранее остававшиеся в бинарных участках. Соседние исходные байты вне этого блока не изменялись. Наблюдаемые прямые применения разобраны ниже. Полный граф игровых применений, распределение, период и вероятности проверок вызывающего кода не доказаны.

## Точная рекурсия

Пусть w — LowWord, h — FoldByte. Все явно обозначенные операции modulo
сохраняют исходное оборачивание, включая случай w=0.

1. u=(w−1) modulo 65536.
2. m=(8w modulo 65536)+(64u modulo 65536)+3w.
3. n=m modulo 65536, что также равно (75w−64) modulo 65536.
4. k=(h+popcount(u >> 10)+floor(m/65536)) modulo 256.
5. d=256k+floor(n/256)−(n AND 255), t=d modulo 65536.
6. a=(k−[d<0]) modulo 256.
7. новый LowWord=(n−t−1) modulo 65536.
8. новый FoldByte=(a−[n<t]) modulo 256.

Скобки `[условие]` обозначают 1 при истинном условии и 0 иначе.
Сумма popcount возникает из шести переносов удвоения младшего слова.
Высокий байт увеличивается каждым переносом, сам он не удваивается.
Поэтому это не обычное умножение всего 24-битного состояния на 75.
Последний DEC HL оборачивает только младшее слово, его заём в FoldByte
не переносится.

## Регистры и проверка

Внешние входы возвращают новый LowWord в HL, DE и BC сохраняют.
AF содержит новый FoldByte и флаги последнего SBC A,0.
Альтернативные HL' указывает на физическую запись, DE' содержит новое
слово, BC' имеет B'=0 и C', равный младшему байту n.
AF', IX и IY сохраняются. SP после RET равен входному+2.
Временные два байта ниже SP сначала получают адрес третьего байта записи,
затем новое слово для передачи через PUSH DE, EXX и POP HL.

При прямом входе в ядро без предварительного EXX основные DE и BC
получаются из входных альтернативных DE' и BC'. Этот вариант отличается
от внешних трёх входов и проверен отдельно.
Ядро выполняет 61 инструкцию и 63 выборки M1, внешние входы 66 M1.
R изменяется по его младшим семи разрядам, старший сохраняется.

[Числовой эталон](../Tools/Disasm/Research/ReferenceActionFoldedRandom.py)
задаёт формулу, заёмы и все флаги независимо от Z80.
[Проверка](../Tools/Disasm/Research/CheckActionFoldedRandom.py) исполнила
218383 сценариев, все младшие слова при FoldByte=0, 127, 255,
все FoldByte при граничных словах, переход страницы, конец RAM,
все пятнадцать внешних входов и исходные состояния записей.

[Отчёт](../Tools/Disasm/Reports/ActionFoldedRandomVerification.json)
подтверждает все регистры включая R, все восемь банков RAM и кратность
записей. Все 2²⁴ состояния не исчерпаны, период, распределение, IRQ,
точные T и нативное использование в игре не доказаны.


## Подтверждённые прямые потребители

[Статическая проверка](../Tools/Disasm/Research/CheckActionRandomDirectCallers.py) сопоставляет все зарегистрированные CALL и JP на 15 входов, исходные байты TRD, физический SourceMap и текущие символические вызовы в исходниках. Установлены 47 прямых инструкций, включая восемь мест инициализации в ActionBoot. Повторные исполнения цикла здесь не считаются отдельными местами. Другие банковые контексты отделяются до назначения роли по числовому адресу.

| Поток | Прямых мест | Подтверждённое местное применение |
|---|---|---|
| 0 | 18 | подтверждены начальное заполнение потоков, планировщик создания, проверки классов, фаз и связей |
| 1 | 3 | подтверждены слово CheckStream и компонента Component1 при создании и поправке координат |
| 2 | 4 | подтверждены выбор планировщика, подготовка вектора и проверки состояний в StepSelectedWideVector и UpdatePreferredClass18 |
| 3 | 1 | подтверждены чтения LowWord Stream3 для Phase0OrLink и LocalPhase1, следующее обновление выполняется в конце SpawnAlternate |
| 4 | 5 | подтверждены исходные компоненты и поправки координат создаваемых записей |
| 5 | 4 | подтверждены компонента Component0, поправка Component2, выбор начального индекса цели и проверка перехода фазы объекта |
| 6 | 0 | в зарегистрированном коде прямых вызовов не найдено, это не доказывает отсутствие косвенного входа |
| 7 | 1 | подтверждён выбор ModelOffset альтернативно создаваемой записи через XOR H с L и маску 1C |
| 8 | 2 | подтверждены компоненты обломка ускорения и допуск связи класса 3 |
| 9 | 1 | подтверждён расчёт OffsetPhase1 в SpawnAlternate через H и знаковую поправку из L |
| 10 | 2 | подтверждены OffsetPhase2 в SpawnAlternate и случайный вход фильтра поиска записей |
| 11 | 1 | подтверждён допуск создания дочерних записей класса 9 по младшему байту слова |
| 12 | 2 | подтверждены вызовы обоих создателей перед вычислением Unknown11, маски 55 и 2A не пересекаются |
| 13 | 2 | подтверждён кандидат для поля 13 создаваемой записи с изменяемыми маской и пределом |
| 14 | 1 | подтверждена проверка слова 8746 перед переходом режима движения в 2 |

Для Stream3 дополнительно проверены прямые чтения слова #EBDB в [SpawnAlternate](../Source/Action/SpawnAlternate.asm) и [FinishSpawnRecord](../Source/Action/FinishSpawnRecord.asm). Это слово копируется в Phase0OrLink и LocalPhase1. В SpawnAlternate чтение предшествует обновлению через NextRandomWord3, поэтому новая пара полей получает предыдущее LowWord Stream3. Следующий вызов меняет состояние для будущего использования. Назначение потока нельзя описывать только по месту его CALL, непосредственные чтения состояния также существенны.

Для Stream6 не найдено прямой инструкции CALL или JP на #EB95 в зарегистрированных видах кода. Это не исключает вычисляемых целей, модифицируемого кода или иных контекстов. Поток и его начальные байты сохранены.

В [полном отчёте](../Tools/Disasm/Reports/ActionRandomDirectCallersVerification.json) указаны исходные адреса каждого вызова, условие, байты, файл и описание вызывающей процедуры. Отдельно перечислены прямые байтовые и словные чтения и записи состояний, включая перекрытие поля словом. Косвенная работа ядра следует отдельному договору StepFoldedRandom, отсутствие всех других косвенных обращений здесь не доказывается. Ссылки на процедуры устанавливают конкретные местные применения, это не новое доказательство их достижимости из нативной игры или вероятности ветвей. Сборка и модель исполнения в этой статической проверке не запускаются.
