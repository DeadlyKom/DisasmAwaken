                module PreviewClipTargetHigh
                ; Документация [разнесённые адресные страницы](../../../Docs/PreviewClipTablePages.md)
                assert $ == #CD00
                ; -----------------------------------------
                ; исходная физическая запись Start0
Start0:         FPreviewClipTargetRow {
                    HIGH(@D3D.AppendPreviewClipSecond.Entry),                   ; End0, старший байт цели
                    HIGH(@D3D.AppendPreviewClipRightIntersection.Entry),        ; End1, старший байт цели
                    HIGH(@D3D.AppendPreviewClipLeftIntersection.Entry),         ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.AppendPreviewClipBottomIntersection.Entry),       ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseI_BR),                       ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseI_BL),                       ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.AppendPreviewClipTopIntersection.Entry),          ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseI_TR),                       ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseI_TL),                       ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start1
Start1:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseR_I),                        ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseR_L),                        ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseR_B),                        ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseR_BR),                       ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseR_BL),                       ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseR_T),                        ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseR_TR),                       ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseR_TL),                       ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #55,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #01,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start2
Start2:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseL_I),                        ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseL_R),                        ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseL_B),                        ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseL_BR),                       ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseL_BL),                       ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseL_T),                        ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseL_TR),                       ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseL_TL),                       ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start3
Start3:         FPreviewClipTargetRow {
                    #00,                                                        ; End0, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End1, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End2, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End4, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End5, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End6, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End8, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End9, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndA, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start4
Start4:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseB_I),                        ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_R),                        ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_L),                        ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_BR),                       ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_BL),                       ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseB_T),                        ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_TR),                       ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseB_TL),                       ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #02,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start5
Start5:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseBR_I),                       ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBR_R),                       ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBR_L),                       ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseBR_B),                       ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBR_BL),                      ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseBR_T),                       ; End8, старший байт цели
                    HIGH(@D3D.UnwindPreviewClipFrame.Entry),                    ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBR_TL),                      ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start6
Start6:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseBL_I),                       ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBL_R),                       ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBL_L),                       ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseBL_B),                       ; End4, старший байт цели
                    HIGH(@D3D.UnwindPreviewClipFrame.Entry),                    ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseBL_T),                       ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBL_TR),                      ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseBL_TL),                      ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start7
Start7:         FPreviewClipTargetRow {
                    #00,                                                        ; End0, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End1, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End2, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End4, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End5, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End6, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End8, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; End9, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndA, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start8
Start8:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseT_I),                        ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_R),                        ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_L),                        ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseT_B),                        ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_BR),                       ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_BL),                       ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_TR),                       ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseT_TL),                       ; EndA, старший байт цели
                    #20,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #B2,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #64                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись Start9
Start9:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseTR_I),                       ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTR_R),                       ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTR_L),                       ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseTR_B),                       ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTR_BR),                      ; End5, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTR_BL),                      ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseTR_T),                       ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; End9, старший байт цели
                    HIGH(@D3D.UnwindPreviewClipFrame.Entry),                    ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                ; -----------------------------------------
                ; исходная физическая запись StartA
StartA:         FPreviewClipTargetRow {
                    HIGH(@D3D.PreviewClipCases.CaseTL_I),                       ; End0, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTL_R),                       ; End1, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTL_L),                       ; End2, старший байт цели
                    #00,                                                        ; End3, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseTL_B),                       ; End4, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTL_BR),                      ; End5, старший байт цели
                    HIGH(@D3D.UnwindPreviewClipFrame.Entry),                    ; End6, старший байт цели
                    #00,                                                        ; End7, исходный байт за пределами девяти допустимых кодов
                    HIGH(@D3D.PreviewClipCases.CaseTL_T),                       ; End8, старший байт цели
                    HIGH(@D3D.PreviewClipCases.CaseTL_TR),                      ; End9, старший байт цели
                    HIGH(@D3D.PreviewClipCases.Entry),                          ; EndA, старший байт цели
                    #00,                                                        ; EndB, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndC, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndD, исходный байт за пределами девяти допустимых кодов
                    #00,                                                        ; EndE, исходный байт за пределами девяти допустимых кодов
                    #00                                                         ; EndF, исходный байт за пределами девяти допустимых кодов
                }
                assert $ == #CDB0
                endmodule
