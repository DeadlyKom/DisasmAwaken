                module Intro
                module RunTimedEffect
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
; -----------------------------------------
; Повторение обработчика HL в течение BC шагов с проверкой клавиши Space
; исходная запись 3, файловые смещения #074B..#0766
; In:
;   HL - адрес обработчика шага эффекта, BC - число повторений
; Out:
;   по исчерпании BC разрешаются прерывания и выполняется FillBitmap с C=0
; Corrupt:
;   HL, DE, BC, AF, остальные регистры зависят от переданного обработчика
; Note:
;   нулевой BC даёт 65536 повторений, адрес StepCall записывается в его операнд перед первым шагом
;   перед каждым шагом читается порт #7FFE, точное значение #BE немедленно переводит к загрузке станции
;   выход по клавиатуре оставляет временные значения на стеке, завершающий загрузчик восстанавливает SP
;   конец файлового фрагмента переходит в FillBitmap без CALL, это общий хвост процедуры
; -----------------------------------------
Entry:          LD (@Intro.RunTimedEffect.StepCall + 1), HL
CheckSpace:     PUSH BC
                PUSH AF
                LD BC, #7FFE
                IN A, (C)
                CP #BE
                JP Z, @Intro.InitializeIntro.EnterStation                       ; переход, если строка клавиатуры равна #BE и вступление нужно завершить


                POP AF
                POP BC
                PUSH BC
StepCall:       CALL #CDCD
                POP BC
                DEC BC
                LD A, B
                OR C
                JR NZ, @Intro.RunTimedEffect.CheckSpace                         ; переход, если счётчик шагов эффекта BC ещё не обнулился


                EI
                ; JP @Intro.FillBitmap.Entry, продолжение в FillBitmap.asm

                endmodule
                endmodule
