                module ExtraDeferredC
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DE0E
EnvelopeSlide:  FMusicEffectTarget { @Music.ReadEnvelopeSlide.Entry }           ; Handler, команда 08, исходное слово DB8C
Tempo:          FMusicEffectTarget { @Music.SetRowTempo.Entry }                 ; Handler, команда 09, исходное слово E6FA
                assert $ == #DE12
                endmodule
