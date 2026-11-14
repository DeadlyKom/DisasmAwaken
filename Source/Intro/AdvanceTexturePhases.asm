                module Intro
                module AdvanceTexturePhases
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; Подробный разбор [Intro.md](../../Docs/Intro.md)
                ; Полный договор фаз [разбор](../../Docs/IntroGeneratedEffects.md#полные-договоры-обновления-фаз)
; -----------------------------------------
; Обновление трёх фаз и четвёртого смещения по таблице #6400 в операндах текстурного обработчика
; исходная запись 3, файловые смещения #08F6..#0920
                ; In:
                ;   TexturePhases.PhaseA, PhaseB и PhaseC - три доступные записи FTexturePhase, действуют условия AdvanceParameters
                ;   старший байт IntroState.SampleCursor равен #64, младший произволен, страница IntroTables.PhaseSamples читаема
                ;   операнды LookupHL, LookupBCAlt, LookupHLAlt и LookupDEAlt доступны для записи, исходный код сохранён
                ;   внешний возврат и два байта под входным SP доступны, стек отделён от кода, операндов, фаз и таблицы
                ;   IRQ/NMI не вмешиваются, вызовы AdvanceParameters изменяют IFF независимо от входного состояния
                ; Out:
                ;   HL - #6400 OR ((старый LOW SampleCursor+3) AND #FF), DE - эффективный StepDelta третьей фазы, BC - её прежний Phase
                ;   AF - A выбранный байт таблицы, сдвинутый вправо на один, F соответствует SRL исходного байта
                ;   HL', DE', BC', AF', IX, IY, I, IM и paging сохраняются, IFF=1, SP равен входному SP+2
                ;   три записи фаз обновлены, их новые старшие байты Phase записаны в LookupHL, LookupBCAlt и LookupHLAlt
                ;   SampleCursor получает HL, LookupDEAlt получает A, RestoreStack+1 дочерней процедуры содержит входной SP-2
                ; Corrupt:
                ;   HL, DE, BC, AF, R, IFF, три записи фаз, четыре фазовых байта и слово SampleCursor, дочерний RestoreStack+1, два байта под входным SP и SP снятием возврата
                ; Note:
                ;   параметры передаются трём настоящим вызовам AdvanceParameters, их StepDelta сохраняются по значению
                ;   старшие байты указателей #9400, #9500 и #9600 не меняются, обновляются их младшие байты
                ;   три INC L не переносят переполнение в H, после курсора #FF следующий младший байт равен #02
                ;   два байта под входным SP последовательно получают возвраты #6BFC, #6C05 и #6C0E, последний остаётся в RAM
                ;   число M1 равно 76+7*n, n количество отрицательных прежних Phase, младшие семь битов R увеличиваются на этот счёт modulo 128
                ;   4096 случаев проверяют все восемь знаковых сочетаний, все байты выборки и курсора, два стека и IFF=1
                ;   сверены все регистры кроме времени, восемь банков и кратность записей, полный совместный перебор и нативный показ не доказаны
; -----------------------------------------
                ; обновление трёх шестибайтовых состояний и встроенных фаз выборок
Entry:          LD HL, @TexturePhases.PhaseA
                CALL @Intro.AdvanceParameters.Entry
                LD (@IntroState.LookupHL), A
                LD HL, @TexturePhases.PhaseB
                CALL @Intro.AdvanceParameters.Entry
                LD (@IntroState.LookupBCAlt), A
                LD HL, @TexturePhases.PhaseC
                CALL @Intro.AdvanceParameters.Entry
                LD (@IntroState.LookupHLAlt), A
                LD HL, @IntroTables.PhaseSamples
                ; расчёт следующего индекса таблицы с шагом три без переноса в номер страницы
                INC L
                INC L
                INC L
                LD (@IntroState.SampleCursor), HL
                LD A, (HL)
                ; расчёт четвёртого смещения, табличный байт делится на два без знака
                SRL A
                LD (@IntroState.LookupDEAlt), A
                RET

                endmodule
                endmodule
