                module KeyboardCodes
; Документация [одиночная клавиша](../../../Docs/MatrixKey.md)
; Anchor не проверяется, Code1D..Code5A задают код своей позицией, нулевые пары сохраняются
                assert $ == #96AA
Anchor:         FKeyBinding { #00, #00 }                                        ; якорь перед первым проверяемым элементом
Code1D:         FKeyBinding { #FE, #01 }                                        ; RowMask, KeyMask для кода позиции
Code1E:         FKeyBinding { #BF, #01 }                                        ; RowMask, KeyMask для кода позиции
Code1F:         FKeyBinding { #7F, #02 }                                        ; RowMask, KeyMask для кода позиции
Code20:         FKeyBinding { #7F, #01 }                                        ; RowMask, KeyMask для кода позиции
Code21:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code22:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code23:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code24:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code25:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code26:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code27:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code28:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code29:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2A:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2B:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2C:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2D:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2E:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code2F:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code30:         FKeyBinding { #EF, #01 }                                        ; RowMask, KeyMask для кода позиции
Code31:         FKeyBinding { #F7, #01 }                                        ; RowMask, KeyMask для кода позиции
Code32:         FKeyBinding { #F7, #02 }                                        ; RowMask, KeyMask для кода позиции
Code33:         FKeyBinding { #F7, #04 }                                        ; RowMask, KeyMask для кода позиции
Code34:         FKeyBinding { #F7, #08 }                                        ; RowMask, KeyMask для кода позиции
Code35:         FKeyBinding { #F7, #10 }                                        ; RowMask, KeyMask для кода позиции
Code36:         FKeyBinding { #EF, #10 }                                        ; RowMask, KeyMask для кода позиции
Code37:         FKeyBinding { #EF, #08 }                                        ; RowMask, KeyMask для кода позиции
Code38:         FKeyBinding { #EF, #04 }                                        ; RowMask, KeyMask для кода позиции
Code39:         FKeyBinding { #EF, #02 }                                        ; RowMask, KeyMask для кода позиции
Code3A:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code3B:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code3C:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code3D:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code3E:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code3F:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code40:         FKeyBinding { #00, #00 }                                        ; RowMask, KeyMask, нулевая пара не ограничивает поиск
Code41:         FKeyBinding { #FD, #01 }                                        ; RowMask, KeyMask для кода позиции
Code42:         FKeyBinding { #7F, #10 }                                        ; RowMask, KeyMask для кода позиции
Code43:         FKeyBinding { #FE, #08 }                                        ; RowMask, KeyMask для кода позиции
Code44:         FKeyBinding { #FD, #04 }                                        ; RowMask, KeyMask для кода позиции
Code45:         FKeyBinding { #FB, #04 }                                        ; RowMask, KeyMask для кода позиции
Code46:         FKeyBinding { #FD, #08 }                                        ; RowMask, KeyMask для кода позиции
Code47:         FKeyBinding { #FD, #10 }                                        ; RowMask, KeyMask для кода позиции
Code48:         FKeyBinding { #BF, #10 }                                        ; RowMask, KeyMask для кода позиции
Code49:         FKeyBinding { #DF, #04 }                                        ; RowMask, KeyMask для кода позиции
Code4A:         FKeyBinding { #BF, #08 }                                        ; RowMask, KeyMask для кода позиции
Code4B:         FKeyBinding { #BF, #04 }                                        ; RowMask, KeyMask для кода позиции
Code4C:         FKeyBinding { #BF, #02 }                                        ; RowMask, KeyMask для кода позиции
Code4D:         FKeyBinding { #7F, #04 }                                        ; RowMask, KeyMask для кода позиции
Code4E:         FKeyBinding { #7F, #08 }                                        ; RowMask, KeyMask для кода позиции
Code4F:         FKeyBinding { #DF, #02 }                                        ; RowMask, KeyMask для кода позиции
Code50:         FKeyBinding { #DF, #01 }                                        ; RowMask, KeyMask для кода позиции
Code51:         FKeyBinding { #FB, #01 }                                        ; RowMask, KeyMask для кода позиции
Code52:         FKeyBinding { #FB, #08 }                                        ; RowMask, KeyMask для кода позиции
Code53:         FKeyBinding { #FD, #02 }                                        ; RowMask, KeyMask для кода позиции
Code54:         FKeyBinding { #FB, #10 }                                        ; RowMask, KeyMask для кода позиции
Code55:         FKeyBinding { #DF, #08 }                                        ; RowMask, KeyMask для кода позиции
Code56:         FKeyBinding { #FE, #10 }                                        ; RowMask, KeyMask для кода позиции
Code57:         FKeyBinding { #FB, #02 }                                        ; RowMask, KeyMask для кода позиции
Code58:         FKeyBinding { #FE, #04 }                                        ; RowMask, KeyMask для кода позиции
Code59:         FKeyBinding { #DF, #10 }                                        ; RowMask, KeyMask для кода позиции
Code5A:         FKeyBinding { #FE, #02 }                                        ; RowMask, KeyMask для кода позиции
                assert $ == #9728
                endmodule
