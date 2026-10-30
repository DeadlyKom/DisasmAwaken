                module Action
                module StartFlight
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Вывод панели из страницы 6 и инициализация полётного режима
; исходная запись 17, файловые смещения #482D..#4858
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
Entry:          DI
                LD A, #1E
                CALL @Action.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #4000
                LD BC, #1B00
                LDIR
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.Unknown6145.Entry
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL #DE0A
                CALL @Action.Unknown6CD6.Entry
                PUSH DE
                LD DE, #F1AB
                CALL @Action.Unknown6040.Entry
                POP DE
                ; JP @Action.MainLoop.Entry, продолжение в MainLoop.asm

                endmodule
                endmodule
