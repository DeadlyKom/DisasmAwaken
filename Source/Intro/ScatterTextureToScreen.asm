                module Intro
                module ScatterTextureToScreen
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Документация [алгоритм и проверка](../../Docs/IntroInterlacedFrame.md)
                ; Документация [экранный перенос](../../Docs/IntroScatter.md)
; -----------------------------------------
; Копирование 38 строк по 32 байта, адреса источников берутся из временного стека
; исходная запись 3, файловые смещения #0527..#05A3
                                ; In:
                ;   HL - таблица 38 записей по четыре байта, слово указателя на 32 слова источников и слово адреса приёмника
                ;   BC - начальный побочный счётчик LDI, AF - входной Carry сохраняется до выхода
                ;   вставка IntroScatterState.AddressPatch содержит 00 00 либо 00 14, то есть NOP NOP либо NOP INC D
                ;   таблицы и источники доступны для чтения, назначения не перекрывают код, таблицы, будущие источники и CPU-стек
                ;   операнды IntroScatterState.RecordCursor и IntroScatterState.CpuSavedSP доступны для самомодификации, IRQ не вмешивается во временный SP
                ; Out:
                ;   HL - последний прочитанный адрес источника плюс один modulo 65536
                ;   DE - адрес приёмника последней строки после коррекции D, увеличенный на 32 modulo 65536
                ;   BC - входное BC минус 1216 modulo 65536, A=0, F=42 OR входной Carry
                ;   HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются
                ;   38 строк по 32 байта перенесены, при вставке 00 14 перед каждой строкой D увеличен на один modulo 256
                ;   операнд IntroScatterState.RecordCursor содержит входное HL+152 modulo 65536, операнд IntroScatterState.CpuSavedSP содержит входной SP
                ;   CPU-стек не записывается, после восстановления SP конечный RET даёт входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, операнды IntroScatterState.RecordCursor и IntroScatterState.CpuSavedSP, 1216 байтов назначений
                ; Note:
                ;   POP HL и POP DE читают одну запись, затем SP переключается на указатели источников
                ;   INC D корректирует старший байт назначения, адрес таблицы источников HL не изменяется этой вставкой
                ;   LDI уменьшает BC, однако окончание строки определяется развёрнутыми 32 парами POP HL и LDI
                ;   последний DEC A задаёт Z=1, N=1 и сохраняет Carry, процедура сама DI не выполняет
                ;   вызывающий PresentInterlacedFrame перед переносом выполняет EI HALT DI через WaitInterrupt
                ;   1536 сценариев используют обе вставки, созданные реальным выбором фазы, все F и три CPU-стека
                ;   регистры кроме R, все банки RAM и кратность записей проверены, произвольные перекрытия, время, IRQ и нативный запуск не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Общий перенос 38 строк
                ; Сохранение адреса первой четырёхбайтовой записи в изменяемом операнде RecordCursor.
Entry:          LD (@IntroScatterState.RecordCursor), HL
                ; сохранение исходного SP в операнде восстановления перед чтением таблиц через POP
                ; Сохранение CPU SP, после выбора указателей он временно станет стеком слов источников.
                LD (@IntroScatterState.CpuSavedSP), SP
                LD A, #26
                ; Чтение следующей записи через подготовленный RecordCursor, два POP дают адрес списка источников и адрес назначения.
ReadRecord:     LD SP, #3131
                ; получение указателя на 32 слова источников и адреса экранной строки
                POP HL
                POP DE
                ; Обновление RecordCursor по SP сразу после прочитанной четырёхбайтовой записи.
                LD (@IntroScatterState.RecordCursor), SP
                ; двухбайтовая изменяемая вставка, соседняя страница приёмника выбирается инструкцией INC D
                ; Исходная двухбайтовая вставка, рабочие варианты NOP NOP и NOP INC D корректируют только назначение.
                NOP
                NOP
                ; перенос 32 разрозненных байтов источника в последовательную строку экрана
                ; Переключение SP на 32 указателя источников, развёрнутые пары POP HL и LDI дают одну строку.
                LD SP, HL
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                POP HL
                LDI
                ; Проверка числа оставшихся строк, исходный Carry фазы сохраняется DEC A.
                DEC A
                JP NZ, @Intro.ScatterTextureToScreen.ReadRecord                 ; переход, если ещё не перенесены все 38 строк


                ; восстановление исходного SP для возврата в вызывающую процедуру
                ; Восстановление CpuSavedSP, у хвостовой второй половины он равен внешнему SP всего обработчика.
                LD SP, #3131
                RET


                endmodule
                endmodule
