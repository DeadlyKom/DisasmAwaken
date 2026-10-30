                module MapVariantPaths
                module Radius10
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CA7E
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #0A, #00 }
Point01:        FMapPathPoint { #0A, #02 }
Point02:        FMapPathPoint { #0A, #03 }
Point03:        FMapPathPoint { #09, #05 }
Point04:        FMapPathPoint { #08, #06 }
Point05:        FMapPathPoint { #07, #07 }
Point06:        FMapPathPoint { #06, #08 }
Point07:        FMapPathPoint { #05, #09 }
Point08:        FMapPathPoint { #03, #0A }
Point09:        FMapPathPoint { #02, #0A }
Point10:        FMapPathPoint { #00, #0A }
Point11:        FMapPathPoint { #FE, #0A }
Point12:        FMapPathPoint { #FD, #0A }
Point13:        FMapPathPoint { #FB, #09 }
Point14:        FMapPathPoint { #FA, #08 }
Point15:        FMapPathPoint { #F9, #07 }
Point16:        FMapPathPoint { #F8, #06 }
Point17:        FMapPathPoint { #F7, #05 }
Point18:        FMapPathPoint { #F6, #03 }
Point19:        FMapPathPoint { #F6, #02 }
Point20:        FMapPathPoint { #F6, #00 }
Point21:        FMapPathPoint { #F6, #FE }
Point22:        FMapPathPoint { #F6, #FD }
Point23:        FMapPathPoint { #F7, #FB }
Point24:        FMapPathPoint { #F8, #FA }
Point25:        FMapPathPoint { #F9, #F9 }
Point26:        FMapPathPoint { #FA, #F8 }
Point27:        FMapPathPoint { #FB, #F7 }
Point28:        FMapPathPoint { #FD, #F6 }
Point29:        FMapPathPoint { #FE, #F6 }
Point30:        FMapPathPoint { #00, #F6 }
Point31:        FMapPathPoint { #02, #F6 }
Point32:        FMapPathPoint { #03, #F6 }
Point33:        FMapPathPoint { #05, #F7 }
Point34:        FMapPathPoint { #06, #F8 }
Point35:        FMapPathPoint { #07, #F9 }
Point36:        FMapPathPoint { #08, #FA }
Point37:        FMapPathPoint { #09, #FB }
Point38:        FMapPathPoint { #0A, #FD }
Point39:        FMapPathPoint { #0A, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CACF
                endmodule
                endmodule
