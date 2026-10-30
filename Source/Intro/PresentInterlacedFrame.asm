                module Intro
                module PresentInterlacedFrame
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Чередование двух раскладок, синхронизация с кадром и перенос данных текстуры в экран
; исходная запись 3, файловые смещения #04F1..#0526
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   байт фазы #67F2 меняется между #00 и #80, это собственный счётчик, не обработчик IRQ
;   в #6839 записываются NOP NOP либо INC H NOP, меняется половина таблицы источников
;   одна экранная половина выводится до атрибутов, вторая после них, порядок зависит от фазы
;   WaitInterrupt выполняет EI, HALT, DI и сохраняет флаги предыдущего расчёта фазы
; -----------------------------------------
                ; расчёт фазы чередования, операнд #67F2 переключается между нулём и #80
Entry:          LD A, #00
                ADD A, #80
                LD (#67F2), A
                LD HL, #0000
                JR NZ, @Intro.PresentInterlacedFrame.Point67FF                  ; переход, если фаза равна #80 и добавление к H не требуется


                LD H, #14
                ; обновление двух байтов кода коррекции адреса, NOP NOP либо INC H NOP
Point67FF:      LD (#6839), HL
                CALL @Intro.WaitInterrupt.Entry
                JR NZ, @Intro.PresentInterlacedFrame.Point6818                  ; переход, если текущая фаза равна #80


                LD HL, #6100
                CALL @Intro.ScatterTextureToScreen.Entry
                LD HL, #60C0
                CALL @Intro.RunAttributeWriter.Entry
                LD HL, #6000
                JR @Intro.ScatterTextureToScreen.Entry


Point6818:      LD HL, #6000
                CALL @Intro.ScatterTextureToScreen.Entry
                LD HL, #61C0
                CALL @Intro.RunAttributeWriter.Entry
                LD HL, #6100
                ; JP @Intro.ScatterTextureToScreen.Entry, продолжение в ScatterTextureToScreen.asm

                endmodule
                endmodule
