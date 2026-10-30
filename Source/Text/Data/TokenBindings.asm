                module ScriptTokens
; Документация [торговый язык](../../../Docs/ScriptLanguage.md)
; физические записи FScriptToken, исходный диапазон #C935..#CA66
; имена экземпляров обозначают символы, смысл неизвестных свойств ещё разбирается
                assert $ == #C935

                module Commands
Question:       FScriptToken {
                    #3F,                                                        ; Symbol, исходный ASCII-код
                    @Text.TestExpression.Entry                                  ; Handler, адрес из исходной записи
                }
Colon:          FScriptToken {
                    #3A,                                                        ; Symbol, исходный ASCII-код
                    @Text.ApplyCondition.Entry                                  ; Handler, адрес из исходной записи
                }
OpenBrace:      FScriptToken {
                    #7B,                                                        ; Symbol, исходный ASCII-код
                    @Text.BeginBlock.Entry                                      ; Handler, адрес из исходной записи
                }
CloseBrace:     FScriptToken {
                    #7D,                                                        ; Symbol, исходный ASCII-код
                    @Text.EndBlock.Entry                                        ; Handler, адрес из исходной записи
                }
At:             FScriptToken {
                    #40,                                                        ; Symbol, исходный ASCII-код
                    @Text.ApplyInverseCondition.Entry                           ; Handler, адрес из исходной записи
                }
Plus:           FScriptToken {
                    #2B,                                                        ; Symbol, исходный ASCII-код
                    @Text.ApplyAddFieldOperation.Entry                          ; Handler, адрес из исходной записи
                }
Minus:          FScriptToken {
                    #2D,                                                        ; Symbol, исходный ASCII-код
                    @Text.ApplyRemoveFieldOperation.Entry                       ; Handler, адрес из исходной записи
                }
Equal:          FScriptToken {
                    #3D,                                                        ; Symbol, исходный ASCII-код
                    @Text.AssignValue.Entry                                     ; Handler, адрес из исходной записи
                }
Comma:          FScriptToken {
                    #2C,                                                        ; Symbol, исходный ASCII-код
                    @Text.Command2C.Entry                                       ; Handler, адрес из исходной записи
                }
UpperT:         FScriptToken {
                    #54,                                                        ; Symbol, исходный ASCII-код
                    @Text.RecomputeTonnage.Entry                                ; Handler, адрес из исходной записи
                }
UpperM:         FScriptToken {
                    #4D,                                                        ; Symbol, исходный ASCII-код
                    @Text.QueueTextAndStopAtLine.Entry                          ; Handler, адрес из исходной записи
                }
LowerM:         FScriptToken {
                    #6D,                                                        ; Symbol, исходный ASCII-код
                    @Text.QueueTextCommand.Entry                                ; Handler, адрес из исходной записи
                }
Caret:          FScriptToken {
                    #5E,                                                        ; Symbol, исходный ASCII-код
                    @Text.FinishScript.Entry                                    ; Handler, адрес из исходной записи
                }
Hash:           FScriptToken {
                    #23,                                                        ; Symbol, исходный ASCII-код
                    @Text.Command23.Entry                                       ; Handler, адрес из исходной записи
                }
UpperW:         FScriptToken {
                    #57,                                                        ; Symbol, исходный ASCII-код
                    @Text.Command57.Entry                                       ; Handler, адрес из исходной записи
                }
                endmodule

                module Operators
Equal:          FScriptToken {
                    #3D,                                                        ; Symbol, исходный ASCII-код
                    @Text.CompareEqual.Entry                                    ; Handler, адрес из исходной записи
                }
Multiply:       FScriptToken {
                    #2A,                                                        ; Symbol, исходный ASCII-код
                    @Text.MultiplyWithChecks.Entry                              ; Handler, адрес из исходной записи
                }
Plus:           FScriptToken {
                    #2B,                                                        ; Symbol, исходный ASCII-код
                    @Text.AddSaturated.Entry                                    ; Handler, адрес из исходной записи
                }
Minus:          FScriptToken {
                    #2D,                                                        ; Symbol, исходный ASCII-код
                    @Text.SubtractSaturated.Entry                               ; Handler, адрес из исходной записи
                }
Less:           FScriptToken {
                    #3C,                                                        ; Symbol, исходный ASCII-код
                    @Text.CompareLess.Entry                                     ; Handler, адрес из исходной записи
                }
Greater:        FScriptToken {
                    #3E,                                                        ; Symbol, исходный ASCII-код
                    @Text.CompareGreater.Entry                                  ; Handler, адрес из исходной записи
                }
NotGreater:     FScriptToken {
                    #5B,                                                        ; Symbol, исходный ASCII-код
                    @Text.CompareNotGreater.Entry                               ; Handler, адрес из исходной записи
                }
NotLess:        FScriptToken {
                    #5D,                                                        ; Symbol, исходный ASCII-код
                    @Text.CompareNotLess.Entry                                  ; Handler, адрес из исходной записи
                }
And:            FScriptToken {
                    #26,                                                        ; Symbol, исходный ASCII-код
                    @Text.AndWords.Entry                                        ; Handler, адрес из исходной записи
                }
Or:             FScriptToken {
                    #21,                                                        ; Symbol, исходный ASCII-код
                    @Text.OrWords.Entry                                         ; Handler, адрес из исходной записи
                }
Colon:          FScriptToken {
                    #3A,                                                        ; Symbol, исходный ASCII-код
                    @Text.CopyRightOperand.Entry                                ; Handler, адрес из исходной записи
                }
                endmodule

                module Fields
LowerC:         FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadCredits.Entry                                     ; Handler, адрес из исходной записи
                }
LowerO:         FScriptToken {
                    #6F,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowero.Entry                                 ; Handler, адрес из исходной записи
                }
LowerI:         FScriptToken {
                    #69,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLoweri.Entry                                 ; Handler, адрес из исходной записи
                }
LowerK:         FScriptToken {
                    #6B,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerk.Entry                                 ; Handler, адрес из исходной записи
                }
LowerR:         FScriptToken {
                    #72,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerr.Entry                                 ; Handler, адрес из исходной записи
                }
LowerJ:         FScriptToken {
                    #6A,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerj.Entry                                 ; Handler, адрес из исходной записи
                }
UpperJ:         FScriptToken {
                    #4A,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperJ.Entry                                 ; Handler, адрес из исходной записи
                }
LowerY:         FScriptToken {
                    #79,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushTrue.Entry                                        ; Handler, адрес из исходной записи
                }
LowerN:         FScriptToken {
                    #6E,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushFalse.Entry                                       ; Handler, адрес из исходной записи
                }
UpperX:         FScriptToken {
                    #58,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadEventCode.Entry                                   ; Handler, адрес из исходной записи
                }
LowerU:         FScriptToken {
                    #75,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLoweru.Entry                                 ; Handler, адрес из исходной записи
                }
UpperG:         FScriptToken {
                    #47,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperG.Entry                                 ; Handler, адрес из исходной записи
                }
UpperO:         FScriptToken {
                    #4F,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperO.Entry                                 ; Handler, адрес из исходной записи
                }
UpperI:         FScriptToken {
                    #49,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperI.Entry                                 ; Handler, адрес из исходной записи
                }
UpperK:         FScriptToken {
                    #4B,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperK.Entry                                 ; Handler, адрес из исходной записи
                }
UpperR:         FScriptToken {
                    #52,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperR.Entry                                 ; Handler, адрес из исходной записи
                }
LowerG:         FScriptToken {
                    #67,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerg.Entry                                 ; Handler, адрес из исходной записи
                }
LowerE:         FScriptToken {
                    #65,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowere.Entry                                 ; Handler, адрес из исходной записи
                }
LowerM:         FScriptToken {
                    #6D,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerm.Entry                                 ; Handler, адрес из исходной записи
                }
LowerP:         FScriptToken {
                    #70,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerp.Entry                                 ; Handler, адрес из исходной записи
                }
LowerT:         FScriptToken {
                    #74,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowert.Entry                                 ; Handler, адрес из исходной записи
                }
OpenParen:      FScriptToken {
                    #28,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode28.Entry                                 ; Handler, адрес из исходной записи
                }
Digit1:         FScriptToken {
                    #31,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit2:         FScriptToken {
                    #32,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit3:         FScriptToken {
                    #33,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit4:         FScriptToken {
                    #34,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit5:         FScriptToken {
                    #35,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit6:         FScriptToken {
                    #36,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit7:         FScriptToken {
                    #37,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit8:         FScriptToken {
                    #38,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit9:         FScriptToken {
                    #39,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
Digit0:         FScriptToken {
                    #30,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldCode1.Entry                                  ; Handler, адрес из исходной записи
                }
UpperL:         FScriptToken {
                    #4C,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperL.Entry                                 ; Handler, адрес из исходной записи
                }
LowerL:         FScriptToken {
                    #6C,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowerl.Entry                                 ; Handler, адрес из исходной записи
                }
UpperY:         FScriptToken {
                    #59,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldUpperY.Entry                                 ; Handler, адрес из исходной записи
                }
LowerY2:        FScriptToken {
                    #79,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadFieldLowery.Entry                                 ; Handler, адрес из исходной записи
                }
                endmodule

                module Suffixes
LowerS:         FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.CheckThresholdSet30.Entry                             ; Handler, адрес из исходной записи
                }
LowerN:         FScriptToken {
                    #6E,                                                        ; Symbol, исходный ASCII-код
                    @Text.HasActiveNeighbor.Entry                               ; Handler, адрес из исходной записи
                }
LowerS2:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.CheckThresholdSet14.Entry                             ; Handler, адрес из исходной записи
                }
LowerN2:        FScriptToken {
                    #6E,                                                        ; Symbol, исходный ASCII-код
                    @Text.HasSecondActiveNeighbor.Entry                         ; Handler, адрес из исходной записи
                }
LowerC:         FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadStridedWord.Entry                                 ; Handler, адрес из исходной записи
                }
LowerV:         FScriptToken {
                    #76,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadStridedByte.Entry                                 ; Handler, адрес из исходной записи
                }
LowerS3:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.IsByteMissingFromFour.Entry                           ; Handler, адрес из исходной записи
                }
LowerK:         FScriptToken {
                    #6B,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetHighBitCode.Entry                                  ; Handler, адрес из исходной записи
                }
LowerC2:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property070.Entry                                     ; Handler, адрес из исходной записи
                }
LowerV2:        FScriptToken {
                    #76,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property071.Entry                                     ; Handler, адрес из исходной записи
                }
LowerS4:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property072.Entry                                     ; Handler, адрес из исходной записи
                }
LowerK2:        FScriptToken {
                    #6B,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property073.Entry                                     ; Handler, адрес из исходной записи
                }
LowerC3:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetCargoSecondByte.Entry                              ; Handler, адрес из исходной записи
                }
LowerC4:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetMarketPrice.Entry                                  ; Handler, адрес из исходной записи
                }
LowerS5:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.IsMarketMarkClear.Entry                               ; Handler, адрес из исходной записи
                }
LowerM:         FScriptToken {
                    #6D,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetIndexedLoad.Entry                                  ; Handler, адрес из исходной записи
                }
LowerC5:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadStrideFiveWord.Entry                              ; Handler, адрес из исходной записи
                }
LowerT:         FScriptToken {
                    #74,                                                        ; Symbol, исходный ASCII-код
                    @Text.ReadStrideFiveByte.Entry                              ; Handler, адрес из исходной записи
                }
LowerS6:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property080.Entry                                     ; Handler, адрес из исходной записи
                }
LowerS7:        FScriptToken {
                    #73,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetKeyMajor.Entry                                     ; Handler, адрес из исходной записи
                }
LowerC6:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetKeyMinor.Entry                                     ; Handler, адрес из исходной записи
                }
LowerU:         FScriptToken {
                    #75,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetKeySize.Entry                                      ; Handler, адрес из исходной записи
                }
LowerP:         FScriptToken {
                    #70,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetKeyFingerprint.Entry                               ; Handler, адрес из исходной записи
                }
LowerG:         FScriptToken {
                    #67,                                                        ; Symbol, исходный ASCII-код
                    @Text.GetKeyRegion.Entry                                    ; Handler, адрес из исходной записи
                }
LowerC7:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property086.Entry                                     ; Handler, адрес из исходной записи
                }
LowerV3:        FScriptToken {
                    #76,                                                        ; Symbol, исходный ASCII-код
                    @Text.Property087.Entry                                     ; Handler, адрес из исходной записи
                }
LowerC8:        FScriptToken {
                    #63,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushWordFieldWriter.Entry                             ; Handler, адрес из исходной записи
                }
LowerU2:        FScriptToken {
                    #75,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushByteUWriter.Entry                                 ; Handler, адрес из исходной записи
                }
LowerG2:        FScriptToken {
                    #67,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushCargo7BitWriter.Entry                             ; Handler, адрес из исходной записи
                }
UpperG:         FScriptToken {
                    #47,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushMarket7BitWriter.Entry                            ; Handler, адрес из исходной записи
                }
LowerO:         FScriptToken {
                    #6F,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushEquipmentWeightWriter.Entry                       ; Handler, адрес из исходной записи
                }
LowerI:         FScriptToken {
                    #69,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushSecondWeightWriter.Entry                          ; Handler, адрес из исходной записи
                }
UpperJ:         FScriptToken {
                    #4A,                                                        ; Symbol, исходный ASCII-код
                    @Text.PushByteJWriter.Entry                                 ; Handler, адрес из исходной записи
                }
LowerT2:        FScriptToken {
                    #74,                                                        ; Symbol, исходный ASCII-код
                    @Text.ActivateResourceRecord.Entry                          ; Handler, адрес из исходной записи
                }
LowerP2:        FScriptToken {
                    #70,                                                        ; Symbol, исходный ASCII-код
                    @Text.WriteIndexedPMode.Entry                               ; Handler, адрес из исходной записи
                }
LowerV4:        FScriptToken {
                    #76,                                                        ; Symbol, исходный ASCII-код
                    @Text.WriteIndexedVMode.Entry                               ; Handler, адрес из исходной записи
                }
LowerM2:        FScriptToken {
                    #6D,                                                        ; Symbol, исходный ASCII-код
                    @Text.WriteIndexedMMode.Entry                               ; Handler, адрес из исходной записи
                }
LowerE:         FScriptToken {
                    #65,                                                        ; Symbol, исходный ASCII-код
                    @Text.WriteIndexedEMode.Entry                               ; Handler, адрес из исходной записи
                }
UpperK:         FScriptToken {
                    #4B,                                                        ; Symbol, исходный ASCII-код
                    @Text.SetPrimarySelection.Entry                             ; Handler, адрес из исходной записи
                }
UpperR:         FScriptToken {
                    #52,                                                        ; Symbol, исходный ASCII-код
                    @Text.SetSecondarySelection.Entry                           ; Handler, адрес из исходной записи
                }
                endmodule
                assert $ == #CA67
                endmodule
