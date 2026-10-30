                module Music
                module TickDispatch
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Изменяемый вход музыкального тика, исходный JP выбирает синтез без обновления строки паттерна
; исходная запись 10, файловые смещения #031F..#0373
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
Entry:          JP @Music.RenderChannelA.Entry


                EXX
                LD A, #C3
                LD (#DE1F), A
                XOR A
                LD L, A
                LD H, A
                LD DE, #0618
                LD (#E098), HL
                JR @Music.TickDispatch.PointDE5C


                LD (#DFFA), A
                LD (#E03E), A
                LD (#E055), A
                LD (#E07C), A
                LD (#E09F), A
                LD (#E0D7), A
                LD (#E06C), HL
                CPL
                LD (#DFEF), A
                LD A, #00
                LD (#E0BB), A
                LD HL, #0000
                LD (#DFF6), HL
                LD A, #10
                LD (#E011), A
PointDE5C:      LD A, #00
                LD (#E02D), A
                JR @Music.TickDispatch.PointDE72


                XOR A
                LD (#E07C), A
                LD HL, #0000
                LD (#E078), HL
                LD A, #00
                LD (#E037), A
PointDE72:      JR @Music.UnknownDE90.Entry


                endmodule
                endmodule
