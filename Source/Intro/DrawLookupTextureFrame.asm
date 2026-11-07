                module Intro
                module DrawLookupTextureFrame
                ; Документация [столбцовый и табличный эффекты](../../Docs/IntroGeneratedEffects.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Ожидание кадра, обновление масштаба и фаз перед формированием текстурного кадра
; исходная запись 3, файловые смещения #0893..#089B
                ; In:
                ;   параметры масштаба и фаз подготовлены, действуют условия WaitInterrupt и RenderLookupTexture
                ;   физические таблицы, цепочки и CPU-стек доступны, IRQ не вмешиваются во временные стеки
                ; Out:
                ;   обновлены счётчики масштаба, три записи фаз и четыре фазовых операнда
                ;   после последнего CALL исполнение продолжается в RenderLookupTexture с исходным CPU SP
                ;   конечный вывод и возврат определяются договором RenderLookupTexture и его продолжения
                ; Corrupt:
                ;   HL, DE, BC, AF, R, IFF, рабочие байты стека, записи фаз, счётчики масштаба и состояние IRQ
                ;   после передачи действуют побочные эффекты рендера
                ; Note:
                ;   128 сценариев проверили вход до рендера, его две части проверены отдельными моделями
                ;   обычный экранный путь предполагает исходный CALL в #6BDA, зеркальный режим описан отдельно
; -----------------------------------------
Entry:          CALL @Intro.WaitInterrupt.Entry
                CALL @Intro.AdvanceTextureScale.Entry
                CALL @Intro.AdvanceTexturePhases.Entry
                ; JP @Intro.RenderLookupTexture.Entry, продолжение в RenderLookupTexture.asm

                endmodule
                endmodule
