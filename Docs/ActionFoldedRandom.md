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

Все 45 байтов состояний EBDB..EC07 оформлены физическими экземплярами STRUCT. Восстановлены все 105 байтов пятнадцати входов EB72..EBDA, включая 84 байта, ранее остававшиеся в бинарных участках. Соседние исходные байты вне этого блока не изменялись. Высокоуровневые игровые роли потоков ещё не названы, распределение, период и вероятности проверок вызывающего кода не доказаны.

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
