                module Save5ControlOptions
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #018D
MouseOption:    FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
PitchUp:        FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
PitchDown:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
YawLeft:        FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
YawRight:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RollLeft:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RollRight:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
LaserKey:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
SpeedUp:        FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
SpeedDown:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ComputerKey:    FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
MissileAim:     FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ClearTargets:   FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile1:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile2:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Missile3:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
BoostKey:       FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
FreeFlightKey:  FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
GuidanceKey:    FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ReturnKey:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
TractorKey:     FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
AntimissileKey: FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
CargoEject:     FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
MineEject:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
HyperJumpKey:   FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
NeonKey:        FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ViewToggle:     FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
RadiationKey:   FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown28:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown29:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown30:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown31:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown32:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown33:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown34:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown35:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown36:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown37:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown38:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown39:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown40:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown41:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
ResourceSelect: FScriptResourceSelection {
                    #00,                                                        ; FScriptResourceSelection.GroupCount, значение дискового слота
                    #00                                                         ; FScriptResourceSelection.RecordCount, значение дискового слота
                }
                assert $ == #01E3
                endmodule
