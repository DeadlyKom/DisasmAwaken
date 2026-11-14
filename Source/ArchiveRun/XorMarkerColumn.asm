                module ArchiveRun
                module XorMarkerColumn
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; наложение восьми строк знака больше из исходного шрифта
                ; In:
                ;   HL - первый байт стрелки на выровненной знакоместной строке
                ; Out:
                ;   восемь байтов растра изменены XOR, HL и DE продвинуты
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; выбор исходного глифа и обработка восьми экранных строк
Entry:          LD DE, @ArchiveRunImages.MarkerGlyph
                LD B, @ArchiveRunConst.GlyphHeight
NextRow:        LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC H
                DJNZ @ArchiveRun.XorMarkerColumn.NextRow

                RET

                endmodule
                endmodule
