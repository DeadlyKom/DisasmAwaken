                module Intro
                module AdvanceTexturePhases
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; Подробный разбор [Intro.md](../../Docs/Intro.md)
; -----------------------------------------
; Обновление трёх фаз и четвёртого смещения по таблице #6400 в операндах текстурного обработчика
; исходная запись 3, файловые смещения #08F6..#0920
; In:
;   TexturePhases.PhaseA, PhaseB и PhaseC - три записи FTexturePhase, страница IntroTables.PhaseSamples доступна
; Out:
;   HL - следующий указатель выборки в странице #64, DE - эффективный StepDelta третьей фазы, BC - её прежний Phase
;   AF - A выбранный байт таблицы, делённый на два, F соответствует SRL этого байта
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   все три состояния обновляются через AdvanceParameters, старшие байты Phase меняют LookupHL, LookupBCAlt и LookupHLAlt
;   младший байт SampleCursor увеличивается на три по модулю 256 без переноса в H, результат выборки меняет LookupDEAlt
;   SP восстанавливается, альтернативные и индексные регистры сохраняются, IFF устанавливается в единицу вызовами AdvanceParameters
;   PhaseA, PhaseB и PhaseC передаются в AdvanceParameters
;   старшие байты Phase записываются в младшие байты указателей таблиц #9400, #9500 и #9600
;   четвёртый параметр берётся из IntroTables.PhaseSamples с шагом три по младшему байту и делится на два
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
