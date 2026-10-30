                module IntroTemplates
                module PointerSample
; Документация [IntroTemplates](../../Docs/FunctionDetails/IntroTemplates.md)
; -----------------------------------------
; Шестибайтовый образец косвенной выборки, 64 копии по адресу #9100
; исходная запись 3, файловые смещения #0A78..#0A7D
; In:
;   HL - H задаёт страницу таблицы, BC - приёмник, SP - слово указателя источника
; Out:
;   байт по косвенному указателю записан в BC, C увеличен на один modulo 256, SP увеличен на два
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   старший байт указателя приходит из POP DE, младший заменяется таблицей по исходному E
;   образец без RET, последний INC C из 64 копий по #9100 заменён JP #6BED
; -----------------------------------------
Entry:          POP DE
                LD L, E
                LD E, (HL)
                LD A, (DE)
                LD (BC), A
                INC C
                ; JP @IntroTemplates.PhaseSum.Entry, продолжение в PhaseSum.asm

                endmodule
                endmodule
