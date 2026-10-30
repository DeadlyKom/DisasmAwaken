                module PointerSprites
; Документация [указатель](../../../Docs/Pointer.md)
; исходные фазы сдвига, MaskLeft, XorLeft, MaskRight, XorRight
                assert $ == #6000
                module Normal
Shift0Row0:     FPointerRasterRow {
                    #3F,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row1:     FPointerRasterRow {
                    #1F,                                                        ; FPointerRasterRow.MaskLeft
                    #40,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row2:     FPointerRasterRow {
                    #0F,                                                        ; FPointerRasterRow.MaskLeft
                    #60,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row3:     FPointerRasterRow {
                    #07,                                                        ; FPointerRasterRow.MaskLeft
                    #70,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row4:     FPointerRasterRow {
                    #03,                                                        ; FPointerRasterRow.MaskLeft
                    #78,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row5:     FPointerRasterRow {
                    #07,                                                        ; FPointerRasterRow.MaskLeft
                    #60,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row6:     FPointerRasterRow {
                    #1F,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row7:     FPointerRasterRow {
                    #7F,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row0:     FPointerRasterRow {
                    #9F,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row1:     FPointerRasterRow {
                    #8F,                                                        ; FPointerRasterRow.MaskLeft
                    #20,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row2:     FPointerRasterRow {
                    #87,                                                        ; FPointerRasterRow.MaskLeft
                    #30,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row3:     FPointerRasterRow {
                    #83,                                                        ; FPointerRasterRow.MaskLeft
                    #38,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row4:     FPointerRasterRow {
                    #81,                                                        ; FPointerRasterRow.MaskLeft
                    #3C,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row5:     FPointerRasterRow {
                    #83,                                                        ; FPointerRasterRow.MaskLeft
                    #30,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row6:     FPointerRasterRow {
                    #8F,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row7:     FPointerRasterRow {
                    #BF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row0:     FPointerRasterRow {
                    #CF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row1:     FPointerRasterRow {
                    #C7,                                                        ; FPointerRasterRow.MaskLeft
                    #10,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row2:     FPointerRasterRow {
                    #C3,                                                        ; FPointerRasterRow.MaskLeft
                    #18,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row3:     FPointerRasterRow {
                    #C1,                                                        ; FPointerRasterRow.MaskLeft
                    #1C,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row4:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row5:     FPointerRasterRow {
                    #C1,                                                        ; FPointerRasterRow.MaskLeft
                    #18,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row6:     FPointerRasterRow {
                    #C7,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row7:     FPointerRasterRow {
                    #DF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row0:     FPointerRasterRow {
                    #E7,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row1:     FPointerRasterRow {
                    #E3,                                                        ; FPointerRasterRow.MaskLeft
                    #08,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row2:     FPointerRasterRow {
                    #E1,                                                        ; FPointerRasterRow.MaskLeft
                    #0C,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row3:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row4:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row5:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0C,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row6:     FPointerRasterRow {
                    #E3,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row7:     FPointerRasterRow {
                    #EF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row0:     FPointerRasterRow {
                    #F3,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row1:     FPointerRasterRow {
                    #F1,                                                        ; FPointerRasterRow.MaskLeft
                    #04,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row2:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #06,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row3:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row4:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row5:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #06,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row6:     FPointerRasterRow {
                    #F1,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row7:     FPointerRasterRow {
                    #F7,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row0:     FPointerRasterRow {
                    #F9,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row1:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #02,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row2:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row3:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row4:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row5:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row6:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row7:     FPointerRasterRow {
                    #FB,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row0:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row1:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row2:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row3:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row4:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row5:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row6:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row7:     FPointerRasterRow {
                    #FD,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row0:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row1:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row2:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row3:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row4:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #F0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row5:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row6:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row7:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
                endmodule
                module Top
Shift0Row0:     FPointerRasterRow {
                    #07,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row1:     FPointerRasterRow {
                    #03,                                                        ; FPointerRasterRow.MaskLeft
                    #78,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row2:     FPointerRasterRow {
                    #01,                                                        ; FPointerRasterRow.MaskLeft
                    #48,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row3:     FPointerRasterRow {
                    #00,                                                        ; FPointerRasterRow.MaskLeft
                    #4E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row4:     FPointerRasterRow {
                    #00,                                                        ; FPointerRasterRow.MaskLeft
                    #7A,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row5:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #12,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row6:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row7:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row0:     FPointerRasterRow {
                    #83,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row1:     FPointerRasterRow {
                    #81,                                                        ; FPointerRasterRow.MaskLeft
                    #3C,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row2:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #24,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row3:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #27,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row4:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #3D,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row5:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #09,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row6:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row7:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row0:     FPointerRasterRow {
                    #C1,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row1:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row2:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #12,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row3:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #13,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row4:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row5:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #04,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row6:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row7:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row0:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row1:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row2:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #09,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row3:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #09,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row4:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #40                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row5:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #02,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #40                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row6:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row7:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row0:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row1:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row2:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #04,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row3:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #04,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row4:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #A0                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row5:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #20                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row6:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row7:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row0:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row1:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row2:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #02,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #40                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row3:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #02,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #70                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row4:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #D0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row5:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #90                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row6:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #F0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row7:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row0:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row1:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row2:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #20                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row3:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #38                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row4:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #E8                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row5:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #48                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row6:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #78                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row7:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #83,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row0:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row1:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #F0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row2:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #90                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row3:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #01,                                                        ; FPointerRasterRow.MaskRight
                    #9C                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row4:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #01,                                                        ; FPointerRasterRow.MaskRight
                    #F4                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row5:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #01,                                                        ; FPointerRasterRow.MaskRight
                    #24                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row6:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #81,                                                        ; FPointerRasterRow.MaskRight
                    #3C                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row7:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #C1,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
                endmodule
                module Bottom
Shift0Row0:     FPointerRasterRow {
                    #01,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row1:     FPointerRasterRow {
                    #02,                                                        ; FPointerRasterRow.MaskLeft
                    #78,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row2:     FPointerRasterRow {
                    #04,                                                        ; FPointerRasterRow.MaskLeft
                    #70,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row3:     FPointerRasterRow {
                    #08,                                                        ; FPointerRasterRow.MaskLeft
                    #62,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row4:     FPointerRasterRow {
                    #10,                                                        ; FPointerRasterRow.MaskLeft
                    #46,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row5:     FPointerRasterRow {
                    #20,                                                        ; FPointerRasterRow.MaskLeft
                    #0E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row6:     FPointerRasterRow {
                    #40,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift0Row7:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row0:     FPointerRasterRow {
                    #80,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #FF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row1:     FPointerRasterRow {
                    #81,                                                        ; FPointerRasterRow.MaskLeft
                    #3C,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row2:     FPointerRasterRow {
                    #82,                                                        ; FPointerRasterRow.MaskLeft
                    #38,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row3:     FPointerRasterRow {
                    #84,                                                        ; FPointerRasterRow.MaskLeft
                    #31,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row4:     FPointerRasterRow {
                    #88,                                                        ; FPointerRasterRow.MaskLeft
                    #23,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row5:     FPointerRasterRow {
                    #90,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row6:     FPointerRasterRow {
                    #A0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift1Row7:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row0:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #7F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row1:     FPointerRasterRow {
                    #C0,                                                        ; FPointerRasterRow.MaskLeft
                    #1E,                                                        ; FPointerRasterRow.XorLeft
                    #BF,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row2:     FPointerRasterRow {
                    #C1,                                                        ; FPointerRasterRow.MaskLeft
                    #1C,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row3:     FPointerRasterRow {
                    #C2,                                                        ; FPointerRasterRow.MaskLeft
                    #18,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row4:     FPointerRasterRow {
                    #C4,                                                        ; FPointerRasterRow.MaskLeft
                    #11,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row5:     FPointerRasterRow {
                    #C8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row6:     FPointerRasterRow {
                    #D0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift2Row7:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row0:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #3F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row1:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0F,                                                        ; FPointerRasterRow.XorLeft
                    #5F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row2:     FPointerRasterRow {
                    #E0,                                                        ; FPointerRasterRow.MaskLeft
                    #0E,                                                        ; FPointerRasterRow.XorLeft
                    #9F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row3:     FPointerRasterRow {
                    #E1,                                                        ; FPointerRasterRow.MaskLeft
                    #0C,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #40                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row4:     FPointerRasterRow {
                    #E2,                                                        ; FPointerRasterRow.MaskLeft
                    #08,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row5:     FPointerRasterRow {
                    #E4,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row6:     FPointerRasterRow {
                    #E8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift3Row7:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row0:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #1F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row1:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #2F,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row2:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #07,                                                        ; FPointerRasterRow.XorLeft
                    #4F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row3:     FPointerRasterRow {
                    #F0,                                                        ; FPointerRasterRow.MaskLeft
                    #06,                                                        ; FPointerRasterRow.XorLeft
                    #8F,                                                        ; FPointerRasterRow.MaskRight
                    #20                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row4:     FPointerRasterRow {
                    #F1,                                                        ; FPointerRasterRow.MaskLeft
                    #04,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #60                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row5:     FPointerRasterRow {
                    #F2,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row6:     FPointerRasterRow {
                    #F4,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift4Row7:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row0:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #0F,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row1:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #17,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row2:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #27,                                                        ; FPointerRasterRow.MaskRight
                    #80                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row3:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #03,                                                        ; FPointerRasterRow.XorLeft
                    #47,                                                        ; FPointerRasterRow.MaskRight
                    #10                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row4:     FPointerRasterRow {
                    #F8,                                                        ; FPointerRasterRow.MaskLeft
                    #02,                                                        ; FPointerRasterRow.XorLeft
                    #87,                                                        ; FPointerRasterRow.MaskRight
                    #30                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row5:     FPointerRasterRow {
                    #F9,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #70                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row6:     FPointerRasterRow {
                    #FA,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #F0                                                         ; FPointerRasterRow.XorRight
                }
Shift5Row7:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row0:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #07,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row1:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #0B,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row2:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #13,                                                        ; FPointerRasterRow.MaskRight
                    #C0                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row3:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #23,                                                        ; FPointerRasterRow.MaskRight
                    #88                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row4:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #01,                                                        ; FPointerRasterRow.XorLeft
                    #43,                                                        ; FPointerRasterRow.MaskRight
                    #18                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row5:     FPointerRasterRow {
                    #FC,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #83,                                                        ; FPointerRasterRow.MaskRight
                    #38                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row6:     FPointerRasterRow {
                    #FD,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #78                                                         ; FPointerRasterRow.XorRight
                }
Shift6Row7:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row0:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #03,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row1:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #05,                                                        ; FPointerRasterRow.MaskRight
                    #F0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row2:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #09,                                                        ; FPointerRasterRow.MaskRight
                    #E0                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row3:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #11,                                                        ; FPointerRasterRow.MaskRight
                    #C4                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row4:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #21,                                                        ; FPointerRasterRow.MaskRight
                    #8C                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row5:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #41,                                                        ; FPointerRasterRow.MaskRight
                    #1C                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row6:     FPointerRasterRow {
                    #FE,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #81,                                                        ; FPointerRasterRow.MaskRight
                    #3C                                                         ; FPointerRasterRow.XorRight
                }
Shift7Row7:     FPointerRasterRow {
                    #FF,                                                        ; FPointerRasterRow.MaskLeft
                    #00,                                                        ; FPointerRasterRow.XorLeft
                    #01,                                                        ; FPointerRasterRow.MaskRight
                    #00                                                         ; FPointerRasterRow.XorRight
                }
                endmodule
                assert $ == #6300
                endmodule
