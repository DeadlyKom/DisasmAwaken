                module ArchiveRunImages
                ; Документация [экраны и шрифт](../../../Docs/StartArchiveMenu.md)
MainScreen:     incbin "../../../Tools/Disasm/Extracted/Archived/45_RUN.C.sectors.bin", #03DD, #1B00
ShadowScreen:   incbin "../../../Tools/Disasm/Extracted/Archived/45_RUN.C.sectors.bin", #1EDD, #1B00
Font:           incbin "../../../Tools/Disasm/Extracted/Archived/45_RUN.C.sectors.bin", #39DD, #00F0
MarkerGlyph:    incbin "../../../Tools/Disasm/Extracted/Archived/45_RUN.C.sectors.bin", #3ACD, #0008
                incbin "../../../Tools/Disasm/Extracted/Archived/45_RUN.C.sectors.bin", #3AD5, #0208
                endmodule
