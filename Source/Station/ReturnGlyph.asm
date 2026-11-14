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
                ;   HL, DE, BC восстановлены из кадра, AF через Entry равен 0045, через Status равен переданному AF
                ;   HL', DE', BC', AF' восстановлены из кадра, IX, IY, I, IM и IFF сохраняются
                ;   SP увеличен на #10 после RET, R получает 13 M1 через Entry либо 11 M1 через Status
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', R
                ; Note:
                ;   RAM не записывается, семь сохранённых слов и внешний возврат только читаются
                ;   сначала возвращается альтернативный AF, затем альтернативные HL, BC, DE и основной набор через EXX
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
