                module Text
                module FinishScript
; Документация [Text](../../Docs/FunctionDetails/Text.md)
; Подробный разбор [команды, стек, CR и условные блоки](../../Docs/ScriptControl.md)
; -----------------------------------------
; Возврат вызывающему сценарию через первоначально сохранённый SP
; исходная запись 5, файловые смещения #00E7..#00EB
; In:
;   ScriptRuntimeState.SavedSP содержит доступное слово возврата, LANG выбран
; Out:
;   PC снимается со стека SavedSP, SP=SavedSP+2
;   HL, DE, BC, AF, альтернативные и индексные регистры, I и IFF сохранены
; Corrupt:
;   SP, PC
; Note:
;   входной SP игнорируется, возврат не зависит от числа промежуточных CALL
; -----------------------------------------
                ; восстановление первоначального стека, текущие временные возвраты отбрасываются
Entry:          LD SP, (@ScriptRuntimeState.SavedSP)
                RET

                endmodule
                endmodule
