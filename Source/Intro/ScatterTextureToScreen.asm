                module Intro
                module ScatterTextureToScreen
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Копирование 38 строк по 32 байта, адреса источников берутся из временного стека
; исходная запись 3, файловые смещения #0527..#05A3
; In:
;   HL - таблица 38 четырёхбайтовых записей с указателями источника и приёмника
;   в #6839 должны быть NOP NOP либо INC H NOP, источник содержит 32 указателя на байты
; Out:
;   38 строк по 32 байта перенесены по адресам из таблицы, SP восстановлен
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   каждая запись читается через POP HL и POP DE, BC у LDI служит только побочным счётчиком
;   SP во время строки указывает на 32 слова источников, CALL и прерывания в этом участке недопустимы
;   вызывающий PresentInterlacedFrame заранее выполняет DI через WaitInterrupt
; -----------------------------------------
Entry:          LD (#6831), HL
                ; сохранение исходного SP в операнде восстановления перед чтением таблиц через POP
                LD (#68A1), SP
                LD A, #26
Point6830:      LD SP, #3131
                ; получение указателя на 32 слова источников и адреса экранной строки
                POP HL
                POP DE
                LD (#6831), SP
                ; двухбайтовая изменяемая вставка, соседняя страница источников выбирается инструкцией INC H
                NOP
                NOP
                ; перенос 32 разрозненных байтов источника в последовательную строку экрана
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
                DEC A
                JP NZ, @Intro.ScatterTextureToScreen.Point6830                  ; переход, если ещё не перенесены все 38 строк


                ; восстановление исходного SP для возврата в вызывающую процедуру
                LD SP, #3131
                RET


                endmodule
                endmodule
