                module Save1ControlOptions
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #018D
MouseOption:    FSettingWord {
                    #81,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
PitchUp:        FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
PitchDown:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
YawLeft:        FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
YawRight:       FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RollLeft:       FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RollRight:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
LaserKey:       FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
SpeedUp:        FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
SpeedDown:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ComputerKey:    FSettingWord {
                    #DF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
MissileAim:     FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ClearTargets:   FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile1:       FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile2:       FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile3:       FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
BoostKey:       FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
FreeFlightKey:  FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
GuidanceKey:    FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ReturnKey:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
TractorKey:     FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
AntimissileKey: FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
CargoEject:     FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
MineEject:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
HyperJumpKey:   FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
NeonKey:        FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ViewToggle:     FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RadiationKey:   FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown28:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown29:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown30:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown31:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown32:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown33:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown34:      FSettingWord {
                    #DF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown35:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown36:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown37:      FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown38:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown39:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown40:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown41:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ResourceSelect: FScriptResourceSelection {
                    #00,                                                        ; FScriptResourceSelection.GroupCount, значение дискового слота
                    #00                                                         ; FScriptResourceSelection.RecordCount, значение дискового слота
                }
                assert $ == #01E3
                endmodule
