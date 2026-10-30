                module Intro
                module RunTimedEffect
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
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
;   нулевой BC даёт 65536 повторений, адрес CALL подменяется через операнд #6A5E
;   перед каждым шагом читается порт #7FFE, точное значение #BE немедленно переводит к загрузке станции
;   выход по клавиатуре оставляет временные значения на стеке, завершающий загрузчик восстанавливает SP
;   конец файлового фрагмента переходит в FillBitmap без CALL, это общий хвост процедуры
; -----------------------------------------
Entry:          LD (#6A5E), HL
Point6A4E:      PUSH BC
                PUSH AF
                LD BC, #7FFE
                IN A, (C)
                CP #BE
                JP Z, @Intro.InitializeIntro.Point65B0                          ; переход, если строка клавиатуры равна #BE и вступление нужно завершить


                POP AF
                POP BC
                PUSH BC
                CALL #CDCD
                POP BC
                DEC BC
                LD A, B
                OR C
                JR NZ, @Intro.RunTimedEffect.Point6A4E                          ; переход, если счётчик шагов эффекта BC ещё не обнулился


                EI
                ; JP @Intro.FillBitmap.Entry, продолжение в FillBitmap.asm

                endmodule
                endmodule
