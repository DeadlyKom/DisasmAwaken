                module Controls
                module EncodeProjectionRatio
                ; Документация [алгоритм и проверка](../../Docs/ControlsBodyProjection.md)
                ; -----------------------------------------
                ; Нормализация отношения модулей с возвратом из внешней проекции при отказе
                ; исходная запись 22, банк 1, смещения #10CA..#1109
                ; In:
                ;   HL и C задают N=256*HL+C, DE и B задают Q=256*DE+B, 0<=N,Q<=7FFFFF
                ;   C'=3 для X либо 2 для Y, B' содержит уже накопленные флаги
                ;   банк 1 выбран, на стеке внутренний возврат, следом внешний возврат проекции
                ; Out:
                ;   при обычном возврате D содержит код, E=0 кроме особых Q<2, точные HL, DE, BC, AF заданы формулами документации
                ;   при отказе HL и DE содержат нормализованные слова, BC младшие коэффициенты, A=0, F=44
                ;   при N<=Q устанавливается бит 2 либо 3 в B', C' уменьшается на один
                ;   SP=входной SP+2 при кодировании, +4 при отказе с переходом к внешнему возврату
                ;   HL', DE', AF', IX, IY сохраняются, I, IM, IFF и страница не меняются
                ;   R и значения временных байтов CPU-стека моделью не доказаны, прерывания не исполнялись
                ; Corrupt:
                ;   HL, DE, BC, AF, BC', R и четыре временных байта стека
                ; Note:
                ;   память вне временного стека не изменяется, точное R не доказано
                ;   результат внешней ветви не заменяется точным делением N/Q, сохранены усечения и SCF/RR только старшего байта
                ;   физический конец файла продолжается в ContinueProjectionRatio без дополнительной инструкции
                ; -----------------------------------------
                ; Сохранение числителя и сравнение старших слов, младшие байты проверяются только при равенстве.
Entry:          PUSH HL
                EXX
                DEC C
                EXX
                OR A
                SBC HL, DE
                JP C, @Controls.ContinueProjectionRatio.NormalizeInside         ; переход, если старшее слово N меньше старшего слова Q, отношение находится внутри

                JP Z, @Controls.EncodeProjectionRatio.CompareLow                ; переход, если старшие слова равны, требуется сравнение младших байтов

PrepareOutside: POP HL
                LD A, H
                AND A
                JR Z, @Controls.BuildBodyProjection.LoadLowWords                ; переход, если N меньше 65536, загружаются его младшие разряды

                LD A, @ControlsProjectConst.WordBits
                ; Расчёт нормализации полного числителя и синхронный сдвиг делителя.
ShiftFullInput: SLA C
                ADC HL, HL
                JP C, @Controls.ContinueProjectionRatio.OutsideCarry            ; переход, если числитель вышел за 24 разряда, завершается внешняя нормализация

                SLA B
                RL E
                RL D
                DEC A
                JR NZ, @Controls.EncodeProjectionRatio.ShiftFullInput           ; переход, если остались сдвиги полной трёхбайтовой величины

ShiftLowWords:  LD A, @ControlsProjectConst.WordBits
                ; Расчёт нормализации младших слов, младшие C и B здесь больше не сдвигаются.
NormalizeWords: ADD HL, HL
                JP C, @Controls.ContinueProjectionRatio.OutsideCarry            ; переход, если числитель вышел за слово, завершается внешняя нормализация

                EX DE, HL
                ADD HL, HL
                EX DE, HL
                DEC A
                JR NZ, @Controls.EncodeProjectionRatio.NormalizeWords           ; переход, если остались сдвиги младшего слова

                LD A, @ControlsProjectConst.WordBits
                ; Расчёт последней байтовой ступени нормализации короткого числителя.
NormalizeHigh:  SLA H
                JP C, @Controls.ContinueProjectionRatio.OutsideCarry            ; переход, если старший байт числителя вышел в Carry, завершается нормализация

                SLA D
                DEC A
                JR NZ, @Controls.EncodeProjectionRatio.NormalizeHigh            ; переход, если остались сдвиги старшего байта

                RET

                ; Сравнение младших байтов при равенстве старших слов.
CompareLow:     PUSH BC
                LD A, C
                SUB B
                ; JP @Controls.ContinueProjectionRatio.Entry, продолжение в ContinueProjectionRatio.asm

                endmodule
                endmodule
