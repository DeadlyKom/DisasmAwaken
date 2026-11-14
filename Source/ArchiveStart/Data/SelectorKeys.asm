                module ArchiveStartKeys
                ; Документация [клавиши и селекторы](../../../Docs/BankArchiveTileLayers.md)
                ; клавиша D, увеличение младшего индекса левой стороны
KeyD:           FArchiveStartKey {
                    #04,                                                        ; LatchCode
                    #03,                                                        ; Limit
                    @ArchiveStartData.Frame.LeftKeyLatch,                       ; Latch
                    @ArchiveStartData.Frame.LeftMinor,                          ; Selector
                    #01,                                                        ; Step
                    @ArchiveStart.CommitLeftRoute.Entry,                        ; Commit
                    @ArchiveStart.PrepareLeftLayerUpdate.Entry,                 ; Redraw
                    #00                                                         ; Side
                }

                ; клавиша A, уменьшение младшего индекса левой стороны
KeyA:           FArchiveStartKey {
                    #03,                                                        ; LatchCode
                    #00,                                                        ; Limit
                    @ArchiveStartData.Frame.LeftKeyLatch,                       ; Latch
                    @ArchiveStartData.Frame.LeftMinor,                          ; Selector
                    #FF,                                                        ; Step
                    @ArchiveStart.CommitLeftRoute.Entry,                        ; Commit
                    @ArchiveStart.PrepareLeftLayerUpdate.Entry,                 ; Redraw
                    #00                                                         ; Side
                }

                ; клавиша S, увеличение старшего индекса левой стороны
KeyS:           FArchiveStartKey {
                    #02,                                                        ; LatchCode
                    #02,                                                        ; Limit
                    @ArchiveStartData.Frame.LeftKeyLatch,                       ; Latch
                    @ArchiveStartData.Frame.LeftMajor,                          ; Selector
                    #01,                                                        ; Step
                    @ArchiveStart.CommitLeftRoute.Entry,                        ; Commit
                    @ArchiveStart.PrepareLeftLayerUpdate.Entry,                 ; Redraw
                    #00                                                         ; Side
                }

                ; клавиша W, уменьшение старшего индекса левой стороны
KeyW:           FArchiveStartKey {
                    #01,                                                        ; LatchCode
                    #00,                                                        ; Limit
                    @ArchiveStartData.Frame.LeftKeyLatch,                       ; Latch
                    @ArchiveStartData.Frame.LeftMajor,                          ; Selector
                    #FF,                                                        ; Step
                    @ArchiveStart.CommitLeftRoute.Entry,                        ; Commit
                    @ArchiveStart.PrepareLeftLayerUpdate.Entry,                 ; Redraw
                    #00                                                         ; Side
                }

                ; клавиша I, увеличение младшего индекса правой стороны
KeyI:           FArchiveStartKey {
                    #04,                                                        ; LatchCode
                    #03,                                                        ; Limit
                    @ArchiveStartData.Frame.RightKeyLatch,                      ; Latch
                    @ArchiveStartData.Frame.RightMinor,                         ; Selector
                    #01,                                                        ; Step
                    @ArchiveStart.CommitRightRoute.Entry,                       ; Commit
                    @ArchiveStart.PrepareRightLayerUpdate.Entry,                ; Redraw
                    #01                                                         ; Side
                }

                ; клавиша Y, уменьшение младшего индекса правой стороны
KeyY:           FArchiveStartKey {
                    #03,                                                        ; LatchCode
                    #00,                                                        ; Limit
                    @ArchiveStartData.Frame.RightKeyLatch,                      ; Latch
                    @ArchiveStartData.Frame.RightMinor,                         ; Selector
                    #FF,                                                        ; Step
                    @ArchiveStart.CommitRightRoute.Entry,                       ; Commit
                    @ArchiveStart.PrepareRightLayerUpdate.Entry,                ; Redraw
                    #01                                                         ; Side
                }

                ; клавиша U, увеличение старшего индекса правой стороны
KeyU:           FArchiveStartKey {
                    #02,                                                        ; LatchCode
                    #02,                                                        ; Limit
                    @ArchiveStartData.Frame.RightKeyLatch,                      ; Latch
                    @ArchiveStartData.Frame.RightMajor,                         ; Selector
                    #01,                                                        ; Step
                    @ArchiveStart.CommitRightRoute.Entry,                       ; Commit
                    @ArchiveStart.PrepareRightLayerUpdate.Entry,                ; Redraw
                    #01                                                         ; Side
                }

                ; клавиша 7, уменьшение старшего индекса правой стороны
Key7:           FArchiveStartKey {
                    #01,                                                        ; LatchCode
                    #00,                                                        ; Limit
                    @ArchiveStartData.Frame.RightKeyLatch,                      ; Latch
                    @ArchiveStartData.Frame.RightMajor,                         ; Selector
                    #FF,                                                        ; Step
                    @ArchiveStart.CommitRightRoute.Entry,                       ; Commit
                    @ArchiveStart.PrepareRightLayerUpdate.Entry,                ; Redraw
                    #01                                                         ; Side
                }

                endmodule
