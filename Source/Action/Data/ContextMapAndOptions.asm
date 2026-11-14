                module ActionContextMapAndOptions
                ; Документация [средняя часть переносимого состояния](../../../Docs/ActionContextTail.md)
                assert $ == #9C8B
BeforeMap:      db #00                                                          ; старший байт архивного DALNO, современный читатель неизвестен
                ; -----------------------------------------
                ; Переносимая группа StoredMapPoints
                assert $ == #9C8C
Point00:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point01:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point02:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point03:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point04:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point05:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point06:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point07:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point08:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point09:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point10:        db #80                                                          ; граница станционного списка
Point11:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point12:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point13:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point14:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point15:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point16:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point17:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point18:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point19:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point20:        FStoredMapPoint {
                    #FFFF,                                                      ; FirstWord, исходное значение ACTION
                    #FFFF,                                                      ; SecondWord, исходное значение ACTION
                    #FF                                                         ; Variant, исходное значение ACTION
                }
Point21:        db #80                                                          ; граница станционного списка
                ; -----------------------------------------
                ; Переносимая группа StoredMapOrder
                assert $ == #9CF2
Order00:        FStoredMapOrder {
                    #22,                                                        ; Layout, исходное значение ACTION
                    #00,                                                        ; Order00, исходное значение ACTION
                    #00,                                                        ; Order01, исходное значение ACTION
                    #00,                                                        ; Order02, исходное значение ACTION
                    #00,                                                        ; Order03, исходное значение ACTION
                    #00,                                                        ; Order04, исходное значение ACTION
                    #00,                                                        ; Order05, исходное значение ACTION
                    #00,                                                        ; Order06, исходное значение ACTION
                    #00,                                                        ; Order07, исходное значение ACTION
                    #00,                                                        ; Order08, исходное значение ACTION
                    #00                                                         ; Order09, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа MapAuxiliaryPoints
                assert $ == #9CFD
Aux00:          FMapCoordinateKey {
                    #4B39,                                                      ; FirstWord, исходное значение ACTION
                    #0006                                                       ; SecondWord, исходное значение ACTION
                }
Aux01:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux02:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux03:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux04:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux05:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux06:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux07:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux08:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
Aux09:          FMapCoordinateKey {
                    #0000,                                                      ; FirstWord, исходное значение ACTION
                    #0000                                                       ; SecondWord, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа MapAuxiliaryCodes
                assert $ == #9D25
Codes00:        FMapMarkerCodes {
                    #01,                                                        ; ActiveCode, исходное значение ACTION
                    #00,                                                        ; CompletionCode, исходное значение ACTION
                    #00,                                                        ; Unknown02, исходное значение ACTION
                    #00,                                                        ; Unknown03, исходное значение ACTION
                    #00,                                                        ; Unknown04, исходное значение ACTION
                    #00,                                                        ; Unknown05, исходное значение ACTION
                    #00,                                                        ; Unknown06, исходное значение ACTION
                    #00,                                                        ; Unknown07, исходное значение ACTION
                    #00,                                                        ; Unknown08, исходное значение ACTION
                    #00,                                                        ; Unknown09, исходное значение ACTION
                    #80                                                         ; Unknown10, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа InterfaceChoices
                assert $ == #9D30
MouseOption:    FSettingWord {
                    #81,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
JoyOption:      FSettingWord {
                    #80,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
MusicMode:      FSettingWord {
                    #81,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
FillMode:       FSettingWord {
                    #80,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа PointerKeys
                assert $ == #9D38
PointerUp:      FKeyBinding {
                    #FB,                                                        ; RowMask, исходное значение ACTION
                    #01                                                         ; KeyMask, исходное значение ACTION
                }
PointerDown:    FKeyBinding {
                    #FD,                                                        ; RowMask, исходное значение ACTION
                    #01                                                         ; KeyMask, исходное значение ACTION
                }
PointerLeft:    FKeyBinding {
                    #DF,                                                        ; RowMask, исходное значение ACTION
                    #02                                                         ; KeyMask, исходное значение ACTION
                }
PointerRight:   FKeyBinding {
                    #DF,                                                        ; RowMask, исходное значение ACTION
                    #01                                                         ; KeyMask, исходное значение ACTION
                }
PointerAction2: FKeyBinding {
                    #7F,                                                        ; RowMask, исходное значение ACTION
                    #01                                                         ; KeyMask, исходное значение ACTION
                }
PointerAction1: FKeyBinding {
                    #7F,                                                        ; RowMask, исходное значение ACTION
                    #04                                                         ; KeyMask, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа InterfaceColors
                assert $ == #9D44
InkBits:        FSettingWord {
                    #00,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
PaperRotate:    FSettingWord {
                    #05,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
HighRotate:     FSettingWord {
                    #00,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
                ; -----------------------------------------
                ; Переносимая группа ControlOptions
                assert $ == #9D4A
FlightMouse:    FSettingWord {
                    #81,                                                        ; ValueOrRow, исходное значение ACTION
                    #00                                                         ; KeyMask, исходное значение ACTION
                }
                assert $ == #9D4C
                endmodule
