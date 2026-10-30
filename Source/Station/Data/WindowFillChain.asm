                module WindowFillChain
; Документация [WindowGraphics](../../../Docs/WindowGraphics.md)
                assert $ == #A102
State:          FWindowReturnChain {
                    #0000,                                                      ; FWindowReturnChain.InterruptPC
                    @Station.FillWindowBody.Scan1,                              ; FWindowReturnChain.Row1
                    @Station.FillWindowBody.Scan2,                              ; FWindowReturnChain.Row2
                    @Station.FillWindowBody.Scan3,                              ; FWindowReturnChain.Row3
                    @Station.FillWindowBody.Scan4,                              ; FWindowReturnChain.Row4
                    @Station.FillWindowBody.Scan5,                              ; FWindowReturnChain.Row5
                    @Station.FillWindowBody.Scan6,                              ; FWindowReturnChain.Row6
                    @Station.FillWindowBody.Scan7,                              ; FWindowReturnChain.Row7
                    @Station.FillWindowBody.AfterGroup,                         ; FWindowReturnChain.AfterGroup
                    #A0B6                                                       ; FWindowReturnChain.TailWord
                }
                endmodule
