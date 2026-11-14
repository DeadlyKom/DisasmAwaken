                module ArchiveTimerRaster
                ; Документация [цифры таймера](../../../Docs/ArchiveEngineTimerRaster.md)
Font:           incbin "../../../Tools/Disasm/Extracted/Archived/46_ENGINE.C.sectors.bin", #0B28, #0140
Buffer:         incbin "../../../Tools/Disasm/Extracted/Archived/46_ENGINE.C.sectors.bin", #0C68, #0020
Address:        FArchiveTimerAddress {
                    #0000                                                       ; Background, рассчитывается перед наложением цифр
                }
                endmodule
