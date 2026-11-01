                module ExtraDeferredB
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DDEE
EnvelopeSlide:  FMusicEffectTarget { @Music.ReadEnvelopeSlide.Entry }           ; Handler, команда 08, исходное слово DB8C
Tempo:          FMusicEffectTarget { @Music.SetRowTempo.Entry }                 ; Handler, команда 09, исходное слово E6FA
                assert $ == #DDF2
                endmodule
