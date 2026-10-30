                module Intro
                module CombineAttributeNibbles
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Объединение восьми младших полубайтов HL с восемью старшими полубайтами BC в 64 атрибута DE
; исходная запись 3, файловые смещения #0664..#0682
; In:
;   HL - восемь байтов младших полубайтов, DE - приёмник, BC - восемь байтов старших полубайтов
; Out:
;   HL увеличен на 8, BC сохранён, E увеличен на 64 modulo 256, D сохранён
; Corrupt:
;   HL, DE, AF, IX, IY
; Note:
;   результат строки r и столбца c равен (BC[c] AND #F0) OR (HL[r] AND #0F)
;   при увеличении E перенос в D не выполняется, IXH и IXL равны нулю, изменяется только IYL
; -----------------------------------------
Entry:          LD IXH, #08
Point6967:      LD IXL, #08
                LD A, (HL)
                INC HL
                AND #0F
                LD IYL, A
                PUSH BC
                ; объединение старшего полубайта очередного столбца и младшего полубайта текущей строки
Point6971:      LD A, (BC)
                INC BC
                AND #F0
                OR IYL
                LD (DE), A
                INC E
                DEC IXL
                JR NZ, @Intro.CombineAttributeNibbles.Point6971                 ; переход, если ещё не сформированы восемь атрибутов строки


                POP BC
                DEC IXH
                JR NZ, @Intro.CombineAttributeNibbles.Point6967                 ; переход, если ещё не сформированы восемь строк атрибутов


                RET


                endmodule
                endmodule
