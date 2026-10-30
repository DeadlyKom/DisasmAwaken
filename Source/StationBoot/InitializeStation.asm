                module StationBoot
                module InitializeStation
; Документация [StationBoot](../../Docs/FunctionDetails/StationBoot.md)
; -----------------------------------------
; Перенос ядра из #65CE в #6322, загрузка банков и создание таблиц
; исходная запись 4, файловые смещения #0319..#0342
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
Entry:          LD HL, #65CE
                LD DE, #6322
                LD BC, #1C6A
                LDIR
                DI
                XOR A
                OUT (#FE), A
                LD (#9E78), A
                LD A, #17
                CALL #639F
                LD HL, #C000
                LD DE, #C001
                LD BC, #1AFF
                LD (HL), L
                LDIR
                LD A, #18
                CALL #639F
                JR @StationBoot.StartStation.Entry


                endmodule
                endmodule
