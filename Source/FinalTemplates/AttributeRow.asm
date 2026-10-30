                module FinalTemplates
                module AttributeRow
; Документация [FinalTemplates](../../Docs/FunctionDetails/FinalTemplates.md)
; -----------------------------------------
; 23-байтовый образец заполнения 32 атрибутов байтом из альтернативного A
; исходная запись 29, файловые смещения #027D..#0293
; In:
;   AF' - A байт атрибутов, операнд SP задаёт адрес после конца текущего ряда
; Out:
;   32 атрибута ряда содержат исходный A альтернативного набора
; Corrupt:
;   HL
; Note:
;   два EX AF,AF' сохраняют оба AF, 16 PUSH HL записывают 32 байта
;   SP уменьшается на 32 после загрузки адреса ряда, исходный стек восстанавливает общая цепочка
; -----------------------------------------
Entry:          EX AF, AF'
                LD L, A
                LD H, A
                EX AF, AF'
                LD SP, #5820
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                endmodule
                endmodule
