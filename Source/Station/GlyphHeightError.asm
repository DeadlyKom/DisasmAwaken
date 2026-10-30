                module Station
                module GlyphHeightError
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; Возврат кода 2 при достижении относительной высоты текстового окна
; исходная запись 4, файловые смещения #4E6B..#4E70
; In:
;   AF - A проверенная относительная строка
;   SP - FGlyphFrame, подготовленный DrawGlyph
; Out:
;   A=2, F от AND входного A
;   обычные и альтернативные регистры восстановлены общим выходом, SP увеличен на #10 после RET
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра
; Note:
;   общий выход использует ReturnGlyph.Status либо ReturnGlyph.Entry, дополнительный адрес возврата не создаётся
;   IX, IY, I и IFF сохраняются, пиксели не записываются, самостоятельный CALL без кадра недопустим
; -----------------------------------------
                ; подготовка флагов отказа по относительной высоте без изменения сохранённого кадра
Entry:          AND A
                LD A, @GlyphStatus.Height
                JP @Station.ReturnGlyph.Status

                endmodule
                endmodule
