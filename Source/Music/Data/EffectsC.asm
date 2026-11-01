                module DeferredC
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DE00
Slide:          FMusicEffectTarget { @Music.SetToneSlideC.Entry }               ; Handler, команда 01, исходное слово E6AE
Portamento:     FMusicEffectTarget { @Music.SetTonePortamentoC.Entry }          ; Handler, команда 02, исходное слово E6C9
SamplePos:      FMusicEffectTarget { @Music.SetSamplePositionC.Entry }          ; Handler, команда 03, исходное слово E6EE
OrnamentPos:    FMusicEffectTarget { @Music.SetOrnamentPositionC.Entry }        ; Handler, команда 04, исходное слово E6F4
Gate:           FMusicEffectTarget { @Music.ReadGateTimingC.Entry }             ; Handler, команда 05, исходное слово DE0A
                assert $ == #DE0A
                endmodule
