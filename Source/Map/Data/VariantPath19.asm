                module MapVariantPaths
                module Radius19
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CBB9
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #13, #00 }
Point01:        FMapPathPoint { #13, #02 }
Point02:        FMapPathPoint { #13, #03 }
Point03:        FMapPathPoint { #12, #05 }
Point04:        FMapPathPoint { #12, #06 }
Point05:        FMapPathPoint { #11, #08 }
Point06:        FMapPathPoint { #11, #09 }
Point07:        FMapPathPoint { #10, #0A }
Point08:        FMapPathPoint { #0F, #0C }
Point09:        FMapPathPoint { #0E, #0D }
Point10:        FMapPathPoint { #0D, #0E }
Point11:        FMapPathPoint { #0C, #0F }
Point12:        FMapPathPoint { #0A, #10 }
Point13:        FMapPathPoint { #09, #11 }
Point14:        FMapPathPoint { #08, #11 }
Point15:        FMapPathPoint { #06, #12 }
Point16:        FMapPathPoint { #05, #12 }
Point17:        FMapPathPoint { #03, #13 }
Point18:        FMapPathPoint { #02, #13 }
Point19:        FMapPathPoint { #00, #13 }
Point20:        FMapPathPoint { #FE, #13 }
Point21:        FMapPathPoint { #FD, #13 }
Point22:        FMapPathPoint { #FB, #12 }
Point23:        FMapPathPoint { #FA, #12 }
Point24:        FMapPathPoint { #F8, #11 }
Point25:        FMapPathPoint { #F7, #11 }
Point26:        FMapPathPoint { #F6, #10 }
Point27:        FMapPathPoint { #F4, #0F }
Point28:        FMapPathPoint { #F3, #0E }
Point29:        FMapPathPoint { #F2, #0D }
Point30:        FMapPathPoint { #F1, #0C }
Point31:        FMapPathPoint { #F0, #0A }
Point32:        FMapPathPoint { #EF, #09 }
Point33:        FMapPathPoint { #EF, #08 }
Point34:        FMapPathPoint { #EE, #06 }
Point35:        FMapPathPoint { #EE, #05 }
Point36:        FMapPathPoint { #ED, #03 }
Point37:        FMapPathPoint { #ED, #02 }
Point38:        FMapPathPoint { #ED, #00 }
Point39:        FMapPathPoint { #ED, #FE }
Point40:        FMapPathPoint { #ED, #FD }
Point41:        FMapPathPoint { #EE, #FB }
Point42:        FMapPathPoint { #EE, #FA }
Point43:        FMapPathPoint { #EF, #F8 }
Point44:        FMapPathPoint { #EF, #F7 }
Point45:        FMapPathPoint { #F0, #F6 }
Point46:        FMapPathPoint { #F1, #F4 }
Point47:        FMapPathPoint { #F2, #F3 }
Point48:        FMapPathPoint { #F3, #F2 }
Point49:        FMapPathPoint { #F4, #F1 }
Point50:        FMapPathPoint { #F6, #F0 }
Point51:        FMapPathPoint { #F7, #EF }
Point52:        FMapPathPoint { #F8, #EF }
Point53:        FMapPathPoint { #FA, #EE }
Point54:        FMapPathPoint { #FB, #EE }
Point55:        FMapPathPoint { #FD, #ED }
Point56:        FMapPathPoint { #FE, #ED }
Point57:        FMapPathPoint { #00, #ED }
Point58:        FMapPathPoint { #02, #ED }
Point59:        FMapPathPoint { #03, #ED }
Point60:        FMapPathPoint { #05, #EE }
Point61:        FMapPathPoint { #06, #EE }
Point62:        FMapPathPoint { #08, #EF }
Point63:        FMapPathPoint { #09, #EF }
Point64:        FMapPathPoint { #0A, #F0 }
Point65:        FMapPathPoint { #0C, #F1 }
Point66:        FMapPathPoint { #0D, #F2 }
Point67:        FMapPathPoint { #0E, #F3 }
Point68:        FMapPathPoint { #0F, #F4 }
Point69:        FMapPathPoint { #10, #F6 }
Point70:        FMapPathPoint { #11, #F7 }
Point71:        FMapPathPoint { #11, #F8 }
Point72:        FMapPathPoint { #12, #FA }
Point73:        FMapPathPoint { #12, #FB }
Point74:        FMapPathPoint { #13, #FD }
Point75:        FMapPathPoint { #13, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CC52
                endmodule
                endmodule
