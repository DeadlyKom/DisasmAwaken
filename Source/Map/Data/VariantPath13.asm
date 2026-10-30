                module MapVariantPaths
                module Radius13
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CACF
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #0D, #00 }
Point01:        FMapPathPoint { #0D, #02 }
Point02:        FMapPathPoint { #0D, #03 }
Point03:        FMapPathPoint { #0C, #05 }
Point04:        FMapPathPoint { #0C, #06 }
Point05:        FMapPathPoint { #0B, #07 }
Point06:        FMapPathPoint { #0A, #09 }
Point07:        FMapPathPoint { #09, #0A }
Point08:        FMapPathPoint { #07, #0B }
Point09:        FMapPathPoint { #06, #0C }
Point10:        FMapPathPoint { #05, #0C }
Point11:        FMapPathPoint { #03, #0D }
Point12:        FMapPathPoint { #02, #0D }
Point13:        FMapPathPoint { #00, #0D }
Point14:        FMapPathPoint { #FE, #0D }
Point15:        FMapPathPoint { #FD, #0D }
Point16:        FMapPathPoint { #FB, #0C }
Point17:        FMapPathPoint { #FA, #0C }
Point18:        FMapPathPoint { #F9, #0B }
Point19:        FMapPathPoint { #F7, #0A }
Point20:        FMapPathPoint { #F6, #09 }
Point21:        FMapPathPoint { #F5, #07 }
Point22:        FMapPathPoint { #F4, #06 }
Point23:        FMapPathPoint { #F4, #05 }
Point24:        FMapPathPoint { #F3, #03 }
Point25:        FMapPathPoint { #F3, #02 }
Point26:        FMapPathPoint { #F3, #00 }
Point27:        FMapPathPoint { #F3, #FE }
Point28:        FMapPathPoint { #F3, #FD }
Point29:        FMapPathPoint { #F4, #FB }
Point30:        FMapPathPoint { #F4, #FA }
Point31:        FMapPathPoint { #F5, #F9 }
Point32:        FMapPathPoint { #F6, #F7 }
Point33:        FMapPathPoint { #F7, #F6 }
Point34:        FMapPathPoint { #F9, #F5 }
Point35:        FMapPathPoint { #FA, #F4 }
Point36:        FMapPathPoint { #FB, #F4 }
Point37:        FMapPathPoint { #FD, #F3 }
Point38:        FMapPathPoint { #FE, #F3 }
Point39:        FMapPathPoint { #00, #F3 }
Point40:        FMapPathPoint { #02, #F3 }
Point41:        FMapPathPoint { #03, #F3 }
Point42:        FMapPathPoint { #05, #F4 }
Point43:        FMapPathPoint { #06, #F4 }
Point44:        FMapPathPoint { #07, #F5 }
Point45:        FMapPathPoint { #09, #F6 }
Point46:        FMapPathPoint { #0A, #F7 }
Point47:        FMapPathPoint { #0B, #F9 }
Point48:        FMapPathPoint { #0C, #FA }
Point49:        FMapPathPoint { #0C, #FB }
Point50:        FMapPathPoint { #0D, #FD }
Point51:        FMapPathPoint { #0D, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CB38
                endmodule
                endmodule
