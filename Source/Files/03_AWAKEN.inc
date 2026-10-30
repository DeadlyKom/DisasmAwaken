; -----------------------------------------
; запись 3, AWAKEN.B
; логическая длина 119, полный секторный размер 11520
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified000.bin"
                assert $ == #0006
                disp #5CD1
                include "../Basic/ReadIntroSectors.asm"
                ent
                assert $ == #001E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified001.bin"
                assert $ == #0200
                disp #6500
                include "../Intro/InitializeIntro.asm"
                ent
                assert $ == #02B3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified002.bin"
                assert $ == #02B7
                disp #65B7
                include "../Intro/LoadStation.asm"
                ent
                assert $ == #0315
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified003.bin"
                assert $ == #031E
                disp #661E
                include "../Intro/DrawFinalTextureFrame.asm"
                ent
                assert $ == #032C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified004.bin"
                assert $ == #0338
                disp #6638
                include "../Intro/BuildAlternatingTexture.asm"
                ent
                assert $ == #0363
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified005.bin"
                assert $ == #03A3
                disp #66A3
                include "../Intro/DrawScrolledTexture.asm"
                ent
                assert $ == #03E2
                disp #66E2
                include "../Intro/SampleTextureRows.asm"
                ent
                assert $ == #03F3
                disp #66F3
                include "../Intro/NextSampledRow.asm"
                ent
                assert $ == #03FB
                disp #66FB
                include "../Intro/InitializeScrolledTexture.asm"
                ent
                assert $ == #0422
                disp #6722
                include "../IntroTemplates/ScrolledSample.asm"
                ent
                assert $ == #0429
                disp #6729
                include "../Intro/ExpandTextureRows.asm"
                ent
                assert $ == #0457
                disp #6757
                include "../Intro/CopyTextureToBank.asm"
                ent
                assert $ == #0463
                disp #6763
                include "../Intro/BuildTextureLookup.asm"
                ent
                assert $ == #04F1
                disp #67F1
                include "../Intro/PresentInterlacedFrame.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0527
                disp #6827
                include "../Intro/ScatterTextureToScreen.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05A4
                disp #68A4
                include "../Intro/RunAttributeWriter.asm"
                ent
                assert $ == #062D
                disp #692D
                include "../Intro/BuildAttributeWriter.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0664
                disp #6964
                include "../Intro/CombineAttributeNibbles.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0683
                disp #6983
                include "../Intro/PresentAttributes.asm"
                ent
                assert $ == #0693
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified006.bin"
                assert $ == #06A3
                disp #69A3
                include "../Intro/BuildPairedPointers.asm"
                ent
                assert $ == #06B6
                disp #69B6
                include "../Intro/BuildScreenTables.asm"
                ent
                assert $ == #06FE
                disp #69FE
                include "../Intro/WriteJump.asm"
                ent
                assert $ == #0705
                disp #6A05
                include "../Intro/WriteIndexJump.asm"
                ent
                assert $ == #070B
                disp #6A0B
                include "../Intro/SelectIntroPage.asm"                          ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #070D
                disp #6A0D
                include "../Intro/SelectMemoryPage.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0713
                disp #6A13
                include "../Intro/WaitInterrupt.asm"
                ent
                assert $ == #0717
                disp #6A17
                include "../Intro/FillForward.asm"
                ent
                assert $ == #071E
                disp #6A1E
                include "../Intro/RepeatPattern.asm"
                ent
                assert $ == #072C
                disp #6A2C
                include "../Intro/AdvanceParameters.asm"
                ent
                assert $ == #074B
                disp #6A4B
                include "../Intro/RunTimedEffect.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0767
                disp #6A67
                include "../Intro/FillBitmap.asm"                               ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07C1
                disp #6AC1
                include "../Intro/InitializeColumnEffect.asm"
                ent
                assert $ == #085A
                disp #6B5A
                include "../IntroTemplates/ColumnSample.asm"
                ent
                assert $ == #0873
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified007.bin"
                assert $ == #0893
                disp #6B93
                include "../Intro/DrawLookupTextureFrame.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #089C
                disp #6B9C
                include "../Intro/RenderLookupTexture.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #08BC
                disp #6BBC
                include "../Intro/PresentLookupTexture.asm"
                ent
                assert $ == #08E3
                disp #6BE3
                include "../Intro/RunTextureSampler.asm"
                ent
                assert $ == #08ED
                disp #6BED
                include "../Intro/NextTextureSampleRow.asm"
                ent
                assert $ == #08F6
                disp #6BF6
                include "../Intro/AdvanceTexturePhases.asm"
                ent
                assert $ == #0921
                disp #6C21
                include "../Intro/AdvanceTextureScale.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0953
                disp #6C53
                include "../Intro/SelectTexturePointerRow.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0962
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified008.bin"
                assert $ == #098A
                disp #6C8A
                include "../Intro/Data/TexturePhases.asm"
                ent
                assert $ == #099C
                disp #6C9C
                include "../Intro/InitializeLookupEffect.asm"
                ent
                assert $ == #0A6A
                disp #6D6A
                include "../Intro/BuildPhaseTable.asm"
                ent
                assert $ == #0A78
                disp #6D78
                include "../IntroTemplates/PointerSample.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A7E
                disp #6D7E
                include "../IntroTemplates/PhaseSum.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A8D
                disp #6D8D
                include "../Intro/BuildIntroTexture.asm"
                ent
                assert $ == #0AB6
                disp #6DB6
                include "../Intro/BuildMirroredTexture.asm"
                ent
                assert $ == #0B31
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified009.bin"
                assert $ == #2631
                disp #6E31
                include "../IntroUnpack/UnpackScreen.asm"
                ent
                assert $ == #26CB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/03_AWAKEN/Unclassified010.bin"
                assert $ == #2D00
