                module Intro
                module AdvanceParameters
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; Подробный разбор [Intro.md](../../Docs/Intro.md)
; -----------------------------------------
; Обновление двух первых слов шестибайтового состояния через временный стек, третье слово сохраняется
; исходная запись 3, файловые смещения #072C..#074A
; In:
;   HL - запись FTexturePhase со словами Phase, Step и StepDelta в младшем порядке байтов
; Out:
;   HL - новый Phase, DE - StepDelta либо его отрицание по прежнему знаку Phase, BC - прежний Phase, AF - A старший байт нового Phase
;   Step увеличен на StepDelta при сброшенном знаке прежнего Phase либо уменьшен при установленном, Phase увеличен на новый Step
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   арифметика по модулю #10000, исходный StepDelta остаётся в записи, SP восстанавливается
;   прерывания на выходе разрешены через EI, входное состояние IFF не сохраняется
;   альтернативные и индексные регистры сохраняются, общий изменяемый операнд сохранения SP исключает реентерабельный вызов
; -----------------------------------------
Entry:          LD (#6A47), SP
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
                LD SP, #3131
                EI
                RET

                endmodule
                endmodule
