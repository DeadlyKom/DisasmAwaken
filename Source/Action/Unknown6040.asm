                module Action
                module Unknown6040
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #027D..#02EA
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          PUSH AF
                PUSH BC
                PUSH HL
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL #EC59
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                POP HL
                POP BC
                POP AF
                RET


Point6054:      PUSH DE
                LD DE, #F2A5
                CALL @Action.Unknown6040.Entry
                POP DE
                LD HL, #EE4D
                LD (#ECF6), HL
                LD A, #3F
                LD I, A
                LD IY, #5C3A
                LD B, #64
Point606C:      PUSH BC
                LD DE, #8000
                LD A, R
                LD L, A
                LD H, #05
                LD BC, #0C00
                LDIR
                EI
                HALT
                DI
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL #C870
                CALL #ECA2
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UnknownECA8.Entry
                POP BC
                DEC B
                JP NZ, @Action.Unknown6040.Point60A3                            ; переход, если флаг Z сброшен


                LD B, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR Z, @Action.Unknown6040.Point606C                             ; переход, если флаг Z установлен


                JP @Action.UpdateFrame.PointAAC4


Point60A3:      LD A, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR @Action.Unknown6040.Point606C


                endmodule
                endmodule
