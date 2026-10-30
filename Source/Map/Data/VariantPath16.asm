                module MapVariantPaths
                module Radius16
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CB38
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #10, #00 }
Point01:        FMapPathPoint { #10, #02 }
Point02:        FMapPathPoint { #10, #03 }
Point03:        FMapPathPoint { #0F, #05 }
Point04:        FMapPathPoint { #0F, #06 }
Point05:        FMapPathPoint { #0E, #08 }
Point06:        FMapPathPoint { #0D, #09 }
Point07:        FMapPathPoint { #0C, #0A }
Point08:        FMapPathPoint { #0B, #0B }
Point09:        FMapPathPoint { #0A, #0C }
Point10:        FMapPathPoint { #09, #0D }
Point11:        FMapPathPoint { #08, #0E }
Point12:        FMapPathPoint { #06, #0F }
Point13:        FMapPathPoint { #05, #0F }
Point14:        FMapPathPoint { #03, #10 }
Point15:        FMapPathPoint { #02, #10 }
Point16:        FMapPathPoint { #00, #10 }
Point17:        FMapPathPoint { #FE, #10 }
Point18:        FMapPathPoint { #FD, #10 }
Point19:        FMapPathPoint { #FB, #0F }
Point20:        FMapPathPoint { #FA, #0F }
Point21:        FMapPathPoint { #F8, #0E }
Point22:        FMapPathPoint { #F7, #0D }
Point23:        FMapPathPoint { #F6, #0C }
Point24:        FMapPathPoint { #F5, #0B }
Point25:        FMapPathPoint { #F4, #0A }
Point26:        FMapPathPoint { #F3, #09 }
Point27:        FMapPathPoint { #F2, #08 }
Point28:        FMapPathPoint { #F1, #06 }
Point29:        FMapPathPoint { #F1, #05 }
Point30:        FMapPathPoint { #F0, #03 }
Point31:        FMapPathPoint { #F0, #02 }
Point32:        FMapPathPoint { #F0, #00 }
Point33:        FMapPathPoint { #F0, #FE }
Point34:        FMapPathPoint { #F0, #FD }
Point35:        FMapPathPoint { #F1, #FB }
Point36:        FMapPathPoint { #F1, #FA }
Point37:        FMapPathPoint { #F2, #F8 }
Point38:        FMapPathPoint { #F3, #F7 }
Point39:        FMapPathPoint { #F4, #F6 }
Point40:        FMapPathPoint { #F5, #F5 }
Point41:        FMapPathPoint { #F6, #F4 }
Point42:        FMapPathPoint { #F7, #F3 }
Point43:        FMapPathPoint { #F8, #F2 }
Point44:        FMapPathPoint { #FA, #F1 }
Point45:        FMapPathPoint { #FB, #F1 }
Point46:        FMapPathPoint { #FD, #F0 }
Point47:        FMapPathPoint { #FE, #F0 }
Point48:        FMapPathPoint { #00, #F0 }
Point49:        FMapPathPoint { #02, #F0 }
Point50:        FMapPathPoint { #03, #F0 }
Point51:        FMapPathPoint { #05, #F1 }
Point52:        FMapPathPoint { #06, #F1 }
Point53:        FMapPathPoint { #08, #F2 }
Point54:        FMapPathPoint { #09, #F3 }
Point55:        FMapPathPoint { #0A, #F4 }
Point56:        FMapPathPoint { #0B, #F5 }
Point57:        FMapPathPoint { #0C, #F6 }
Point58:        FMapPathPoint { #0D, #F7 }
Point59:        FMapPathPoint { #0E, #F8 }
Point60:        FMapPathPoint { #0F, #FA }
Point61:        FMapPathPoint { #0F, #FB }
Point62:        FMapPathPoint { #10, #FD }
Point63:        FMapPathPoint { #10, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CBB9
                endmodule
                endmodule
