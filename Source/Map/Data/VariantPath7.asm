                module MapVariantPaths
                module Radius7
; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)
                assert $ == #CA45
                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала
Point00:        FMapPathPoint { #07, #00 }
Point01:        FMapPathPoint { #07, #02 }
Point02:        FMapPathPoint { #06, #03 }
Point03:        FMapPathPoint { #05, #04 }
Point04:        FMapPathPoint { #04, #05 }
Point05:        FMapPathPoint { #03, #06 }
Point06:        FMapPathPoint { #02, #07 }
Point07:        FMapPathPoint { #00, #07 }
Point08:        FMapPathPoint { #FE, #07 }
Point09:        FMapPathPoint { #FD, #06 }
Point10:        FMapPathPoint { #FC, #05 }
Point11:        FMapPathPoint { #FB, #04 }
Point12:        FMapPathPoint { #FA, #03 }
Point13:        FMapPathPoint { #F9, #02 }
Point14:        FMapPathPoint { #F9, #00 }
Point15:        FMapPathPoint { #F9, #FE }
Point16:        FMapPathPoint { #FA, #FD }
Point17:        FMapPathPoint { #FB, #FC }
Point18:        FMapPathPoint { #FC, #FB }
Point19:        FMapPathPoint { #FD, #FA }
Point20:        FMapPathPoint { #FE, #F9 }
Point21:        FMapPathPoint { #00, #F9 }
Point22:        FMapPathPoint { #02, #F9 }
Point23:        FMapPathPoint { #03, #FA }
Point24:        FMapPathPoint { #04, #FB }
Point25:        FMapPathPoint { #05, #FC }
Point26:        FMapPathPoint { #06, #FD }
Point27:        FMapPathPoint { #07, #FE }
                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы
End:            db #80
                assert $ == #CA7E
                endmodule
                endmodule
