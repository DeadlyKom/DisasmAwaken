                module FinalTemplates
                module BitmapLine
; Документация [FinalTemplates](../../Docs/FunctionDetails/FinalTemplates.md)
; -----------------------------------------
; 52-байтовый образец переноса 32 байтов строки через два набора регистров и временный SP
; исходная запись 29, файловые смещения #0247..#027A
; In:
;   четыре операнда SP задают две половины источника и конца приёмника, прерывания запрещены
; Out:
;   32 байта одной строки bitmap перенесены из окна банка в экран #4000
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', IX
; Note:
;   SP используется как указатель сначала при POP, затем при PUSH, исходный стек восстанавливает вся цепочка
;   две команды EXX в каждой половине возвращают расположение наборов, IY и AF' не используются
; -----------------------------------------
Entry:          LD SP, #C000
                POP HL
                POP BC
                POP DE
                EXX
                POP HL
                POP BC
                POP DE
                POP IX
                POP AF
                LD SP, #4010
                PUSH AF
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH HL
                EXX
                PUSH DE
                PUSH BC
                PUSH HL
                LD SP, #C010
                POP HL
                POP BC
                POP DE
                EXX
                POP HL
                POP BC
                POP DE
                POP IX
                POP AF
                LD SP, #4020
                PUSH AF
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH HL
                EXX
                PUSH DE
                PUSH BC
                PUSH HL
                endmodule
                endmodule
