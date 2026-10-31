; -----------------------------------------
; запись 5, LANG.C
; логическая длина 3864, полный секторный размер 4096
; -----------------------------------------
                assert $ == #0000
                disp #C000
                include "../Text/RunMarketScript.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #000C
                disp #C00C
                include "../Text/NextCommand.asm"                               ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #001B
                disp #C01B
                include "../Text/SkipLine.asm"                                  ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0039
                disp #C039
                include "../Text/TestExpression.asm"
                ent
                assert $ == #0057
                disp #C057
                include "../Text/ApplyCondition.asm"
                ent
                assert $ == #0080
                disp #C080
                include "../Text/ApplyInverseCondition.asm"
                ent
                assert $ == #008D
                disp #C08D
                include "../Text/Command2C.asm"
                ent
                assert $ == #0090
                disp #C090
                include "../Text/ApplyAddFieldOperation.asm"
                ent
                assert $ == #009C
                disp #C09C
                include "../Text/ApplyRemoveFieldOperation.asm"
                ent
                assert $ == #009F
                disp #C09F
                include "../Text/AssignValue.asm"
                ent
                assert $ == #00D5
                disp #C0D5
                include "../Text/BeginBlock.asm"
                ent
                assert $ == #00D8
                disp #C0D8
                include "../Text/EndBlock.asm"
                ent
                assert $ == #00DB
                disp #C0DB
                include "../Text/RecomputeTonnage.asm"
                ent
                assert $ == #00E7
                disp #C0E7
                include "../Text/FinishScript.asm"
                ent
                assert $ == #00EC
                disp #C0EC
                include "../Text/QueueTextAndStopAtLine.asm"
                ent
                assert $ == #0100
                disp #C100
                include "../Text/QueueTextCommand.asm"
                ent
                assert $ == #0103
                disp #C103
                include "../Text/Command57.asm"
                ent
                assert $ == #010B
                disp #C10B
                include "../Text/Command23.asm"
                ent
                assert $ == #010E
                disp #C10E
                include "../Text/ActivateResourceRecord.asm"
                ent
                assert $ == #0177
                disp #C177
                include "../Text/WriteIndexedPMode.asm"
                ent
                assert $ == #0181
                disp #C181
                include "../Text/WriteIndexedVMode.asm"
                ent
                assert $ == #0189
                disp #C189
                include "../Text/WriteIndexedMMode.asm"
                ent
                assert $ == #0191
                disp #C191
                include "../Text/WriteIndexedEMode.asm"
                ent
                assert $ == #0199
                disp #C199
                include "../Text/SetPrimarySelection.asm"
                ent
                assert $ == #01A7
                disp #C1A7
                include "../Text/SetSecondarySelection.asm"
                ent
                assert $ == #01B5
                disp #C1B5
                include "../Text/ReadCredits.asm"                               ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #01B9
                disp #C1B9
                include "../Text/PushExpressionWord.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #01C2
                disp #C1C2
                include "../Text/ReadFieldLowero.asm"
                ent
                assert $ == #01C8
                disp #C1C8
                include "../Text/ReadEquipmentWeight.asm"
                ent
                assert $ == #01E6
                disp #C1E6
                include "../Text/ReadFieldLoweri.asm"
                ent
                assert $ == #01EC
                disp #C1EC
                include "../Text/ReadSecondWeight.asm"
                ent
                assert $ == #0201
                disp #C201
                include "../Text/ReadFieldLowerk.asm"
                ent
                assert $ == #0207
                disp #C207
                include "../Text/ReadSelectedPrimaryFields.asm"
                ent
                assert $ == #0221
                disp #C221
                include "../Text/ReadFieldLowerr.asm"
                ent
                assert $ == #0227
                disp #C227
                include "../Text/ReadSelectedSecondaryFields.asm"
                ent
                assert $ == #0241
                disp #C241
                include "../Text/ReadFieldLowerj.asm"
                ent
                assert $ == #024C
                disp #C24C
                include "../Text/ReadFieldUpperJ.asm"
                ent
                assert $ == #0252
                disp #C252
                include "../Text/PushTrue.asm"
                ent
                assert $ == #0257
                disp #C257
                include "../Text/PushFalse.asm"
                ent
                assert $ == #025B
                disp #C25B
                include "../Text/ReadEventCode.asm"
                ent
                assert $ == #0261
                disp #C261
                include "../Text/ReadFieldLoweru.asm"
                ent
                assert $ == #0267
                disp #C267
                include "../Text/ReadFieldUpperG.asm"
                ent
                assert $ == #026D
                disp #C26D
                include "../Text/ReadMarketField.asm"
                ent
                assert $ == #0289
                disp #C289
                include "../Text/ReadFieldUpperO.asm"
                ent
                assert $ == #028F
                disp #C28F
                include "../Text/CheckEquipmentThreshold.asm"
                ent
                assert $ == #02B5
                disp #C2B5
                include "../Text/ReadFieldUpperI.asm"
                ent
                assert $ == #02BB
                disp #C2BB
                include "../Text/CheckSecondEntryThreshold.asm"
                ent
                assert $ == #02D0
                disp #C2D0
                include "../Text/ReadFieldUpperK.asm"
                ent
                assert $ == #02D6
                disp #C2D6
                include "../Text/ReadBank4PrimaryFields.asm"
                ent
                assert $ == #02EA
                disp #C2EA
                include "../Text/ReadFieldUpperR.asm"
                ent
                assert $ == #02F0
                disp #C2F0
                include "../Text/ReadBank4SecondaryFields.asm"
                ent
                assert $ == #0304
                disp #C304
                include "../Text/ReadFieldLowerg.asm"
                ent
                assert $ == #030A
                disp #C30A
                include "../Text/ReadCargoField.asm"
                ent
                assert $ == #0323
                disp #C323
                include "../Text/ReadFieldCode1.asm"
                ent
                assert $ == #032C
                disp #C32C
                include "../Text/ReadFieldCode28.asm"
                ent
                assert $ == #0342
                disp #C342
                include "../Text/ReadFieldLowere.asm"
                ent
                assert $ == #034D
                disp #C34D
                include "../Text/ReadFieldLowerm.asm"
                ent
                assert $ == #0355
                disp #C355
                include "../Text/ReadFieldLowert.asm"
                ent
                assert $ == #0362
                disp #C362
                include "../Text/ReadFieldLowerp.asm"
                ent
                assert $ == #037D
                disp #C37D
                include "../Text/ReadFieldUpperL.asm"
                ent
                assert $ == #0383
                disp #C383
                include "../Text/ReadCurrentKeyParams.asm"
                ent
                assert $ == #0393
                disp #C393
                include "../Text/ReadFieldLowerl.asm"
                ent
                assert $ == #0399
                disp #C399
                include "../Text/ReadOtherKeyParams.asm"
                ent
                assert $ == #03A9
                disp #C3A9
                include "../Text/ReadFieldUpperY.asm"
                ent
                assert $ == #03AF
                disp #C3AF
                include "../Text/ReadCurrentKeyCodes.asm"
                ent
                assert $ == #03BF
                disp #C3BF
                include "../Text/ReadFieldLowery.asm"
                ent
                assert $ == #03C5
                disp #C3C5
                include "../Text/ReadOtherKeyCodes.asm"
                ent
                assert $ == #03D5
                disp #C3D5
                include "../Text/CompareEqual.asm"
                ent
                assert $ == #03DF
                disp #C3DF
                include "../Text/MultiplyWithChecks.asm"
                ent
                assert $ == #0488
                disp #C488
                include "../Text/AddSaturated.asm"
                ent
                assert $ == #0491
                disp #C491
                include "../Text/SubtractSaturated.asm"
                ent
                assert $ == #049C
                disp #C49C
                include "../Text/CompareLess.asm"
                ent
                assert $ == #04A6
                disp #C4A6
                include "../Text/CompareGreater.asm"
                ent
                assert $ == #04B1
                disp #C4B1
                include "../Text/CompareNotGreater.asm"
                ent
                assert $ == #04BC
                disp #C4BC
                include "../Text/CompareNotLess.asm"
                ent
                assert $ == #04C6
                disp #C4C6
                include "../Text/AndWords.asm"
                ent
                assert $ == #04CD
                disp #C4CD
                include "../Text/OrWords.asm"
                ent
                assert $ == #04D4
                disp #C4D4
                include "../Text/CopyRightOperand.asm"
                ent
                assert $ == #04D7
                disp #C4D7
                include "../Text/ReadStridedWord.asm"
                ent
                assert $ == #04E3
                disp #C4E3
                include "../Text/ReadStridedByte.asm"
                ent
                assert $ == #04EF
                disp #C4EF
                include "../Text/CheckThresholdSet30.asm"
                ent
                assert $ == #051A
                disp #C51A
                include "../Text/HasActiveNeighbor.asm"
                ent
                assert $ == #0558
                disp #C558
                include "../Text/IsByteMissingFromFour.asm"
                ent
                assert $ == #0577
                disp #C577
                include "../Text/GetHighBitCode.asm"
                ent
                assert $ == #058A
                disp #C58A
                include "../Text/Property070.asm"
                ent
                assert $ == #0590
                disp #C590
                include "../Text/Property071.asm"
                ent
                assert $ == #0596
                disp #C596
                include "../Text/CheckThresholdSet14.asm"
                ent
                assert $ == #05A9
                disp #C5A9
                include "../Text/HasSecondActiveNeighbor.asm"
                ent
                assert $ == #05B2
                disp #C5B2
                include "../Text/Property072.asm"
                ent
                assert $ == #05BB
                disp #C5BB
                include "../Text/Property073.asm"
                ent
                assert $ == #05C1
                disp #C5C1
                include "../Text/GetCargoSecondByte.asm"
                ent
                assert $ == #05C7
                disp #C5C7
                include "../Text/GetMarketPrice.asm"
                ent
                assert $ == #05CD
                disp #C5CD
                include "../Text/IsMarketSaleLegal.asm"
                ent
                assert $ == #05DF
                disp #C5DF
                include "../Text/GetIndexedLoad.asm"
                ent
                assert $ == #05E9
                disp #C5E9
                include "../Text/ReadStrideFiveWord.asm"
                ent
                assert $ == #05F9
                disp #C5F9
                include "../Text/ReadStrideFiveByte.asm"
                ent
                assert $ == #0609
                disp #C609
                include "../Text/Property080.asm"
                ent
                assert $ == #060F
                disp #C60F
                include "../Text/Property086.asm"
                ent
                assert $ == #0615
                disp #C615
                include "../Text/Property087.asm"
                ent
                assert $ == #061B
                disp #C61B
                include "../Text/GetKeyMajor.asm"
                ent
                assert $ == #0623
                disp #C623
                include "../Text/GetKeyMinor.asm"
                ent
                assert $ == #062A
                disp #C62A
                include "../Text/GetKeySize.asm"
                ent
                assert $ == #0632
                disp #C632
                include "../Text/GetKeyFingerprint.asm"
                ent
                assert $ == #063A
                disp #C63A
                include "../Text/GetKeyRegion.asm"
                ent
                assert $ == #0642
                disp #C642
                include "../Text/PushWordFieldWriter.asm"
                ent
                assert $ == #0657
                disp #C657
                include "../Text/PushByteUWriter.asm"
                ent
                assert $ == #066E
                disp #C66E
                include "../Text/PushByteJWriter.asm"
                ent
                assert $ == #0685
                disp #C685
                include "../Text/PushCargo7BitWriter.asm"
                ent
                assert $ == #06B6
                disp #C6B6
                include "../Text/PushMarket7BitWriter.asm"
                ent
                assert $ == #06BC
                disp #C6BC
                include "../Text/PushEquipmentWeightWriter.asm"
                ent
                assert $ == #06E4
                disp #C6E4
                include "../Text/PushSecondWeightWriter.asm"
                ent
                assert $ == #06EA
                disp #C6EA
                include "../Text/ReadDecimal5.asm"
                ent
                assert $ == #079C
                disp #C79C
                include "../Text/EmitOperator.asm"
                ent
                assert $ == #07B6
                disp #C7B6
                include "../Text/DispatchUnaryField.asm"
                ent
                assert $ == #07C3
                disp #C7C3
                include "../Text/DispatchWriteField.asm"
                ent
                assert $ == #07D0
                disp #C7D0
                include "../Text/DispatchReadField.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07DA
                disp #C7DA
                include "../Text/DispatchToken.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07E3
                disp #C7E3
                include "../Text/FindToken.asm"
                ent
                assert $ == #07EE
                disp #C7EE
                include "../Text/ParseFieldSuffix.asm"
                ent
                assert $ == #0825
                disp #C825
                include "../Text/CallExpression.asm"
                ent
                assert $ == #0849
                disp #C849
                include "../Text/FindDelimitedRecord.asm"
                ent
                assert $ == #086F
                disp #C86F
                include "../Text/ComputeWeightedLoad.asm"
                ent
                assert $ == #0900
                disp #C900
                include "../Text/GetEquipIndex.asm"
                ent
                assert $ == #090C
                disp #C90C
                include "../Text/SumSecondaryIndex.asm"
                ent
                assert $ == #0918
                disp #C918
                include "../Text/GetCargoIndex.asm"
                ent
                assert $ == #0924
                disp #C924
                include "../Text/DescribeKeyChoice.asm"
                ent
                assert $ == #0935
                disp #C935
                include "../Text/Data/TokenBindings.asm"
                ent
                assert $ == #0A67
                ; исходные физические слова стека выражений между таблицей и присваиванием
                disp #CA67
                include "../Text/Data/ExpressionStack.asm"
                ent
                assert $ == #0A7B
                disp #CA7B
                include "../Text/Data/AssignmentScratch.asm"
                ent
                assert $ == #0A81
                ; Unknown, четырнадцать исходных байтов между рабочей записью и сценарием
                incbin "../Resources/05_LANG/BeforeMarketScript.bin"
                assert $ == #0A8F
                disp #CA8F
                include "../Text/Data/MarketScript.asm"
                ent
                assert $ == #0F18
                ; исходный хвост после первого NUL, дополнительные потребители пока не установлены
                incbin "../Resources/05_LANG/AfterMarketScript.bin"
                assert $ == #1000
