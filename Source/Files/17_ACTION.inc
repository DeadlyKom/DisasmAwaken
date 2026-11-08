; -----------------------------------------
; запись 17, ACTION.C
; логическая длина 40960, полный секторный размер 40960
; -----------------------------------------
                assert $ == #0000
                disp #6000
                include "../ActionBoot/RelocateBootstrap.asm"
                ent
                assert $ == #0043
                disp #4200
                include "../ActionBoot/InitializeFlight.asm"
                ent
                assert $ == #00EE
                disp #42AB
                include "../ActionBoot/GetFileLocation.asm"
                ent
                assert $ == #0109
                disp #42C6
                include "../ActionBoot/LoadFileToBank.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #010C
                disp #42C9
                include "../ActionBoot/LoadFileAtAddress.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0113
                disp #42D0
                include "../ActionBoot/Data/FileKeys.asm"
                ent
                assert $ == #0149
                disp #4306
                include "../ActionBoot/InitializeRandomStates.asm"
                ent
                assert $ == #0198
                disp #4355
                include "../ActionBoot/BuildExponentialTable.asm"
                ent
                assert $ == #01D2
                disp #438F
                include "../ActionBoot/BuildLogarithmTable.asm"
                ent
                assert $ == #0212
                disp #43CF
                include "../ActionBoot/BuildBitmapTables.asm"
                ent
                assert $ == #023D
                disp #6000
                include "../Action/QueueNumberBank1.asm"
                ent
                assert $ == #024D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #024D
                disp #6010
                include "../Action/PrintByteAndScrollBank1.asm"
                ent
                assert $ == #0266
                assert $ == #0266
                disp #6029
                include "../Action/PrintByteBank1.asm"
                ent
                assert $ == #027D
                disp #6040
                include "../Action/QueueTextItemBank1.asm"
                ent
                assert $ == #0291
                disp #6054
                include "../Action/ShowNoiseBeforeReload.asm"
                ent
                assert $ == #02EB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #60AE
                include "../Action/CreateMissileForTarget.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0325
                disp #60E8
                include "../Action/CreateClass17LinkedRecord.asm"               ; (1) жёсткий порядок, общий вход создания
                ent
                assert $ == #0382
                disp #6145
                include "../Action/RefreshFlightPanel.asm"
                ent
                assert $ == #03AF
                disp #6172
                include "../Action/ReleaseClass14Records.asm"
                ent
                assert $ == #03BA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #03BA
                assert $ == #03BA
                assert $ == #03BA
                disp #617D
                include "../Action/CreateRandomClass20Record.asm"
                ent
                assert $ == #043E
                disp #6201
                include "../Action/StepRandomizedThirdPhase.asm"
                ent
                assert $ == #0488
                disp #624B
                include "../Action/CheckLinkedDistanceAndStepCodes.asm"         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04A2
                disp #6265
                include "../Action/StepRecordTargetCodes.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04F2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #04F2
                disp #62B5
                include "../Action/EnterTimedPhaseFromMotion.asm"
                ent
                assert $ == #050C
                disp #62CF
                include "../Action/CountClass3LinksUpToTwo.asm"
                ent
                assert $ == #054E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #054E
                disp #6311
                include "../Action/ApproachWordAndAccumulate.asm"
                ent
                assert $ == #0588
                disp #634B
                include "../Action/Data/TypeDeltas.asm"
                ent
                assert $ == #0598
                assert $ == #0598
                disp #635B
                include "../Action/ApplyPendingRecordLink.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                include "../Action/ApplyIndexedDelta.asm"                       ; (1) жёсткий порядок, продолжение после условного RET Z
                ent
                assert $ == #05F3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #05F3
                assert $ == #05F3
                disp #63B6
                include "../Action/RequestPairedAimLines.asm"
                ent
                assert $ == #0654
                disp #6417
                include "../Action/SpawnClass19AndUpdateList.asm"
                ent
                assert $ == #071C
                disp #64DF
                include "../Action/DispatchRecordClass.asm"
                ent
                assert $ == #072D
                disp #64F0
                include "../Action/Data/ClassHandlers.asm"
                ent
                assert $ == #0761
                ; Unknown, код после 26 указателей классов
                assert $ == #0761
                assert $ == #0761
                assert $ == #0761
                disp #6524
                include "../Action/ReturnIgnoredRecordClass.asm"
                ent
                assert $ == #0762
                assert $ == #0762
                assert $ == #0762
                disp #6525
                include "../Action/ConfigureClass5Link.asm"
                ent
                assert $ == #0773
                assert $ == #0773
                disp #6536
                include "../Action/ConfigureClass8Link.asm"
                ent
                assert $ == #0786
                disp #6549
                include "../Action/ConfigureClass2Link.asm"
                ent
                assert $ == #07A3
                assert $ == #07A3
                disp #6566
                include "../Action/ConfigureClass7Link.asm"
                ent
                assert $ == #07BC
                assert $ == #07BC
                disp #657F
                include "../Action/ConfigureClass6Link.asm"
                ent
                assert $ == #07D1
                assert $ == #07D1
                disp #6594
                include "../Action/ConfigureClass1Link.asm"
                ent
                assert $ == #07EA
                assert $ == #07EA
                disp #65AD
                include "../Action/ConfigureClass4Link.asm"
                ent
                assert $ == #0803
                disp #65C6
                include "../Action/ConfigureClass9Link.asm"
                ent
                assert $ == #081B
                assert $ == #081B
                assert $ == #081B
                disp #65DE
                include "../Action/ConfigureClass3Link.asm"
                ent
                assert $ == #084B
                disp #660E
                include "../Action/ConfigureClass0Link.asm"
                ent
                assert $ == #0868
                disp #662B
                include "../Action/CopyRecordLinkOverride.asm"
                ent
                assert $ == #0876
                disp #6639
                include "../Action/DrawBankedGauge.asm"
                ent
                assert $ == #0886
                disp #6649
                include "../Action/UpdatePanelGauges.asm"
                ent
                assert $ == #090F
                disp #66D2
                include "../Action/SubtractScaledWorkVector.asm"
                ent
                assert $ == #0964
                disp #6727
                include "../Action/TransitionBodyMode.asm"
                ent
                assert $ == #09BD
                disp #6780
                include "../Action/UpdateBodyMotion.asm"
                ent
                assert $ == #0BBA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #0BBA
                ; Unknown, соседние байты вне доказанного входа BuildBankedParameterSet
                incbin "../Resources/17_ACTION/Unclassified0BBA_0BBB.bin"
                assert $ == #0BBB
                disp #697E
                include "../Action/BuildBankedParameterSet.asm"
                ent
                assert $ == #0BC3
                disp #6986
                include "../Action/CompareContextWordPairs.asm"
                ent
                assert $ == #0BD9
                disp #699C
                include "../Action/MaxFoldedVectorHigh.asm"
                ent
                assert $ == #0BFB
                disp #69BE
                include "../Action/FindFirstNearWideVector.asm"
                ent
                assert $ == #0C66
                disp #6A29
                include "../Action/CheckThreeUpperWordsNear.asm"
                ent
                assert $ == #0CAB
                disp #6A6E
                include "../Action/PrepareBodyTransform.asm"
                ent
                assert $ == #0CEA
                disp #6AAD
                include "../Action/RestoreBodyStack.asm"                        ; (0) жёсткий порядок, восстановление SP перед проверкой P/V
                ent
                assert $ == #0CED
                disp #6AB0
                include "../Action/PublishTransformedBody.asm"                  ; (1) жёсткий порядок, продолжение после восстановления SP
                ent
                assert $ == #0D53
                disp #6B16
                include "../Action/ProjectWideVectors.asm"
                ent
                assert $ == #0E3C
                disp #6BFF
                include "../Action/CopyAndTransformComponents.asm"              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E56
                disp #6C19
                include "../Action/TransformWorkComponents.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E7D
                disp #6C40
                include "../Action/RestoreComponentStack.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E80
                disp #6C43
                include "../Action/EncodeSignedComponents.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0EBB
                disp #6C7E
                include "../Action/DrawBankedProjectedBody.asm"
                ent
                assert $ == #0ECC
                disp #6C8F
                include "../Action/UpdateThirdGlyphVector.asm"
                ent
                assert $ == #0EEE
                disp #6CB1
                include "../Action/RestoreThirdGlyphStack.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0EF1
                disp #6CB4
                include "../Action/PublishThirdGlyphVector.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0F13
                disp #6CD6
                include "../Action/InitializeBankedBufferPoints.asm"
                ent
                assert $ == #0F21
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6CE4
                include "../Action/TransferToStationLoader.asm"
                ent
                assert $ == #0F2C
                disp #6CEF
                include "../Action/DispatchBank3Callback.asm"
                ent
                assert $ == #0F3D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #0F3D
                disp #6D00
                include "../Action/RestoreRuntimePage.asm"
                ent
                assert $ == #0F43
                assert $ == #0F43
                disp #6D06
                include "../Action/ApplyObjectOffsetVector.asm"
                ent
                assert $ == #0F75
                disp #6D38
                include "../Action/UpdateVisualEffects.asm"
                ent
                assert $ == #100E
                disp #6DD1
                include "../Action/ResumeVisualEffect.asm"
                ent
                assert $ == #1068
                disp #6E2B
                include "../Action/ClassifyCoordinateRegion.asm"
                ent
                assert $ == #10A9
                disp #6E6C
                include "../Action/UpdateMotionFromControls.asm"
                ent
                assert $ == #10E9
                disp #6EAC
                include "../Action/StepNearZeroWord.asm"
                ent
                assert $ == #111B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6EDE
                include "../Action/ReverseScaledVector.asm"
                ent
                assert $ == #115A
                disp #6F1D
                include "../Action/ScanActionKeys.asm"
                ent
                assert $ == #118B
                ; Подтверждённый хвост восстановления рамки клавиатуры
                disp #6F4E
                include "../Action/RestoreKeyScanFrame.asm"
                ent
                assert $ == #1192
                disp #6F55
                include "../Action/LatchControlsAndDecay.asm"
                ent
                assert $ == #1254
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7017
                include "../Action/Data/KeyHandlerPointers.asm"
                ent
                assert $ == #1288
                disp #704B
                include "../Action/IgnoreKey.asm"
                ent
                assert $ == #1289
                ; Unknown, остальные обработчики ещё не разобраны
                disp #704C
                include "../Action/RequestMissile0.asm"                         ; (0) жёсткий порядок продолжения RequestMissile0
                include "../Action/CompleteMissileLaunch.asm"                   ; (1) жёсткий порядок продолжения RequestMissile0
                include "../Action/RequestMissile1.asm"
                include "../Action/RequestMissile2.asm"
                ent
                assert $ == #12D8
                disp #709B
                include "../Action/ReportMissingMissileTarget.asm"
                ent
                assert $ == #12E1
                disp #70A4
                include "../Action/CheckMissileLaunch.asm"
                ent
                assert $ == #1303
                disp #70C6
                include "../Action/ConsumeMissileStock.asm"
                ent
                assert $ == #132A
                assert $ == #132A
                disp #70ED
                include "../Action/SelectMissileStock.asm"
                ent
                assert $ == #1333
                ; Unknown, остальные обработчики ещё не разобраны
                incbin "../Resources/17_ACTION/Unclassified017_AfterMissileStock.bin"
                assert $ == #1738
                disp #74FB
                include "../Action/SelectPreferredByte.asm"
                ent
                assert $ == #1741
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #1741
                assert $ == #1741
                ; Unknown, соседние байты вне доказанного входа IncreaseGaugeWord
                incbin "../Resources/17_ACTION/Unclassified018_BeforeGaugeKeys.bin"
                assert $ == #18BD
                disp #7680
                include "../Action/IncreaseGaugeWord.asm"
                ent
                assert $ == #18E0
                assert $ == #18E0
                disp #76A3
                include "../Action/DecreaseGaugeWord.asm"
                ent
                assert $ == #1904
                disp #76C7
                include "../Action/RequestTurnNegative.asm"
                ent
                assert $ == #1927
                assert $ == #1927
                disp #76EA
                include "../Action/RequestTurnPositive.asm"
                ent
                assert $ == #194A
                assert $ == #194A
                disp #770D
                include "../Action/RequestXNegative.asm"
                ent
                assert $ == #196D
                assert $ == #196D
                disp #7730
                include "../Action/RequestXPositive.asm"
                ent
                assert $ == #1990
                assert $ == #1990
                disp #7753
                include "../Action/RequestYNegative.asm"
                ent
                assert $ == #19B3
                assert $ == #19B3
                disp #7776
                include "../Action/RequestYPositive.asm"
                ent
                assert $ == #19D6
                ; Unknown, соседние байты вне доказанного входа RequestYPositive
                disp #7799
                include "../Action/Data/SpawnTemplates.asm"
                ent
                assert $ == #1A96
                disp #7859
                include "../Action/SpawnAlternate.asm"
                ent
                assert $ == #1D03
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7AC6
                include "../Action/Data/SpawnModelChoices.asm"
                ent
                assert $ == #1D85
                ; Соседние 16 байтов не имеют подтверждённого потребителя.
                incbin "../Resources/17_ACTION/UnknownAfterSpawnModelChoices.bin"
                assert $ == #1D95
                disp #7B58
                include "../Action/ScheduleSpawn.asm"                           ; (0) жёсткий порядок продолжения
                ent
                assert $ == #2011
                disp #7DD4
                include "../Action/FinishSpawnRecord.asm"                       ; (1) жёсткий порядок продолжения
                ent
                assert $ == #20DA
                disp #7E9D
                include "../Action/SelectWideTargetAndStep.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #20F4
                disp #7EB7
                include "../Action/StepRecordTowardWideVector.asm"              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #214B
                disp #7F0E
                include "../Action/ClampPatchedVectorWords.asm"
                ent
                assert $ == #21B3
                disp #7F76
                include "../Action/AbsSigned32.asm"
                ent
                assert $ == #21CC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #21CC
                ; начальное содержимое 81CC..8BFF, хвост строки 14 с байта 12 и строки 15..95 линейного буфера
                incbin "../Action/Resources/InitialLinearBufferTail.bin"
                assert $ == #2C00
                ; Unknown, промежуток 8C00..90FF не классифицирован этим разбором
                incbin "../Resources/17_ACTION/Unclassified2C00_3100.bin"
                assert $ == #3100
                ; исходные байты страницы 9100, BuildLogarithmTable заменяет их младшими байтами результатов
                incbin "../Action/Resources/InitialLogarithmLow.bin"
                assert $ == #3200
                ; исходные байты страницы 9200, BuildLogarithmTable заменяет их старшими байтами результатов
                incbin "../Action/Resources/InitialLogarithmHigh.bin"
                assert $ == #3300
                ; исходные байты страницы 9300, BuildExponentialTable создаёт значения во время загрузки
                incbin "../Action/Resources/InitialExponential.bin"
                assert $ == #3400
                ; исходные байты страницы 9400, затем HIGH(8000+32*Y) для Y от 0 до 255
                incbin "../Action/Resources/InitialRowHigh.bin"
                assert $ == #3500
                ; исходные байты страницы 9500, затем LOW(32*Y) для Y от 0 до 255
                incbin "../Action/Resources/InitialRowLow.bin"
                assert $ == #3600
                ; исходные байты страницы 9600, затем X DIV 8 для X от 0 до 255
                incbin "../Action/Resources/InitialColumnByte.bin"
                assert $ == #3700
                ; исходные байты страницы 9700, затем 80 >> (X AND 7) для X от 0 до 255
                incbin "../Action/Resources/InitialColumnMask.bin"
                assert $ == #3800
                disp #9800
                include "../Action/Data/ProjectionSquares.asm"
                ent
                assert $ == #3900
                disp #9900
                include "../Action/Data/SineTable.asm"
                ent
                assert $ == #3A00
                ; Unknown, исходные байты после синусоиды ACTION
                disp #9A00
                include "../Action/Data/SignedRatioCodes.asm"
                ent
                assert $ == #3B00
                ; Unknown, следующие 18 байтов вне таблицы кодов отношения
                disp #9B00
                include "../Action/Data/RenderBasis.asm"
                ent
                assert $ == #3B12
                disp #9B12
                include "../Action/Data/RenderPhases.asm"
                ent
                assert $ == #3B15
                disp #9B15
                include "../Action/Data/WordRandomState.asm"
                ent
                assert $ == #3B19
                ; Unknown, исходные байты после состояния генератора
                disp #9B19
                include "../Action/Data/AimPoint.asm"
                ent
                assert $ == #3B1B
                disp #9B1B
                include "../Action/Data/MissileTargets.asm"
                ent
                assert $ == #3B1E
                ; Unknown, соседние данные ещё не разобраны
                disp #9B1E
                include "../Action/Data/ComponentWork.asm"
                ent
                assert $ == #3B27
                disp #9B27
                include "../Action/Data/WideVectors.asm"
                ent
                assert $ == #3B6F
                disp #9B6F
                include "../Action/Data/TransformWorkVector24.asm"
                ent
                assert $ == #3B78
                disp #9B78
                include "../Action/Data/WorkVector24.asm"
                ent
                assert $ == #3B81
                disp #9B81
                include "../Action/Data/GlyphIndicatorState.asm"
                ent
                assert $ == #3B8D
                ; Unknown, исходная область после входов знаков
                incbin "../Resources/17_ACTION/Unclassified020_BeforePreferredByte.bin"
                assert $ == #3C10
                disp #9C10
                include "../Action/Data/PreferredByteState.asm"
                ent
                assert $ == #3C12
                ; Unknown, соседний ресурс ещё не разобран
                disp #9C12
                include "../Action/Data/MissileStock.asm"
                ent
                assert $ == #3C14
                ; Unknown, соседние данные ещё не разобраны
                assert $ == #3C14
                disp #9C14
                include "../Action/Data/ShipEquipment.asm"
                ent
                assert $ == #3C32
                disp #9C32
                include "../Action/Data/SkimmerEquipment.asm"
                ent
                assert $ == #3C41
                ; Unknown, соседние байты вне подтверждённой раскладки оборудования
                incbin "../Resources/17_ACTION/Unclassified3C41_3D4C.bin"
                assert $ == #3D4C
                disp #9D4C
                include "../Action/Data/KeyScanInputs.asm"
                ent
                assert $ == #3D82
                ; Unknown, соседние данные ещё не разобраны
                assert $ == #3D82
                ; Unknown, соседние байты вне доказанной таблицы OBJECT3D
                incbin "../Resources/17_ACTION/Unclassified020_BeforeObjectPointers.bin"
                assert $ == #3E00
                disp #9E00
                include "../Action/Data/ObjectPointers.asm"
                ent
                assert $ == #3F00
                ; Unknown, соседние байты вне доказанной таблицы OBJECT3D
                assert $ == #3F00
                ; Unknown, соседние байты не классифицированы типизацией списка кандидатов
                assert $ == #3F00
                ; Unknown, соседние байты вне доказанного назначения CopyObjectData
                incbin "../Resources/17_ACTION/Unclassified3F00_3F1C.bin"
                assert $ == #3F1C
                ; Документация [исходное содержимое буфера объекта](../../Docs/ActionObjectStreamStorage.md)
                ; исходные 238 байтов назначения CopyObjectData, подтверждённых всеми исходными чётными указателями
                incbin "../Action/Resources/InitialObjectStreamBuffer.bin"
                assert $ == #400A
                ; Unknown, соседние байты вне доказанного назначения CopyObjectData
                incbin "../Resources/17_ACTION/Unclassified400A_401C.bin"
                assert $ == #401C
                disp #A01C
                include "../Action/Data/CandidateList.asm"
                ent
                assert $ == #4027
                ; Unknown, соседние байты не классифицированы типизацией списка кандидатов
                incbin "../Resources/17_ACTION/Unclassified4027_4100.bin"
                assert $ == #4100
                disp #A100
                include "../Action/Data/ObjectRecords.asm"
                ent
                assert $ == #4780
                ; Unknown, соседнее состояние A780..A794 ещё не разобрано
                incbin "../Resources/17_ACTION/Unclassified020_BeforeVisualEffects.bin"
                assert $ == #4795
                disp #A795
                include "../Action/Data/VisualEffects.asm"
                ent
                assert $ == #482D
                disp #A82D
                include "../Action/StartFlight.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #4859
                disp #A859
                include "../Action/MainLoop.asm"                                ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #485E
                disp #A85E
                include "../Action/UpdateFrame.asm"
                ent
                assert $ == #4ACC
                disp #AACC
                include "../Action/ReadObjectHeaderWord.asm"
                ent
                assert $ == #4AE2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #AAE2
                include "../Action/CopyObjectData.asm"
                ent
                assert $ == #4B1B
                disp #AB1B
                include "../Action/SelectMemoryPage.asm"
                ent
                assert $ == #4B23
                disp #AB23
                include "../Action/UnpackResource.asm"
                ent
                assert $ == #4C38
                disp #AC38
                include "../Action/ReadWordFromIX.asm"
                ent
                assert $ == #4C44
                disp #AC44
                include "../Action/ActivateParameterSet.asm"
                ent
                assert $ == #4C5D
                disp #AC5D
                include "../Action/ApplyParameterSet.asm"
                ent
                assert $ == #4CAB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #4CAB
                disp #ACAB
                include "../Action/QueueDiagnosticCounters.asm"
                ent
                assert $ == #4CD6
                disp #ACD6
                include "../Action/Data/DiagnosticMessages.asm"
                ent
                assert $ == #4CEA
                disp #ACEA
                include "../Action/TransformVectorTransposed.asm"
                ent
                assert $ == #4D1D
                disp #AD1D
                include "../Action/SwapCodePatchWords.asm"
                ent
                assert $ == #4D48
                disp #AD48
                include "../Action/SqrtWordBank1.asm"
                ent
                assert $ == #4D5A
                disp #AD5A
                include "../Action/EncodeHalfCoordinateDeltas.asm"
                ent
                assert $ == #4DB7
                disp #ADB7
                include "../Action/RotateBankedBasis.asm"
                ent
                assert $ == #4DC5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #4DC5
                disp #ADC5
                include "../Action/ProjectOverlayCoordinates.asm"
                ent
                assert $ == #4E15
                assert $ == #4E15
                disp #AE15
                include "../Action/EncodeComponentDeltas.asm"                   ; (0) жёсткий порядок, последовательное исполнение AE15 затем AE24
                ent
                assert $ == #4E24
                disp #AE24
                include "../Action/EncodeSignedRatio.asm"                       ; (1) жёсткий порядок, последовательное исполнение AE15 затем AE24
                ent
                assert $ == #4E73
                disp #AE73
                include "../Action/DivideScaledLogarithmic.asm"
                include "../Action/ComputePatchedVector.asm"
                ent
                assert $ == #4FF5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #4FF5
                ; Unknown, соседние байты вне доказанного входа BuildObjectOffsetCoefficients
                incbin "../Resources/17_ACTION/Unclassified024_BeforeActionObjectOffsetCoefficients.bin"
                assert $ == #5044
                disp #B044
                include "../Action/BuildObjectOffsetCoefficients.asm"
                ent
                assert $ == #50E9
                disp #B0E9
                include "../Action/SqrtWordCached.asm"
                ent
                assert $ == #516F
                ; Документация [фрагмент заметок о данных](../../Docs/ActionEmbeddedNotes.md)
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified025.bin"
                assert $ == #6000
                disp #C000
                include "../Action/ClipPolygon.asm"
                ent
                assert $ == #6071
                disp #C071
                include "../Action/ContinueClipPolygon.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #607A
                disp #C07A
                include "../Action/ReturnClipCase.asm"                          ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #607B
                disp #C07B
                include "../Action/ClipInsideToBottomRight.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #608A
                disp #C08A
                include "../Action/ClipRightToBottomRight.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6095
                disp #C095
                include "../Action/ClipInsideToBottomLeft.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60A4
                disp #C0A4
                include "../Action/ClipBottomToBottomLeft.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60AF
                disp #C0AF
                include "../Action/ClipInsideToTopRight.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60BE
                disp #C0BE
                include "../Action/ClipTopToTopRight.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60C9
                disp #C0C9
                include "../Action/ClipInsideToTopLeft.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60D8
                disp #C0D8
                include "../Action/ClipLeftToTopLeft.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60E3
                disp #C0E3
                include "../Action/ClipRightToInside.asm"
                ent
                assert $ == #60E9
                disp #C0E9
                include "../Action/ClipRightToLeft.asm"
                ent
                assert $ == #60EF
                disp #C0EF
                include "../Action/ClipRightToBottom.asm"
                ent
                assert $ == #6101
                disp #C101
                include "../Action/ClipRightToBottomLeft.asm"
                ent
                assert $ == #6119
                disp #C119
                include "../Action/ClipRightToTop.asm"
                ent
                assert $ == #612B
                disp #C12B
                include "../Action/ClipRightToTopRight.asm"
                ent
                assert $ == #6132
                disp #C132
                include "../Action/ClipRightToTopLeft.asm"
                ent
                assert $ == #6144
                disp #C144
                include "../Action/ClipLeftToInside.asm"
                ent
                assert $ == #614A
                disp #C14A
                include "../Action/ClipLeftToRight.asm"
                ent
                assert $ == #6150
                disp #C150
                include "../Action/ClipLeftToBottom.asm"
                ent
                assert $ == #6162
                disp #C162
                include "../Action/ClipLeftToBottomRight.asm"
                ent
                assert $ == #6174
                disp #C174
                include "../Action/ClipLeftToBottomLeft.asm"
                ent
                assert $ == #617B
                disp #C17B
                include "../Action/ClipLeftToTop.asm"
                ent
                assert $ == #618D
                disp #C18D
                include "../Action/ClipLeftToTopRight.asm"
                ent
                assert $ == #61A5
                disp #C1A5
                include "../Action/ClipBottomToInside.asm"
                ent
                assert $ == #61AB
                disp #C1AB
                include "../Action/ClipBottomToRight.asm"
                ent
                assert $ == #61BD
                disp #C1BD
                include "../Action/ClipBottomToLeft.asm"
                ent
                assert $ == #61CF
                disp #C1CF
                include "../Action/ClipBottomToBottomRight.asm"
                ent
                assert $ == #61D6
                disp #C1D6
                include "../Action/ClipBottomToTop.asm"
                ent
                assert $ == #61DC
                disp #C1DC
                include "../Action/ClipBottomToTopRight.asm"
                ent
                assert $ == #61F1
                disp #C1F1
                include "../Action/ClipBottomToTopLeft.asm"
                ent
                assert $ == #620C
                disp #C20C
                include "../Action/ClipBottomRightToInside.asm"
                ent
                assert $ == #6228
                disp #C228
                include "../Action/ClipBottomRightToRight.asm"
                ent
                assert $ == #622F
                disp #C22F
                include "../Action/ClipBottomRightToLeft.asm"
                ent
                assert $ == #624E
                disp #C24E
                include "../Action/ClipBottomRightToBottom.asm"
                ent
                assert $ == #6259
                disp #C259
                include "../Action/ClipBottomRightToBottomLeft.asm"
                ent
                assert $ == #625F
                disp #C25F
                include "../Action/ClipBottomRightToTop.asm"
                ent
                assert $ == #6274
                disp #C274
                include "../Action/ClipBottomRightToTopLeft.asm"
                ent
                assert $ == #628D
                disp #C28D
                include "../Action/ClipBottomLeftToInside.asm"
                ent
                assert $ == #62A9
                disp #C2A9
                include "../Action/ClipBottomLeftToRight.asm"
                ent
                assert $ == #62BE
                disp #C2BE
                include "../Action/ClipBottomLeftToLeft.asm"
                ent
                assert $ == #62C9
                disp #C2C9
                include "../Action/ClipBottomLeftToBottom.asm"
                ent
                assert $ == #62D0
                disp #C2D0
                include "../Action/ClipBottomLeftToTop.asm"
                ent
                assert $ == #62EF
                disp #C2EF
                include "../Action/ClipBottomLeftToTopRight.asm"
                ent
                assert $ == #6308
                disp #C308
                include "../Action/ClipBottomLeftToTopLeft.asm"
                ent
                assert $ == #630E
                disp #C30E
                include "../Action/ClipTopToInside.asm"
                ent
                assert $ == #6314
                disp #C314
                include "../Action/ClipTopToRight.asm"
                ent
                assert $ == #6326
                disp #C326
                include "../Action/ClipTopToLeft.asm"
                ent
                assert $ == #6338
                disp #C338
                include "../Action/ClipTopToBottom.asm"
                ent
                assert $ == #633E
                disp #C33E
                include "../Action/ClipTopToBottomRight.asm"
                ent
                assert $ == #6359
                disp #C359
                include "../Action/ClipTopToBottomLeft.asm"
                ent
                assert $ == #636E
                disp #C36E
                include "../Action/ClipTopToTopLeft.asm"
                ent
                assert $ == #6375
                disp #C375
                include "../Action/ClipTopRightToInside.asm"
                ent
                assert $ == #6391
                disp #C391
                include "../Action/ClipTopRightToRight.asm"
                ent
                assert $ == #639C
                disp #C39C
                include "../Action/ClipTopRightToLeft.asm"
                ent
                assert $ == #63B1
                disp #C3B1
                include "../Action/ClipTopRightToBottom.asm"
                ent
                assert $ == #63D0
                disp #C3D0
                include "../Action/ClipTopRightToBottomRight.asm"
                ent
                assert $ == #63D6
                disp #C3D6
                include "../Action/ClipTopRightToBottomLeft.asm"
                ent
                assert $ == #63EF
                disp #C3EF
                include "../Action/ClipTopRightToTop.asm"
                ent
                assert $ == #63F6
                disp #C3F6
                include "../Action/ClipTopLeftToInside.asm"
                ent
                assert $ == #6412
                disp #C412
                include "../Action/ClipTopLeftToRight.asm"
                ent
                assert $ == #6431
                disp #C431
                include "../Action/ClipTopLeftToLeft.asm"
                ent
                assert $ == #6438
                disp #C438
                include "../Action/ClipTopLeftToBottom.asm"
                ent
                assert $ == #644D
                disp #C44D
                include "../Action/ClipTopLeftToBottomRight.asm"
                ent
                assert $ == #6466
                disp #C466
                include "../Action/ClipTopLeftToTop.asm"
                ent
                assert $ == #6471
                disp #C471
                include "../Action/ClipTopLeftToTopRight.asm"
                ent
                assert $ == #6477
                disp #C477
                include "../Action/ComputeTopClipProduct.asm"
                ent
                assert $ == #6496
                disp #C496
                include "../Action/ComputeBottomClipProduct.asm"
                ent
                assert $ == #64B5
                disp #C4B5
                include "../Action/ComputeLeftClipProduct.asm"
                ent
                assert $ == #64D4
                disp #C4D4
                include "../Action/ComputeRightClipProduct.asm"
                ent
                assert $ == #64F3
                disp #C4F3
                include "../Action/ClipInsideToTop.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #64F6
                disp #C4F6
                include "../Action/AppendTopClipIntersection.asm"               ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #653D
                disp #C53D
                include "../Action/ClipInsideToBottom.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6540
                disp #C540
                include "../Action/AppendBottomClipIntersection.asm"            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6588
                disp #C588
                include "../Action/ClipInsideToLeft.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #658B
                disp #C58B
                include "../Action/AppendLeftClipIntersection.asm"              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #65E4
                disp #C5E4
                include "../Action/ClipInsideToRight.asm"                       ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #65E7
                disp #C5E7
                include "../Action/AppendRightClipIntersection.asm"             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6641
                disp #C641
                include "../Action/AppendTopLeftClipCorner.asm"
                ent
                assert $ == #664C
                disp #C64C
                include "../Action/AppendTopRightClipCorner.asm"
                ent
                assert $ == #6657
                disp #C657
                include "../Action/AppendBottomLeftClipCorner.asm"
                ent
                assert $ == #6662
                disp #C662
                include "../Action/AppendBottomRightClipCorner.asm"
                ent
                assert $ == #666D
                disp #C66D
                include "../Action/CompareTopLeftProducts.asm"
                ent
                assert $ == #6681
                disp #C681
                include "../Action/CompareTopRightProducts.asm"
                ent
                assert $ == #6695
                disp #C695
                include "../Action/CompareBottomLeftProducts.asm"
                ent
                assert $ == #66A9
                disp #C6A9
                include "../Action/CompareBottomRightProducts.asm"
                ent
                assert $ == #66BD
                disp #C6BD
                include "../Action/ComputeSecondAxisDelta.asm"
                ent
                assert $ == #66C8
                disp #C6C8
                include "../Action/ComputeFirstAxisDelta.asm"
                ent
                assert $ == #66D3
                disp #C6D3
                include "../Action/AppendSecondClipPoint.asm"
                ent
                assert $ == #66EA
                disp #C6EA
                include "../Action/ExitClipContour.asm"
                ent
                assert $ == #66F4
                disp #C6F4
                include "../Action/MultiplySigned16.asm"
                ent
                assert $ == #688C
                disp #C88C
                include "../Action/DivideSigned32To16.asm"
                ent
                assert $ == #6941
                disp #C941
                include "../Action/ClipSingleEdge.asm"
                ent
                assert $ == #699B
                disp #C99B
                include "../Action/BuildRenderCoefficients.asm"
                ent
                assert $ == #6B23
                disp #CB23
                include "../Action/ComposeRenderMatrix.asm"
                ent
                assert $ == #6EE3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified026.bin"
                assert $ == #6F08
                disp #CF08
                include "../Action/UnknownCF08.asm"
                ent
                assert $ == #6F0B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #6F0B
                assert $ == #6F0B
                disp #CF0B
                include "../Action/Data/ClipFirstPoint.asm"
                ent
                assert $ == #6F10
                ; Соседние байты таблицы, поэлементная разметка ещё не оформлена
                incbin "../Resources/17_ACTION/Unclassified027_BetweenClipPoints.bin"
                assert $ == #6F1B
                disp #CF1B
                include "../Action/Data/ClipSecondPoint.asm"
                ent
                assert $ == #6F20
                ; Соседние байты таблицы, поэлементная разметка ещё не оформлена
                incbin "../Resources/17_ACTION/Unclassified027_AfterClipPoints.bin"
                assert $ == #6F2B
                disp #CF2B
                include "../Action/Data/ClipProducts.asm"
                ent
                assert $ == #6F3B
                incbin "../Resources/17_ACTION/Unclassified027_AfterProducts.bin"
                assert $ == #710A
                disp #D10A
                include "../Action/ClearWorkBuffer.asm"
                ent
                assert $ == #712C
                disp #D12C
                include "../Action/MultiplySignedScaled.asm"
                ent
                assert $ == #7194
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа ProjectRenderVertex
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа ProjectRenderVertexGroup
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа PrepareRenderVertexProducts
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа TransformObjectVertices
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа PreparePolygonFill
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа SelectPolygonRowLimit
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа UpdatePolygonLeftEdge
                assert $ == #7194
                ; Unknown, соседние байты вне доказанного входа PolygonFillRows
                incbin "../Resources/17_ACTION/Unclassified028_BeforePolygonRows.bin"
                assert $ == #71C0
                disp #D1C0
                include "../Action/PolygonFillRows.asm"
                ent
                assert $ == #7268
                ; Unknown, соседние байты вне доказанного входа PolygonFillRows
                assert $ == #7268
                disp #D268
                include "../Action/SelectPolygonRightEdge.asm"
                ent
                assert $ == #726B
                ; Unknown, соседние байты вне доказанного входа SelectPolygonRightEdge
                assert $ == #726B
                disp #D26B
                include "../Action/WrapPolygonLeftEdge.asm"
                ent
                assert $ == #7272
                disp #D272
                include "../Action/UpdatePolygonLeftEdge.asm"
                ent
                assert $ == #73A8
                ; Unknown, соседние байты вне доказанного входа UpdatePolygonLeftEdge
                assert $ == #73A8
                ; Unknown, соседние байты вне доказанного входа UpdatePolygonRightEdge
                assert $ == #73A8
                disp #D3A8
                include "../Action/WrapPolygonRightEdge.asm"
                ent
                assert $ == #73AD
                disp #D3AD
                include "../Action/UpdatePolygonRightEdge.asm"                  ; (0) жёсткий порядок, отрицательный длинный путь продолжается в (1)
                ent
                assert $ == #74C1
                disp #D4C1
                include "../Action/SelectPolygonRowLimit.asm"                   ; (1) жёсткий порядок, общий хвост после (0)
                ent
                assert $ == #74F5
                ; Unknown, соседние байты вне доказанного входа SelectPolygonRowLimit
                assert $ == #74F5
                disp #D4F5
                include "../Action/SetShortNegativeRightStep.asm"
                ent
                assert $ == #7503
                ; Unknown, соседние байты вне доказанного входа SetShortNegativeRightStep
                assert $ == #7503
                disp #D503
                include "../Action/WrapPolygonLeftTop.asm"
                ent
                assert $ == #750A
                ; Unknown, соседние байты вне доказанного входа WrapPolygonLeftTop
                assert $ == #750A
                disp #D50A
                include "../Action/WrapPolygonRightTop.asm"
                ent
                assert $ == #750F
                ; Unknown, соседние байты вне доказанного входа WrapPolygonRightTop
                assert $ == #750F
                disp #D50F
                include "../Action/ReturnPolygonFill.asm"
                ent
                assert $ == #7511
                disp #D511
                include "../Action/PreparePolygonFill.asm"
                ent
                assert $ == #75C9
                disp #D5C9
                include "../Action/TransformObjectVertices.asm"
                ent
                assert $ == #75F9
                disp #D5F9
                include "../Action/PrepareRenderVertexProducts.asm"             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #7694
                disp #D694
                include "../Action/ProjectRenderVertexGroup.asm"                ; (1) жёсткий порядок, продолжение подготовителя
                ent
                assert $ == #77A0
                disp #D7A0
                include "../Action/ProjectRenderVertex.asm"
                ent
                assert $ == #7BBD
                disp #DBBD
                include "../Action/RenderClippedRecords.asm"
                ent
                assert $ == #7D23
                disp #DD23
                include "../Action/RenderInsideRecords.asm"
                ent
                assert $ == #7DD1
                disp #DDD1
                include "../Action/CombineListedVertexCodes.asm"
                ent
                assert $ == #7DF0
                disp #DDF0
                include "../Action/DrawLinearLine.asm"
                ent
                assert $ == #7EF0
                disp #DEF0
                include "../Action/AbortProjectedVertexScan.asm"
                ent
                assert $ == #7EF3
                disp #DEF3
                include "../Action/ClassifyProjectedVertices.asm"
                ent
                assert $ == #7FB6
                ; Unknown, соседние байты вне доказанного входа ClassifyProjectedVertices
                assert $ == #7FB6
                disp #DFB6
                include "../Action/CheckFaceOrientation.asm"
                ent
                assert $ == #8009
                ; Unknown, соседние байты вне доказанного входа CheckFaceOrientation
                assert $ == #8009
                incbin "../Resources/17_ACTION/Unclassified028_BeforeLineMasks.bin"
                assert $ == #8010
                disp #E010
                include "../Action/Data/LineMasks.asm"
                ent
                assert $ == #8020
                disp #E020
                include "../Action/RenderSceneFrame.asm"                        ; (0) жёсткий порядок продолжения E020
                ent
                assert $ == #81B9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #E1B9
                include "../Action/PrepareProjectionScale.asm"                  ; (1) жёсткий порядок продолжения E020
                ent
                assert $ == #81D1
                disp #E1D1
                include "../Action/CheckCloseRecordBounds.asm"                  ; (2) жёсткий порядок продолжения E020
                ent
                assert $ == #8213
                disp #E213
                include "../Action/ClipProjectionBounds.asm"                    ; (3) жёсткий порядок продолжения E020
                ent
                assert $ == #8299
                disp #E299
                include "../Action/PrepareProjectedBounds.asm"                  ; (4) жёсткий порядок продолжения E020
                ent
                disp #E30F
                include "../Action/CaptureProjectedRecord.asm"                  ; (5) жёсткий порядок продолжения E020
                ent
                disp #E36A
                include "../Action/FollowProjectedTarget.asm"                   ; (6) жёсткий порядок продолжения E020
                ent
                assert $ == #840F
                disp #E40F
                include "../Action/InsertRenderQueue.asm"                       ; (7) жёсткий порядок продолжения E020
                ent
                assert $ == #84A6
                disp #E4A6
                include "../Action/ReadRenderQueue.asm"                         ; (0) жёсткий порядок чтения очереди
                ent
                assert $ == #84DB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #E4DB
                include "../Action/RenderQueuedObject.asm"                      ; (1) жёсткий порядок чтения очереди
                ent
                assert $ == #84FF
                disp #E4FF
                include "../Action/SelectRenderQueueNode.asm"                   ; (2) жёсткий порядок чтения очереди
                ent
                assert $ == #8506
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8506
                disp #E506
                include "../Action/DispatchCloseRecord.asm"
                ent
                assert $ == #851F
                disp #E51F
                include "../Action/CheckCloseRecordComponents.asm"              ; (0) жёсткий порядок дополнительного входа E51F
                ent
                assert $ == #854A
                disp #E54A
                include "../Action/ReverseCloseRecordState.asm"                 ; (1) жёсткий порядок дополнительного входа E51F
                ent
                assert $ == #855C
                disp #E55C
                include "../Action/PrepareRecordScale.asm"
                ent
                assert $ == #859F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified032.bin"
                assert $ == #85A0
                disp #E5A0
                include "../Action/UpdateRecordComponents.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #8655
                disp #E655
                include "../Action/FinishRecordWarning.asm"                     ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #8658
                disp #E658
                include "../Action/RejectRecordUpdate.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #865F
                disp #E65F
                include "../Action/ReleaseClass12Records.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #8685
                disp #E685
                include "../Action/RestoreHalvedOffsets.asm"
                ent
                assert $ == #869E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #869E
                disp #E69E
                include "../Action/SelectRecordByIndex.asm"
                ent
                assert $ == #86A7
                disp #E6A7
                include "../Action/RecordIndexToAddress.asm"
                ent
                assert $ == #86B5
                disp #E6B5
                include "../Action/RecordIXToIndex.asm"
                ent
                assert $ == #86BE
                disp #E6BE
                include "../Action/RecordIYToIndex.asm"
                ent
                assert $ == #86C7
                disp #E6C7
                include "../Action/RecordAddressToIndex.asm"
                ent
                assert $ == #86D1
                disp #E6D1
                include "../Action/NextActiveRecord.asm"
                ent
                assert $ == #86E2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #86E2
                assert $ == #86E2
                disp #E6E2
                include "../Action/FindFilteredRecordOr26.asm"
                ent
                assert $ == #870D
                disp #E70D
                include "../Action/FindRecordExcept6And7.asm"
                ent
                assert $ == #8729
                assert $ == #8729
                disp #E729
                include "../Action/FindRecordClass6Or7.asm"
                ent
                assert $ == #8745
                assert $ == #8745
                disp #E745
                include "../Action/FindRecordClass5Or14.asm"
                ent
                assert $ == #8761
                assert $ == #8761
                assert $ == #8761
                assert $ == #8761
                assert $ == #8761
                disp #E761
                include "../Action/PrepareLinkedRecordContext.asm"
                ent
                assert $ == #8794
                assert $ == #8794
                disp #E794
                include "../Action/LoadLinkedRecordVectors.asm"
                ent
                assert $ == #8804
                assert $ == #8804
                assert $ == #8804
                assert $ == #8804
                disp #E804
                include "../Action/CheckAndToggleLinkedOverlay.asm"
                ent
                assert $ == #8863
                disp #E863
                include "../Action/SpawnClass9ForClass8.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #886B
                disp #E86B
                include "../Action/SpawnLinkedClass9Records.asm"                ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #891E
                disp #E91E
                include "../Action/CheckLinkedTargetTransition.asm"
                ent
                assert $ == #8935
                disp #E935
                include "../Action/CheckObjectPhaseTransition.asm"
                ent
                assert $ == #897C
                disp #E97C
                include "../Action/SelectClass8ForRecord.asm"
                ent
                assert $ == #898D
                disp #E98D
                include "../Action/FindRecordByCode.asm"
                ent
                assert $ == #89A1
                disp #E9A1
                include "../Action/FindReusableRecord.asm"
                ent
                assert $ == #89C2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #89C2
                assert $ == #89C2
                disp #E9C2
                include "../Action/FindNearestListedRecord.asm"
                ent
                assert $ == #8A00
                disp #EA00
                include "../Action/CheckCandidateListClass.asm"
                ent
                assert $ == #8A15
                assert $ == #8A15
                disp #EA15
                include "../Action/CheckCandidateListReady.asm"
                ent
                assert $ == #8A29
                disp #EA29
                include "../Action/PrepareLargeEffect.asm"                      ; (0) жёсткий порядок продолжения EA29
                ent
                assert $ == #8A3D
                disp #EA3D
                include "../Action/AllocateLargeEffect.asm"                     ; (1) жёсткий порядок продолжения EA29
                ent
                assert $ == #8AE9
                assert $ == #8AE9
                disp #EAE9
                include "../Action/MaxRecordDeltaHigh.asm"
                ent
                assert $ == #8B41
                assert $ == #8B41
                disp #EB41
                include "../Action/ToggleTargetOverlay.asm"
                ent
                assert $ == #8B6E
                ; Unknown, соседние байты вне доказанного входа ToggleTargetOverlay
                disp #EB6E
                include "../Action/Data/OverlayLine.asm"
                ent
                assert $ == #8B72
                disp #EB72
                include "../Action/NextRandomWord0.asm"
                ent
                assert $ == #8B79
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8B79
                disp #EB79
                include "../Action/NextRandomWord3.asm"
                ent
                assert $ == #8B80
                disp #EB80
                include "../Action/NextRandomWord4.asm"
                ent
                assert $ == #8B87
                disp #EB87
                include "../Action/NextRandomWord1.asm"
                ent
                assert $ == #8B8E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8B8E
                disp #EB8E
                include "../Action/NextRandomWord5.asm"
                ent
                assert $ == #8B95
                disp #EB95
                include "../Action/NextRandomWord6.asm"
                ent
                assert $ == #8B9C
                disp #EB9C
                include "../Action/NextRandomWord7.asm"
                ent
                assert $ == #8BA3
                disp #EBA3
                include "../Action/NextRandomWord8.asm"
                ent
                assert $ == #8BAA
                disp #EBAA
                include "../Action/NextRandomWord9.asm"
                ent
                assert $ == #8BB1
                disp #EBB1
                include "../Action/NextRandomWord10.asm"
                ent
                assert $ == #8BB8
                disp #EBB8
                include "../Action/NextRandomWord2.asm"
                ent
                assert $ == #8BBF
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8BBF
                ; Соседние исходные байты, назначение не установлено
                assert $ == #8BBF
                disp #EBBF
                include "../Action/NextRandomWord11.asm"
                ent
                assert $ == #8BC6
                disp #EBC6
                include "../Action/NextRandomWord12.asm"
                ent
                assert $ == #8BCD
                disp #EBCD
                include "../Action/NextRandomWord13.asm"
                ent
                assert $ == #8BD4
                disp #EBD4
                include "../Action/NextRandomWord14.asm"
                ent
                assert $ == #8BDB
                disp #EBDB
                include "../Action/Data/FoldRandomStream3.asm"
                ent
                assert $ == #8BDE
                disp #EBDE
                include "../Action/Data/FoldRandomStream0.asm"
                ent
                assert $ == #8BE1
                ; Соседние исходные байты, назначение не установлено
                assert $ == #8BE1
                disp #EBE1
                include "../Action/Data/FoldRandomStream8.asm"
                ent
                assert $ == #8BE4
                disp #EBE4
                include "../Action/Data/FoldRandomStream9.asm"
                ent
                assert $ == #8BE7
                disp #EBE7
                include "../Action/Data/FoldRandomStream10.asm"
                ent
                assert $ == #8BEA
                disp #EBEA
                include "../Action/Data/FoldRandomStream2.asm"
                ent
                assert $ == #8BED
                ; Соседние исходные байты, назначение не установлено
                assert $ == #8BED
                disp #EBED
                include "../Action/Data/FoldRandomStream11.asm"
                ent
                assert $ == #8BF0
                disp #EBF0
                include "../Action/Data/FoldRandomStream12.asm"
                ent
                assert $ == #8BF3
                disp #EBF3
                include "../Action/Data/FoldRandomStream13.asm"
                ent
                assert $ == #8BF6
                disp #EBF6
                include "../Action/Data/FoldRandomStream14.asm"
                ent
                assert $ == #8BF9
                disp #EBF9
                include "../Action/Data/FoldRandomStream6.asm"
                ent
                assert $ == #8BFC
                disp #EBFC
                include "../Action/Data/FoldRandomStream7.asm"
                ent
                assert $ == #8BFF
                disp #EBFF
                include "../Action/Data/FoldRandomStream4.asm"
                ent
                assert $ == #8C02
                disp #EC02
                include "../Action/Data/FoldRandomStream1.asm"
                ent
                assert $ == #8C05
                ; Соседние исходные байты, назначение не установлено
                assert $ == #8C05
                disp #EC05
                include "../Action/Data/FoldRandomStream5.asm"
                ent
                assert $ == #8C08
                disp #EC08
                include "../Action/StepFoldedRandom.asm"
                ent
                assert $ == #8C54
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8C54
                disp #EC54
                include "../Action/ClassifyProjectedPair.asm"
                ent
                assert $ == #8CA8
                disp #ECA8
                include "../Action/UpdateAyEffects.asm"
                ent
                assert $ == #8D8F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #8D8F
                disp #ED8F
                include "../Action/Data/AyStreamsFirst.asm"
                ent
                assert $ == #8DC1
                ; Unknown, соседние байты вне пяти доказанных потоков
                assert $ == #8DC1
                ; Unknown, соседние байты вне доказанных потоков назначения цели
                incbin "../Resources/17_ACTION/Unclassified044_BeforeCaptureStreams.bin"
                assert $ == #8E02
                disp #EE02
                include "../Action/Data/AyCaptureStreams.asm"
                ent
                assert $ == #8E34
                ; Unknown, соседние байты вне доказанных потоков назначения цели
                disp #EE34
                include "../Action/Data/AyPairedAimStream.asm"
                ent
                assert $ == #8E4D
                disp #EE4D
                include "../Action/Data/AyStreamsLater.asm"
                ent
                assert $ == #8F50
                ; Unknown, соседние байты вне пяти доказанных потоков
                assert $ == #8F50
                ; Unknown, соседние байты вне доказанного входа MarkIYRecordForReuse
                disp #EF50
                include "../Action/Data/ObjectStateHandlers.asm"
                ent
                assert $ == #8F7C
                assert $ == #8F7C
                ; Unknown, соседние байты вне доказанного входа AdvanceObjectOffsetRise
                incbin "../Resources/17_ACTION/AfterObjectStateHandlers_BeforeActionObjectOffsetRise.bin"
                assert $ == #8F7D
                disp #EF7D
                include "../Action/AdvanceObjectOffsetRise.asm"
                ent
                assert $ == #8F9A
                assert $ == #8F9A
                disp #EF9A
                include "../Action/AdvanceObjectOffsetFall.asm"
                ent
                assert $ == #8FB5
                assert $ == #8FB5
                disp #EFB5
                include "../Action/AdvanceObjectPhaseWait.asm"
                ent
                assert $ == #9003
                assert $ == #9003
                disp #F003
                include "../Action/RefreshRecordClassAndOffsets.asm"
                ent
                assert $ == #9009
                assert $ == #9009
                disp #F009
                include "../Action/HandleLinkedRecordProximity.asm"
                ent
                assert $ == #903D
                disp #F03D
                include "../Action/MarkIYRecordForReuse.asm"
                ent
                assert $ == #904A
                assert $ == #904A
                disp #F04A
                include "../Action/HandleSelectedRecordProximity.asm"
                ent
                assert $ == #9075
                disp #F075
                include "../Action/SetClass18ObjectState.asm"
                ent
                assert $ == #907C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #907C
                assert $ == #907C
                assert $ == #907C
                disp #F07C
                include "../Action/UpdatePhaseAndNearVector.asm"
                ent
                assert $ == #9081
                assert $ == #9081
                disp #F081
                include "../Action/UpdateLinkedOrNearPhase.asm"                 ; (0) жёсткий порядок, продолжение после невыполненного JP C
                ent
                assert $ == #9087
                disp #F087
                include "../Action/UpdateNearVectorPhase.asm"                   ; (1) жёсткий порядок, продолжение после невыполненного JP C
                ent
                assert $ == #90BE
                assert $ == #90BE
                disp #F0BE
                include "../Action/StepSelectedWideVector.asm"                  ; (0) жёсткий порядок, последовательное исполнение после CALL
                ent
                assert $ == #90F8
                disp #F0F8
                include "../Action/PrepareObjectOffsetTransform.asm"            ; (1) жёсткий порядок, последовательное исполнение после CALL
                ent
                assert $ == #9138
                assert $ == #9138
                assert $ == #9138
                assert $ == #9138
                assert $ == #9138
                assert $ == #9138
                disp #F138
                include "../Action/HandleLinkedTargetState.asm"
                ent
                assert $ == #9222
                disp #F222
                include "../Action/CheckClass17SpawnWindow.asm"
                ent
                assert $ == #924F
                assert $ == #924F
                disp #F24F
                include "../Action/SpawnLinkedClass17AndContinue.asm"
                ent
                assert $ == #9255
                disp #F255
                include "../Action/SpawnClass17FromCurrentLink.asm"
                ent
                assert $ == #9280
                assert $ == #9280
                ; Unknown, соседние байты вне доказанного входа HandleLinkedPhaseState
                disp #F280
                include "../Action/Data/ClassSpawnValues.asm"
                ent
                assert $ == #9289
                disp #F289
                include "../Action/HandleLinkedPhaseState.asm"
                ent
                assert $ == #9356
                disp #F356
                include "../Action/HandleClass18Proximity.asm"
                ent
                assert $ == #936B
                disp #F36B
                include "../Action/StepCodesTowardRecord.asm"
                ent
                assert $ == #9394
                disp #F394
                include "../Action/MarkRecordForReuse.asm"
                ent
                assert $ == #93A1
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #93A1
                disp #F3A1
                include "../Action/StepTimedPhasePattern.asm"
                ent
                assert $ == #93C8
                assert $ == #93C8
                assert $ == #93C8
                disp #F3C8
                include "../Action/StepTimedLinkedOverlay.asm"
                ent
                assert $ == #93F0
                disp #F3F0
                include "../Action/SpawnPeriodicClass3Record.asm"
                ent
                assert $ == #949C
                assert $ == #949C
                disp #F49C
                include "../Action/SweepClass17AndPrepareSpawn.asm"
                ent
                assert $ == #951E
                disp #F51E
                include "../Action/UpdatePreferredClass18.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #9527
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #9527
                disp #F527
                include "../Action/CheckPreferredRandomWord.asm"                ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #9535
                disp #F535
                include "../Action/FindPreferredClass0.asm"                     ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #953F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #953F
                disp #F53F
                include "../Action/ContinuePreferredClass0.asm"                 ; (3) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #9541
                disp #F541
                include "../Action/FindPreferredClass7.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #954B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #954B
                disp #F54B
                include "../Action/ContinuePreferredClass7.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #954D
                disp #F54D
                include "../Action/FindPreferredClass5.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #9557
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #9557
                disp #F557
                include "../Action/ApplyPreferredToClass18.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #9572
                disp #F572
                include "../Action/ResetRecordUpdateBases.asm"                  ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #957F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #957F
                assert $ == #957F
                disp #F57F
                include "../Action/ApproachTargetRecordAndResolve.asm"
                ent
                assert $ == #966A
                disp #F66A
                include "../Action/StepTimedRecordDecay.asm"
                ent
                assert $ == #967F
                assert $ == #967F
                assert $ == #967F
                disp #F67F
                include "../Action/StepIdleObjectOffset.asm"
                ent
                assert $ == #968E
                ; Unknown, соседние байты вне доказанного входа StepIdleObjectOffset
                incbin "../Resources/17_ACTION/Unclassified051_AfterActionTimedDecayState_BeforeActionIdleBaseReset_AfterActionIdleState.bin"
                assert $ == #9691
                disp #F691
                include "../Action/ResetIdleRecordBases.asm"
                ent
                assert $ == #969E
                assert $ == #969E
                assert $ == #969E
                assert $ == #969E
                disp #F69E
                include "../Action/DispatchClassOnHighRandomWord.asm"
                ent
                assert $ == #96AB
                disp #F6AB
                include "../Action/StepFastRecordPhases.asm"
                ent
                assert $ == #96BD
                assert $ == #96BD
                disp #F6BD
                include "../Action/AcquireLinkAndApplyOffsets.asm"              ; (0) жёсткий порядок, последовательное исполнение после CALL
                ent
                assert $ == #96CD
                disp #F6CD
                include "../Action/ApplyRecordLocalOffsets.asm"                 ; (1) жёсткий порядок, последовательное исполнение после CALL
                ent
                assert $ == #96EC
                assert $ == #96EC
                disp #F6EC
                include "../Action/StartSmallRecordEffect.asm"
                ent
                assert $ == #9729
                disp #F729
                include "../Action/UpdateObjects.asm"
                ent
                assert $ == #9792
                disp #F792
                include "../Action/CheckRecordEffectThreshold.asm"              ; (0) жёсткий порядок возврата большого эффекта
                ent
                assert $ == #97BF
                disp #F7BF
                include "../Action/ResumeAfterRecordEffect.asm"                 ; (1) жёсткий порядок возврата большого эффекта
                ent
                assert $ == #97C6
                disp #F7C6
                include "../Action/DispatchObjectState.asm"
                ent
                assert $ == #9866
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified054.bin"
                assert $ == #A000
