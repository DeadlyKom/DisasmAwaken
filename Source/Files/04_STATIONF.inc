; -----------------------------------------
; запись 4, STATIONF.C
; логическая длина 40960, полный секторный размер 40960
; -----------------------------------------
                assert $ == #0000
                disp #6000
                include "../Station/Data/PointerSprites.asm"
                ent
                assert $ == #0300
                disp #6300
                include "../StationBoot/RelocateBootstrap.asm"
                ent
                assert $ == #0319
                disp #4000
                include "../StationBoot/InitializeStation.asm"
                ent
                assert $ == #0343
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified001.bin"
                assert $ == #0389
                disp #4070
                include "../StationBoot/StartStation.asm"
                ent
                assert $ == #05CE
                disp #6322
                include "../Station/BuildSpriteLineTable.asm"
                ent
                assert $ == #0610
                disp #6364
                include "../Station/TogglePreviewFaceFill.asm"
                ent
                assert $ == #0642
                disp #6396
                include "../Station/SelectRamBank.asm"                          ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #064B
                disp #639F
                include "../Station/SelectMemoryPage.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0656
                disp #63AA
                include "../Station/StopMusic.asm"
                ent
                assert $ == #066F
                disp #63C3
                include "../Station/SuspendPointer.asm"
                ent
                assert $ == #0684
                disp #63D8
                include "../Station/ResumePointer.asm"
                ent
                assert $ == #069D
                disp #63F1
                include "../Station/TestMotionParameters.asm"
                ent
                assert $ == #06B8
                disp #640C
                include "../Station/UpdatePointer.asm"                          ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06BF
                disp #6413
                include "../Station/DrawPointer.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07F3
                disp #6547
                include "../Station/RestorePointer.asm"
                ent
                assert $ == #0821
                disp #6575
                include "../Station/Data/PointerBackground.asm"
                ent
                assert $ == #0831
                disp #6585
                include "../Station/Data/MouseInput.asm"
                ent
                assert $ == #083A
                disp #658E
                include "../Station/ConfigureMouseButtons.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0853
                disp #65A7
                include "../Station/PollMouse.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0875
                disp #65C9
                include "../Station/DecodeMouseButtons.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #087F
                disp #65D3
                include "../Station/DecodeThirdButton.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0884
                disp #65D8
                include "../Station/ReadMouseMotion.asm"                        ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #08E4
                disp #6638
                include "../Station/PollJoystick.asm"
                ent
                assert $ == #08ED
                disp #6641
                include "../Station/PollKeys.asm"                               ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0934
                disp #6688
                include "../Station/ApplyPointerInput.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #097F
                disp #66D3
                include "../Station/CommitPointerInput.asm"
                ent
                assert $ == #0984
                disp #66D8
                include "../Station/ClearInputFlags.asm"
                ent
                assert $ == #0994
                disp #66E8
                include "../Station/Data/InputFlags.asm"
                ent
                assert $ == #099A
                disp #66EE
                include "../Station/Data/PointerDirections.asm"
                ent
                assert $ == #09BA
                disp #670E
                include "../Station/StepUpLeft.asm"
                ent
                assert $ == #09C8
                disp #671C
                include "../Station/StepDownLeft.asm"
                ent
                assert $ == #09D6
                disp #672A
                include "../Station/StepUpRight.asm"
                ent
                assert $ == #09E9
                disp #673D
                include "../Station/StepDownRight.asm"
                ent
                assert $ == #09FC
                disp #6750
                include "../Station/StepLeft.asm"
                ent
                assert $ == #0A03
                disp #6757
                include "../Station/StepRight.asm"
                ent
                assert $ == #0A0E
                disp #6762
                include "../Station/NoPointerMotion.asm"
                ent
                assert $ == #0A0F
                disp #6763
                include "../Station/StepUp.asm"
                ent
                assert $ == #0A16
                disp #676A
                include "../Station/StepDown.asm"
                ent
                assert $ == #0A1D
                disp #6771
                include "../Station/HandleItem25.asm"
                ent
                assert $ == #0A20
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6774
                include "../Station/Unknown6774.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A2C
                assert $ == #0A2C
                disp #6780
                include "../Station/Unknown6780.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A55
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #67A9
                include "../Station/Unknown67A9.asm"
                ent
                assert $ == #0A7C
                assert $ == #0A7C
                disp #67D0
                include "../Station/UpdateShipListHover.asm"
                ent
                assert $ == #0A8C
                disp #67E0
                include "../Station/DrawModelListPanel.asm"
                ent
                assert $ == #0AE3
                disp #6837
                include "../Station/IgnoreModelPreviewHover.asm"
                ent
                assert $ == #0AE6
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #683A
                include "../Station/HandleModelPreviewClick.asm"
                ent
                assert $ == #0B1B
                assert $ == #0B1B
                disp #686F
                include "../Station/ReturnModelPreviewHover.asm"
                ent
                assert $ == #0B1C
                disp #6870
                include "../Station/Unknown6870.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0B23
                assert $ == #0B23
                disp #6877
                include "../Station/DrawItem26.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0B78
                disp #68CC
                include "../Station/Unknown68CC.asm"
                ent
                assert $ == #0B96
                disp #68EA
                include "../Station/Unknown68EA.asm"
                ent
                assert $ == #0BBF
                assert $ == #0BBF
                disp #6913
                include "../Station/HandleModelDescriptionHover.asm"
                ent
                assert $ == #0BC2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6916
                include "../Station/HandleModelDescriptionClick.asm"
                ent
                assert $ == #0BE9
                assert $ == #0BE9
                disp #693D
                include "../Station/ReturnModelDescriptionHover.asm"
                ent
                assert $ == #0BEA
                disp #693E
                include "../Station/TryDrawModelDescription.asm"                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0BF1
                assert $ == #0BF1
                disp #6945
                include "../Station/DrawModelDescriptionPanel.asm"              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0BFE
                disp #6952
                include "../Station/PrintModelDescription.asm"
                ent
                assert $ == #0C0F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6963
                include "../Station/CountModelDescriptionRows.asm"
                ent
                assert $ == #0C24
                assert $ == #0C24
                disp #6978
                include "../Station/HandleItem23.asm"
                ent
                assert $ == #0C27
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #697B
                include "../Station/Unknown697B.asm"
                ent
                assert $ == #0C53
                assert $ == #0C53
                disp #69A7
                include "../Station/Unknown69A7.asm"
                ent
                assert $ == #0C54
                disp #69A8
                include "../Station/DrawItem23.asm"
                ent
                assert $ == #0C64
                disp #69B8
                include "../Station/Unknown69B8.asm"
                ent
                assert $ == #0C7B
                disp #69CF
                include "../Station/Unknown69CF.asm"
                ent
                assert $ == #0C89
                disp #69DD
                include "../Station/HandleItem22.asm"
                ent
                assert $ == #0C8C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #69E0
                include "../Station/Unknown69E0.asm"
                ent
                assert $ == #0CF7
                assert $ == #0CF7
                disp #6A4B
                include "../Station/UpdateIndexListHover.asm"
                ent
                assert $ == #0D07
                disp #6A5B
                include "../Station/DrawItem22.asm"
                ent
                assert $ == #0D2A
                disp #6A7E
                include "../Station/Unknown6A7E.asm"
                ent
                assert $ == #0D2F
                disp #6A83
                include "../Station/HandleItem39.asm"
                ent
                assert $ == #0D32
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6A86
                include "../Station/Unknown6A86.asm"
                ent
                assert $ == #0D5A
                assert $ == #0D5A
                disp #6AAE
                include "../Station/Unknown6AAE.asm"
                ent
                assert $ == #0D5B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6AAF
                include "../Station/Unknown6AAF.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0D62
                assert $ == #0D62
                disp #6AB6
                include "../Station/DrawItem39.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0D72
                disp #6AC6
                include "../Station/Unknown6AC6.asm"
                ent
                assert $ == #0D8A
                disp #6ADE
                include "../Station/Unknown6ADE.asm"
                ent
                assert $ == #0D95
                disp #6AE9
                include "../Station/HandleItem41.asm"
                ent
                assert $ == #0D98
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6AEC
                include "../Station/Unknown6AEC.asm"
                ent
                assert $ == #0E3A
                assert $ == #0E3A
                disp #6B8E
                include "../Station/UpdateEnvironmentHover.asm"
                ent
                assert $ == #0E4A
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6B9E
                include "../Station/Unknown6B9E.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E51
                assert $ == #0E51
                disp #6BA5
                include "../Station/DrawItem41.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E6A
                disp #6BBE
                include "../Station/Unknown6BBE.asm"
                ent
                assert $ == #0EAC
                disp #6C00
                include "../Station/Unknown6C00.asm"
                ent
                assert $ == #0EB6
                disp #6C0A
                include "../Station/HandleItem11.asm"
                ent
                assert $ == #0EB9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6C0D
                include "../Station/HandleMapPanelEvent.asm"
                ent
                assert $ == #0F1A
                disp #6C6E
                include "../Station/PanMapView.asm"
                ent
                assert $ == #0FB9
                disp #6D0D
                include "../Station/SelectMapPointAndRefresh.asm"
                ent
                assert $ == #0FEF
                assert $ == #0FEF
                assert $ == #0FEF
                disp #6D43
                include "../Station/Unknown6D43.asm"
                ent
                assert $ == #0FF0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6D44
                include "../Station/RefreshMapPanel.asm"
                ent
                assert $ == #0FFA
                disp #6D4E
                include "../Station/ClearAndDrawMapPanel.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1004
                assert $ == #1004
                disp #6D58
                include "../Station/DrawMapPanelContents.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1054
                disp #6DA8
                include "../Station/DrawMapPanel.asm"
                ent
                assert $ == #106E
                disp #6DC2
                include "../Station/HandleDecodedMessageHover.asm"
                ent
                assert $ == #1071
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6DC5
                include "../Station/HandleDecodedMessageClick.asm"
                ent
                assert $ == #107F
                assert $ == #107F
                disp #6DD3
                include "../Station/ReturnDecodedMessageHover.asm"
                ent
                assert $ == #1080
                disp #6DD4
                include "../Station/DrawDecodedMessagePanel.asm"
                ent
                assert $ == #10BD
                ; исходные байты 6E11..6E75, исполнение загрузчика после переноса в 4000
                disp #4000
                include "../StationFinalExit/LoadFinal.asm"
                ent
                assert $ == #1119
                disp #405C
                include "../StationFinalExit/Data/FinalFileName.asm"
                ent
                assert $ == #1122
                disp #6E76
                include "../Station/PrintDecodedMessage.asm"
                ent
                assert $ == #112B
                disp #6E7F
                include "../Station/HandleQueuedMessageHover.asm"
                ent
                assert $ == #112E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6E82
                include "../Station/HandleQueuedMessageClick.asm"
                ent
                assert $ == #1135
                assert $ == #1135
                disp #6E89
                include "../Station/ReturnQueuedMessageHover.asm"
                ent
                assert $ == #1136
                disp #6E8A
                include "../Station/DrawQueuedMessagePanel.asm"
                ent
                assert $ == #1145
                disp #6E99
                include "../Station/HandleItem31.asm"
                ent
                assert $ == #1148
                ; исходное тело нажатия миссии, семантический разбор продолжается
                disp #6E9C
                include "../Station/ProcessMissionAction.asm"
                ent
                assert $ == #11EE
                disp #6F42
                include "../Station/Data/MissionTonnageMessage.asm"
                ent
                assert $ == #11F9
                disp #6F4D
                include "../Station/UpdateMissionRowHover.asm"
                ent
                assert $ == #1209
                ; исходное тело нажатия миссии, семантический разбор продолжается
                disp #6F5D
                include "../Station/CancelMission.asm"
                ent
                assert $ == #1261
                disp #6FB5
                include "../Station/Data/MissionCancelMessage.asm"
                ent
                assert $ == #1271
                disp #6FC5
                include "../Station/DrawItem31.asm"
                ent
                assert $ == #129A
                disp #6FEE
                include "../Station/HandleTradePanelHover.asm"
                ent
                assert $ == #129D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #6FF1
                include "../Station/HandleTradePanelClick.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #12F0
                assert $ == #12F0
                disp #7044
                include "../Station/RunTradeEventAndRedraw.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #130D
                disp #7061
                include "../Station/UpdateTradeRowHover.asm"
                ent
                assert $ == #131D
                assert $ == #131D
                disp #7071
                include "../Station/DrawTradePanel.asm"
                ent
                assert $ == #1342
                disp #7096
                include "../Station/DrawTradeNumericColumns.asm"
                ent
                assert $ == #1400
                disp #7154
                include "../Station/SetMarketTextColumns.asm"
                ent
                assert $ == #141E
                disp #7172
                include "../Station/HandleItem38.asm"
                ent
                assert $ == #1421
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7175
                include "../Station/Unknown7175.asm"
                ent
                assert $ == #14BC
                assert $ == #14BC
                disp #7210
                include "../Station/UpdateEquipmentHover.asm"
                ent
                assert $ == #14CC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7220
                include "../Station/Unknown7220.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #14D3
                assert $ == #14D3
                disp #7227
                include "../Station/DrawItem38.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #14F8
                disp #724C
                include "../Station/Unknown724C.asm"
                ent
                assert $ == #15EB
                disp #733F
                include "../Station/Unknown733F.asm"
                ent
                assert $ == #160B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified030.bin"
                assert $ == #16CA
                disp #741E
                include "../Station/HandleItem43.asm"
                ent
                assert $ == #16CD
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7421
                include "../Station/Unknown7421.asm"
                ent
                assert $ == #172E
                assert $ == #172E
                disp #7482
                include "../Station/UpdateToPositionHover.asm"
                ent
                assert $ == #173E
                disp #7492
                include "../Station/DrawItem43.asm"
                ent
                assert $ == #1753
                disp #74A7
                include "../Station/HandleItem44.asm"
                ent
                assert $ == #1756
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #74AA
                include "../Station/Unknown74AA.asm"
                ent
                assert $ == #17B7
                assert $ == #17B7
                disp #750B
                include "../Station/UpdateFromPositionHover.asm"
                ent
                assert $ == #17C7
                disp #751B
                include "../Station/DrawItem44.asm"
                ent
                assert $ == #17DC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified033.bin"
                assert $ == #17E5
                disp #7539
                include "../Station/HandleItem40.asm"
                ent
                assert $ == #17E8
                disp #753C
                include "../Station/ActivateContextMenu.asm"
                ent
                assert $ == #181F
                disp #7573
                include "../Station/HoverContextMenu.asm"
                ent
                assert $ == #182F
                disp #7583
                include "../Station/DrawItem40.asm"
                ent
                assert $ == #1845
                disp #7599
                include "../Station/HandleItem42.asm"
                ent
                assert $ == #1848
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #759C
                include "../Station/Unknown759C.asm"
                ent
                assert $ == #18CC
                assert $ == #18CC
                disp #7620
                include "../Station/UpdateGameSettingsHover.asm"
                ent
                assert $ == #18DC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7630
                include "../Station/Unknown7630.asm"                            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #18E3
                assert $ == #18E3
                disp #7637
                include "../Station/DrawItem42.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #18FC
                disp #7650
                include "../Station/Unknown7650.asm"
                ent
                assert $ == #1918
                disp #766C
                include "../Station/Unknown766C.asm"
                ent
                assert $ == #1922
                disp #7676
                include "../Station/HandleItem19.asm"
                ent
                assert $ == #1925
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7679
                include "../Station/Unknown7679.asm"
                ent
                assert $ == #1933
                assert $ == #1933
                disp #7687
                include "../Station/Unknown7687.asm"
                ent
                assert $ == #1934
                disp #7688
                include "../Station/TryDrawSystemInfo.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #193B
                disp #768F
                include "../Station/DrawSystemInfoPanel.asm"                    ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1AE4
                disp #7838
                include "../Station/HandleItem20.asm"
                ent
                assert $ == #1AE7
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #783B
                include "../Station/Unknown783B.asm"
                ent
                assert $ == #1B30
                assert $ == #1B30
                disp #7884
                include "../Station/Unknown7884.asm"
                ent
                assert $ == #1B31
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #7885
                include "../Station/TryDrawVariantPanel.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1B38
                assert $ == #1B38
                disp #788C
                include "../Station/DrawVariantPanel.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1B69
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #78BD
                include "../Station/RefreshVariantPanel.asm"
                ent
                assert $ == #1B82
                disp #78D6
                include "../Station/UpdateVariantPanel.asm"
                ent
                assert $ == #1BF4
                assert $ == #1BF4
                disp #7948
                include "../Station/HandleItem45.asm"
                ent
                assert $ == #1BF7
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #794B
                include "../Station/Unknown794B.asm"
                ent
                assert $ == #1C00
                assert $ == #1C00
                disp #7954
                include "../Station/Unknown7954.asm"
                ent
                assert $ == #1C01
                disp #7955
                include "../Station/DrawItem45.asm"
                ent
                assert $ == #1C69
                disp #79BD
                include "../Station/HandleItem30.asm"
                ent
                assert $ == #1C73
                disp #79C7
                include "../Station/Unknown79C7.asm"
                ent
                assert $ == #1CC1
                disp #7A15
                include "../Station/DrawItem30.asm"
                ent
                assert $ == #1CC7
                disp #7A1B
                include "../Station/HandleItem28.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1CD0
                disp #7A24
                include "../Station/Unknown7A24.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1D01
                disp #7A55
                include "../Station/DrawItem28.asm"
                ent
                assert $ == #1D07
                disp #7A5B
                include "../Station/HandleItem29.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1D10
                disp #7A64
                include "../Station/Unknown7A64.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1D2E
                disp #7A82
                include "../Station/DrawItem29.asm"
                ent
                assert $ == #1D34
                disp #7A88
                include "../Station/HandleItem09.asm"
                ent
                assert $ == #1D3E
                disp #7A92
                include "../Station/Unknown7A92.asm"
                ent
                assert $ == #1D4A
                disp #7A9E
                include "../Station/DrawItem09.asm"
                ent
                assert $ == #1D50
                disp #7AA4
                include "../Station/HandleItem02.asm"
                ent
                assert $ == #1D5A
                disp #7AAE
                include "../Station/Unknown7AAE.asm"
                ent
                assert $ == #1D60
                disp #7AB4
                include "../Station/DrawItem02.asm"
                ent
                assert $ == #1D66
                disp #7ABA
                include "../Station/HandleItem03.asm"
                ent
                assert $ == #1D70
                disp #7AC4
                include "../Station/Unknown7AC4.asm"
                ent
                assert $ == #1DB7
                disp #7B0B
                include "../Station/DrawItem03.asm"
                ent
                assert $ == #1DBD
                disp #7B11
                include "../Station/HandleItem37.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1DC6
                disp #7B1A
                include "../Station/Unknown7B1A.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1DD1
                disp #7B25
                include "../Station/DrawItem37.asm"
                ent
                assert $ == #1DD7
                disp #7B2B
                include "../Station/HandleItem36.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1DE0
                disp #7B34
                include "../Station/Unknown7B34.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1DEC
                disp #7B40
                include "../Station/DrawItem36.asm"
                ent
                assert $ == #1DF2
                disp #7B46
                include "../Station/HandleItem21.asm"
                ent
                assert $ == #1DFC
                disp #7B50
                include "../Station/Unknown7B50.asm"
                ent
                assert $ == #1DFD
                disp #7B51
                include "../Station/DrawItem21.asm"
                ent
                assert $ == #1E03
                disp #7B57
                include "../Station/HandleStoredPointToggle.asm"
                ent
                assert $ == #1E0D
                disp #7B61
                include "../Station/ToggleStoredMapPoint.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1E47
                disp #7B9B
                include "../Station/RefreshStoredMapPanels.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1E54
                assert $ == #1E54
                disp #7BA8
                include "../Station/DrawStoredPointToggle.asm"
                ent
                assert $ == #1E5A
                disp #7BAE
                include "../Station/RemoveFoundStoredPoint.asm"
                ent
                assert $ == #1E62
                assert $ == #1E62
                disp #7BB6
                include "../Station/HandleSecondaryPointToggle.asm"
                ent
                assert $ == #1E6C
                disp #7BC0
                include "../Station/ToggleSecondaryMapPoint.asm"
                ent
                assert $ == #1ECA
                disp #7C1E
                include "../Station/DrawSecondaryPointToggle.asm"
                ent
                assert $ == #1ED0
                disp #7C24
                include "../Station/RemoveFoundSecondaryPoint.asm"              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1EF6
                disp #7C4A
                include "../Station/RefreshSecondaryListPanels.asm"             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1F06
                assert $ == #1F06
                disp #7C5A
                include "../Station/HandleSecondaryClear.asm"
                ent
                assert $ == #1F10
                disp #7C64
                include "../Station/ClearSecondaryMapPoints.asm"
                ent
                assert $ == #1F2A
                disp #7C7E
                include "../Station/DrawItem14.asm"
                ent
                assert $ == #1F30
                disp #7C84
                include "../Station/HandleStoredPointCycle.asm"
                ent
                assert $ == #1F3A
                disp #7C8E
                include "../Station/CycleStoredMapPoint.asm"
                ent
                assert $ == #1F62
                disp #7CB6
                include "../Station/DrawItem15.asm"
                ent
                assert $ == #1F68
                disp #7CBC
                include "../Station/HandleItem18.asm"
                ent
                assert $ == #1F72
                disp #7CC6
                include "../Station/Unknown7CC6.asm"
                ent
                assert $ == #1FA4
                disp #7CF8
                include "../Station/DrawItem18.asm"
                ent
                assert $ == #1FAA
                disp #7CFE
                include "../Station/HandleCurrentMapCenter.asm"
                ent
                assert $ == #1FB4
                disp #7D08
                include "../Station/CenterCurrentMapPoint.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1FC0
                disp #7D14
                include "../Station/CenterKeyAndRefreshMap.asm"                 ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1FD0
                assert $ == #1FD0
                disp #7D24
                include "../Station/DrawItem17.asm"
                ent
                assert $ == #1FD6
                disp #7D2A
                include "../Station/HandleSecondaryCursor.asm"
                ent
                assert $ == #1FE0
                disp #7D34
                include "../Station/SelectSecondaryListCursor.asm"
                ent
                assert $ == #1FFF
                disp #7D53
                include "../Station/DrawItem16.asm"
                ent
                assert $ == #2005
                disp #7D59
                include "../Station/HandleSellControl.asm"
                ent
                assert $ == #200F
                disp #7D63
                include "../Station/SellCurrentCargo.asm"
                ent
                assert $ == #2023
                disp #7D77
                include "../Station/DrawSellControl.asm"
                ent
                assert $ == #2029
                disp #7D7D
                include "../Station/HandleContractsControl.asm"
                ent
                assert $ == #2033
                disp #7D87
                include "../Station/OpenContractPanels.asm"
                ent
                assert $ == #2045
                disp #7D99
                include "../Station/DrawItem04.asm"
                ent
                assert $ == #204B
                disp #7D9F
                include "../Station/HandleTradeControl.asm"
                ent
                assert $ == #2055
                disp #7DA9
                include "../Station/OpenTradePanels.asm"
                ent
                assert $ == #2061
                disp #7DB5
                include "../Station/DrawItem05.asm"
                ent
                assert $ == #2067
                disp #7DBB
                include "../Station/HandleEquipmentControl.asm"
                ent
                assert $ == #2071
                disp #7DC5
                include "../Station/OpenEquipmentPanels.asm"
                ent
                assert $ == #208D
                disp #7DE1
                include "../Station/DrawItem06.asm"
                ent
                assert $ == #2093
                disp #7DE7
                include "../Station/HandleShipControl.asm"
                ent
                assert $ == #209D
                disp #7DF1
                include "../Station/OpenShipPanels.asm"
                ent
                assert $ == #20C5
                disp #7E19
                include "../Station/DrawShipControl.asm"
                ent
                assert $ == #20CB
                disp #7E1F
                include "../Station/ResetShipPanelSelection.asm"
                ent
                assert $ == #20FF
                disp #7E53
                include "../Station/HandleItem08.asm"
                ent
                assert $ == #216C
                ; исходный переход исполняется после переноса 7EC0 в 4200
                disp #4200
                include "../StationExit/LoadAction.asm"
                ent
                assert $ == #21B4
                disp #4248
                include "../StationExit/Data/ActionFileName.asm"
                ent
                assert $ == #21BD
                disp #7F11
                include "../Station/DrawItem08.asm"
                ent
                assert $ == #21C3
                disp #7F17
                include "../Station/HandleItem00.asm"
                ent
                assert $ == #21DC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified043.bin"
                assert $ == #21DF
                disp #7F33
                include "../Station/Unknown7F33.asm"
                ent
                assert $ == #21E1
                disp #7F35
                include "../Station/DrawItem00.asm"
                ent
                assert $ == #2238
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified044.bin"
                assert $ == #2900
                ; исходный ресурс FONT_WIDTHS_256
                incbin "../Station/Resources/FontWidths.bin"
                assert $ == #2A00
                ; исходный ресурс FONT_256_GLYPHS_8_ROWS
                incbin "../Station/Resources/FontGlyphs.bin"
                assert $ == #3200
                ; Unknown, исходные байты после шрифта
                disp #9200
                include "../Station/Data/GlyphRoutes.asm"
                ent
                assert $ == #3400
                ; Unknown, исходные байты вне подтверждённых записей рынка
                incbin "../Resources/04_STATIONF/BeforeModelAvailability.bin"
                assert $ == #34BC
                disp #94BC
                include "../Station/Data/ModelAvailability.asm"
                ent
                assert $ == #34DC
                assert $ == #34DC
                disp #94DC
                include "../Station/Data/MarketCategories.asm"
                ent
                assert $ == #34F7
                ; Unknown, исходные байты вне подтверждённых записей рынка
                incbin "../Resources/04_STATIONF/BeforeMarketRules.bin"
                assert $ == #3518
                disp #9518
                include "../Station/Data/MarketRules.asm"
                ent
                assert $ == #3554
                ; Unknown, исходные байты вне подтверждённых записей рынка
                incbin "../Resources/04_STATIONF/BeforeMarketRows.bin"
                assert $ == #3555
                disp #9555
                include "../Station/Data/MarketRows.asm"
                ent
                assert $ == #3592
                ; Unknown, исходные байты вне подтверждённых записей рынка
                incbin "../Resources/04_STATIONF/AfterMarketRows.bin"
                assert $ == #36AA
                disp #96AA
                include "../Station/Data/KeyboardCodes.asm"
                ent
                assert $ == #3728
                disp #9728
                include "../Station/Data/SettingsText.asm"
                ent
                assert $ == #3762
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified044TailAfterKeyCodesAfterSettings.bin"
                assert $ == #383B
                disp #983B
                include "../Station/Data/StationTimer.asm"
                ent
                assert $ == #383F
                disp #983F
                include "../Station/Data/CurrentSignature.asm"
                ent
                assert $ == #3844
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified044TailAfterIrqGraphics.bin"
                assert $ == #38B0
                disp #98B0
                include "../Station/Data/MissionOffer.asm"
                ent
                assert $ == #38C0
                ; Unknown, исходные данные после состояния предложения
                incbin "../Resources/04_STATIONF/BeforeStoredMapPoints.bin"
                assert $ == #390A
                disp #990A
                include "../Station/Data/StoredMapPoints.asm"
                ent
                assert $ == #3970
                ; оставшиеся байты состояния после двух списков, их назначение ещё разбирается
                disp #9970
                include "../Station/Data/StoredMapOrder.asm"
                ent
                assert $ == #397B
                ; оставшиеся данные после массива порядка, семантический разбор продолжается
                disp #997B
                include "../Station/Data/MapAuxiliaryPoints.asm"
                ent
                assert $ == #39A3
                disp #99A3
                include "../Station/Data/MapAuxiliaryCodes.asm"
                ent
                assert $ == #39AE
                assert $ == #39AE
                disp #99AE
                include "../Station/Data/InterfaceChoices.asm"
                ent
                assert $ == #39B6
                disp #99B6
                include "../Station/Data/PointerKeys.asm"
                ent
                assert $ == #39C2
                disp #99C2
                include "../Station/Data/InterfaceColors.asm"
                ent
                assert $ == #39C8
                disp #99C8
                include "../Station/Data/ControlOptions.asm"
                ent
                assert $ == #3A1E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified044TailAfterKeysAfterSettings.bin"
                assert $ == #3A58
                disp #9A58
                include "../Station/EmptyCallback.asm"
                ent
                assert $ == #3A59
                disp #9A59
                include "../Station/MainLoop.asm"
                ent
                assert $ == #3AEA
                disp #9AEA
                include "../Station/Interrupt.asm"
                ent
                assert $ == #3C13
                disp #9C13
                include "../Station/Data/InterruptStack.asm"
                ent
                assert $ == #3C43
                disp #9C43
                include "../Station/MergeActionInputs.asm"
                ent
                assert $ == #3C59
                disp #9C59
                include "../Station/DisableDrawList.asm"
                ent
                assert $ == #3C68
                disp #9C68
                include "../Station/EnableDrawList.asm"
                ent
                assert $ == #3C77
                disp #9C77
                include "../Station/RebuildInterface.asm"
                ent
                assert $ == #3D25
                disp #9D25
                include "../Station/RestoreBackground.asm"
                ent
                assert $ == #3D96
                disp #9D96
                include "../Station/GetPointerOwner.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3DA6
                disp #9DA6
                include "../Station/GetCellOwner.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3DBA
                disp #9DBA
                include "../Station/DispatchInterfaceEvent.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3E1F
                disp #9E1F
                include "../Station/RemoveOtherPopups.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3E4E
                disp #9E4E
                include "../Station/PrepareContextMenu.asm"
                ent
                assert $ == #3E77
                disp #9E77
                include "../Station/CloseActiveItem.asm"
                ent
                assert $ == #3E97
                disp #9E97
                include "../Station/GetItemFrameBit.asm"
                ent
                assert $ == #3EA5
                disp #9EA5
                include "../Station/ToggleItemFrame.asm"
                ent
                assert $ == #3EC4
                disp #9EC4
                include "../Station/ClearWorkspace.asm"
                ent
                assert $ == #3ED7
                disp #9ED7
                include "../Station/ResetIndexTable.asm"
                ent
                assert $ == #3EEB
                disp #9EEB
                include "../Station/GetItemFlags.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3EED
                disp #9EED
                include "../Station/GetItemField.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #3EFF
                disp #9EFF
                include "../Station/UnpackResource.asm"
                ent
                assert $ == #4014
                disp #A014
                include "../Station/UnknownA014.asm"
                ent
                assert $ == #4020
                disp #A020
                include "../Station/CopyWindowIcon.asm"
                ent
                assert $ == #405B
                disp #A05B
                include "../Station/FillWindowBody.asm"
                ent
                assert $ == #40C4
                disp #A0C4
                include "../Station/FillBodyRow.asm"
                ent
                assert $ == #4102
                disp #A102
                include "../Station/Data/WindowFillChain.asm"
                ent
                assert $ == #4116
                disp #A116
                include "../Station/ReadMatrixKey.asm"
                ent
                assert $ == #414A
                disp #A14A
                include "../Station/LookupMatrixKey.asm"
                ent
                assert $ == #4163
                disp #A163
                include "../Station/FormatSettingsLabel.asm"
                ent
                assert $ == #4191
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #A191
                include "../Station/ParseSettingsLabel.asm"
                ent
                assert $ == #41CD
                disp #A1CD
                include "../Station/RestoreScrollPointer.asm"
                ent
                assert $ == #41D6
                assert $ == #41D6
                disp #A1D6
                include "../Station/ScrollWindowRows.asm"
                ent
                assert $ == #426F
                disp #A26F
                include "../Station/XorRowIfSelected.asm"
                ent
                assert $ == #4280
                assert $ == #4280
                disp #A280
                include "../Station/GetRowHitData.asm"
                ent
                assert $ == #428F
                disp #A28F
                include "../Station/ClampRowHeight.asm"
                ent
                assert $ == #42A4
                disp #A2A4
                include "../Station/GetPointerRow.asm"
                ent
                assert $ == #42B4
                disp #A2B4
                include "../Station/XorPointerRow.asm"
                ent
                assert $ == #42BB
                disp #A2BB
                include "../Station/XorItemRow.asm"
                ent
                assert $ == #4311
                disp #A311
                include "../Station/UpdateRowHover.asm"
                ent
                assert $ == #4341
                disp #A341
                include "../Station/UpdatePixelHover.asm"
                ent
                assert $ == #436E
                disp #A36E
                include "../Station/PrintAfterCR.asm"
                ent
                assert $ == #4374
                disp #A374
                include "../Station/JustifyAfterLF.asm"
                ent
                assert $ == #437A
                disp #A37A
                include "../Station/PrintAfterLF.asm"
                ent
                assert $ == #4380
                disp #A380
                include "../Station/SkipCrRecords.asm"
                ent
                assert $ == #4390
                disp #A390
                include "../Station/SkipLfRecords.asm"
                ent
                assert $ == #43A1
                disp #A3A1
                include "../Station/PrintSystemTraits.asm"
                ent
                assert $ == #43FF
                disp #A3FF
                include "../Station/SaveTextWindow.asm"
                ent
                assert $ == #4436
                disp #A436
                include "../Station/RestoreTextWindow.asm"
                ent
                assert $ == #4464
                disp #A464
                include "../Station/DescribeCurrentKey.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #446E
                disp #A46E
                include "../Station/DescribeKeyBanked.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #4480
                disp #A480
                include "../Station/DescribeCurrentKeyForLang.asm"
                ent
                assert $ == #448B
                disp #A48B
                include "../Station/DescribeKeyForLang.asm"
                ent
                assert $ == #4496
                disp #A496
                include "../Station/EndScreenUpdate.asm"
                ent
                assert $ == #449F
                disp #A49F
                include "../Station/BeginScreenUpdate.asm"
                ent
                assert $ == #46C4
                disp #A6C4
                include "../Station/CheckItemRect.asm"
                ent
                assert $ == #46EA
                disp #A6EA
                include "../Station/HandleItem01.asm"
                ent
                assert $ == #46EE
                disp #A6EE
                include "../Station/DrawItem01.asm"
                ent
                assert $ == #4770
                disp #A770
                include "../Station/HideAllItems.asm"
                ent
                assert $ == #4781
                disp #A781
                include "../Station/CloseAllItems.asm"
                ent
                assert $ == #47B7
                disp #A7B7
                include "../Station/RememberItemBounds.asm"
                ent
                assert $ == #47E0
                disp #A7E0
                include "../Station/ArrangeAllItems.asm"
                ent
                assert $ == #47E3
                disp #A7E3
                include "../Station/OpenEnvOptions.asm"
                ent
                assert $ == #47E9
                disp #A7E9
                include "../Station/OpenGameOptions.asm"
                ent
                assert $ == #47EF
                disp #A7EF
                include "../Station/OpenRestoreDialog.asm"
                ent
                assert $ == #47F5
                disp #A7F5
                include "../Station/GetSelectedVariantCount.asm"
                ent
                assert $ == #4806
                disp #A806
                include "../Station/SwitchItemContour.asm"
                ent
                assert $ == #482D
                disp #A82D
                include "../Station/CountTextRows.asm"
                ent
                assert $ == #4843
                disp #A843
                include "../Station/PrintFromRow.asm"
                ent
                assert $ == #485F
                disp #A85F
                include "../Station/QueueTextRow.asm"
                ent
                assert $ == #486B
                disp #A86B
                include "../Station/QueueTextRowForLang.asm"
                ent
                assert $ == #487B
                disp #A87B
                include "../Station/NextRandom1.asm"
                ent
                assert $ == #4882
                disp #A882
                include "../Station/NextRandom0.asm"
                ent
                assert $ == #4889
                disp #A889
                include "../Station/NextRandom4.asm"
                ent
                assert $ == #4890
                disp #A890
                include "../Station/NextRandom5.asm"
                ent
                assert $ == #4897
                disp #A897
                include "../Station/NextRandom6.asm"
                ent
                assert $ == #489E
                disp #A89E
                include "../Station/NextRandom2.asm"
                ent
                assert $ == #48A5
                disp #A8A5
                include "../Station/NextRandom3.asm"
                ent
                assert $ == #48AC
                disp #A8AC
                include "../Station/Data/RandomStates.asm"
                ent
                assert $ == #48C1
                disp #A8C1
                include "../Station/StepRandomState.asm"
                ent
                assert $ == #490D
                disp #A90D
                include "../Station/ClearMarketRows.asm"
                ent
                assert $ == #491B
                disp #A91B
                include "../Station/GenerateMarket.asm"
                ent
                assert $ == #49F3
                disp #A9F3
                include "../Station/StepSignatureKey.asm"
                ent
                assert $ == #4A1D
                disp #AA1D
                include "../Station/SumBank4Index.asm"
                ent
                assert $ == #4A33
                disp #AA33
                include "../Station/HandleItem33.asm"
                ent
                assert $ == #4A3D
                disp #AA3D
                include "../Station/UnknownAA3D.asm"
                ent
                assert $ == #4A4F
                disp #AA4F
                include "../Station/DrawItem33.asm"
                ent
                assert $ == #4A55
                disp #AA55
                include "../Station/HandleItem32.asm"
                ent
                assert $ == #4A58
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #AA58
                include "../Station/UnknownAA58.asm"
                ent
                assert $ == #4A82
                ; Unknown, сохранённые байты вне новых доказанных входов
                incbin "../Resources/04_STATIONF/EventGap4A82.bin"
                assert $ == #4A84
                assert $ == #4A84
                disp #AA84
                include "../Station/UnknownAA84.asm"
                ent
                assert $ == #4A85
                disp #AA85
                include "../Station/DrawItem32.asm"
                ent
                assert $ == #4B66
                ; семь исходных потоков условий и результата миссии
                disp #AB66
                include "../Station/Data/MissionTexts.asm"
                ent
                assert $ == #4C14
                disp #AC14
                include "../Station/GenerateMissionOffer.asm"
                ent
                assert $ == #4C74
                disp #AC74
                include "../Station/PrintPlayerRank.asm"
                ent
                assert $ == #4CE3
                ; строки, физические пороги и подпись рангов
                disp #ACE3
                include "../Station/Data/PlayerRanks.asm"
                ent
                assert $ == #4D35
                disp #AD35
                include "../Station/SkipJustifyRow.asm"
                ent
                assert $ == #4DA7
                disp #ADA7
                include "../Station/PrintTextWord.asm"
                ent
                assert $ == #4DCD
                disp #ADCD
                include "../Station/PrintJustified.asm"
                ent
                assert $ == #4E2A
                disp #AE2A
                include "../Station/PrintWrapWord.asm"
                ent
                assert $ == #4E55
                disp #AE55
                include "../Station/AdvanceTextRow.asm"
                ent
                assert $ == #4E6B
                disp #AE6B
                include "../Station/GlyphHeightError.asm"
                ent
                assert $ == #4E71
                disp #AE71
                include "../Station/GlyphWidthError.asm"
                ent
                assert $ == #4E77
                disp #AE77
                include "../Station/GlyphOriginXError.asm"
                ent
                assert $ == #4E7F
                disp #AE7F
                include "../Station/GlyphOriginYError.asm"
                ent
                assert $ == #4E88
                disp #AE88
                include "../Station/GlyphBottomError.asm"
                ent
                assert $ == #4E8D
                disp #AE8D
                include "../Station/DrawGlyph.asm"
                ent
                assert $ == #4F0C
                disp #AF0C
                include "../Station/DrawGlyphShift0.asm"
                ent
                assert $ == #4F36
                disp #AF36
                include "../Station/SplitGlyphShift0.asm"
                ent
                assert $ == #4F67
                disp #AF67
                include "../Station/DrawGlyphShift1.asm"
                ent
                assert $ == #4FE0
                disp #AFE0
                include "../Station/SplitGlyphShift1.asm"
                ent
                assert $ == #5057
                disp #B057
                include "../Station/DrawGlyphEdge1.asm"
                ent
                assert $ == #5089
                disp #B089
                include "../Station/SplitGlyphEdge1.asm"
                ent
                assert $ == #50C1
                disp #B0C1
                include "../Station/DrawGlyphShift2.asm"
                ent
                assert $ == #5152
                disp #B152
                include "../Station/SplitGlyphShift2.asm"
                ent
                assert $ == #51DE
                disp #B1DE
                include "../Station/DrawGlyphEdge2.asm"
                ent
                assert $ == #5220
                disp #B220
                include "../Station/SplitGlyphEdge2.asm"
                ent
                assert $ == #5266
                disp #B266
                include "../Station/DrawGlyphShift3.asm"
                ent
                assert $ == #530F
                disp #B30F
                include "../Station/SplitGlyphShift3.asm"
                ent
                assert $ == #53B0
                disp #B3B0
                include "../Station/DrawGlyphEdge3.asm"
                ent
                assert $ == #5402
                disp #B402
                include "../Station/SplitGlyphEdge3.asm"
                ent
                assert $ == #5456
                disp #B456
                include "../Station/DrawGlyphShift4.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5514
                disp #B514
                include "../Station/ReturnGlyph.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5521
                disp #B521
                include "../Station/SplitGlyphShift4.asm"
                ent
                assert $ == #55D7
                disp #B5D7
                include "../Station/DrawGlyphEdge4.asm"
                ent
                assert $ == #5631
                disp #B631
                include "../Station/SplitGlyphEdge4.asm"
                ent
                assert $ == #568C
                disp #B68C
                include "../Station/DrawGlyphShift5.asm"
                ent
                assert $ == #5735
                disp #B735
                include "../Station/SplitGlyphShift5.asm"
                ent
                assert $ == #57D6
                disp #B7D6
                include "../Station/DrawGlyphEdge5.asm"
                ent
                assert $ == #5828
                disp #B828
                include "../Station/SplitGlyphEdge5.asm"
                ent
                assert $ == #587C
                disp #B87C
                include "../Station/DrawGlyphShift6.asm"
                ent
                assert $ == #590D
                disp #B90D
                include "../Station/SplitGlyphShift6.asm"
                ent
                assert $ == #5999
                disp #B999
                include "../Station/DrawGlyphEdge6.asm"
                ent
                assert $ == #59E3
                disp #B9E3
                include "../Station/SplitGlyphEdge6.asm"
                ent
                assert $ == #5A30
                disp #BA30
                include "../Station/DrawGlyphShift7.asm"
                ent
                assert $ == #5AA9
                disp #BAA9
                include "../Station/SplitGlyphShift7.asm"
                ent
                assert $ == #5B20
                disp #BB20
                include "../Station/DrawGlyphEdge7.asm"
                ent
                assert $ == #5B62
                disp #BB62
                include "../Station/SplitGlyphEdge7.asm"
                ent
                assert $ == #5BA8
                disp #BBA8
                include "../Station/PrintMin4.asm"
                ent
                assert $ == #5BBE
                disp #BBBE
                include "../Station/PrintMin2.asm"
                ent
                assert $ == #5BD7
                disp #BBD7
                include "../Station/PrintMin3.asm"
                ent
                assert $ == #5C01
                disp #BC01
                include "../Station/PrintWord.asm"
                ent
                assert $ == #5CAB
                disp #BCAB
                include "../Station/Print4DigitCore.asm"
                ent
                assert $ == #5D01
                disp #BD01
                include "../Station/RecoverTextX.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5D08
                disp #BD08
                include "../Station/PrintText.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5DA6
                disp #BDA6
                include "../Station/MeasureTextRun.asm"
                ent
                assert $ == #5DCA
                disp #BDCA
                include "../Station/MeasureTextRunSaved.asm"
                ent
                assert $ == #5DF0
                disp #BDF0
                include "../Station/UnknownBDF0.asm"
                ent
                assert $ == #5E1B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                ; Unknown, сохранённые байты вне новых доказанных входов
                incbin "../Resources/04_STATIONF/EventGap5E1B.bin"
                assert $ == #5E27
                disp #BE27
                include "../Station/MoveItemToTailIfListed.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5E38
                assert $ == #5E38
                disp #BE38
                include "../Station/MoveItemToTail.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #5E91
                disp #BE91
                include "../Station/InvalidateItemIndex.asm"
                ent
                assert $ == #5EAE
                disp #BEAE
                include "../Station/RegisterItemCells.asm"
                ent
                assert $ == #5F4E
                disp #BF4E
                include "../Station/PrepareFrameRaster.asm"
                ent
                assert $ == #5FAD
                disp #BFAD
                include "../Station/RegisterAndFillItem.asm"
                ent
                assert $ == #5FF5
                disp #BFF5
                include "../Station/FillItemBitmap.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6000
                disp #C000
                include "../Station/FinishItemFill.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6039
                disp #C039
                include "../Station/SetupTextWindow.asm"
                ent
                assert $ == #6084
                disp #C084
                include "../Station/DrawBandSync.asm"
                ent
                assert $ == #6093
                disp #C093
                include "../Station/DrawBandFrame.asm"                          ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60C9
                disp #C0C9
                include "../Station/FinishBandFrame.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6165
                disp #C165
                include "../Station/AdvanceClipRow.asm"
                ent
                assert $ == #616F
                disp #C16F
                include "../Station/NextCharRow.asm"
                ent
                assert $ == #617B
                disp #C17B
                include "../Station/DrawSpanRow.asm"
                ent
                assert $ == #61C0
                disp #C1C0
                include "../Station/SetOutlinePattern.asm"
                ent
                assert $ == #61CF
                disp #C1CF
                include "../Station/SetCutoutPattern.asm"
                ent
                assert $ == #61DE
                disp #C1DE
                include "../Station/SetSixBitPattern.asm"
                ent
                assert $ == #61ED
                disp #C1ED
                include "../Station/ClearSpanPattern.asm"
                ent
                assert $ == #61F2
                disp #C1F2
                include "../Station/SetInsetPattern.asm"
                ent
                assert $ == #6201
                disp #C201
                include "../Station/SetDeepInset.asm"
                ent
                assert $ == #6210
                disp #C210
                include "../Station/SetInnerOutline.asm"
                ent
                assert $ == #621F
                disp #C21F
                include "../Station/FillSpanPattern.asm"
                ent
                assert $ == #6224
                disp #C224
                include "../Station/SetOutlineCopy.asm"
                ent
                assert $ == #6233
                disp #C233
                include "../Station/SetupInsetTextWindow.asm"
                ent
                assert $ == #6287
                disp #C287
                include "../Station/DrawCaptionItem.asm"
                ent
                assert $ == #62CB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified076.bin"
                assert $ == #62DF
                disp #C2DF
                include "../Station/DrawCenteredItem.asm"                       ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6325
                disp #C325
                include "../Station/CenterItemLine.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #634B
                disp #C34B
                include "../Station/SetupCenterText.asm"
                ent
                assert $ == #639E
                disp #C39E
                include "../Station/DrawFrameKeepHL.asm"
                ent
                assert $ == #63A4
                disp #C3A4
                include "../Station/DrawFrameType.asm"
                ent
                assert $ == #6436
                disp #C436
                include "../Station/DrawInsetFrame.asm"
                ent
                assert $ == #64BE
                disp #C4BE
                include "../Station/XorRectOutline.asm"
                ent
                assert $ == #6566
                disp #C566
                include "../Station/XorOutlineRow.asm"
                ent
                assert $ == #65F2
                disp #C5F2
                include "../Station/XorOutlineColumn.asm"
                ent
                assert $ == #6626
                disp #C626
                include "../Station/FillRectangle.asm"
                ent
                assert $ == #66B0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #C6B0
                include "../Station/ClearScrollWindowBody.asm"
                ent
                assert $ == #685E
                assert $ == #685E
                disp #C85E
                include "../Station/CloseMenuOnRow.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6873
                disp #C873
                include "../Station/DropItemDraw.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #687C
                disp #C87C
                include "../Station/TrackItemGeometry.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6A04
                disp #CA04
                include "../Station/FinishGeometry.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6A11
                disp #CA11
                include "../Station/MarkGeometry.asm"
                ent
                assert $ == #6A15
                disp #CA15
                include "../Station/CancelHitFrame.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6A17
                disp #CA17
                include "../Station/ReturnGeometry.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6A1F
                disp #CA1F
                include "../Station/ResizeGeometry.asm"
                ent
                assert $ == #6B1C
                disp #CB1C
                include "../Station/RemoveItemDraw.asm"
                ent
                assert $ == #6B52
                disp #CB52
                include "../Station/GetLastDraw.asm"
                ent
                assert $ == #6B64
                disp #CB64
                include "../Station/TestDrawPointer.asm"
                ent
                assert $ == #6B7F
                disp #CB7F
                include "../Station/RestoreAllBounds.asm"
                ent
                assert $ == #6BA9
                disp #CBA9
                include "../Station/RestoreItemBounds.asm"
                ent
                assert $ == #6BE0
                disp #CBE0
                include "../Station/RepaintAndTrack.asm"
                ent
                assert $ == #6BEB
                disp #CBEB
                include "../Station/RepaintAndFlag.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6BF2
                disp #CBF2
                include "../Station/RepaintItemCore.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6C21
                disp #CC21
                include "../Station/ActivateInterfaceCallback.asm"              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6C2C
                disp #CC2C
                include "../Station/FinishItemAction.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6C30
                disp #CC30
                include "../Station/ToggleItemBounds.asm"                       ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6C81
                disp #CC81
                include "../Station/ActivateItem.asm"
                ent
                assert $ == #6CAA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified084.bin"
                assert $ == #6CAF
                disp #CCAF
                include "../Station/SetBandFillMode.asm"
                ent
                assert $ == #6CD4
                disp #CCD4
                include "../Station/ResetBandMode.asm"
                ent
                assert $ == #6CF3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified085.bin"
                assert $ == #832E
                disp #E32E
                include "../Station/Data/ContextMenuText.asm"
                ent
                assert $ == #839A
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified085AfterPopupText.bin"
                assert $ == #90FD
                disp #F0FD
                include "../Station/Data/InterfaceItems.asm"
                ent
                assert $ == #93DE
                disp #F3DE
                include "../Station/Data/DrawList.asm"
                ent
                assert $ == #93F4
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/04_STATIONF/Unclassified086.bin"
                assert $ == #A000
