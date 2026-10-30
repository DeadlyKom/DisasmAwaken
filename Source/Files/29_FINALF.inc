; -----------------------------------------
; запись 29, FINALF.C
; логическая длина 19114, полный секторный размер 19200
; -----------------------------------------
                assert $ == #0000
                disp #6000
                include "../Final/InitializeFinal.asm"
                ent
                assert $ == #0123
                disp #6123
                include "../Final/ReadSpeedKeys.asm"
                ent
                assert $ == #0148
                disp #6148
                include "../Final/HaltFinal.asm"                                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #016C
                disp #616C
                include "../Final/Interrupt.asm"                                ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #017A
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/29_FINALF/Unclassified000.bin"
                assert $ == #0196
                disp #6196
                include "../Final/PrepareFrame.asm"
                ent
                assert $ == #01DF
                disp #61DF
                include "../Final/BuildDisplayChain.asm"
                ent
                assert $ == #020E
                disp #620E
                include "../Final/EmitBitmapLine.asm"
                ent
                assert $ == #0234
                disp #6234
                include "../Final/EmitAttributeRow.asm"
                ent
                assert $ == #0247
                disp #6247
                include "../FinalTemplates/BitmapLine.asm"
                ent
                assert $ == #027B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/29_FINALF/Unclassified001.bin"
                assert $ == #027D
                disp #627D
                include "../FinalTemplates/AttributeRow.asm"
                ent
                assert $ == #0294
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/29_FINALF/Unclassified002.bin"
                assert $ == #0296
                disp #6296
                include "../Final/NextBitmapLine.asm"
                ent
                assert $ == #02A5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/29_FINALF/Unclassified003.bin"
                assert $ == #02A9
                ; исходный ресурс ZX_BITMAP
                incbin "../Final/Resources/Frame0.bitmap"
                assert $ == #1AA9
                ; исходный ресурс ZX_BITMAP
                incbin "../Final/Resources/Frame1.bitmap"
                assert $ == #32A9
                ; исходный ресурс ZX_BITMAP
                incbin "../Final/Resources/Frame2.bitmap"
                assert $ == #4AA9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/29_FINALF/Unclassified004.bin"
                assert $ == #4B00
