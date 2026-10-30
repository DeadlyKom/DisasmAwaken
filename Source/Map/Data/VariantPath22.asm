                module MapVariantPaths
                module Radius22
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CC52
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #16, #00 }
Point01:        FMapPathPoint { #16, #02 }
Point02:        FMapPathPoint { #16, #03 }
Point03:        FMapPathPoint { #15, #05 }
Point04:        FMapPathPoint { #15, #06 }
Point05:        FMapPathPoint { #15, #08 }
Point06:        FMapPathPoint { #14, #09 }
Point07:        FMapPathPoint { #13, #0B }
Point08:        FMapPathPoint { #13, #0C }
Point09:        FMapPathPoint { #12, #0D }
Point10:        FMapPathPoint { #11, #0E }
Point11:        FMapPathPoint { #10, #10 }
Point12:        FMapPathPoint { #0E, #11 }
Point13:        FMapPathPoint { #0D, #12 }
Point14:        FMapPathPoint { #0C, #13 }
Point15:        FMapPathPoint { #0B, #13 }
Point16:        FMapPathPoint { #09, #14 }
Point17:        FMapPathPoint { #08, #15 }
Point18:        FMapPathPoint { #06, #15 }
Point19:        FMapPathPoint { #05, #15 }
Point20:        FMapPathPoint { #03, #16 }
Point21:        FMapPathPoint { #02, #16 }
Point22:        FMapPathPoint { #00, #16 }
Point23:        FMapPathPoint { #FE, #16 }
Point24:        FMapPathPoint { #FD, #16 }
Point25:        FMapPathPoint { #FB, #15 }
Point26:        FMapPathPoint { #FA, #15 }
Point27:        FMapPathPoint { #F8, #15 }
Point28:        FMapPathPoint { #F7, #14 }
Point29:        FMapPathPoint { #F5, #13 }
Point30:        FMapPathPoint { #F4, #13 }
Point31:        FMapPathPoint { #F3, #12 }
Point32:        FMapPathPoint { #F2, #11 }
Point33:        FMapPathPoint { #F0, #10 }
Point34:        FMapPathPoint { #EF, #0E }
Point35:        FMapPathPoint { #EE, #0D }
Point36:        FMapPathPoint { #ED, #0C }
Point37:        FMapPathPoint { #ED, #0B }
Point38:        FMapPathPoint { #EC, #09 }
Point39:        FMapPathPoint { #EB, #08 }
Point40:        FMapPathPoint { #EB, #06 }
Point41:        FMapPathPoint { #EB, #05 }
Point42:        FMapPathPoint { #EA, #03 }
Point43:        FMapPathPoint { #EA, #02 }
Point44:        FMapPathPoint { #EA, #00 }
Point45:        FMapPathPoint { #EA, #FE }
Point46:        FMapPathPoint { #EA, #FD }
Point47:        FMapPathPoint { #EB, #FB }
Point48:        FMapPathPoint { #EB, #FA }
Point49:        FMapPathPoint { #EB, #F8 }
Point50:        FMapPathPoint { #EC, #F7 }
Point51:        FMapPathPoint { #ED, #F5 }
Point52:        FMapPathPoint { #ED, #F4 }
Point53:        FMapPathPoint { #EE, #F3 }
Point54:        FMapPathPoint { #EF, #F2 }
Point55:        FMapPathPoint { #F0, #F0 }
Point56:        FMapPathPoint { #F2, #EF }
Point57:        FMapPathPoint { #F3, #EE }
Point58:        FMapPathPoint { #F4, #ED }
Point59:        FMapPathPoint { #F5, #ED }
Point60:        FMapPathPoint { #F7, #EC }
Point61:        FMapPathPoint { #F8, #EB }
Point62:        FMapPathPoint { #FA, #EB }
Point63:        FMapPathPoint { #FB, #EB }
Point64:        FMapPathPoint { #FD, #EA }
Point65:        FMapPathPoint { #FE, #EA }
Point66:        FMapPathPoint { #00, #EA }
Point67:        FMapPathPoint { #02, #EA }
Point68:        FMapPathPoint { #03, #EA }
Point69:        FMapPathPoint { #05, #EB }
Point70:        FMapPathPoint { #06, #EB }
Point71:        FMapPathPoint { #08, #EB }
Point72:        FMapPathPoint { #09, #EC }
Point73:        FMapPathPoint { #0B, #ED }
Point74:        FMapPathPoint { #0C, #ED }
Point75:        FMapPathPoint { #0D, #EE }
Point76:        FMapPathPoint { #0E, #EF }
Point77:        FMapPathPoint { #10, #F0 }
Point78:        FMapPathPoint { #11, #F2 }
Point79:        FMapPathPoint { #12, #F3 }
Point80:        FMapPathPoint { #13, #F4 }
Point81:        FMapPathPoint { #13, #F5 }
Point82:        FMapPathPoint { #14, #F7 }
Point83:        FMapPathPoint { #15, #F8 }
Point84:        FMapPathPoint { #15, #FA }
Point85:        FMapPathPoint { #15, #FB }
Point86:        FMapPathPoint { #16, #FD }
Point87:        FMapPathPoint { #16, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CD03
                endmodule
                endmodule
