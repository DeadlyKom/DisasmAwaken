; -----------------------------------------
; запись 6, D3D.C
; логическая длина 15978, полный секторный размер 16128
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/06_D3D/BeforePreviewClip.bin"
                assert $ == #2011
                disp #E011
                include "../D3D/ConfigurePreviewClip.asm"
                ent
                assert $ == #207F
                incbin "../Resources/06_D3D/BeforePreviewThird.bin"
                assert $ == #20B5
                disp #E0B5
                include "../D3D/AdjustPreviewThird.asm"
                ent
                assert $ == #20C5
                incbin "../Resources/06_D3D/BeforePreviewSetup.bin"
                assert $ == #213C
                disp #E13C
                include "../D3D/SetupPreviewModel.asm"
                ent
                assert $ == #2154
                incbin "../Resources/06_D3D/AfterPreviewSetup.bin"
                assert $ == #3F00
