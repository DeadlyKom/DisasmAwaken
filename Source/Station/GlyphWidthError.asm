                module Station
                module GlyphWidthError
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; Возврат кода 3 при переполнении или достижении относительной ширины окна
; исходная запись 4, файловые смещения #4E71..#4E76
; In:
;   AF - A проверенная байтовая сумма ширин
;   SP - FGlyphFrame, подготовленный DrawGlyph
; Out:
;   A=3, F от AND входного A
;   обычные и альтернативные регистры восстановлены общим выходом, SP увеличен на #10 после RET
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра
; Note:
;   общий выход использует ReturnGlyph.Status либо ReturnGlyph.Entry, дополнительный адрес возврата не создаётся
;   IX, IY, I и IFF сохраняются, пиксели не записываются, самостоятельный CALL без кадра недопустим
; -----------------------------------------
                ; подготовка флагов отказа по байтовой сумме ширин
Entry:          AND A
                LD A, @GlyphStatus.Width
                JP @Station.ReturnGlyph.Status

                endmodule
                endmodule
