                module ExtraDeferredA
                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)
                assert $ == #DDCE
EnvelopeSlide:  FMusicEffectTarget { @Music.ReadEnvelopeSlide.Entry }           ; Handler, команда 08, исходное слово DB8C
Tempo:          FMusicEffectTarget { @Music.SetRowTempo.Entry }                 ; Handler, команда 09, исходное слово E6FA
                assert $ == #DDD2
                endmodule
