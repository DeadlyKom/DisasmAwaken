                module ActionBoot
                module InitializeRandomStates
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Начальное заполнение слов состояний от регистра R и повторных вызовов обработчика #EB72
; исходная запись 17, файловые смещения #0149..#0197
; In:
;   банк 0 подключён, обработчик #EB72 и слова состояний доступны
; Out:
;   начальные слова #EBDB, #EBFF, #EC02, #EC05, #EBE1, #EBE4, #EBE7 и #EBEA обновлены
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC'
; Note:
;   в #5CC2 записываются байты #F1 и #C9, младший байт семени #EBDE берётся из R
;   первоначально выполняются от одного до четырёх вызовов в зависимости от R AND 3
;   затем восемь результатов #EB72 записываются в слова состояний, #AA9A получает 1, #A8BC получает #2E
;   используется доказанный поток NextRandomWord0 и общий StepFoldedRandom, игровое назначение потока не установлено
; -----------------------------------------
Entry:          LD HL, #C9F1
                LD (#5CC2), HL
                LD A, R
                LD L, A
                LD (#EBDE), HL
                AND #03
                INC A
                LD B, A
WarmRandom:     PUSH BC
                CALL @Action.NextRandomWord0.Entry
                POP BC
                DJNZ @ActionBoot.InitializeRandomStates.WarmRandom

                LD (#EBDB), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EBFF), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EC02), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EC05), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EBE1), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EBE4), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EBE7), HL
                CALL @Action.NextRandomWord0.Entry
                LD (#EBEA), HL
                LD A, #01
                LD (#AA9A), A
                LD A, #2E
                LD (#A8BC), A
                RET


                endmodule
                endmodule
