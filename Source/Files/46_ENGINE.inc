                ; Архивный ENGINE.C, фактический адрес загрузки #4000.
                ; [Исходный каталог и чтение](../../Docs/ArchiveMenuHandoff.md)
                assert $ == #0000
                disp #4000
                include "../ArchiveEngine/RunCombatScene.asm"
                ent
                assert $ == #004B
                disp #404B
                include "../ArchiveEngine/RestoreCombatFrame.asm"
                ent
                assert $ == #005D
                disp #405D
                include "../ArchiveEngine/ComposeCombatFrame.asm"
                ent
                assert $ == #0072
                disp #4072
                include "../ArchiveEngine/ClearShadowScreen.asm"
                ent
                assert $ == #008C
                disp #408C
                include "../ArchiveEngine/LoadCombatResources.asm"
                ent
                assert $ == #0096
                disp #4096
                include "../ArchiveEngine/PrepareCombatScene.asm"
                ent
                assert $ == #00A9
                disp #40A9
                include "../ArchiveEngine/TransferTo5C26.asm"
                ent
                assert $ == #00B1
                disp #40B1
                include "../ArchiveEngine/EnableSceneInterrupts.asm"
                ent
                assert $ == #00D2
                disp #40D2
                include "../ArchiveEngine/FrameHook.asm"
                ent
                assert $ == #00D3
                disp #40D3
                include "../ArchiveEngine/ReconcileFacing.asm"
                ent
                assert $ == #00DA
                disp #40DA
                include "../ArchiveEngine/CheckSecondFacing.asm"
                ent
                assert $ == #0105
                disp #4105
                include "../ArchiveEngine/CheckFirstFacing.asm"
                ent
                assert $ == #0130
                disp #4130
                include "../ArchiveEngine/RequestFighterTurn.asm"
                ent
                assert $ == #015D
                disp #415D
                include "../ArchiveEngine/ReconcileCombatView.asm"
                ent
                assert $ == #0178
                disp #4178
                include "../ArchiveEngine/CompareFighterPositions.asm"
                ent
                assert $ == #01B6
                disp #41B6
                include "../ArchiveEngine/MoveFirstApartLeft.asm"
                ent
                assert $ == #01BC
                disp #41BC
                include "../ArchiveEngine/MoveSecondApartRight.asm"
                ent
                assert $ == #01C2
                disp #41C2
                include "../ArchiveEngine/MoveFirstApartRight.asm"
                ent
                assert $ == #01C8
                disp #41C8
                include "../ArchiveEngine/MoveSecondApartLeft.asm"
                ent
                assert $ == #01CE
                disp #41CE
                include "../ArchiveEngine/AccumulateVerticalOffset.asm"
                ent
                assert $ == #01E9
                disp #41E9
                include "../ArchiveEngine/AdvanceFighterFrames.asm"
                ent
                assert $ == #01F8
                disp #41F8
                include "../ArchiveEngine/AdvanceFighterStep.asm"
                ent
                assert $ == #0236
                disp #4236
                include "../ArchiveEngine/ApplyFighterFrames.asm"
                ent
                assert $ == #024A
                disp #424A
                include "../ArchiveEngine/ReuseFrameIndex.asm"
                ent
                assert $ == #024E
                disp #424E
                include "../ArchiveEngine/ResumeRightAction.asm"
                ent
                assert $ == #0258
                disp #4258
                include "../ArchiveEngine/ResumeLeftAction.asm"
                ent
                assert $ == #0262
                disp #4262
                include "../ArchiveEngine/MirrorFrameIndex.asm"
                ent
                assert $ == #0270
                disp #4270
                include "../ArchiveEngine/FlipFighterSide.asm"
                ent
                assert $ == #027B
                disp #427B
                include "../ArchiveEngine/ApplyFighterAction.asm"        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0309
                disp #4309
                include "../ArchiveEngine/ApplyFighterStep.asm"          ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #03BD
                disp #43BD
                include "../ArchiveEngine/ClampAtLeft.asm"
                ent
                assert $ == #03E4
                disp #43E4
                include "../ArchiveEngine/ClampAtRight.asm"
                ent
                assert $ == #040B
                disp #440B
                include "../ArchiveEngine/ApplySideDelta.asm"
                ent
                assert $ == #0416
                disp #4416
                include "../ArchiveEngine/ApplyCombatInput.asm"
                ent
                assert $ == #0425
                disp #4425
                include "../ArchiveEngine/CollectCombatInput.asm"
                ent
                assert $ == #0439
                disp #4439
                include "../ArchiveEngine/PollFighterKeys.asm"
                ent
                assert $ == #048B
                disp #448B
                include "../ArchiveEngine/SelectFighterAction.asm"
                ent
                assert $ == #04DE
                disp #44DE
                include "../ArchiveEngine/Data/InputRules.asm"
                ent
                assert $ == #0617
                ; Исходные нули перед подтверждённой частью временного стека IRQ.
                incbin "../../Tools/Disasm/Extracted/Archived/46_ENGINE.C.sectors.bin", #0617, #000A
                assert $ == #0621
                disp #4621
                include "../ArchiveEngine/Data/IrqStack.asm"
                ent
                assert $ == #063F
                disp #463F
                include "../ArchiveEngine/Interrupt.asm"
                ent
                assert $ == #066C
                disp #466C
                include "../ArchiveEngine/LoadAnimationSteps.asm"
                ent
                assert $ == #069C
                disp #469C
                include "../ArchiveEngine/LoadSpriteBanks.asm"
                ent
                assert $ == #06C4
                disp #46C4
                include "../ArchiveEngine/BuildMirrorTable.asm"
                ent
                assert $ == #06EE
                disp #46EE
                include "../ArchiveEngine/RestoreFighterBackground.asm"
                ent
                assert $ == #0744
                disp #4744
                include "../ArchiveEngine/SwitchSceneTail.asm"
                ent
                assert $ == #0753
                disp #4753
                include "../ArchiveEngine/DrawFighter.asm"
                ent
                assert $ == #07FA
                disp #47FA
                include "../ArchiveEngine/Data/SpriteFileKeys.asm"
                ent
                assert $ == #0842
                disp #4842
                include "../ArchiveEngine/Data/Fighters.asm"
                ent
                assert $ == #08E8
                disp #48E8
                include "../ArchiveEngine/MoveViewRight.asm"
                ent
                assert $ == #08F5
                disp #48F5
                include "../ArchiveEngine/IncreaseViewY.asm"
                ent
                assert $ == #0902
                disp #4902
                include "../ArchiveEngine/DecreaseViewY.asm"
                ent
                assert $ == #090C
                disp #490C
                include "../ArchiveEngine/MoveViewLeft.asm"
                ent
                assert $ == #0916
                disp #4916
                include "../ArchiveEngine/LoadScenePixels.asm"
                ent
                assert $ == #092D
                disp #492D
                include "../ArchiveEngine/PrepareScenePages.asm"
                ent
                assert $ == #0974
                disp #4974
                include "../ArchiveEngine/ShowViewport.asm"
                ent
                assert $ == #0A00
                disp #4A00
                include "../ArchiveEngine/CopyViewportRows.asm"
                ent
                assert $ == #0A4B
                disp #4A4B
                include "../ArchiveEngine/Data/Scene.asm"
                ent
                assert $ == #0A5C
                disp #4A5C
                include "../ArchiveEngine/UpdateTimer.asm"
                ent
                assert $ == #0A8A
                disp #4A8A
                include "../ArchiveEngine/InitializeTimer.asm"
                ent
                assert $ == #0A95
                disp #4A95
                include "../ArchiveEngine/DrawTimerDigits.asm"
                ent
                assert $ == #0AD5
                disp #4AD5
                include "../ArchiveEngine/DrawTimerGlyph.asm"
                ent
                assert $ == #0AF2
                disp #4AF2
                include "../ArchiveEngine/CalculateTimerAddress.asm"
                ent
                assert $ == #0B0B
                disp #4B0B
                include "../ArchiveEngine/RestoreTimerBackground.asm"
                ent
                assert $ == #0B28
                disp #4B28
                include "../ArchiveEngine/Data/TimerRaster.asm"
                ent
                assert $ == #0C8A
                disp #4C8A
                include "../ArchiveEngine/Data/Timer.asm"
                ent
                assert $ == #0C8C
                disp #4C8C
                include "../ArchiveEngine/InitializeMeters.asm"
                ent
                assert $ == #0CC6
                disp #4CC6
                include "../ArchiveEngine/CopyMeterBitmap.asm"
                ent
                assert $ == #0CD7
                disp #4CD7
                include "../ArchiveEngine/UpdateMeters.asm"
                ent
                assert $ == #0CEF
                disp #4CEF
                include "../ArchiveEngine/ExtendLeftMeter.asm"
                ent
                assert $ == #0D1E
                disp #4D1E
                include "../ArchiveEngine/ExtendRightMeter.asm"
                ent
                assert $ == #0D4D
                ; Два исходных нуля, потребитель не установлен.
                incbin "../../Tools/Disasm/Extracted/Archived/46_ENGINE.C.sectors.bin", #0D4D, #0002
                assert $ == #0D4F
                disp #4D4F
                include "../ArchiveEngine/Data/MeterImages.asm"
                ent
                assert $ == #0FA7
                disp #4FA7
                include "../ArchiveEngine/Data/Meters.asm"
                ent
                assert $ == #0FB1
                disp #4FB1
                include "../ArchiveEngine/SelectPage.asm"
                ent
                assert $ == #0FB8
                disp #4FB8
                include "../ArchiveEngine/SelectPentagonPage.asm"
                ent
                assert $ == #0FCF
                disp #4FCF
                include "../ArchiveEngine/SelectScorpionPage.asm"
                ent
                assert $ == #0FE5
                disp #4FE5
                include "../ArchiveEngine/SelectAtmPage.asm"
                ent
                assert $ == #0FFF
                disp #4FFF
                include "../ArchiveEngine/OutputThroughDos.asm"
                ent
                assert $ == #1006
                disp #5006
                include "../ArchiveEngine/SelectSpritePage.asm"
                ent
                assert $ == #1012
                disp #5012
                include "../ArchiveEngine/Data/Paging.asm"
                ent
                assert $ == #101E
                disp #501E
                include "../ArchiveEngine/NextMeterRow.asm"
                ent
                assert $ == #102D
                disp #502D
                include "../ArchiveEngine/MultiplyByteWord.asm"
                ent
                assert $ == #103E
                disp #503E
                include "../ArchiveEngine/Data/OpponentMask.asm"
                ent
                assert $ == #1040
                disp #5040
                include "../ArchiveEngine/Data/SceneFileKey.asm"
                ent
                assert $ == #1049
                disp #5049
                include "../ArchiveEngine/Data/AnimationFileKeys.asm"
                ent
                assert $ == #105B
                ; Оригинальный секторный хвост, сохраняется вне логической длины файла.
                incbin "../../Tools/Disasm/Extracted/Archived/46_ENGINE.C.tail.bin"
                assert $ == #1100
