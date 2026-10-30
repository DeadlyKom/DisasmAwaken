                module Intro
                module RunAttributeWriter
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Выполнение 32 генерируемых пар POP HL и LD (nn),HL с восстановлением SP
; исходная запись 3, файловые смещения #05A4..#062C
; In:
;   HL - адрес 32 последовательных слов атрибутов, код #68A9..#6928 заранее создан
; Out:
;   32 слова записаны по адресам, встроенным BuildAttributeWriter, SP восстановлен
; Corrupt:
;   HL
; Note:
;   128 исходных NOP заменяются на 32 последовательности POP HL и LD (nn),HL
;   перед вызовом требуется запрет прерываний, процедура сама DI не выполняет
;   флаги и остальные регистры развёрнутые POP и LD не изменяют
; -----------------------------------------
Entry:          LD (#692A), SP
                LD SP, HL
                ; 128 байтов места для 32 генерируемых пар POP HL и LD (nn),HL
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                LD SP, #3131
                RET


                endmodule
                endmodule
