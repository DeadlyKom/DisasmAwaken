                module Action
                module SelectMemoryPage
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Запись A в #7FFD с сохранением BC
; исходная запись 17, файловые смещения #4B1B..#4B22
; In:
;   AF - A содержит полный байт управления #7FFD
; Out:
;   порт #7FFD содержит A, регистры сохраняются
; Corrupt:
;   нет изменяемых регистров
; Note:
;   в отличие от станционного варианта теневая копия здесь не записывается
; -----------------------------------------
Entry:          PUSH BC
                LD BC, #7FFD
                OUT (C), A
                POP BC
                RET


                endmodule
                endmodule
