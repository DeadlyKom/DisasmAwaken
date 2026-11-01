                module DeferredA
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DDC0
Slide:          FMusicEffectTarget { @Music.SetToneSlideA.Entry }               ; Handler, команда 01, исходное слово E60C
Portamento:     FMusicEffectTarget { @Music.SetTonePortamentoA.Entry }          ; Handler, команда 02, исходное слово E623
SamplePos:      FMusicEffectTarget { @Music.SetSamplePositionA.Entry }          ; Handler, команда 03, исходное слово E647
OrnamentPos:    FMusicEffectTarget { @Music.SetOrnamentPositionA.Entry }        ; Handler, команда 04, исходное слово E652
Gate:           FMusicEffectTarget { @Music.ReadGateTimingA.Entry }             ; Handler, команда 05, исходное слово DDCA
                assert $ == #DDCA
                endmodule
