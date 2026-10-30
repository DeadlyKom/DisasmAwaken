; Документация [ранги](../../../Docs/PlayerRank.md)
                module RankTexts
                assert $ == #ACE3
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Rookie:         db #91, #8E, #91, #93, #8D, #8E, #8A, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score10000:     db #81, #8E, #83, #20, #82, #8E, #88, #8D, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score3000:      db #31, #9B, #89, #20, #82, #8E, #88, #8D, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score1000:      db #32, #8E, #89, #20, #82, #8E, #88, #8D, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score300:       db #33, #88, #89, #20, #82, #8E, #88, #8D, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score100:       db #8E, #95, #8E, #92, #8D, #88, #8A, #0A
                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено
Score30:        db #85, #81, #93, #92, #20, #92, #85, #81, #9F, #0A
                assert $ == #AD21
                endmodule

                module RankThresholds
Score10000:     FRankThreshold { #27, #10 }                                     ; HighByte, LowByte, порог 10000
Score3000:      FRankThreshold { #0B, #B8 }                                     ; HighByte, LowByte, порог 3000
Score1000:      FRankThreshold { #03, #E8 }                                     ; HighByte, LowByte, порог 1000
Score300:       FRankThreshold { #01, #2C }                                     ; HighByte, LowByte, порог 300
Score100:       FRankThreshold { #00, #64 }                                     ; HighByte, LowByte, порог 100
Score30:        FRankThreshold { #00, #1E }                                     ; HighByte, LowByte, порог 30
                assert $ == #AD2D
                endmodule

                module RankCaption
Entry:          db #20, #90, #A0, #AD, #A3, #3A, #20, #0A
                assert $ == #AD35
                endmodule
