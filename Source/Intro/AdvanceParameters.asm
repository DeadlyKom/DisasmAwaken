                module Intro
                module AdvanceParameters
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; Подробный разбор [Intro.md](../../Docs/Intro.md)
                ; Полный договор фаз [разбор](../../Docs/IntroGeneratedEffects.md#полные-договоры-обновления-фаз)
; -----------------------------------------
; Обновление двух первых слов шестибайтового состояния через временный стек, третье слово сохраняется
; исходная запись 3, файловые смещения #072C..#074A
                ; In:
                ;   HL - шестибайтовая запись FTexturePhase, Phase, Step и StepDelta доступны для чтения и записи
                ;   код и операнд RestoreStack+1 доступны для записи, запись фазы не пересекается с ними и внешним возвратом
                ;   CPU-стек содержит внешний возврат, IRQ/NMI не вмешиваются, общий операнд исключает реентерабельный вызов
                ; Out:
                ;   HL - новый Phase, DE - эффективный StepDelta, BC - прежний Phase, AF - A старший байт нового Phase
                ;   b равен биту 15 прежнего Phase, d=StepDelta при b=0 либо -StepDelta при b=1 modulo 65536
                ;   новый Step=(старый Step+d) modulo 65536, новый Phase=(старый Phase+новый Step) modulo 65536
                ;   HL', DE', BC', AF', IX, IY, I, IM и paging сохраняются, IFF=1, SP равен входному SP+2
                ;   F сохраняет S=b, Z=P/V=1-b, N=0, H и C от последнего ADD HL,BC, биты 5 и 3 от старшего байта нового Phase
                ;   все шесть байтов записи переписаны, значение StepDelta сохранено, RestoreStack+1 получает исходный SP
                ; Corrupt:
                ;   HL, DE, BC, AF, R, IFF, шесть байтов записи FTexturePhase, два байта операнда RestoreStack+1 и SP снятием возврата
                ; Note:
                ;   отрицание StepDelta=#8000 оставляет #8000, специального исправления знакового переполнения нет
                ;   собственный SP временно проходит по записи, PUSH DE восстанавливает исходный StepDelta, затем PUSH обновляют Step и Phase
                ;   записей ниже исходного CPU-стека нет, только чтение внешнего возврата, максимальная область данных равна шести байтам записи
                ;   DI защищает фазовый SP, EI перед RET разрешает IRQ, исходный IFF не восстанавливается
                ;   число M1 равно 19+7*b, младшие семь битов R увеличиваются на этот счёт modulo 128, старший сохраняется
                ;   729 троек граничных слов проверяют флаги, регистры кроме времени, восемь банков и кратность всех записей
                ;   полное совместное пространство слов, IRQ/NMI, аппаратное время и нативная игра не доказаны
; -----------------------------------------
Entry:          LD (@Intro.AdvanceParameters.RestoreStack + 1), SP
                DI
                LD SP, HL
                POP BC
                POP HL
                POP DE
                PUSH DE
                ; проверка знака прежней Phase перед выбором направления изменения Step
                BIT @IntroConst.PhaseSignBit, B
                JR Z, @Intro.AdvanceParameters.UpdateStep                       ; переход, если знак прежней Phase сброшен и StepDelta нужно прибавить к Step

                ; расчёт отрицания StepDelta для ветви с установленным знаком Phase
                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
                ; расчёт нового приращения Step с выбранным знаком StepDelta
UpdateStep:     ADD HL, DE
                PUSH HL
                ; расчёт новой Phase по обновлённому приращению Step
                ADD HL, BC
                PUSH HL
                LD A, H
RestoreStack:   LD SP, #3131
                EI
                RET

                endmodule
                endmodule
