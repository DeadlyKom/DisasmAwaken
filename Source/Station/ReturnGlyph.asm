                module Station
                module ReturnGlyph
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; Общий успешный выход и восстановление сохранённого кадра регистров глифа
; исходная запись 4, файловые смещения #5514..#5520
; In:
;   SP - FGlyphFrame с сохранёнными регистрами и исходным адресом возврата
;   Entry формирует успех, дополнительный вход Status принимает готовый AF статуса
; Out:
;   Entry возвращает A=0,F=#45, Status возвращает переданный AF
;   HL, DE, BC и альтернативные регистры восстановлены из кадра, SP увеличен на #10 после RET
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра
; Note:
;   сначала возвращается альтернативный AF, затем альтернативные HL,BC,DE и основной набор через EXX
;   IX, IY, I и IFF сохраняются, прямой CALL без кадра DrawGlyph недопустим
; -----------------------------------------
                ; формирование успешного статуса после вывода либо допустимого пропуска глифа
Entry:          XOR A
                SCF
                ; восстановление обоих наборов общих регистров и альтернативного AF из FGlyphFrame
Status:         EX AF, AF'
                ; восстановление FGlyphFrame.SavedAFAlt перед возвратом статуса в основной AF
                POP AF
                EX AF, AF'
                ; восстановление FGlyphFrame.SavedHLAlt, SavedBCAlt и SavedDEAlt
                POP HL
                POP BC
                POP DE
                EXX
                ; восстановление FGlyphFrame.SavedHL, SavedBC и SavedDE после обмена наборов
                POP HL
                POP BC
                POP DE
                ; возврат по FGlyphFrame.ReturnAddress, весь шестнадцатибайтовый кадр снят со стека
                RET

                endmodule
                endmodule
