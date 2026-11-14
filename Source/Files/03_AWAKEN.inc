; -----------------------------------------
; запись 3, AWAKEN.B
; логическая длина 119, полный секторный размер 11520
; -----------------------------------------
                assert $ == #0000
                disp #5D3B
                include "../Basic/Data/Prefix.asm"
                ent
                assert $ == #0006
                disp #5D41
                include "../Basic/ReadIntroSectors.asm"
                ent
                assert $ == #001E
                disp #5D59
                include "../Basic/Data/Line10Tail.asm"
                ent
                assert $ == #0065
                disp #5DA0
                include "../Basic/Data/EntryLine.asm"
                ent
                assert $ == #0077
                ; После 119 байтов программы ROM переносит четыре байта автозапуска и ещё один байт сектора.
                ; Документация [чтение первого сектора](../../Docs/BasicProgram.md#чтение-первого-сектора-командой-run)
                include "../Basic/Data/Autostart.asm"
                assert $ == #007B
                include "../Basic/Data/DetachedLineSuffix.asm"
                assert $ == #0084
                include "../Basic/Data/DetachedSectorNumber.asm"
                assert $ == #0090
                ; Физический хвост буфера, при RUN исходные байты вытесняются до входа USR
                ; Документация [чтение первого сектора](../../Docs/BasicProgram.md#чтение-первого-сектора-командой-run)
                incbin "../Resources/03_AWAKEN/FirstSectorBufferTail.bin"
                assert $ == #0100
                ; Эта страница читается вместе со вступлением по адресу 6400 отдельным дисковым вызовом.
                disp #6400
                include "../Intro/Data/CoordinateSeed.asm"
                ent
                assert $ == #0200
                disp #6500
                include "../Intro/InitializeIntro.asm"
                ent
                assert $ == #02B3
                ; Документация [снимок стека и выборка](../../Docs/IntroStationTransition.md#снимок-стека-в-выборке-текстуры)
                disp #65B3
                include "../Intro/Data/StackSampleBefore.asm"
                ent
                assert $ == #02B4
                disp #65B4
                include "../Intro/Data/StackSnapshot.asm"
                ent
                assert $ == #02B6
                disp #65B6
                include "../Intro/Data/StackSampleAfter.asm"
                ent
                assert $ == #02B7
                disp #65B7
                include "../Intro/LoadStation.asm"
                ent
                assert $ == #0315
                disp #6615
                include "../Intro/Data/StationFileKey.asm"
                ent
                assert $ == #031E
                disp #661E
                include "../Intro/DrawFinalTextureFrame.asm"
                ent
                assert $ == #032C
                disp #662C
                include "../Intro/Data/FinalTexturePhases.asm"
                ent
                assert $ == #0338
                disp #6638
                include "../Intro/BuildAlternatingTexture.asm"
                ent
                assert $ == #0363
                disp #6663
                include "../Intro/Data/AlternatingLookup.asm"
                ent
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
                disp #6993
                include "../Intro/Data/AttributeNibbleSeeds.asm"
                ent
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
                disp #6B73
                include "../Intro/Data/ColumnTailSamples.asm"
                ent
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
                disp #6C62
                include "../Intro/Data/ScaleCycle.asm"
                ent
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
                ; Начальный экран до переноса распаковщика, 6144 bitmap и 768 атрибутов.
                incbin "../Intro/Data/InitialScreenBitmap.bin"
                assert $ == #2331
                disp #8631
                include "../Intro/Data/InitialScreenAttributes.asm"
                ent
                assert $ == #2631
                disp #6E31
                include "../IntroUnpack/UnpackScreen.asm"
                ent
                assert $ == #26CB
                ; Поток после кода распаковщика, он переносится по адресу 6ECB.
                incbin "../Intro/Data/StationScreenPacked.bin"
                assert $ == #2C6B
                ; Следующие 149 байтов не читаются установленным экранным потоком.
                ; Unknown, назначение 41 байта перед подготовкой обхода не установлено, исходный #8F93 обнуляется после переноса.
                incbin "../Resources/03_AWAKEN/Unclassified2C6B_2C94.bin"
                assert $ == #2C94
                disp #7494
                include "../IntroUnpack/SetAttributeScanDest.asm"                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2C97
                disp #7497
                include "../IntroUnpack/ScanAttributeCountTail.asm"             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2CCD
                disp #74CD
                include "../IntroUnpack/WaitNonzeroKeyByte.asm"
                ent
                assert $ == #2CD8
                disp #74D8
                include "../IntroUnpack/CopyScreenToBankWindow.asm"
                ent
                assert $ == #2CE4
                disp #74E4
                include "../IntroUnpack/CopyScreenFromBankWindow.asm"
                ent
                assert $ == #2CEC
                disp #74EC
                include "../IntroUnpack/UnpackTailGate.asm"
                ent
                assert $ == #2CFF
                ; Опкод JR Z, смещение по #7500 приходит из RAM за концом секторов.
                incbin "../Resources/03_AWAKEN/DetachedJumpOpcode.bin"
                assert $ == #2D00
