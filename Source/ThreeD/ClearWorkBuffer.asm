                module ThreeD
                module ClearWorkBuffer
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Заполнение #0C00 байт до #8C00 значением #FF через стек с восстановлением SP
; исходная запись 19, файловые смещения #110A..#112B
; In:
;   SP - действующий стек вызывающего кода
; Out:
;   #8000..#8BFF заполнены #FF, SP восстановлен
; Corrupt:
;   HL, BC
; Note:
;   96 повторений по 16 PUSH HL, код не выполняет DI, безопасность прерываний задаёт вызывающий код
; -----------------------------------------
Entry:          LD (#D129), SP
                LD SP, #8C00
                LD HL, #FFFF
                LD B, #60
PointD116:      PUSH HL
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
                DJNZ @ThreeD.ClearWorkBuffer.PointD116

                LD SP, #0000
                RET


                endmodule
                endmodule
