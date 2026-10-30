                module PointerDirections
; Документация [опрос ввода](../../../Docs/PointerInputs.md)
; индекс из младших четырёх битов текущей выборки, порядок 0..15
                assert $ == #66EE
None:           FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #0
Right:          FPointerDirection { @Station.StepRight.Entry }                  ; Handler для маски #1
Left:           FPointerDirection { @Station.StepLeft.Entry }                   ; Handler для маски #2
BothX:          FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #3
Down:           FPointerDirection { @Station.StepDown.Entry }                   ; Handler для маски #4
DownRight:      FPointerDirection { @Station.StepDownRight.Entry }              ; Handler для маски #5
DownLeft:       FPointerDirection { @Station.StepDownLeft.Entry }               ; Handler для маски #6
DownBothX:      FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #7
Up:             FPointerDirection { @Station.StepUp.Entry }                     ; Handler для маски #8
UpRight:        FPointerDirection { @Station.StepUpRight.Entry }                ; Handler для маски #9
UpLeft:         FPointerDirection { @Station.StepUpLeft.Entry }                 ; Handler для маски #A
UpBothX:        FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #B
BothY:          FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #C
RightBothY:     FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #D
LeftBothY:      FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #E
BothXY:         FPointerDirection { @Station.NoPointerMotion.Entry }            ; Handler для маски #F
                assert $ == #670E
                endmodule
