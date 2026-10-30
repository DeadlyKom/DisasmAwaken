                module Intro
                module PresentLookupTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Восстановление SP после #A800, две серии выборок и общий вывод кадра
; исходная запись 3, файловые смещения #08BC..#08E2
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   дополнительный вход после генерируемого #A800, исходный SP берётся из операнда #6BBD
;   13 строк из #AD00 и 25 строк из #B380 заполняют две части буфера выборок
;   между частями ожидается кадр, масштаб обновляется после каждой части
; -----------------------------------------
                ; операнд восстановления SP заполняется перед переходом в #A800
Entry:          LD SP, #3131
                LD IXL, #0D
                LD HL, #AD00
                LD BC, #8000
                CALL @Intro.RunTextureSampler.Entry
                CALL @Intro.WaitInterrupt.Entry
                CALL @Intro.AdvanceTextureScale.Entry
                LD IXL, #19
                LD HL, #B380
                LD BC, #8340
                CALL @Intro.RunTextureSampler.Entry
                CALL @Intro.AdvanceTextureScale.Entry
                JP @Intro.PresentInterlacedFrame.Entry


                endmodule
                endmodule
