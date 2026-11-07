                module Intro
                module DrawFinalTextureFrame
                ; Физические параметры [источники и потребители](../../Docs/IntroPhysicalParameters.md)
                ; Документация [прокручиваемая текстура](../../Docs/IntroScrolledFrame.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Настройка смещения и параметров последнего текстурного эффекта вступления
; исходная запись 3, файловые смещения #031E..#032B
                ; In:
                ;   числовые регистровые аргументы не нужны, должны выполняться условия DrawScrolledTexture
                ; Out:
                ;   DrawScrolledTexture получает HL=#662C, DE=#FFFF, BC=#6632, A=#16
                ;   исходный F сохранён до входа рисователя, SP не меняется на хвостовом JP
                ; Corrupt:
                ;   HL, DE, BC, A и R до передачи, затем действует договор DrawScrolledTexture
                ; Note:
                ;   оба смещения уменьшаются на единицу по модулю 64, 12 сценариев выполнены через этот вход
; -----------------------------------------
Entry:          LD A, #16
                LD DE, #FFFF
                LD HL, @IntroFinalTexturePhases.First
                LD BC, @IntroFinalTexturePhases.Second
                JP @Intro.DrawScrolledTexture.Entry


                endmodule
                endmodule
