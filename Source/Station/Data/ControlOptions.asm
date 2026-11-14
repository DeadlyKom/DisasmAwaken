                module ControlOptions
; Документация [настройки](../../../Docs/SettingsLabels.md)
                assert $ == #99C8
MouseOption:    FSettingWord { #81, #00 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
PitchUp:        FSettingWord { #FD, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
PitchDown:      FSettingWord { #FE, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
YawLeft:        FSettingWord { #BF, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
YawRight:       FSettingWord { #BF, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
RollLeft:       FSettingWord { #7F, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
RollRight:      FSettingWord { #7F, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
LaserKey:       FSettingWord { #FD, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
SpeedUp:        FSettingWord { #7F, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
SpeedDown:      FSettingWord { #7F, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
ComputerKey:    FSettingWord { #DF, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
MissileAim:     FSettingWord { #BF, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
ClearTargets:   FSettingWord { #FE, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Missile1:       FSettingWord { #F7, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Missile2:       FSettingWord { #F7, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Missile3:       FSettingWord { #F7, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
BoostKey:       FSettingWord { #BF, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
FreeFlightKey:  FSettingWord { #FD, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
GuidanceKey:    FSettingWord { #FE, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
ReturnKey:      FSettingWord { #FB, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
TractorKey:     FSettingWord { #7F, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
AntimissileKey: FSettingWord { #FB, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
CargoEject:     FSettingWord { #FB, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
MineEject:      FSettingWord { #FB, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
HyperJumpKey:   FSettingWord { #FD, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
NeonKey:        FSettingWord { #FD, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
ViewToggle:     FSettingWord { #FE, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
RadiationKey:   FSettingWord { #FD, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown28:      FSettingWord { #FE, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown29:      FSettingWord { #BF, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown30:      FSettingWord { #BF, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown31:      FSettingWord { #FD, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown32:      FSettingWord { #7F, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown33:      FSettingWord { #7F, #02 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown34:      FSettingWord { #DF, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown35:      FSettingWord { #BF, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown36:      FSettingWord { #FE, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown37:      FSettingWord { #F7, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown38:      FSettingWord { #BF, #08 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown39:      FSettingWord { #FB, #01 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown40:      FSettingWord { #FD, #04 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
Unknown41:      FSettingWord { #7F, #10 }                                       ; ValueOrRow, KeyMask, порядок исходного массива
ResourceSelect: FScriptResourceSelection { #00, #00 }                           ; GroupCount, RecordCount, исходный выбор ресурса LANG
                assert $ == #9A1E
                endmodule
