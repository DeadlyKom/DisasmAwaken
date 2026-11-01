                module DeferredB
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DDE0
Slide:          FMusicEffectTarget { @Music.SetToneSlideB.Entry }               ; Handler, команда 01, исходное слово E65D
Portamento:     FMusicEffectTarget { @Music.SetTonePortamentoB.Entry }          ; Handler, команда 02, исходное слово E674
SamplePos:      FMusicEffectTarget { @Music.SetSamplePositionB.Entry }          ; Handler, команда 03, исходное слово E698
OrnamentPos:    FMusicEffectTarget { @Music.SetOrnamentPositionB.Entry }        ; Handler, команда 04, исходное слово E6A3
Gate:           FMusicEffectTarget { @Music.ReadGateTimingB.Entry }             ; Handler, команда 05, исходное слово DDEA
                assert $ == #DDEA
                endmodule
