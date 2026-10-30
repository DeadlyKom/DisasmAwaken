                module Intro
                module SelectIntroPage
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Выбор страницы 1 с записью #11 в порт #7FFD
; исходная запись 3, файловые смещения #070B..#070C
; In:
;   дополнительные параметры не требуются
; Out:
;   BC - #7FFD, AF - A=#11, выбран банк 1 и ПЗУ по биту 4
; Corrupt:
;   BC, AF
; Note:
;   F и остальные регистры не меняются, выход общим хвостом SelectMemoryPage
; -----------------------------------------
Entry:          LD A, #11
                ; JP @Intro.SelectMemoryPage.Entry, продолжение в SelectMemoryPage.asm

                endmodule
                endmodule
