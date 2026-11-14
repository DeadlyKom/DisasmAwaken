                module Station
                module GlyphBottomError
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
                ; -----------------------------------------
                ; Возврат кода 1 при верхней строке глифа не меньше 185
                ; исходная запись 4, файловые смещения #4E88..#4E8C
                ; In:
                ;   AF - F от сравнения физического Y с 185
                ;   SP - FGlyphFrame, подготовленный DrawGlyph
                ; Out:
                ;   HL, DE, BC восстановлены из кадра, AF задаёт статус, A=1, входной F сохраняется
                ;   HL', DE', BC', AF' восстановлены из кадра, IX, IY, I, IM и IFF сохраняются
                ;   SP увеличен на #10 после RET, R получает 13 M1
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', R
                ; Note:
                ;   RAM не записывается, семь сохранённых слов и внешний возврат только читаются
                ;   общий выход использует ReturnGlyph.Status либо ReturnGlyph.Entry, дополнительный адрес возврата не создаётся
                ;   IX, IY, I и IFF сохраняются, пиксели не записываются, самостоятельный CALL без кадра недопустим
                ; -----------------------------------------
                ; возврат кода нижней границы с сохранением флагов предшествующего CP
Entry:          LD A, @GlyphStatus.Vertical
                JP @Station.ReturnGlyph.Status

                endmodule
                endmodule
