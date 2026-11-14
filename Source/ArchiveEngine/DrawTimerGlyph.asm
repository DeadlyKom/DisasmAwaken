                module ArchiveEngine
                module DrawTimerGlyph
                ; Документация [цифры таймера](../../Docs/ArchiveEngineTimerRaster.md)
                ; -----------------------------------------
                ; наложение одной цифры маской AND и рисунком OR с сохранением фона
                ; In:
                ;   HL - первый байт назначения, DE - начало пар маска и рисунок
                ;   AF - A, число строк, IX - первый байт сохраняемого фона этой цифры
                ; Out:
                ;   HL и DE продвинуты за последние обработанные строки, IX сдвинут на два на строку
                ;   A равен 0, BC содержит шаг растра
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; сохранение исходного фона и наложение очередной пары маски и рисунка
Entry:          EX AF, AF'
                LD A, (HL)
                LD (IX + #00), A
                INC IX
                INC IX
                LD A, (DE)
                AND (HL)
                LD (HL), A
                INC DE
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE

                ; переход к следующей строке против направления рабочего растра
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                OR A
                SBC HL, BC
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.DrawTimerGlyph.Entry                      ; переход, если остались строки цифры

                RET

                endmodule
                endmodule
