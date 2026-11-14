                module ArchiveStartTileMasks
                ; Документация [маски слоёв](../../../Docs/BankArchiveTileLayers.md)
                ; В каждом байте старший бит соответствует левому пикселю знакоместа.
                ; Основная группа, объединение через OR.
Base00:         FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #C0,                                                        ; Row2
                    #C0,                                                        ; Row3
                    #C0,                                                        ; Row4
                    #C0,                                                        ; Row5
                    #C0,                                                        ; Row6
                    #C0                                                         ; Row7
                }

Base01:         FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #03,                                                        ; Row2
                    #03,                                                        ; Row3
                    #03,                                                        ; Row4
                    #03,                                                        ; Row5
                    #03,                                                        ; Row6
                    #03                                                         ; Row7
                }

Base02:         FArchiveTileRaster {
                    #C0,                                                        ; Row0
                    #C0,                                                        ; Row1
                    #C0,                                                        ; Row2
                    #C0,                                                        ; Row3
                    #C0,                                                        ; Row4
                    #C0,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Base03:         FArchiveTileRaster {
                    #03,                                                        ; Row0
                    #03,                                                        ; Row1
                    #03,                                                        ; Row2
                    #03,                                                        ; Row3
                    #03,                                                        ; Row4
                    #03,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Base04:         FArchiveTileRaster {
                    #C0,                                                        ; Row0
                    #C0,                                                        ; Row1
                    #C0,                                                        ; Row2
                    #C0,                                                        ; Row3
                    #C0,                                                        ; Row4
                    #C0,                                                        ; Row5
                    #C0,                                                        ; Row6
                    #C0                                                         ; Row7
                }

Base05:         FArchiveTileRaster {
                    #03,                                                        ; Row0
                    #03,                                                        ; Row1
                    #03,                                                        ; Row2
                    #03,                                                        ; Row3
                    #03,                                                        ; Row4
                    #03,                                                        ; Row5
                    #03,                                                        ; Row6
                    #03                                                         ; Row7
                }

Base06:         FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #00,                                                        ; Row2
                    #00,                                                        ; Row3
                    #00,                                                        ; Row4
                    #00,                                                        ; Row5
                    #00,                                                        ; Row6
                    #00                                                         ; Row7
                }

Base07:         FArchiveTileRaster {
                    #00,                                                        ; Row0
                    #00,                                                        ; Row1
                    #00,                                                        ; Row2
                    #00,                                                        ; Row3
                    #00,                                                        ; Row4
                    #00,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Base08:         FArchiveTileRaster {
                    #0C,                                                        ; Row0
                    #1C,                                                        ; Row1
                    #3C,                                                        ; Row2
                    #7C,                                                        ; Row3
                    #1C,                                                        ; Row4
                    #1C,                                                        ; Row5
                    #1C,                                                        ; Row6
                    #1C                                                         ; Row7
                }

Base09:         FArchiveTileRaster {
                    #1C,                                                        ; Row0
                    #1C,                                                        ; Row1
                    #1C,                                                        ; Row2
                    #1C,                                                        ; Row3
                    #1C,                                                        ; Row4
                    #3F,                                                        ; Row5
                    #7F,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Base10:         FArchiveTileRaster {
                    #3C,                                                        ; Row0
                    #7E,                                                        ; Row1
                    #FF,                                                        ; Row2
                    #8F,                                                        ; Row3
                    #07,                                                        ; Row4
                    #07,                                                        ; Row5
                    #07,                                                        ; Row6
                    #06                                                         ; Row7
                }

Base11:         FArchiveTileRaster {
                    #06,                                                        ; Row0
                    #0C,                                                        ; Row1
                    #18,                                                        ; Row2
                    #30,                                                        ; Row3
                    #60,                                                        ; Row4
                    #FF,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

                ; Вторая группа, стирание исходных битов через CPL и AND.
Erase00:        FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #FF,                                                        ; Row2
                    #E0,                                                        ; Row3
                    #E0,                                                        ; Row4
                    #E0,                                                        ; Row5
                    #E0,                                                        ; Row6
                    #E0                                                         ; Row7
                }

Erase01:        FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #FF,                                                        ; Row2
                    #07,                                                        ; Row3
                    #07,                                                        ; Row4
                    #07,                                                        ; Row5
                    #07,                                                        ; Row6
                    #07                                                         ; Row7
                }

Erase02:        FArchiveTileRaster {
                    #E0,                                                        ; Row0
                    #E0,                                                        ; Row1
                    #E0,                                                        ; Row2
                    #E0,                                                        ; Row3
                    #E0,                                                        ; Row4
                    #FF,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Erase03:        FArchiveTileRaster {
                    #07,                                                        ; Row0
                    #07,                                                        ; Row1
                    #07,                                                        ; Row2
                    #07,                                                        ; Row3
                    #07,                                                        ; Row4
                    #FF,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Erase04:        FArchiveTileRaster {
                    #E0,                                                        ; Row0
                    #E0,                                                        ; Row1
                    #E0,                                                        ; Row2
                    #E0,                                                        ; Row3
                    #E0,                                                        ; Row4
                    #E0,                                                        ; Row5
                    #E0,                                                        ; Row6
                    #E0                                                         ; Row7
                }

Erase05:        FArchiveTileRaster {
                    #07,                                                        ; Row0
                    #07,                                                        ; Row1
                    #07,                                                        ; Row2
                    #07,                                                        ; Row3
                    #07,                                                        ; Row4
                    #07,                                                        ; Row5
                    #07,                                                        ; Row6
                    #07                                                         ; Row7
                }

Erase06:        FArchiveTileRaster {
                    #FF,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #FF,                                                        ; Row2
                    #00,                                                        ; Row3
                    #00,                                                        ; Row4
                    #00,                                                        ; Row5
                    #00,                                                        ; Row6
                    #00                                                         ; Row7
                }

Erase07:        FArchiveTileRaster {
                    #00,                                                        ; Row0
                    #00,                                                        ; Row1
                    #00,                                                        ; Row2
                    #00,                                                        ; Row3
                    #00,                                                        ; Row4
                    #FF,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Erase08:        FArchiveTileRaster {
                    #1E,                                                        ; Row0
                    #3E,                                                        ; Row1
                    #7E,                                                        ; Row2
                    #FE,                                                        ; Row3
                    #7E,                                                        ; Row4
                    #3E,                                                        ; Row5
                    #3E,                                                        ; Row6
                    #3E                                                         ; Row7
                }

Erase09:        FArchiveTileRaster {
                    #3E,                                                        ; Row0
                    #3E,                                                        ; Row1
                    #3E,                                                        ; Row2
                    #3E,                                                        ; Row3
                    #3F,                                                        ; Row4
                    #7F,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

Erase10:        FArchiveTileRaster {
                    #7E,                                                        ; Row0
                    #FF,                                                        ; Row1
                    #FF,                                                        ; Row2
                    #FF,                                                        ; Row3
                    #8F,                                                        ; Row4
                    #0F,                                                        ; Row5
                    #0F,                                                        ; Row6
                    #0F                                                         ; Row7
                }

Erase11:        FArchiveTileRaster {
                    #0F,                                                        ; Row0
                    #1E,                                                        ; Row1
                    #3C,                                                        ; Row2
                    #78,                                                        ; Row3
                    #FF,                                                        ; Row4
                    #FF,                                                        ; Row5
                    #FF,                                                        ; Row6
                    #FF                                                         ; Row7
                }

                endmodule
