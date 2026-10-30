                module Intro
                module RepeatPattern
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Повторение образца длиной C байт B раз в область DE
; исходная запись 3, файловые смещения #071E..#072B
; In:
;   HL - образец, DE - приёмник, BC - B повторений по C байт
; Out:
;   HL - конец приёмника, DE - начало образца, BC - исходная длина в C при B=0
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   нулевое B означает 256 повторений вследствие DEC A, образец сохраняется на стеке
; -----------------------------------------
Entry:          LD A, B
                LD B, #00
Point6A21:      PUSH HL
                PUSH BC
                LDIR
                POP BC
                POP HL
                DEC A
                JR NZ, @Intro.RepeatPattern.Point6A21                           ; переход, если остались повторения образца


                EX DE, HL
                RET


                endmodule
                endmodule
