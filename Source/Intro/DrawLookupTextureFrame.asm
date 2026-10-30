                module Intro
                module DrawLookupTextureFrame
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Ожидание кадра, обновление масштаба и фаз перед формированием текстурного кадра
; исходная запись 3, файловые смещения #0893..#089B
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
Entry:          CALL @Intro.WaitInterrupt.Entry
                CALL @Intro.AdvanceTextureScale.Entry
                CALL @Intro.AdvanceTexturePhases.Entry
                ; JP @Intro.RenderLookupTexture.Entry, продолжение в RenderLookupTexture.asm

                endmodule
                endmodule
