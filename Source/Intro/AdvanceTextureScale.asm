                module Intro
                module AdvanceTextureScale
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Документация [масштаб текстуры](../../Docs/IntroTextureScale.md)
; -----------------------------------------
; Начальное нарастание масштаба и последующий циклический выбор из таблицы #6C62
; исходная запись 3, файловые смещения #0921..#0952
                ; In:
                ;   WarmupLeft - счётчик 1..161, RampLevel - уровень 0..63, CycleIndex - индекс 0..39
                ;   таблица 6C62..6C89 содержит исходные 40 значений 0..15, три счётчика и PointerRow доступны для самомодификации
                ;   SP указывает на внешний адрес возврата, IRQ не вмешивается в состояние вступления
                ; Out:
                ;   HL - F000+16*A, DE=F000, BC сохранён, A выбранный индекс 39..71, F=20
                ;   HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются
                ;   WarmupLeft становится max(1, прежнее значение минус один)
                ;   при новом WarmupLeft больше единицы RampLevel становится min(63, прежнее значение плюс один), A=39+floor(RampLevel/2)
                ;   при новом WarmupLeft равном единице CycleIndex становится (прежнее значение плюс один) modulo 40, A=56+таблица[CycleIndex]
                ;   неактивный второй или третий счётчик сохранён, PointerRow содержит HL, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, DE, AF, WarmupLeft, один активный счётчик RampLevel либо CycleIndex и два байта PointerRow
                ; Note:
                ;   начальный WarmupLeft=2 уже выбирает циклическую ветку после уменьшения до единицы
                ;   первый вызов циклической ветки читает следующую запись таблицы, исходный индекс ноль сначала становится единицей
                ;   два пути сходятся в SelectTexturePointerRow, процедура использует его RET без дополнительного CALL
                ;   CPU-стек не записывается, инструкция DI отсутствует
                ;   10256 сценариев проверили все сочетания активных счётчиков профиля, регистры кроме R, все банки RAM и кратность записей
                ;   повреждённые счётчики вне профиля не доказаны, аппаратные IRQ, время и нативное исполнение не проверялись
                ; -----------------------------------------
                ; проверка завершения начального изменения масштаба по счётчику в операнде
Entry:          LD A, #A1
                DEC A
                JR NZ, @Intro.AdvanceTextureScale.StoreWarmup                   ; переход, если первый счётчик после уменьшения не равен нулю


                INC A
StoreWarmup:    LD (@IntroScaleState.WarmupLeft), A
                DEC A
                JR Z, @Intro.AdvanceTextureScale.CycleScale                     ; переход, если первый счётчик достиг единицы и нужен табличный масштаб


                LD A, #00
                INC A
                BIT 6, A
                JR Z, @Intro.AdvanceTextureScale.StoreRamp                      ; переход, если второй счётчик ещё не достиг 64


                DEC A
StoreRamp:      LD (@IntroScaleState.RampLevel), A
                SRL A
                ADD A, #27
                JR @Intro.SelectTexturePointerRow.Entry


CycleScale:     LD A, #00
                INC A
                CP #28
                JR NZ, @Intro.AdvanceTextureScale.StoreCycle                    ; переход, если индекс циклического масштаба ещё не достиг 40


                SUB A
StoreCycle:     LD (@IntroScaleState.CycleIndex), A
                LD E, A
                LD D, #00
                LD HL, #6C62
                ADD HL, DE
                LD A, (HL)
                ADD A, #38
                ; JP @Intro.SelectTexturePointerRow.Entry, продолжение в SelectTexturePointerRow.asm

                endmodule
                endmodule
