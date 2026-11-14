                module ArchiveRun
                module XorMenuText
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; наложение строки с нулевым терминатором исходным шрифтом
                ; In:
                ;   IX - начало строки, Cursor - адрес первого экранного знакоместа
                ; Out:
                ;   подпись изменена XOR, IX указывает на терминатор, Cursor восстановлен
                ; Corrupt:
                ;   HL, DE, AF, IX
                ; Note:
                ;   младший байт адреса увеличивается без переноса, строки меню помещаются в одной строке экрана
                ; -----------------------------------------
                ; сохранение начального адреса строки
Entry:          LD HL, (@ArchiveRunState.Menu.Cursor)
                PUSH HL

                ; проверка терминатора и выбор восьми строк глифа
NextGlyph:      LD A, (IX + #00)
                OR A
                JR Z, @ArchiveRun.FinishMenuText.Entry                          ; переход, если найден нулевой терминатор, восстановить начало строки

                INC IX
                SUB @ArchiveRunConst.GlyphBaseCode
                LD L, A
                LD H, #00
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD DE, @ArchiveRunImages.Font
                ADD HL, DE
                LD DE, (@ArchiveRunState.Menu.Cursor)

                ; развёрнутое XOR наложение восьми строк глифа
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC D

                ; продвижение к следующему экранному столбцу
                LD HL, @ArchiveRunState.Menu.Cursor
                INC (HL)
                JR @ArchiveRun.XorMenuText.NextGlyph

                endmodule
                endmodule
