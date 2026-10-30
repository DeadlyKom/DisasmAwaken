                module Text
                module CopyRightOperand
; Документация [Text](../../Docs/FunctionDetails/Text.md)
; -----------------------------------------
; Возврат правого операнда BC в DE
; исходная запись 5, файловые смещения #04D4..#04D6
; In:
;   BC - правый операнд
; Out:
;   DE - копия правого операнда
; Corrupt:
;   DE
; Note:
;   HL, BC, AF, альтернативные и индексные регистры сохраняются
; -----------------------------------------
Entry:          LD D, B
                LD E, C
                RET

                endmodule
                endmodule
