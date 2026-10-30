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
;   A=1, входной F сохраняется
;   обычные и альтернативные регистры восстановлены общим выходом, SP увеличен на #10 после RET
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра
; Note:
;   общий выход использует ReturnGlyph.Status либо ReturnGlyph.Entry, дополнительный адрес возврата не создаётся
;   IX, IY, I и IFF сохраняются, пиксели не записываются, самостоятельный CALL без кадра недопустим
; -----------------------------------------
                ; возврат кода нижней границы с сохранением флагов предшествующего CP
Entry:          LD A, @GlyphStatus.Vertical
                JP @Station.ReturnGlyph.Status

                endmodule
                endmodule
