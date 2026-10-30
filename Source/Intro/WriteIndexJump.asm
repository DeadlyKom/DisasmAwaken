                module Intro
                module WriteIndexJump
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание инструкции JP (IX) в генерируемом коде
; исходная запись 3, файловые смещения #0705..#070A
; In:
;   HL - адрес создаваемой инструкции
; Out:
;   HL - адрес после двухбайтовой инструкции JP (IX)
; Corrupt:
;   HL
; Note:
;   записываются #DD и #E9, значение IX не меняется
; -----------------------------------------
Entry:          LD (HL), #DD
                INC HL
                LD (HL), #E9
                RET


                endmodule
                endmodule
