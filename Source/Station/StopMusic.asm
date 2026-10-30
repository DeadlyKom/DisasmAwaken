                module Station
                module StopMusic
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Остановка музыкального модуля в странице 3 и восстановление IM 1
; исходная запись 4, файловые смещения #0656..#066E
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
Entry:          LD A, #13
                CALL @Station.SelectMemoryPage.Entry
                CALL #DB08
                IM 1
                LD A, #3F
                LD I, A
                LD IY, #5C3A
                LD A, #10
                CALL @Station.SelectMemoryPage.Entry
                POP HL
                RET


                endmodule
                endmodule
