# Разности произведений и координат ACTION

[CompareTopLeftProducts](../Source/Action/CompareTopLeftProducts.asm), исходный вход C66D.

[CompareTopRightProducts](../Source/Action/CompareTopRightProducts.asm), исходный вход C681.

[CompareBottomLeftProducts](../Source/Action/CompareBottomLeftProducts.asm), исходный вход C695.

[CompareBottomRightProducts](../Source/Action/CompareBottomRightProducts.asm), исходный вход C6A9.

[ComputeSecondAxisDelta](../Source/Action/ComputeSecondAxisDelta.asm), исходный вход C6BD.

[ComputeFirstAxisDelta](../Source/Action/ComputeFirstAxisDelta.asm), исходный вход C6C8.

Четыре сравнения читают физические FClipProduct. Сначала вычитаются младшие слова с очищенным Carry. Затем читаются старшие слова, загрузки не меняют флаги, вычитается старшее слово второго произведения с заёмом младшего вычитания. HL содержит только старшую разность, BC старшее слово второго произведения. DE и A сохраняются, F является результатом последнего SBC. Младшая разность не возвращается.

Z проверяет только итоговое старшее слово. Например, если произведения отличаются только младшими словами и заёма нет, Z установлен при неравных полных произведениях. Overflow не исправляется. Проверка Sign в вызывающих обработчиках сохраняется буквально и при переполнении не заменяется универсальным математическим сравнением signed32. R увеличивается на 12 с сохранением старшего бита.

Две разности координат читают одинаковое поле Second либо First второй и первой точки. HL получает wrap16(SecondPoint.Field−FirstPoint.Field), DE получает исходное FirstPoint.Field, BC и A сохраняются. F равен точным флагам SBC с нулевым входным Carry. R увеличивается на 7 с сохранением старшего бита.

Во всех шести входах альтернативные регистры, IX/IY, I/IM/IFF и paging сохраняются. CPU-стек не записывается, после RET SP увеличен на два. RAM и порты не записываются.

[Модель](../Tools/Disasm/Research/CheckActionClipComparisons.py) прошла [803012 сценариев](../Tools/Disasm/Reports/ActionClipComparisonsVerification.json), по 69681 на сравнение произведений и 262144 на разность координат. Проверяются точные регистры, флаги, R, SP и отсутствие записей RAM. Проверены все младшие слова отдельных срезов, заём, знаковые границы и смешанные полные произведения. Все совместные входы, IRQ, сборка и нативный запуск не доказаны.
