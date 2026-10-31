; -----------------------------------------
; запись 6, D3D.C
; логическая длина 15978, полный секторный размер 16128
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/06_D3D/BeforePriceText.bin"
                assert $ == #0E40
                disp #CE40
                include "../D3D/Data/PreviewPrices.asm"
                ent
                assert $ == #0EFA
                incbin "../Resources/06_D3D/AfterPriceText.bin"
                assert $ == #2011
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
                disp #E0C5
                include "../D3D/DrawPreviewPrices.asm"
                ent
                assert $ == #2124
                assert $ == #2124
                disp #E124
                include "../D3D/CountPreviewTextRows.asm"
                ent
                assert $ == #213C
                assert $ == #213C
                disp #E13C
                include "../D3D/SetupPreviewModel.asm"
                ent
                assert $ == #2154
                disp #E154
                include "../D3D/PrintPreviewTextRows.asm"
                ent
                assert $ == #2171
                incbin "../Resources/06_D3D/BeforeDescriptionText.bin"
                assert $ == #3581
                disp #F581
                include "../D3D/Data/ShipDescriptions.asm"
                ent
                assert $ == #3BD8
                disp #FBD8
                include "../D3D/Data/SkimmerDescriptions.asm"
                ent
                assert $ == #3E6A
                incbin "../Resources/06_D3D/AfterDescriptionText.bin"
                assert $ == #3F00
                assert $ == #3F00
